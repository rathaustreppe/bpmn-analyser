import unittest
import pytest

import sys
import os
sys.path.append(os.getcwd())

# unit tests
from test.tests_token import TestToken
from test.tests_token_state_condition import TestTokenStateCondition
from test.tests_bpmn_factory import TestBPMNFactory
from test.tests_xml_reader import TestXMLReader
from test.tests_graph_pointer import TestGraphPointer
from test.tests_token_state_rule import TestTokenStateRule
from test.tests_synonym_composite import TestSynonymComposite

# integration tests of unit compositions
from test.tests_integration import TestIntegration

if __name__ == '__main__':
    unittest.main()
