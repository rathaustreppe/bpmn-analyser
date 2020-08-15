from typing import Optional, List, Tuple
from pedantic import pedantic, pedantic_class
from xml.etree.ElementTree import Element
from igraph import Graph

# local import
from src.converter.bpmn_models.bpmn_activity import \
    BPMNActivity
from src.converter.bpmn_models.bpmn_sequenceflow import \
    BPMNSequenceFlow
from src.converter.bpmn_models.bpmn_startevent import \
    BPMNStartEvent
from src.converter.bpmn_models.bpmn_enum import BPMNEnum
from src.converter.model_builder import ModelBuilder

'''
Takes an *.bpmn file written in bpmn2.0-conform xml
and build a graph out of it
'''


class Converter:
    """
    Class to read bpmn-xml files, traverse them and
    put it together to a machine-readable graph using
    IGraph libary.
    """

    def __init__(self, xml_tree: Optional[Element] = None, graph: Optional[Graph] = None) -> None:
        self.xml_tree = xml_tree
        self.graph = graph


    def _read_xml_file(self, path: str) -> str:
        """
        Takes a relative path from content root and reads
        the xml. Returns a traversable xml-dom object.
        (Not a long string!)
        Args:
            path (str): Path from content root

        Returns:
            Element: with XPath Traversable XML Element Tree.
        """
        abs_path = self._make_absolute_path(relative_path=path)

        try:
            import xml.etree.ElementTree as ET
            xml_tree = ET.parse(abs_path).getroot()

        except Exception as e:
            print(e)
        return xml_tree


    def _make_absolute_path(self, relative_path: str) -> str:
        import os
        abs_path = os.path.abspath(relative_path)
        print(abs_path)
        return abs_path


    #@pedantic
    def all_xml_elements(self, elementname: BPMNEnum) -> List[Tuple[Element, List[Element]]]:
        """
        access all <elementnames> of xml file with XPath syntax
        .// means: in whole xml document (doesnt care about depth)
        https://docs.python.org/3/library/xml.etree.elementtree.html#elementtree-xpath
        optional, you can specifiy a list of elements
        that are ignored
        return a list containing all elements in the xml with
        the <elementname> tag
        Example with exclude_ids: 123
        <hello>
          <world id=123\>
          <world id=456\>
        <\hello>
        elementname: 'world'
        Returns: [<world id=456>] with 'world' beeing an object
        Args:
            elementname (str): elementname of bpmn-specification

        Returns:


        """
        elements_in_file = []
        for element in self.xml_tree.findall('.//' + elementname.value):
            # --> [element, element, ...]
            # case flows: incoming and outgoing sequenceflows are
            # only referenced with their id. But we want them as
            # a full object. So we query them as well.
            flow_list: List[Element] = []
            for child in element:
                child:Element
                if child.tag == 'incoming' or child.tag == 'outgoing':
                    sequence_flow_id:str = child.text
                    sequence_flow = self.xml_tree.find('sequenceFlow[@id="%s"]' % sequence_flow_id)
                    flow_list.append(sequence_flow)

            # We dont need to preserve what sequence flow is
            # incomming and outgoing. This is stored in
            # sourceRef and targetRef of each sequenceFlow.
            # We return something like:
            #[(element, sequenceflow), (element, sequenceflow, sequenceflow)]
            elements_in_file.append((element, flow_list))

        return elements_in_file


    def _strip_xml_definitions(self, path_to_xml:str) -> None:
        """
        The bpmn-xml of demo.bpmn.io contains wrong
        xmlns-definitions that prevent the python xml
        parser to read the xml.
        < definitions xmlns = "http://www.omg.org/spec/BPMN/20100524/MODEL"
        xmlns: bpmndi = "http://www.omg.org/spec/BPMN/20100524/DI"
        ... <several others>
        We kick them out.
        Returns:

        """
        with open(path_to_xml, "r") as f:
            lines = f.readlines()
        # delete 2 lines: opening and closing tags
        for idx, line in enumerate(lines):
            if line.startswith('<definitions'):
                del lines[idx]
                continue
            if line.startswith('</definitions'):
                del lines[idx]
                continue

        with open(path_to_xml, "w") as f:
            for line in lines:
                 f.write(line)


    def _read_all_elements(self) -> None:
        """
        Reads all the elements of the bpmn and put them
        into lists.
        Returns:

        """
        # read startevent. There can only be one startEvent
        # (BPMN-Specification)
        start_event = self.all_xml_elements(elementname=BPMNEnum.STARTEVENT)
        start_event = ModelBuilder.make_startevent(start_event[0])

    @pedantic
    def convert(self, path_to_bpmn: str) -> None:
        """
        Highest function of converter. Does all the stuff:
        reading xml, parsing to elementtree and putting
        it back togther to a Graph.
        Does not pay attention to xml and bpmn specification.
        Before calling this function make sure that your
        bpmn.xml is conform to xml-standard and bpmn-standard
        and doesnt have bpmn-syntax errors.
        Use other and better tools to check this. For example
        bpmn-js-bpmnlint.
                Returns:
            Graph that equals the given BPMN-process
        """

        self.xml_tree = self._read_xml_file(path=path_to_bpmn)

        # the bpmn-xml of demo.bpmn.io contains wrong
        # xmlns-definitions that prevent the python xml
        # parser to read the xml.
        # < definitions xmlns = "http://www.omg.org/spec/BPMN/20100524/MODEL"
        # xmlns: bpmndi = "http://www.omg.org/spec/BPMN/20100524/DI"
        #... <several others>
        # We kick them out.
        self._strip_xml_definitions(path_to_xml=path_to_bpmn)


        self._read_all_elements()
