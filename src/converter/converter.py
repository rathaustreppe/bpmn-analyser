from typing import Optional
from xml.etree.ElementTree import Element

from pedantic import pedantic_class

from src.converter.bpmn_converter import BPMNConverter
from src.converter.bpmn_factory import BPMNFactory
from src.converter.bpmn_models.bpmn_model import BPMNModel
from src.converter.xml_reader import XMLReader
from src.exception.path_errors import NoPathError
from src.util.paths.path_conversion import rel_to_abs_path


@pedantic_class
class Converter:
    """
    Interface to read XML-BPMN2.0-files and building
    a BPMNModel out of it.
    """

    def __init__(self, xml_reader: Optional[XMLReader] = None) -> None:
        self.xml_reader = xml_reader
        if xml_reader is None:
            self.xml_reader = XMLReader()

    def convert(self,
                rel_file_path: Optional[str] = None,
                abs_file_path: Optional[str] = None) -> BPMNModel:
        """
        Does all the stuff:
        reading xml, parsing to elementtree and putting
        it back together to a BPMNModel.
        Before calling this function make sure that your
        bpmn.xml is conform to xml-standard and
        bpmn2.0-standard and doesnt have bpmn-syntax errors.
        Use other and better tools to check bpmn-syntax. For examples
        bpmn-js-bpmnlint.
        """
        if rel_file_path is None and abs_file_path is None:
            raise NoPathError()

        if abs_file_path is None:
            abs_file_path = rel_to_abs_path(rel_path=rel_file_path)

        self.xml_reader.parse_to_dom(abs_file_path=abs_file_path)

        bpmn_converter = BPMNConverter(xml_reader=self.xml_reader,
                                       bpmn_factory=BPMNFactory())

        return bpmn_converter.create_bpmn_model()
