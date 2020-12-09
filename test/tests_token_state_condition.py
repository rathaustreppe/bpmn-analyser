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

    @pytest.mark.skip('Cannot program a missing operator in source code. It will'
                      'print an error.')
    def test_operator_not_implemented(self):
        token = RunningToken(attributes={'attr': 42})
        condition = TokenStateCondition(lambda t: t.attr < 41)
        with pytest.raises(SyntaxError):
            condition.check_condition(token=token)


    # Those test refer to strings as conditions. As long we use python functions
    # instead of string we dont need them. But perhaps when conditions are defined
    # in the BPMN-diagram we might need them.
    # def test_appending_space(self):
    #     token = RunningToken(attributes={'attr': 43})
    #     condition = TokenStateCondition(condition='t.attr==43 ') #notice space at end of string
    #     assert condition.check_condition(token=token)
    #
    # def test_space_after_operator(self):
    #     token = RunningToken(attributes={'attr': 43})
    #     condition = TokenStateCondition(condition='t.attr== 43') #notice space after operator
    #     assert condition.check_condition(token=token)
    #
    # def test_space_after_attribute(self):
    #     token = RunningToken(attributes={'attr': 43})
    #     condition = TokenStateCondition(condition='t.attr ==43') #notice space at end of attribute
    #     assert condition.check_condition(token=token)
    #
    # def test_space_at_beginning(self):
    #     token = RunningToken(attributes={'attr': 43})
    #     condition = TokenStateCondition(condition=' t.attr==43')  # notice space at beginning of string
    #     assert condition.check_condition(token=token)
    #
    # def test_true_value(self):
    #     token = Token(attributes={'hungry': True})
    #     condition = TokenStateCondition(condition='t.hungry==True')
    #     assert condition.check_condition(token=token)
    #
    # def test_false_value(self):
    #     token = Token(attributes={'hungry': False})
    #     condition = TokenStateCondition(condition='t.hungry==False')
    #     assert condition.check_condition(token=token)
    #
    # def test_two_rules(self):
    #     token = Token(attributes={'a': 0, 'b':42})
    #     condition = TokenStateCondition(condition="t.a == 0 and t.b != 41")
    #     assert condition.check_condition(token=token)