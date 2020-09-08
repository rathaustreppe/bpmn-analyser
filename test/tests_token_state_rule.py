import pytest

from src.models.token import Token
from src.models.token_state_rule import TokenStateRule
from src.models.token_state_rule import Operators


class TestTokenStateRule:
    @pytest.fixture(autouse=True)
    def empty_rule(self):
        self.empty_rule = \
            TokenStateRule(
                tok_attribute='',
                operator=Operators.EQUALS,
                tok_value=None)

    @pytest.fixture(autouse=True)
    def example_rule(self):
        self.example_rule = TokenStateRule(
            tok_attribute='k1',
            operator=Operators.EQUALS,
            tok_value='v1')

    @pytest.fixture(autouse=True)
    def example_token(self):
        attributes = {'k1': 'v1', 'k2': 'v2', 'k3': 'v3'}
        self.example_token = Token(attributes=attributes)

    def test_operator_not_implemented(self):
        # even with enums, you never know...
        with pytest.raises(Exception):
            TokenStateRule(tok_attribute='',
                           operator=Operators.XYZ,
                           tok_value=None)

    def test_empty_token_attribute(self, empty_token):
        # empty token attribute raises error
        with pytest.raises(KeyError):
            self.empty_rule.check_rule(
                token=empty_token)

    def test_nonexisting_token_attribute_in_rule(self, empty_token):
        # apply token_attribute in rule that does not
        # exist in token
        with pytest.raises(KeyError):
            self.example_rule.check_rule(
                token=empty_token)

    def test_rule_with_none_value(self):
        # rule checks for none-value
        rule = TokenStateRule(tok_attribute='k1',
                              operator=Operators.EQUALS,
                              tok_value=None)
        token = Token(attributes={'k1': None})
        assert rule.check_rule(token=token)

    def test_rule_with_none_value_2(self):
        # rule checks for none-value but is wrong with that
        rule = TokenStateRule(tok_attribute='k1',
                              operator=Operators.EQUALS,
                              tok_value=None)
        token = Token(attributes={'k1': 'v1'})
        assert rule.check_rule(token=token) is False

    def test_rule_with_none_value_3(self):
        # rule checks for value but finds none
        rule = TokenStateRule(tok_attribute='k1',
                              operator=Operators.EQUALS,
                              tok_value='v1')
        token = Token(attributes={'k1': None})
        assert rule.check_rule(token=token) is False

    def test_rule_normal(self):
        assert self.example_rule.check_rule(
            token=self.example_token)
