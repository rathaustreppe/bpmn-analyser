from typing import Optional
from xml.etree.ElementTree import Element

from igraph import Graph
from pedantic import pedantic_class

from src.converter.bpmn_factory import BPMNFactory
from src.converter.graph_builder import GraphBuilder
from src.converter.xml_reader import XMLReader


@pedantic_class
class Converter:
    """
    Interface to read XML-BPMN2.0-files and building
    a IGraph.Graph out ouf them.
    """

    def __init__(self,
                 xml_tree: Optional[Element] = None,
                 graph_builder: Optional[
                     GraphBuilder] = None) -> None:
        self.xml_tree = xml_tree
        self.xml_reader = XMLReader()
        self.graph_builder = graph_builder

    def convert(self, rel_path_to_bpmn: str) -> Graph:
        """
        Does all the stuff:
        reading xml, parsing to elementtree and putting
        it back together to a Graph.
        Does not pay attention to xml and bpmn specification.
        Before calling this function make sure that your
        bpmn.xml is conform to xml-standard and
        bpmn2.0-standard and doesnt have bpmn-syntax errors.
        Use other and better tools to check this. For example
        bpmn-js-bpmnlint.
                Returns:
            Graph that equals the given BPMN-process
        """
        self.xml_reader.rel_path = rel_path_to_bpmn

        # the bpmn-xml of demo.bpmn.io contains wrong
        # xmlns-definitions that prevent the python xml
        # parser to read the xml:
        # >>> definitions xmlns = "http://ww.omg.org/s...
        # We kick them out.
        self.xml_reader.prepare_dom()

        self.xml_tree = self.xml_reader.parse_to_dom()
        self.graph_builder = GraphBuilder \
            (xml_reader=self.xml_reader,
             bpmn_factory=BPMNFactory())

        # convert all xml-elements into python objects
        bpmn_elements, sequence_flows = \
            self.graph_builder.create_bpmn_objects()

        self.graph_builder.build_graph(
            bpmn_elements=bpmn_elements,
            sequence_flows=sequence_flows)

        return self.graph_builder.graph
