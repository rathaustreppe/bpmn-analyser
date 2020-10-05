import os

import pytest

from src.converter.xml_reader import XMLReader


class TestXMLReader:

    # all xml files are organized into separate folders. Specify the name
    # of the folder containing all xml files relevant for this testclass
    test_folder_name = 'xml_reader'

    @staticmethod
    def read_xml(string):
        import xml.etree.ElementTree as Et
        xml_tree = Et.fromstring(string)
        return xml_tree

    @pytest.fixture(scope='function', autouse=True)
    def xml_reader(self) -> XMLReader:
        return XMLReader()

    # a often used text in this test class
    hunger_noticed = 'hunger noticed'

    def strip_definitions(self, filename: str,
                          xml_reader: XMLReader,
                          xml_folders_path: str) -> str:
        """
        Use this function to call XML parser to parse a unprepared xml-file
        (e.g. has parser-breaking <definition> tag in it)
        to test if the xml parser can parse the file, the function returns
        the <name> tag of the BPMNStartEvent.
        """
        xpath_start_event = './/startEvent'
        abs_file_path = os.path.join(xml_folders_path,
                                     self.test_folder_name,
                                     filename)

        # if we can query the dom, the new xml is parsable
        # this is what we want when calling prepare_dom()
        actual_dom = xml_reader.parse_to_dom(abs_file_path=abs_file_path)
        return actual_dom.find(xpath_start_event).attrib['name']

    def test_strip_definitions_def_def(self, xml_reader, xml_folders_path):
        # has to delete both lines of <definition>
        actual_name = self.strip_definitions(filename='def_def.bpmn',
                                             xml_reader=xml_reader,
                                             xml_folders_path=xml_folders_path)
        assert actual_name == self.hunger_noticed

    def test_strip_definitions_def_none(self, xml_reader, xml_folders_path):
        # has to delete opening brackets of <definition>
        actual_name = self.strip_definitions(filename='def_none.bpmn',
                                             xml_reader=xml_reader,
                                             xml_folders_path=xml_folders_path)
        assert actual_name == self.hunger_noticed

    def test_strip_definitions_none_def(self, xml_reader, xml_folders_path):
        # has to delete closing brackets of <definition>
        actual_name = self.strip_definitions(filename='none_def.bpmn',
                                             xml_reader=xml_reader,
                                             xml_folders_path=xml_folders_path)
        assert actual_name == self.hunger_noticed

    def test_strip_definitions_none_none(self, xml_reader, xml_folders_path):
        # <definitions> already deleted. Case: Nothing to do.
        actual_name = self.strip_definitions(filename='none_none.bpmn',
                                             xml_reader=xml_reader,
                                             xml_folders_path=xml_folders_path)
        assert actual_name == self.hunger_noticed

    def test_strip_definitions_bpmndi(self, xml_reader, xml_folders_path):
        # delete definitions and <bpmndi>
        actual_name = self.strip_definitions(filename='bpmndi.bpmn',
                                             xml_reader=xml_reader,
                                             xml_folders_path=xml_folders_path)
        assert actual_name == self.hunger_noticed

    def test_do_not_touch_files(self, xml_reader, xml_folders_path):
        # checks if original file is left untouched and xml reader therefore
        # only works with copies
        # to test this we parse and query the to_be_untouched file
        # and compare it to the exact copy to_be_untouched_2
        filename = 'to_be_untouched.bpmn'
        filename_2 = 'to_be_untouched_2.bpmn'
        actual_name = self.strip_definitions(filename=filename,
                                             xml_reader=xml_reader,
                                             xml_folders_path=xml_folders_path)
        assert actual_name == self.hunger_noticed

        # open both files and compare line by line
        file_path_untouched = os.path.join(xml_folders_path,
                                           self.test_folder_name,
                                           filename)
        with open(file_path_untouched, "r") as f:
            lines_1 = f.readlines()

        file_path_untouched_2 = os.path.join(xml_folders_path,
                                             self.test_folder_name,
                                             filename_2)
        with open(file_path_untouched_2, "r") as f:
            lines_2 = f.readlines()

        assert lines_1 == lines_2
