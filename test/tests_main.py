import unittest
import pytest

import sys
import os
sys.path.append(os.getcwd())

# data structures
from test.tests_token import TestToken
from test.tests_token_state_condition import TestTokenStateCondition
from test.tests_token_state_modification import TestTokenStateModication
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
from test.tests_rule_finder import TestRuleFinder

# loops and gateways
from test.tests_gateways import TestGateway
from test.tests_loop import TestLoop

# diagram processing algorithm
from test.tests_graph_pointer import TestGraphPointer

# integration tests
from test.tests_integration_bill_process import TestIntegrationBillProcess

if __name__ == '__main__':
    unittest.main()
