import pytest

from src.exception.token_state_errors import MissingAttributeInTokenError
from src.models.running_token import RunningToken
from src.models.token import Token
from src.models.token_state_condition import TokenStateCondition
from src.converter.bpmn_models.gateway.branch_condition import Operators
from src.models.token_state_modification import TokenStateModification
from src.models.token_state_rule import TokenStateRule


class TestTokenStateModication():

    def test_empty_condition_single_modification(self, example_running_token):
        # no conditions but single modifications
        def a(t): t.k1 = 'v42'
        tsm = TokenStateModification(a)
        tsm.change_token(token=example_running_token)

        assert example_running_token.k1 == 'v42'

    def test_empty_condition_multiple_modification(self, example_running_token):
        def m1(t):
            t.k1 = 42
            t.k2 = 43
        tsm1 = TokenStateModification(m1)
        tsr = TokenStateRule(modification=tsm1)
        ret = tsr.check_and_modify(token=example_running_token)

        tsm1.change_token(token=example_running_token)
        assert ret == example_running_token


    def test_increment_int(self):
        key = 'k'
        value = 0
        token = RunningToken(attributes={key: value})
        condition = TokenStateCondition(lambda t: t.k == 0)
        def m1(t): t.k += 1
        modification = TokenStateModification(m1)
        tsr = TokenStateRule(condition=condition,
                             modification=modification)
        return_token = tsr.check_and_modify(token=token)
        assert return_token[key] == 1  # 0++ => 1

    def test_wrong_attribute(self):
        token = RunningToken(attributes={'a': 1})
        def m(t): t.b = 1
        tsm = TokenStateModification(m)
        tsr = TokenStateRule(modification=tsm)

        with pytest.raises(MissingAttributeInTokenError):
            tsr.check_and_modify(token=token)

    def test_f_string(self):
        token = RunningToken(attributes={'a': 0})
        val = 42
        def m(t): t.a = val
        tsm = TokenStateModification(m)
        tsm.change_token(token=token)
        assert token.a == val