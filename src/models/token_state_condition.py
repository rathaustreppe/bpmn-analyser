from enum import Enum
from typing import Any

from pedantic import pedantic_class

from src.models.token import Token


class Operators(Enum):
    EQUALS = '=='


@pedantic_class
class TokenStateCondition:
    """
    This class defines a single condition that is checked
    before a token state can change.
    """
    def __init__(self, tok_attribute: str = '',
                 operator: Operators = Operators.EQUALS,
                 tok_value: Any = None) -> None:
        """
        Example: If you want to define the condition, where
        the token attribute foo has to be bar, then you
        define the condition:
        TokenStateCondition(tok_attribute = 'foo',
            operator = '=', tok_value='bar')
        Args:
            tok_attribute (str): is the key of the attribute dict of a token
            operator (Operators): '==' compares equality.
            tok_value (Any): Defines the value the _tok_attribute has to have.
        """
        self._tok_attribute = tok_attribute
        self._operator = operator
        self._tok_value = tok_value

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
        if self._tok_attribute == '':
            raise KeyError(
                f'tok_attribute cannot be empty string. Accessing token {token}'
                f' while checking TokenStateCondition: {self}')

        if self._tok_attribute not in token:
            raise KeyError(
                f'Token {token} does not have attribute {self._tok_attribute}')

        val = token.get_attribute(key=self._tok_attribute)
        if val == self._tok_value:
            return True
        else:
            return False

    def __str__(self) -> str:
        return f'{self._tok_attribute}{self._operator.value}{self._tok_value}'

    def __repr__(self) -> str:
        return self.__str__()
