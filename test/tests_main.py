import unittest
import pytest

import sys
import os
sys.path.append(os.getcwd())

# local imports
from test.tests_token import TestToken
from test.tests_token_state_rule import TestTokenStateRule
from test.tests_bpmn_factory import TestBPMNFactory

if __name__ == '__main__':
    unittest.main()
