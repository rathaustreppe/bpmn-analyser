from typing import Tuple, List, Optional

from igraph import Graph, VertexSeq, Vertex
from pedantic import pedantic_class

from src.converter.bpmn_factory import BPMNFactory
from src.converter.bpmn_models.bpmn_activity import \
    BPMNActivity
from src.converter.bpmn_models.bpmn_element import \
    BPMNElement
from src.converter.bpmn_models.bpmn_endevent import \
    BPMNEndEvent
from src.converter.bpmn_models.bpmn_enum import BPMNEnum
from src.converter.bpmn_models.bpmn_sequenceflow import \
    BPMNSequenceFlow
from src.converter.bpmn_models.bpmn_startevent import \
    BPMNStartEvent
from src.converter.i_bpmn_factory import IBPMNFactory
from src.converter.xml_reader import XMLReader
from src.models.graph_text import GraphText

#pedantic_class
class GraphBuilder:
    def __init__(self,
                 xml_reader: XMLReader,
                 bpmn_factory: IBPMNFactory,
                 graph: Optional[Graph] = None):
        self.xml_reader = xml_reader
        self.bpmn_factory = bpmn_factory
        self.graph = graph

    def create_bpmn_objects(self) -> Tuple[
        List[BPMNElement], List[BPMNSequenceFlow]]:
        """
        Reads the xml-dom and converts it into python
        BPMN-objects. (e.g BPMNActivy, BPMNSequenceFlow)
        """

        # First we generate all BPMNElements and next
        # we link them with the sequenceflows. So we can
        # update all indices/links/attrbibutes of all
        # BPMNElements with the correct reference of the
        # sequenceflows-objects.
        # For this purpose we create a list that contains
        # all BPMNElements for later linking
        bpmn_elements: List[BPMNElement] = []

        factory = BPMNFactory()

        # read start event. There can only be one startEvent
        # (BPMN-Specification)
        start_event = self.xml_reader.query(
            element_name=BPMNEnum.STARTEVENT)[0]
        start_event_obj = factory.create_bpmn_element(
            element=start_event,
            elem_type=BPMNEnum.STARTEVENT)
        bpmn_elements.append(start_event_obj)

        # read end event. There should be only one endEvent
        end_event = self.xml_reader.query(
            element_name=BPMNEnum.ENDEVENT)[0]
        end_event_obj = factory.create_bpmn_element(
            element=end_event,
            elem_type=BPMNEnum.ENDEVENT)
        bpmn_elements.append(end_event_obj)

        # make activities that lay between start and end
        # may need refactoring in future. Only works with
        # linear chains.
        activities = self.xml_reader.query(
            element_name=BPMNEnum.ACTIVITY)
        for activity in activities:
            activity_obj = factory.create_bpmn_element(
                element=activity,
                elem_type=BPMNEnum.ACTIVITY)
            bpmn_elements.append(activity_obj)

        # read sequence flows with correct references
        # to their sources and targets
        sequence_flows = self.xml_reader.query(
            element_name=BPMNEnum.SEQUENCEFLOW)
        sequence_flows_list: List[BPMNSequenceFlow] = []
        for sequence_flow in sequence_flows:
            sequence_flow_obj = factory.create_bpmn_flow(
                flow=sequence_flow,
                elem_type=BPMNEnum.SEQUENCEFLOW,
                elements=bpmn_elements)
            sequence_flows_list.append(sequence_flow_obj)

        # Update references of sequence flows in bpmn-elements
        for sequence_flow in sequence_flows_list:
            # class where flow points to
            if isinstance(sequence_flow.get_source(),
                          BPMNStartEvent):
                sequence_flow.get_source().set_sequenceFlow(
                    sequence_flow=sequence_flow)
                continue

            if isinstance(sequence_flow.get_target(),
                          BPMNEndEvent):
                sequence_flow.get_target().set_sequenceFlow(
                    sequence_flow=sequence_flow)
                continue

            if isinstance(sequence_flow.get_source(),
                          BPMNActivity):
                sequence_flow.get_source().set_sequenceFlowOut(
                    sequenceFlow=sequence_flow)
                continue

            if isinstance(sequence_flow.get_target(),
                          BPMNActivity):
                sequence_flow.get_target().set_sequenceFlowIn(
                    sequenceFlow=sequence_flow)
                continue

        return bpmn_elements, sequence_flows_list

    def build_graph(self, bpmn_elements: List[BPMNElement],
                    sequence_flows: List[
                        BPMNSequenceFlow]) -> Graph:
        """
        From BPMN-Python objects we construct a IGraph.Graph.
        Args:
            bpmn_elements (List[BPMNElement]): List of many
            python objects including start-and endEvents and
            bpmn-activities. We treat them as vertices.
            sequence_flows (List[BPMNSequenceFlow]): List of
            many sequenceFlows, that are the edges of the
            graph.

        Returns:
            IGraph.Graph
        """
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
            self.graph.vs[idx][
                BPMNEnum.NAME.value] = GraphText(text=_name)
            self.graph.vs[idx][
                BPMNEnum.ID.value] = element.get_id()

        # generate vertices for activity, start-and endEvent
        # does not preserve order of the given list
        # (list is 1-dimensional, graph is 2-dimensional)
        idx = 1
        for elem in bpmn_elements:
            # idx starts with 1, because startEvent takes
            # first index -> 0
            if isinstance(elem, BPMNStartEvent):
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

        # helper function to find a specific vertex in graph
        def _find_vertex(vertex_seq: VertexSeq,
                         vertex_id: str) -> Vertex:
            for vertex in vertex_seq:
                if vertex[BPMNEnum.ID.value] == vertex_id:
                    return vertex

        # generate edges
        for sequence_flow in sequence_flows:
            source_id = sequence_flow.get_source().get_id()
            target_id = sequence_flow.get_target().get_id()

            # search vertex-list of graph for
            # source and target-ids
            vertex_seq = VertexSeq(self.graph)
            vertex_source = _find_vertex(
                vertex_seq=vertex_seq, vertex_id=source_id)
            vertex_target = _find_vertex(
                vertex_seq=vertex_seq, vertex_id=target_id)

            # get idx where the vertex were put in graph.vs
            vtx_src_idx = vertex_source.index
            vtx_tgt_idx = vertex_target.index

            # generate edge in graph
            self.graph.add_edge(source=vtx_src_idx,
                                target=vtx_tgt_idx)

        return self.graph
