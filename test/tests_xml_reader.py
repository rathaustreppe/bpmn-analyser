import os
import shutil

import pytest

from src.converter.bpmn_models.bpmn_enum import BPMNEnum
from src.converter.xml_reader import XMLReader


class TestXMLReader:

    @classmethod
    def setup_class(self):
        # copies test files into new folder
        src = r'..\test\test_files\xml'
        dst = r'..\test\test_files\working_dict'
        src_abs = os.path.abspath(src)
        dst_abs = os.path.abspath(dst)

        try:
            shutil.copytree(src_abs, dst_abs)
        except (FileExistsError):
            pass
        except (Exception):
            raise

    @classmethod
    def teardown_class(self):
        # deletes folder with test files after tests
        dst = r'..\test\test_files\working_dict'
        dst_abs = os.path.abspath(dst)
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
        path = r'..\..\test\test_files\xml\def_def.bpmn'
        self.xml_reader.rel_path = path
        #self.xml_reader.prepare_dom()
        #ToDo: erstelle working directory für file-arbeiten