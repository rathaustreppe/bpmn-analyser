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
    working_dict = os.path.join(pytest_root, 'test_files', 'temp_working_dict')

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
        abs_file_path = os.path.join(self.working_dict, filename)

        # if we can query the dom, the new xml is parsable
        # this is what we want when calling prepare_dom()
        actual_dom = self.xml_reader_actual.parse_to_dom(abs_file_path=
                                                         abs_file_path)
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

    def test_do_not_touch_files(self):
        # checks if original file is left untouched and xml reader therefore
        # only works with copies
        # to test this we parse and query the to_be_untouched file
        # and compare it to the exact copy to_be_untouched_2
        filename = 'to_be_untouched.bpmn'
        filename_2 = 'to_be_untouched_2.bpmn'
        actual_name = self.strip_definitions(filename=filename)
        assert actual_name == self.hunger_noticed

        # open both files and compare line by line
        file_path_untouched = os.path.join(self.working_dict, filename)
        with open(file_path_untouched, "r") as f:
            lines_1 = f.readlines()

        file_path_untouched_2 = os.path.join(self.working_dict, filename_2)
        with open(file_path_untouched_2, "r") as f:
            lines_2 = f.readlines()

        assert lines_1 == lines_2