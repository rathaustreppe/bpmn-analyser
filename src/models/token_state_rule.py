
# This class defines a single rule that is checked
# before a token state can change
from src.models.token import Token


class Token_State_Rule:
    def __init__(self, tok_attribute:str = None,
                 operator: str = None,
                 tok_value: all = None):
        self.tok_attribute = tok_attribute
        self.operator = operator
        self.tok_value = tok_value

    def apply_rule(self, t:Token) -> bool:
        val = t.get_attribute(self.tok_attribute)
        if self.operator == '=':
            if val == self.tok_value:
                return True
            else:
                return False
        else:
            print('ERROR Operator', self.operator,
                  'not defined!')