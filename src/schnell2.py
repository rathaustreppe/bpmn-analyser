import inspect
from typing import TypedDict

from src.models.running_token import RunningToken
from src.models.token import Token
from src.models.token_state_condition import TokenStateCondition
from src.models.token_state_modification import TokenStateModification

if __name__ == '__main__':

    token = RunningToken(attributes={
        'a': 2,
        'b': 2
    })


    def aa(t):
        return t.a == 2
    tsc = TokenStateCondition(condition=aa)


    def ab(t):
        return t.a == 3
    tsc2 = TokenStateCondition(condition=aa)

    print(inspect.getsource(tsc.condition) == inspect.getsource(tsc2.condition))

