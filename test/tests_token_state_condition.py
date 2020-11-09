import pytest

from src.exception.token_state_errors import \
    MissingOperatorInConditionError, \
    MissingAttributeInConditionError, MissingValueInConditionError, \
    MissingAttributeInTokenError
from src.models.token import Token
from src.models.token_state_condition import Operators, \
    TokenStateCondition


class TestTokenStateCondition:
    @pytest.fixture(autouse=True)
    def empty_rule(self):
        self.empty_rule = \
            TokenStateCondition(
                tok_attribute='',
                operator=Operators.EQUALS,
                tok_value='')

    @pytest.fixture(autouse=True)
    def example_rule(self):
        self.example_rule = TokenStateCondition(
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
            TokenStateCondition(tok_attribute='',
                                operator=Operators.XYZ,
                                tok_value=None)

    def test_empty_token_attribute(self, empty_token):
        # empty token attribute raises error
        with pytest.raises(MissingAttributeInTokenError):
            self.empty_rule.check_condition(
                token=empty_token)

    def test_nonexisting_token_attribute_in_rule(self, empty_token):
        # apply token_attribute in rule that does not
        # exist in token
        with pytest.raises(MissingAttributeInTokenError):
            self.example_rule.check_condition(
                token=empty_token)

    def test_rule_normal(self, example_token):
        assert self.example_rule.check_condition(
            token=self.example_token)

    def test_from_string_equals(self):
        condition = 'k1==v1'
        tsc = TokenStateCondition.from_string(condition=condition)
        assert tsc._tok_attribute == 'k1'
        assert tsc._operator == Operators.EQUALS
        assert tsc._tok_value == 'v1'

    def test_from_string_different_lenghts(self):
        # testing all combinations of different string lengths
        short_a = 'a'
        long_a = 'aaa'
        empty = ''
        attributes = [short_a, long_a, empty]

        short_val = '1'
        long_val = '1000'
        values = [short_val, long_val, empty]

        equals = Operators.EQUALS
        greaterthen = Operators.GREATER_THEN
        operators = [equals, greaterthen]

        for attr in attributes:
            for operator in operators:
                for value in values:
                    if attr == empty:
                        with pytest.raises(MissingAttributeInConditionError):
                            TokenStateCondition.from_string(
                                condition=f'{attr}{operator.value}{value}')
                    elif value == empty:
                        with pytest.raises(MissingValueInConditionError):
                            TokenStateCondition.from_string(
                                condition=f'{attr}{operator.value}{value}')
                    else:
                        tsc = TokenStateCondition.from_string(
                            condition=f'{attr}{operator.value}{value}')
                        assert tsc._tok_attribute == attr
                        assert tsc._operator == operator
                        assert tsc._tok_value == value

    def test_from_string_greaterthen(self):
        condition = 'attr>42'
        tsc = TokenStateCondition.from_string(condition=condition)
        assert tsc._tok_attribute == 'attr'
        assert tsc._operator == Operators.GREATER_THEN
        assert tsc._tok_value == '42'

    def test_greater_then(self):
        token = Token(attributes={'attr': '43'})
        condition = 'attr>42'
        tsc = TokenStateCondition.from_string(condition=condition)

        assert tsc.check_condition(token=token) is True

    def test_smaller_then(self):
        token = Token(attributes={'attr': '42'})
        condition = 'attr<43'
        tsc = TokenStateCondition.from_string(condition=condition)
        assert tsc.check_condition(token=token) is True

    def test_from_string_operator_not_implemented(self):
        condition = 'attr(42'
        with pytest.raises(MissingOperatorInConditionError):
            TokenStateCondition.from_string(condition=condition)

    def test_from_string_appending_space(self):
        token = Token(attributes={'attr': '43'})
        condition = 'attr==43 ' #notice space at end of string
        tsc = TokenStateCondition.from_string(condition=condition)
        assert tsc.check_condition(token=token) is True

    def test_from_string_space_after_operator(self):
        token = Token(attributes={'attr': '43'})
        condition = 'attr== 43' #notice space after operator
        tsc = TokenStateCondition.from_string(condition=condition)
        assert tsc.check_condition(token=token) is True

    def test_from_string_space_after_attribute(self):
        token = Token(attributes={'attr': '43'})
        condition = 'attr ==43' #notice space at end of attribute
        tsc = TokenStateCondition.from_string(condition=condition)
        assert tsc.check_condition(token=token) is True

    def test_from_string_space_at_beginning(self):
        token = Token(attributes={'attr': '43'})
        condition = ' attr==43'  # notice space at beginning of string
        tsc = TokenStateCondition.from_string(condition=condition)
        assert tsc.check_condition(token=token) is True

    def test_from_string_space_in_attribute_name(self):
        token = Token(attributes={'attr attr': '43'})
        condition = 'attr attr==43'  # notice space inside attribute
        tsc = TokenStateCondition.from_string(condition=condition)
        assert tsc.check_condition(token=token) is True

    def test_from_string_true_value(self):
        token = Token(attributes={'hungry': True})
        condition = 'hungry==True'
        tsc = TokenStateCondition.from_string(condition=condition)
        assert tsc.check_condition(token=token) is True

    def test_from_string_false_value(self):
        token = Token(attributes={'hungry': False})
        condition = 'hungry==False'
        tsc = TokenStateCondition.from_string(condition=condition)
        assert tsc.check_condition(token=token) is True

