import unittest
import pytest

from src.token import Token

class TestToken:
    @pytest.fixture(autouse=True)
    def empty_token(self):
        self.t = Token()

    def test_new_attribute(self):
        v1 = 'v1'
        k1 = 'k1'
        self.t.new_attribute(k1, v1)
        r =self.t.get_attribute(k1)
        assert r == v1

    def test_new_attribute2(self):
        v2 = 'v2'
        k2 = 'k2'
        self.t.new_attribute(k2, v2)
        r = self.t.get_attribute(k2)
        assert v2 == r

    def test_new_attribute_override(self):
        k2 = 'k2'
        v3 = 'v3'
        self.t.new_attribute(k2, v3)
        r = self.t.get_attribute(k2)
        assert v3 == r

    def test_change_value(self):
        v1 = 'v1'
        k1 = 'k1'
        v2 = 'v2'
        self.t.new_attribute(k1, v1)
        self.t.change_value(k1,v2)
        r = self.t.get_attribute(k1)
        assert v2 == r

    def test_change_value_not_present(self):
        print(self.t)
        k1 = 'k1'
        v2 = 'v2'
        self.t.change_value(k1,v2)




























if __name__ == '__main__':
    unittest.main()
