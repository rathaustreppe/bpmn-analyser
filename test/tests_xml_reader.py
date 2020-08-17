

class TestXMLReader:

    def read_xml(self, string):
        import xml.etree.ElementTree as ET
        xml_tree = ET.fromstring(string)
        return xml_tree