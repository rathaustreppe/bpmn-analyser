import pytest

from src.converter.bpmn_models.gateway.branch_condition import BranchCondition
from src.exception.token_state_errors import MissingOperatorInConditionError
from src.models.running_token import RunningToken


class TestBranchCondition:
    def test_appending_space(self):
        token = RunningToken(attributes={'attr': 43})
        condition = BranchCondition.from_string(condition='attr==43 ') #notice space at end of string
        assert condition.check_condition(token=token)

    def test_space_after_operator(self):
        token = RunningToken(attributes={'attr': 43})
        condition = BranchCondition.from_string(condition='attr== 43') #notice space after operator
        assert condition.check_condition(token=token)

    def test_space_after_attribute(self):
        token = RunningToken(attributes={'attr': 43})
        condition = BranchCondition.from_string(condition='attr ==43') #notice space at end of attribute
        assert condition.check_condition(token=token)

    def test_space_at_beginning(self):
        token = RunningToken(attributes={'attr': 43})
        condition = BranchCondition.from_string(condition=' attr==43')  # notice space at beginning of string
        assert condition.check_condition(token=token)

    def test_true_value(self):
        token = RunningToken(attributes={'hungry': True})
        condition = BranchCondition.from_string(condition='hungry==True')
        assert condition._tok_value is True
        assert condition.check_condition(token=token)

    def test_false_value(self):
        token = RunningToken(attributes={'hungry': False})
        condition = BranchCondition.from_string(condition='hungry==False')
        assert condition._tok_value is False
        assert condition.check_condition(token=token)

    def test_int(self):
        token = RunningToken(attributes={'a': 42})
        condition = BranchCondition.from_string(condition='a==42')
        assert condition._tok_value == 42
        assert condition.check_condition(token=token)

    @pytest.mark.skip(
        'The intended correct behaviour is not so easy to implement'
        'and will be implemented in the future.')
    def test_two_rules(self):
        token = RunningToken(attributes={'a': 0, 'b':42})
        condition = BranchCondition.from_string(condition='a == 0 and b != 41')
        assert condition.check_condition(token=token)

    @pytest.mark.skip(
        'The intended correct behaviour is not so easy to implement'
         'and will be implemented in the future.')
    def test_operator_not_implemented_contains_implemented_operator(self):
        # the operator <!! is not implemented, but < is.
        # Regex will find < and will treat !! as string value
        with pytest.raises(MissingOperatorInConditionError):
            BranchCondition.from_string(condition='attr <!! 41')

    def test_operator_not_implemented(self):
        # the operator h!! is not implemented and does not contain any
        # implemented operators, so regex cannot find anything and will
        # throw an exception.
        with pytest.raises(MissingOperatorInConditionError):
            BranchCondition.from_string(condition='attr h!! 41')
