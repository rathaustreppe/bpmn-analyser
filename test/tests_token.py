import copy

import pytest

from src.models.token import Token
from src.models.token_state_modification import \
    TokenStateModification


class TestToken:

    def test_new_attribute(self, empty_token):
        v1 = 'v1'
        k1 = 'k1'
        empty_token.new_attribute(key=k1, value=v1)
        r = empty_token.get_attribute(key=k1)
        assert r == v1

    def test_new_attribute2(self, empty_token):
        v1, k1 = 'v1', 'k1'
        v2, k2 = 'v2', 'k2'
        empty_token.new_attribute(key=k1, value=v1)
        empty_token.new_attribute(key=k2, value=v2)
        r1 = empty_token.get_attribute(key=k1)
        r2 = empty_token.get_attribute(key=k2)
        assert v1 == r1
        assert v2 == r2

    def test_new_attribute3(self, empty_token):
        # trying to override existing attribute with
        # new_attribute() - should not work
        k1, v1 = 'k1', 'v1'
        v2 = 'v2'
        empty_token.new_attribute(key=k1, value=v1)
        r1 = empty_token.get_attribute(key=k1)
        empty_token.new_attribute(key=k1, value=v2)
        r2 = empty_token.get_attribute(key=k1)
        assert v1 == r1 == r2

    def test_new_attribute_none(self, empty_token):
        k1, v1 = 'k1', None
        empty_token.new_attribute(key=k1, value=v1)
        r = empty_token.get_attribute(key=k1)
        assert r is None

    def test_override_value(self, empty_token):
        v1 = 'v1'
        k1 = 'k1'
        v2 = 'v2'
        empty_token.new_attribute(key=k1, value=v1)
        tsm = TokenStateModification(key=k1, value=v2)
        empty_token.change_value(modification=tsm)
        r = empty_token.get_attribute(key=k1)
        assert v2 == r

    def test_change_value_not_present(self, empty_token):
        # changing value of non existing key
        k1 = 'k1'
        v1 = 'v1'
        with pytest.raises(RuntimeError):
            tsm = TokenStateModification(key=k1, value=v1)
            empty_token.change_value(modification=tsm)

    def test_get_nonexisting_key(self, empty_token):
        with pytest.raises(KeyError):
            empty_token.get_attribute(key='k42')

    def test_not_contains_syntax(self, empty_token):
        assert 'k42' not in empty_token

    def test_contains_syntax(self, example_token):
        assert 'k1' in example_token

    def test_equal_reference(self, example_token):
        token_copy = example_token
        assert token_copy == example_token

    def test_equal_deepcopy_token(self, example_token):
        token_copy = copy.deepcopy(example_token)
        assert token_copy == example_token

    def test_equal_copy_token(self, example_token):
        token_copy = copy.copy(example_token)
        assert token_copy == example_token

    def test_equal_new_token(self, example_token):
        # same keys and values from examples token above
        attributes = {'k1': 'v1', 'k2': 'v2', 'k3': 'v3'}
        token2 = Token(attributes=attributes)
        assert token2 == example_token

    def test_equal_both_empty(self, example_token):
        empty1 = example_token
        empty2 = copy.copy(empty1)
        assert empty1 == empty2

    def test_equal_one_empty(self, empty_token, example_token):
        assert empty_token != example_token

    def test_equal_additional_key(self):
        attributes1 = {'k1': 'v1', 'k2': 'v2', 'k3': 'v3'}
        attributes2 = {'k1': 'v1', 'k2': 'v2'}
        token1 = Token(attributes=attributes1)
        token2 = Token(attributes=attributes2)
        assert token1 != token2

    def test_equal_different_value(self, example_token):
        token2 = copy.deepcopy(example_token)
        tsm = TokenStateModification(key='k1', value='v42')
        token2.change_value(modification=tsm)
        assert token2 != example_token

    def test_equal_two_none_values(self):
        attributes = {'k1': None}
        token1 = Token(attributes=attributes)
        token2 = Token(attributes=attributes)
        assert token1 == token2

    def test_equal_one_none_value(self):
        attributes1 = {'k1': None}
        attributes2 = {'k1': 'v1'}
        token1 = Token(attributes=attributes1)
        token2 = Token(attributes=attributes2)
        assert token1 != token2

    def test_increment(self):
        key = 'k1'
        attributes = {key: '0'}
        token = Token(attributes=attributes)
        tsm = TokenStateModification(key=key, value='++')

        token.change_value(modification=tsm)
        assert token.attributes[key] == '1'
