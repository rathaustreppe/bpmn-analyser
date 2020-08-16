from typing import Optional, List, Tuple
from pedantic import pedantic, pedantic_class
from xml.etree.ElementTree import Element
from igraph import Graph, Vertex, VertexSeq

# local import
from src.converter.bpmn_models.bpmn_activity import \
    BPMNActivity
from src.converter.bpmn_models.bpmn_element import \
    BPMNElement
from src.converter.bpmn_models.bpmn_endevent import \
    BPMNEndEvent
from src.converter.bpmn_models.bpmn_sequenceflow import \
    BPMNSequenceFlow
from src.converter.bpmn_models.bpmn_start_end_event import \
    BPMNStartEndEvent
from src.converter.bpmn_models.bpmn_startevent import \
    BPMNStartEvent
from src.converter.bpmn_models.bpmn_enum import BPMNEnum
from src.converter.model_builder import ModelBuilder
from src.models.graphtext import GraphText

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
    def all_xml_elements(self, elementname: BPMNEnum) -> List[Element]:
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
            # We dont need to preserve which sequence flow is
            # incomming and outgoing. This is stored in
            # sourceRef and targetRef of each sequenceFlow.
            # We return something like:
            #[(sequence_flow, sequenceflow), (sequence_flow, sequenceflow, sequenceflow)]
            elements_in_file.append(element)

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


    def _read_all_elements(self) -> Tuple[List[BPMNElement], List[BPMNSequenceFlow]]:
        """
        Reads all the elements of the bpmn and put them
        into lists.
        Returns:

        """
        # First we generate all BPMNElements and next
        # we link them with the sequenceflows. So we can
        # update all indices/links/attrbibutes of all
        # BPMNElements with the correct reference of the
        # sequenceflows-objects.
        # For this purpose we create a list that contains
        # all BPMNElements for later linking
        bpmn_elements: List[BPMNElement] = []

        # read startevent. There can only be one startEvent
        # (BPMN-Specification)
        start_event = self.all_xml_elements(elementname=BPMNEnum.STARTEVENT)
        start_event_obj = ModelBuilder.make_startevent(element=start_event[0])
        bpmn_elements.append(start_event_obj)

        # read endevent. There should be only one endEvent
        end_event = self.all_xml_elements(elementname=BPMNEnum.ENDEVENT)
        end_event_obj = ModelBuilder.make_end_event(element=end_event[0])
        bpmn_elements.append(end_event_obj)

        # make activities that lie between start and end
        # may need refactoring in future. Only works with
        # linear chains.
        activities = self.all_xml_elements(elementname=BPMNEnum.ACTIVITY)
        for activity in activities:
            activity_obj = ModelBuilder.make_activity(element=activity)
            bpmn_elements.append(activity_obj)

        # read sequence flows with correct references
        # to their sources and targets
        sequence_flows = self.all_xml_elements(elementname=BPMNEnum.SEQUENCEFLOW)
        sequence_flows_list: List[BPMNSequenceFlow] = []
        for sequence_flow in sequence_flows:
            sequence_flow_obj = ModelBuilder.make_sequenceflow(
                sequence_flow=sequence_flow,
                elements=bpmn_elements)
            sequence_flows_list.append(sequence_flow_obj)

        # Update references of sequence flows in bpmn-elements
        for sequence_flow in sequence_flows_list:
            # class where flow points to
            if isinstance(sequence_flow.get_source(), BPMNStartEvent):
                sequence_flow.get_source().set_sequenceFlow(sequence_flow=sequence_flow)
                continue

            if isinstance(sequence_flow.get_target(), BPMNEndEvent):
                sequence_flow.get_target().set_sequenceFlow(sequence_flow=sequence_flow)
                continue

            if isinstance(sequence_flow.get_source(), BPMNActivity):
                sequence_flow.get_source().set_sequenceFlowOut(sequenceFlow = sequence_flow)
                continue

            if isinstance(sequence_flow.get_target(), BPMNActivity):
                sequence_flow.get_target().set_sequenceFlowIn(sequenceFlow = sequence_flow)
                continue

        return bpmn_elements, sequence_flows_list


    def _build_graph(self, bpmn_elements: List[BPMNElement], sequence_flows: List[BPMNSequenceFlow]) -> Graph:
        """
        From BPMN-Python objects we construct a IGraph.Graph.
        Args:
            bpmn_elements (List[BPMNElement]): List of many
            python objects including start-and endEvents and
            bpmn-activities. We treat them as vertecies.
            sequence_flows (List[BPMNSequenceFlow]): List of
            many sequenceFlows, that are the edges of the
            graph.

        Returns:
            IGraph.Graph
        """
        # first things first: call graph-constructor
        self.graph = Graph()
        self.graph = self.graph.as_directed()
        self.graph.add_vertices(len(bpmn_elements))

        def _put_in_graph(element: BPMNElement, idx: int):
            """
            Helper-function that puts every BPMNElement in
            the graph according to idx.
            Args:
                element (BPMNElement): BPMNElement as vertex
                idx (int): position of element in vertex-dict.

            Returns:
                None: but side effect on graph
            """
            _name = element.get_name()
            self.graph.vs[idx][BPMNEnum.NAME.value] = GraphText(text=_name)
            self.graph.vs[idx][BPMNEnum.ID.value] = element.get_id()

        # generate vertices for activity, start-and endEvent
        # does not preserve order of the given list
        # (list is 1-dimensional, graph is 2-dimensional)
        idx = 1
        for elem in bpmn_elements:
            # idx starts with 1, because startEvent is 0
            if isinstance(elem, BPMNStartEvent):
                # start Event => id = 0
                _put_in_graph(element=elem, idx=0)
                continue

            if isinstance(elem, BPMNEndEvent):
                # end event => id = last index => len-1
                idx_end = len(bpmn_elements) - 1
                _put_in_graph(element=elem, idx=idx_end)
                continue

            if isinstance(elem, BPMNActivity):
                _put_in_graph(element=elem, idx=idx)
                idx += 1
                continue


        # generate edges
        def _find_vertex(vertex_seq:VertexSeq, id:str) -> Vertex:
            for vertex in vertex_seq:
                if vertex[BPMNEnum.ID.value] == id:
                    return vertex

        for sequence_flow in sequence_flows:
            source_id = sequence_flow.get_source().get_id()
            target_id = sequence_flow.get_target().get_id()



            # search vertex-list of graph for
            # source and target-ids
            vertex_seq = VertexSeq(self.graph)
            vertex_source = _find_vertex(vertex_seq=vertex_seq, id=source_id)
            vertex_target = _find_vertex(vertex_seq=vertex_seq, id=target_id)

            # get idx where the vertex were put in graph.vs
            vtx_src_idx = vertex_source.index
            vtx_tgt_idx = vertex_target.index

            # generate edge in graph
            self.graph: Graph
            self.graph.add_edge(source=vtx_src_idx, target=vtx_tgt_idx)

            # print(f'sequenceFlow {sequence_flow.get_id()}')
            # print(f'sf-source {sequence_flow.get_source().get_id()}')
            # print(f'sf-target {sequence_flow.get_target().get_id()}')
            # print(f'source {vertex_source}')
            # print(f'target {vertex_target}')

        return self.graph

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

        # convert all xml-elements into python objects
        bpmn_elements, sequence_flows = self._read_all_elements()

        self._build_graph(bpmn_elements=bpmn_elements, sequence_flows=sequence_flows)

        # print graph
        Graph.write_svg(self.graph, "printed_graph.svg", labels=BPMNEnum.NAME.value)
