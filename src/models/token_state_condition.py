import inspect
import logging
from enum import Enum
from typing import Callable

from pedantic import pedantic

from src.exception.token_state_errors import \
    MissingAttributeInTokenError
from src.models.running_token import RunningToken
from src.models.token import Token


class Operators(Enum):
    # list of operators that python can evaluate
    EQUALS = '=='
    GREATER_THEN = '>'
    SMALLER_THEN = '<'
    INCREMENT = '++'

class TokenStateCondition:
    """
    This class defines a single condition that is checked
    before a RunningToken state can change.
    """

    def __init__(self, condition: Callable[[RunningToken], bool]) -> None:
        self.condition = condition

    @pedantic
    def check_condition(self, token: RunningToken) -> bool:
        """
        Takes a token and checks if its pre-defined
        condition is true or false wth the given token.
        """

        return self.condition(token)
        # except NameError:
        #     msg = f'You probably forget to put >>t.<< at beginning of every attribute. Got condition: {self.condition}'
        #     logging.error(msg)
        #     raise NameError(msg)

        # except SyntaxError:
        #     msg = f'TokenStateCondition {self} has a syntax error'
        #     logging.error(msg)
        #     raise SyntaxError(msg)


    def __str__(self) -> str:
        #return inspect.getsource(self.condition)
        return '>>TokenStateCondition<<'

    def __repr__(self) -> str:
        return self.__str__()

    def __eq__(self, other: 'TokenStateCondition') -> bool:
        return self.condition == other.condition
