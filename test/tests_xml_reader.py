import os
import shutil

import pytest

from src.converter.xml_reader import XMLReader


class TestXMLReader:
    # When working with xml files, we copy all files to
    # a new directory to prevent overwriting of test files.
    # All tests are performed there.

    pytest_root = os.path.dirname(os.path.abspath(__file__))
    xml_files = os.path.join(pytest_root, 'test_files', 'xml')
    working_dict = os.path.join(pytest_root, 'test_files', 'working_dict')

    @classmethod
    def setup_class(cls):
        try:
            shutil.copytree(cls.xml_files, cls.working_dict)
        except FileExistsError:
            pass

    @classmethod
    def teardown_class(cls):
        dst_abs = os.path.abspath(cls.working_dict)
        shutil.rmtree(dst_abs)

    @pytest.fixture(autouse=True)
    def xml_reader(self):
        self.xml_reader_expected = XMLReader()
        self.xml_reader_actual = XMLReader()

    @staticmethod
    def read_xml(string):
        import xml.etree.ElementTree as Et
        xml_tree = Et.fromstring(string)
        return xml_tree

    hunger_noticed = 'hunger noticed'

    def strip_definitions(self, filename: str) -> str:
        """
        Use this function to call XML parser to parse a unprepared xml-file
        (e.g. has parser-breaking <definition> tag in it)
        to test if the xml parser can parse the file, the function returns
        the <name> tag of the BPMNStartEvent.
        """
        xpath_start_event = './/startEvent'

        actual = os.path.join(self.working_dict, filename)
        self.xml_reader_actual.rel_path = actual
        self.xml_reader_actual.prepare_dom()

        # if we can query the dom, the new xml is parsable
        # this is what we want when calling prepare_dom()
        actual_dom = self.xml_reader_actual.parse_to_dom(abs_path=actual)
        return actual_dom.find(xpath_start_event).attrib['name']

    def test_strip_definitions_def_def(self):
        # has to delete both lines of <definition>
        actual_name = self.strip_definitions(filename='def_def.bpmn')
        assert actual_name == self.hunger_noticed

    def test_strip_definitions_def_none(self):
        # has to delete opening brackets of <definition>
        actual_name = self.strip_definitions(filename='def_none.bpmn')
        assert actual_name == self.hunger_noticed

    def test_strip_definitions_none_def(self):
        # has to delete closing brackets of <definition>
        actual_name = self.strip_definitions(filename='none_def.bpmn')
        assert actual_name == self.hunger_noticed

    def test_strip_definitions_none_none(self):
        # <definitions> already deleted. Case: Nothing to do.
        actual_name = self.strip_definitions(filename='none_none.bpmn')
        assert actual_name == self.hunger_noticed

    def test_strip_definitions_bpmndi(self):
        # delete definitions and <bpmndi>
        actual_name = self.strip_definitions(filename='bpmndi.bpmn')
        assert actual_name == self.hunger_noticed
