import unittest
import pytest

import sys
import os
sys.path.append(os.getcwd())

# unit tests

# data structures
from test.tests_token import TestToken
from test.tests_token_state_condition import TestTokenStateCondition
from test.tests_token_state_rule import TestTokenStateRule
from test.tests_stack import TestStack

# converter
from test.tests_xml_reader import TestXMLReader
from test.tests_bpmn_converter import TestBPMNConverter
from test.tests_bpmn_factory import TestBPMNFactory

# NLP
from test.tests_chunker import TestChunker
from test.tests_synonym_composite import TestSynonymComposite
from test.tests_synonym_cloud import TestSynonymCloud

# integration tests of unit compositions
from test.tests_gateway_stack_handler import TestGatewayStackHandler
from test.tests_graph_pointer import TestGraphPointer
from test.tests_integration import TestIntegration

if __name__ == '__main__':
    unittest.main()
