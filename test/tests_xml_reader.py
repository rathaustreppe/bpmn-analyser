import os
import shutil
import sys

import pytest

from src.converter.bpmn_models.bpmn_enum import BPMNEnum
from src.converter.xml_reader import XMLReader


class TestXMLReader:
    # When working with xml files, we copy all files to
    # a new directory to prevent overwriting of test files.
    # All tests are performed there.

    pytest_root = os.path.dirname(os.path.abspath(__file__))
    xml_files = os.path.join(pytest_root,'test_files', 'xml')
    working_dict = os.path.join(pytest_root, 'test_files', 'working_dict')

    @classmethod
    def setup_class(self):
        try:
            shutil.copytree(self.xml_files, self.working_dict)
        except (FileExistsError):
            pass
        except (Exception):
            raise

    @classmethod
    def teardown_class(self):
        dst_abs = os.path.abspath(self.working_dict)
        shutil.rmtree(dst_abs)
        pass

    @pytest.fixture(autouse=True)
    def xml_reader(self):
        self.xml_reader_expected = XMLReader()
        self.xml_reader_actual = XMLReader()

    def read_xml(self, string):
        import xml.etree.ElementTree as ET
        xml_tree = ET.fromstring(string)
        return xml_tree
    
    def test_strip_definitions_def_def(self):
        # has to delete both lines of <definition>
        actual = os.path.join(self.working_dict, 'def_def.bpmn')
        self.xml_reader_actual.rel_path = actual
        self.xml_reader_actual.prepare_dom()

        # if we can query the dom, the new xml is parsable
        # this is what we want when calling prepare_dom()
        actual_dom = self.xml_reader_actual.parse_to_dom(
            abs_path=actual)

        actual_name = actual_dom.find('.//startEvent').attrib['name']
        assert actual_name == 'hunger noticed'

    def test_strip_definitions_def_none(self):
        # has to delete opening brackets of <definition>
        actual = os.path.join(self.working_dict, 'def_none.bpmn')
        self.xml_reader_actual.rel_path = actual
        self.xml_reader_actual.prepare_dom()

        actual_dom = self.xml_reader_actual.parse_to_dom(
            abs_path=actual)

        actual_name = \
        actual_dom.find('.//startEvent').attrib['name']
        assert actual_name == 'hunger noticed'

    def test_strip_definitions_none_def(self):
        # has to delete closing brackets of <definition>
        actual = os.path.join(self.working_dict,
                              'def_none.bpmn')
        self.xml_reader_actual.rel_path = actual
        self.xml_reader_actual.prepare_dom()

        actual_dom = self.xml_reader_actual.parse_to_dom(
            abs_path=actual)

        actual_name = \
            actual_dom.find('.//startEvent').attrib[
                'name']
        assert actual_name == 'hunger noticed'

    def test_strip_definitions_none_none(self):
        # <definitions> already deleted. Case: Nothing to do.
        actual = os.path.join(self.working_dict,
                              'none_none.bpmn')
        self.xml_reader_actual.rel_path = actual
        self.xml_reader_actual.prepare_dom()

        actual_dom = self.xml_reader_actual.parse_to_dom(
            abs_path=actual)

        actual_name = \
            actual_dom.find('.//startEvent').attrib[
                'name']
        assert actual_name == 'hunger noticed'

    def test_strip_definitions_bpmndi(self):
        # delete definitions and <bpmndi>
        actual = os.path.join(self.working_dict,
                              'bpmndi.bpmn')
        self.xml_reader_actual.rel_path = actual
        self.xml_reader_actual.prepare_dom()

        actual_dom = self.xml_reader_actual.parse_to_dom(
            abs_path=actual)

        actual_name = \
            actual_dom.find('.//startEvent').attrib[
                'name']
        assert actual_name == 'hunger noticed'