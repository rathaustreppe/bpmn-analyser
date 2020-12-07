import pytest

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


