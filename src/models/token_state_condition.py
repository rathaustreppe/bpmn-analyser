import logging
import re
from enum import Enum
from typing import Any, Union

from pedantic import pedantic_class

from src.exception.token_state_errors import \
    MissingOperatorInConditionError, \
    MissingAttributeInConditionError, MissingValueInConditionError, \
    MissingAttributeInTokenError
from src.exception.wrong_type_errors import WrongTypeError
from src.models.token import Token


class Operators(Enum):
    # list of operators that python can evaluate
    EQUALS = '=='
    GREATER_THEN = '>'
    SMALLER_THEN = '<'
    INCREMENT = '++'


@pedantic_class
class TokenStateCondition:
    """
    This class defines a single condition that is checked
    before a RunningToken state can change.

    TokenStateCondition(condition="t.k1 == 'v1'")
    """

    def __init__(self, condition: str) -> None:
        """
        Example: If you want to define the condition, where
        the token attribute foo has to be bar, then you
        define the condition:
        TokenStateCondition(tok_attribute = 'foo',
            operator = '=', tok_value='bar')
        """
        if condition == '':
            raise TypeError('condition cannot be empty')
        self.condition = condition

    def check_condition(self, token: Token) -> bool:
        """
        Takes a token and checks if its pre-defined
        condition is true or false wth the given token.
        Args:
            token (Token): a Token object you want to check

        Returns:
             bool: True if condition applied to token is okay.
             False if token does not comply with condition
        """
        t = token
        try:
           return eval(self.condition)
        except NameError:
            msg = f'You probably forget to put >>t.<< at beginning of every attribute. Got condition: {self.condition}'
            logging.error(msg)
            raise NameError(msg)
        except AttributeError:
            msg = f'Your defined attribute is not present in the token. Got conition:{self.condition} for token: {token}'
            logging.error(msg)
            raise MissingAttributeInTokenError(token=t, attribute=self.condition)
            # ToDo: Instead of self.condition find out the exact name of the attribute from the error message
        except SyntaxError:
            msg = f'TokenStateCondition {self} has a syntax error'
            logging.error(msg)
            raise SyntaxError(msg)

    def __str__(self) -> str:
        return self.condition

    def __repr__(self) -> str:
        return self.__str__()

    def __eq__(self, other: 'TokenStateCondition') -> bool:
        return self.condition == other.condition
