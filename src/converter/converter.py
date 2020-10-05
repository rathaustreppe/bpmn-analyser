from typing import Optional
from xml.etree.ElementTree import Element

from pedantic import pedantic_class

from src.converter.bpmn_converter import BPMNConverter
from src.converter.bpmn_factory import BPMNFactory
from src.converter.bpmn_models.bpmn_model import BPMNModel
from src.converter.xml_reader import XMLReader


@pedantic_class
class Converter:
    """
    Interface to read XML-BPMN2.0-files and building
    a BPMNModel out of it.
    """

    def __init__(self, xml_reader: Optional[XMLReader] = None,
                 xml_tree: Optional[Element] = None,
                 graph_builder: Optional[BPMNConverter] = None) -> None:
        self.xml_tree = xml_tree
        self.graph_builder = graph_builder
        self.xml_reader = xml_reader
        if xml_reader is None:
            self.xml_reader = XMLReader()

    def convert(self, rel_path_to_bpmn: str) -> BPMNModel:
        """
        Does all the stuff:
        reading xml, parsing to elementtree and putting
        it back together to a BPMNModel.
        Does not pay attention to xml and bpmn specification.
        Before calling this function make sure that your
        bpmn.xml is conform to xml-standard and
        bpmn2.0-standard and doesnt have bpmn-syntax errors.
        Use other and better tools to check this. For examples
        bpmn-js-bpmnlint.
        """
        abs_file_path = self.xml_reader.rel_to_abs_path(rel_path=
                                                        rel_path_to_bpmn)


        # # the bpmn-xml of demo.bpmn.io contains wrong
        # # xmlns-definitions that prevent the python xml
        # # parser to read the xml:
        # # >>> definitions xmlns = "http://ww.omg.org/s...
        # # We kick them out.
        # self.xml_reader.prepare_dom()

        self.xml_tree = self.xml_reader.parse_to_dom(abs_file_path=abs_file_path)

        bpmn_converter = BPMNConverter(xml_reader=self.xml_reader,
                                       bpmn_factory=BPMNFactory())

        # temp files of xml reader now useless.
        # clean them
        self.xml_reader.clean_temp_file_path()

        return bpmn_converter.create_bpmn_model()
