import copy

import pytest

from src.models.token import Token

class TestToken:
    @pytest.fixture(autouse=True)
    def empty_token(self):
        self.empty_token = Token(attributes=None)

    @pytest.fixture(autouse=True)
    def example_token(self):
        attributes = {'k1': 'v1', 'k2': 'v2', 'k3':'v3'}
        self.example_token = Token(attributes=attributes)

    def test_new_attribute(self):
        v1 = 'v1'
        k1 = 'k1'
        self.empty_token.new_attribute(key=k1, value=v1)
        r =self.empty_token.get_attribute(key=k1)
        assert r == v1

    def test_new_attribute2(self):
        v1, k1 = 'v1','k1'
        v2, k2 = 'v2', 'k2'
        self.empty_token.new_attribute(key=k1, value=v1)
        self.empty_token.new_attribute(key=k2, value=v2)
        r1 = self.empty_token.get_attribute(key=k1)
        r2 = self.empty_token.get_attribute(key=k2)
        assert v1 == r1
        assert v2 == r2

    def test_new_attribute3(self):
        # trying to override existing attribute with
        # new_attribute() - should not work
        k1, v1 = 'k1', 'v1'
        v2 = 'v2'
        self.empty_token.new_attribute(key=k1, value=v1)
        r1 = self.empty_token.get_attribute(key=k1)
        self.empty_token.new_attribute(key=k1, value=v2)
        r2 = self.empty_token.get_attribute(key=k1)
        assert v1 == r1 == r2

    def test_new_attribute_none(self):
        k1, v1 = 'k1', None
        self.empty_token.new_attribute(key=k1, value=v1)
        r = self.empty_token.get_attribute(key=k1)
        assert r is None

    def test_override_value(self):
        v1 = 'v1'
        k1 = 'k1'
        v2 = 'v2'
        self.empty_token.new_attribute(key=k1, value=v1)
        self.empty_token.change_value(key=k1, value=v2)
        r = self.empty_token.get_attribute(key=k1)
        assert v2 == r

    def test_change_value_not_present(self):
        # changing value of non existing key
        k1 = 'k1'
        v1 = 'v1'
        with pytest.raises(RuntimeError):
            self.empty_token.change_value(key=k1, value=v1)

    def test_equal_reference(self):
        token_copy = self.example_token
        assert token_copy == self.example_token

    def test_equal_deepcopy_token(self):
        token_copy = copy.deepcopy(self.example_token)
        assert token_copy == self.example_token

    def test_equal_copy_token(self):
        token_copy = copy.copy(self.example_token)
        assert token_copy == self.example_token

    def test_equal_new_token(self):
        # same keys and values from example token above
        attributes = {'k1': 'v1', 'k2': 'v2', 'k3':'v3'}
        token2 = Token(attributes=attributes)
        assert token2 == self.example_token

    def test_equal_both_empty(self):
        empty1 = self.example_token
        empty2 = copy.copy(empty1)
        assert empty1 == empty2

    def test_equal_one_empty(self):
        assert self.empty_token != self.example_token

    def test_equal_additional_key(self):
        attributes1 = {'k1': 'v1', 'k2': 'v2', 'k3':'v3'}
        attributes2 = {'k1': 'v1', 'k2': 'v2'}
        token1 = Token(attributes=attributes1)
        token2 = Token(attributes=attributes2)
        assert token1 != token2

    def test_equal_different_value(self):
        token2 = copy.deepcopy(self.example_token)
        token2.change_value(key='k1', value='v42')
        assert token2 != self.example_token

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
