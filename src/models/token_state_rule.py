from typing import Any, Optional
from pedantic import pedantic, pedantic_class
from enum import Enum

# local file imports
from src.models.token import Token


class Operators(Enum):
    EQUALS = '=='


@pedantic_class
class TokenStateRule:
    """
    This class defines a single rule that is checked
    before a token state can change.
    """

    def __init__(self, tok_attribute: str = '',
                 operator: Operators = Operators.EQUALS,
                 tok_value: Any = None) -> None:
        """
        Example: If you want to define the rule, where
        the token attribute foo has to be bar, then you
        define the rule:
        TokenStateRule(_tok_attribute = 'foo',
            _operator = '=', _tok_value='bar')
        Args:
            tok_attribute (str): is the key of the attribute dict of a token
            operator (Operators): '=' compares equalness. The only _operator implemented so far.
            tok_value (Any): Defines the value the _tok_attribute has to have.
        """
        self._tok_attribute = tok_attribute
        self._operator = operator
        self._tok_value = tok_value

    def apply_rule(self, token: Token) -> bool:
        """
        Takes a token and and and checks if its pre-defined
        rule is true or false wth the given token.
        Args:
            token (Token): a Token object you want to check

        Returns:
             bool: True if rule applied to token is okay.
             False if token does not comply with rule
        """
        if self._tok_attribute == '':
            raise KeyError(
                f'tok_attribute cannot be empty')

        if not self._tok_attribute in token:
            raise KeyError(
                f'Token {token} does not have attribute {self._tok_attribute}')

        val = token.get_attribute(key=self._tok_attribute)
        if val == self._tok_value:
            return True
        else:
            return False


        # else:
        #     raise RuntimeWarning(f'ERROR: opertor '
        #                          f'{self._operator} '
        #                          f'not implemented')
