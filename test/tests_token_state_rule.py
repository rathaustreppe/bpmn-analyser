import pytest

from src.models.running_token import RunningToken
from src.models.token import Token
from src.models.token_state_condition import TokenStateCondition, Operators
from src.models.token_state_modification import TokenStateModification
from src.models.token_state_rule import TokenStateRule


class TestTokenStateRule:
    @pytest.fixture(autouse=True)
    def empty_rule(self):
        return TokenStateRule(state_conditions=[], state_modifications=[])

    def test_empty_rule_on_empty_token(self, empty_rule, empty_running_token):
        # empty token with empty rule
        ret = empty_rule.check_and_modify(token=empty_running_token)
        assert ret == empty_running_token

    def test_empty_rule_on_token(self, empty_rule, empty_running_token):
        # full token with empty rule
        ret = empty_rule.check_and_modify(token=empty_running_token)
        assert ret == empty_running_token

    def test_empty_condition_single_modification(self, example_running_token):
        # no conditions but single modifications
        k = 'k1'
        v = 'v42'
        modification = TokenStateModification(key=k, value=v)
        tsr = TokenStateRule(state_conditions=[],
                             state_modifications=[modification])
        ret = tsr.check_and_modify(token=example_running_token)
        example_running_token.change_value(modification=modification)
        assert ret == example_running_token

    def test_empty_condition_multiple_modification(self, example_running_token):
        k1, v1 = 'k1', 'v42'
        k2, v2 = 'k2', 'v43'
        modification1 = TokenStateModification(key=k1, value=v1)
        modification2 = TokenStateModification(key=k2, value=v2)
        tsr = TokenStateRule(state_conditions=[],
                             state_modifications=[modification1, modification2])
        ret = tsr.check_and_modify(token=example_running_token)

        example_running_token.change_value(modification=modification1)
        example_running_token.change_value(modification=modification2)
        assert ret == example_running_token

    def test_increment(self):
        key = 'k'
        value = '0'
        token = RunningToken(attributes={key: value})
        condition = TokenStateCondition(tok_attribute=key,
                                        operator=Operators.EQUALS,
                                        tok_value=value)
        modification = TokenStateModification(key=key, value='++')

        tsr = TokenStateRule(state_conditions=[condition],
                             state_modifications=[modification])
        return_token = tsr.check_and_modify(token=token)
        assert return_token[key] == '1'  # 0++ => 1
