import pytest

from src.converter.xml_reader import XMLReader


class TestXMLReader:

    pytest.fixture(autouse=True)
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