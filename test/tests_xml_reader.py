import os
import shutil
import sys

import pytest

from src.converter.bpmn_models.bpmn_enum import BPMNEnum
from src.converter.xml_reader import XMLReader


class TestXMLReader:

    pytest_root = os.path.dirname(os.path.abspath(__file__))
    xml_files = os.path.join(pytest_root,'test_files', 'xml')
    working_dict = os.path.join(pytest_root, 'test_files', 'working_dict')

    # def pytest_root(self):
    #     # should return .../bpmn_analyser/test
    #     self.pytest_root = os.path.dirname(os.path.abspath(__file__))

    @classmethod
    def setup_class(self):
        # copies test files into new folder
        try:
            shutil.copytree(self.xml_files, self.working_dict)
        except (FileExistsError):
            pass
        except (Exception):
            raise

    @classmethod
    def teardown_class(self):
        # deletes folder with test files after tests
        dst_abs = os.path.abspath(self.working_dict)
        shutil.rmtree(dst_abs)
        pass

    @pytest.fixture(autouse=True)
    def xml_reader(self):
        self.xml_reader = XMLReader()

    def read_xml(self, string):
        import xml.etree.ElementTree as ET
        xml_tree = ET.fromstring(string)
        return xml_tree
    
    def test_strip_definitions_def_def(self):
        # has to delete both lines of <definition>
        dst = os.path.join(self.working_dict, 'def_def.bpmn')
        self.xml_reader.rel_path = dst
        #self.xml_reader.prepare_dom()
        #ToDo: erstelle working directory für file-arbeiten