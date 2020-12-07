import pytest

from src.exception.token_state_errors import MissingAttributeInTokenError
from src.models.running_token import RunningToken
from src.models.token import Token
from src.models.token_state_condition import TokenStateCondition, Operators
from src.models.token_state_modification import TokenStateModification
from src.models.token_state_rule import TokenStateRule


class TestTokenStateModication():

    def test_empty_condition_single_modification(self, example_running_token):
        # no conditions but single modifications
        tsm = TokenStateModification(modification="t.k1 = 'v42'")
        tsr = TokenStateRule(state_conditions=[],
                             state_modifications=[tsm])
        ret = tsr.check_and_modify(token=example_running_token)

        tsm.change_token(token=example_running_token)
        assert ret == example_running_token

    def test_empty_condition_multiple_modification(self, example_running_token):
        tsm1 = TokenStateModification(modification="t.k1 = 42")
        tsm2 = TokenStateModification(modification="t.k2 = 43")
        tsr = TokenStateRule(state_conditions=[],
                             state_modifications=[tsm1, tsm2])
        ret = tsr.check_and_modify(token=example_running_token)

        tsm1.change_token(token=example_running_token)
        tsm2.change_token(token=example_running_token)
        assert ret == example_running_token


    def test_increment_int(self):
        key = 'k'
        value = 0
        token = RunningToken(attributes={key: value})
        condition = TokenStateCondition(condition="t.k == 0")
        modification = TokenStateModification(modification="t.k += 1")
        tsr = TokenStateRule(state_conditions=[condition],
                             state_modifications=[modification])
        return_token = tsr.check_and_modify(token=token)
        assert return_token[key] == 1  # 0++ => 1

    def test_wrong_attribute(self):
        token = RunningToken(attributes={'a': 1})
        tsm = TokenStateModification(modification='t.b = 1')
        tsr = TokenStateRule(state_conditions = [],
                             state_modifications=[tsm])

        with pytest.raises(MissingAttributeInTokenError):
            tsr.check_and_modify(token=token)

    def test_f_string(self):
        token = RunningToken(attributes={'a': 0})
        val = 42
        tsm = TokenStateModification(modification=f't.a = {val}')
        tsm.change_token(token=token)
        assert token.a == val