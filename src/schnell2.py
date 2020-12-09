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

    # tsc = TokenStateCondition(lambda t: t.a == 2 and t.b == 2)
    # print(tsc.check_condition(token=token))

    def _(t): t.a = 22
    def a(t): return t.a == 2 and t.b == 2


    tsm = TokenStateModification(_)
    tsm.change_token(token=token)

    def _(t):
        t.a = 42
        t.b = 33
    tsm2 = TokenStateModification(_)
    tsm2.change_token(token=token)

    tsm.change_token(token=token)

    tsm3 = TokenStateModification(attribute = 'a', value = 42)

    print(token)
