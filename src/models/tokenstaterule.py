from typing import Any
from pedantic import pedantic


# local file imports
from src.models.token import Token


class TokenStateRule:
    """
    This class defines a single rule that is checked
    before a token state can change.
    """
    @pedantic
    def __init__(self, tok_attribute: str = '',
                 operator: str = '',
                 tok_value: Any = None) -> None:
        """
        Example: If you want to define the rule, where
        the token attribute foo has to be bar, then you
        define the rule:
        TokenStateRule(tok_attribute = 'foo',
            operator = '=', tok_value='bar')
        Args:
            tok_attribute (str): is the key of the attribute dict of a token
            operator (str): '=' compares equalness. The only operator implemented so far.
            tok_value (Any): Defines the value the tok_attribute has to have.
        """
        self.tok_attribute = tok_attribute
        self.operator = operator
        self.tok_value = tok_value

    @pedantic
    def apply_rule(self, token:Token) -> bool:
        val = token.get_attribute(key=self.tok_attribute)
        if self.operator == '=':
            if val == self.tok_value:
                return True
            else:
                return False
        else:
            print('ERROR Operator', self.operator,
                  'not defined!')