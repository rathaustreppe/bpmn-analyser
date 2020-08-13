import unittest
import pytest

import sys
import os
sys.path.append(os.getcwd())

from src.models.token import Token

class TestToken:
    @pytest.fixture(autouse=True)
    def empty_token(self):
        self.t = Token(attributes=None) #workaround for pedantic

    def test_new_attribute(self):
        v1 = 'v1'
        k1 = 'k1'
        self.t.new_attribute(key=k1, value=v1)
        r =self.t.get_attribute(key=k1)
        assert r == v1

    def test_new_attribute2(self):
        v2 = 'v2'
        k2 = 'k2'
        self.t.new_attribute(key=k2, value=v2)
        r = self.t.get_attribute(key=k2)
        assert v2 == r

    def test_new_attribute_override(self):
        k2 = 'k2'
        v3 = 'v3'
        self.t.new_attribute(key=k2, value=v3)
        r = self.t.get_attribute(key=k2)
        assert v3 == r

    def test_change_value(self):
        v1 = 'v1'
        k1 = 'k1'
        v2 = 'v2'
        self.t.new_attribute(key=k1, value=v1)
        self.t.change_value(key=k1,value=v2)
        r = self.t.get_attribute(key=k1)
        assert v2 == r

    def test_change_value_not_present(self):
        k1 = 'k1'
        v2 = 'v2'
        with pytest.raises(RuntimeError):
            self.t.change_value(key=k1,value=v2)



























if __name__ == '__main__':
    unittest.main()
