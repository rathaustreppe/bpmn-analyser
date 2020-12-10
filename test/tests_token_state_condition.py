import pytest

from src.exception.token_state_errors import \
    MissingAttributeInTokenError
from src.models.running_token import RunningToken
from src.models.token import Token
from src.models.token_state_condition import TokenStateCondition


class TestTokenStateCondition:
    @pytest.fixture(autouse=True)
    def example_rule(self):
        self.example_rule = TokenStateCondition(lambda t: t.k1 == 'v1')

    def test_nonexisting_token_attribute_in_rule(self, empty_running_token):
        # apply token_attribute in rule that does not
        # exist in token
        with pytest.raises(MissingAttributeInTokenError):
            self.example_rule.check_condition(token=empty_running_token)

    def test_rule_normal(self, example_running_token):
        # make sure example_rule and example_token match!
        assert self.example_rule.check_condition(token=example_running_token)

    def test_greaterthen(self):
        token = RunningToken(attributes={'attr': 42})
        condition = TokenStateCondition(lambda t: t.attr > 41)
        assert condition.check_condition(token=token)

    def test_smaller_then(self):
        token = RunningToken(attributes={'attr': 42})
        condition = TokenStateCondition(lambda t: t.attr < 43)
        assert condition.check_condition(token=token)

