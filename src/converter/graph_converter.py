from typing import List, Optional

from igraph import Graph, VertexSeq, Vertex, Edge
from pedantic import pedantic_class

from src.converter.bpmn_models.bpmn_activity import \
    BPMNActivity
from src.converter.bpmn_models.bpmn_element import \
    BPMNElement
from src.converter.bpmn_models.bpmn_enum import BPMNEnum
from src.converter.bpmn_models.bpmn_model import BPMNModel
from src.converter.bpmn_models.bpmn_sequenceflow import \
    BPMNSequenceFlow
from src.converter.bpmn_models.event.bpmn_endevent import \
    BPMNEndEvent
from src.converter.bpmn_models.event.bpmn_startevent import \
    BPMNStartEvent
from src.converter.bpmn_models.gateway.bpmn_exclusive_gateway import \
    BPMNExclusiveGateway
from src.converter.bpmn_models.gateway.bpmn_gateway import BPMNGateway
from src.converter.bpmn_models.gateway.bpmn_inclusive_gateway import \
    BPMNInclusiveGateway
from src.converter.bpmn_models.gateway.bpmn_parallel_gateway import \
    BPMNParallelGateway
from src.models.graph_text import GraphText


@pedantic_class
class GraphConverter:
    def __init__(self, bpmn_model: BPMNModel,
                 graph: Optional[Graph] = None) -> None:
        self.graph = graph
        self.bpmn_model = bpmn_model
        if self.graph is None:
            self.graph = Graph()

    def put_vertex_in_graph(self, element: BPMNElement, idx: int) -> None:
        """
        Function that puts a single BPMNElement as vertex in
        the graph according to idx. BPMNElement cannot be sequenceflows, because
        they are treated as Edges, not as vertices.
        Args:
            element (BPMNElement): BPMNElement as vertex
            idx (int): position of element in vertex-dict.
        """

        if isinstance(element, BPMNSequenceFlow):
            raise ValueError(f'BPMNSequenceflow {element} cannot be treated as '
                             f'vertex. Use it as an edge instead.')

        # gateways get a special name in the graph
        if isinstance(element, BPMNGateway):
            if isinstance(element, BPMNParallelGateway):
                _name = BPMNEnum.PARALLGATEWAY_TEXT.value
            elif isinstance(element, BPMNExclusiveGateway):
                _name = BPMNEnum.EXCLGATEWAY_TEXT.value
            elif isinstance(element, BPMNInclusiveGateway):
                _name = BPMNEnum.INCLGATEWAY_TEXT.value
            else:
                raise ValueError(f'type {type(element)} of '
                                 f'gateway {element} is not implemented')
        else:
            _name = element.name

        def _write_vertex():
            self.graph.vs[idx][BPMNEnum.NAME.value] = GraphText(text=_name)
            self.graph.vs[idx][BPMNEnum.ID.value] = element.id

        # creates new vertex with name and id without overwriting existing vertex
        # There are two cases when writing vertex is ok:
        # The vertex at idx is fresh without attributes.
        # OR the vertex at idx has attributes, but they have the value None.
        # In every other case we would wrongfully overwrite an existing vertex.
        if len(self.graph.vs[idx].attributes()) == 0:
            _write_vertex()
        elif len(self.graph.vs[idx].attributes()) >= 1 and \
                self.graph.vs[idx]['id'] is None:
            _write_vertex()
        else:
            raise IndexError(f'trying to overwrite existing vertex '
                             f'{self.graph.vs[idx]} with '
                             f'element {element} (condition: {_name}) at index {idx}')

    def put_vertices_in_graph(self, bpmn_elements: List[BPMNElement]) -> None:
        """
        generate vertices for activity, start-and endEvent and gateways.
        Manages indices of vertices and prevents overwriting of existing
        vertices. Does not map list index to graph index.
        (list is 1-dimensional, graph is 2-dimensional)
        """

        # idx starts with 1, because startEvent takes first index == 0
        idx = 1
        for elem in bpmn_elements:
            if isinstance(elem, BPMNStartEvent):
                self.put_vertex_in_graph(element=elem, idx=0)

            elif isinstance(elem, BPMNEndEvent):
                # end event => id = last index => len-1
                idx_end = len(bpmn_elements) - 1
                self.put_vertex_in_graph(element=elem, idx=idx_end)

            elif isinstance(elem, BPMNActivity) or isinstance(elem,
                                                              BPMNGateway):
                self.put_vertex_in_graph(element=elem, idx=idx)
                idx += 1

            elif isinstance(elem, BPMNSequenceFlow):
                raise ValueError(f'BPMNSequenceflow {elem} cannot be '
                                 f'treated as vertex. Use it as an edge instead')
            else:
                raise ValueError(f'element {elem} of type{type(elem)} is not'
                                 f'implemented')

    def put_edges_in_graph(self,
                           sequence_flows: List[BPMNSequenceFlow]) -> None:
        for sequence_flow in sequence_flows:
            source_id = sequence_flow.source.id
            target_id = sequence_flow.target.id

            # Search vertex-list of graph for
            # source and target-ids. We use VertexSeq which is basicly a list
            # of all vertices of a graph.
            vertex_seq = VertexSeq(self.graph)
            vertex_source = self.find_vertex(
                vertices=vertex_seq, vertex_id=source_id)
            vertex_target = self.find_vertex(
                vertices=vertex_seq, vertex_id=target_id)

            # get idx where the vertex were put in graph.vs
            vtx_src_idx = vertex_source.index
            vtx_tgt_idx = vertex_target.index

            # generate edge in graph only if edge not present
            for edge in self.graph.es:
                if edge.source == vtx_src_idx and edge.target == vtx_tgt_idx:
                    raise ValueError(f'cannot put edge {edge} of sequenceflow '
                                     f'{sequence_flow} twice in graph')

            # We generate a new edge here. By using **kwds we can assign
            # a the BPMNEnum.CONDITION.value (== condition) and BPMNEnum.ID.value attribute to the edge.
            # Unfortunately, we cannot pass BPMNEnum.XYZ.value as parameter.
            # Instead we have to use the value (== condition and id). With a small test
            # we make sure BPMNEnum.CONDITION and BPMNEnum.ID is untouched and we can savely use
            # 'condition' as parameter.
            if BPMNEnum.CONDITION.value != 'condition':
                raise ValueError(f'BPMNEnum.CONDITION.value was changed from "condition" '
                                 f'to {BPMNEnum.CONDITION.value}. One cannot generate '
                                 f'named edges without changing the parameter.')

            if BPMNEnum.ID.value != 'id':
                raise ValueError(f'BPMNEnum.ID.value was changed from "id" '
                                 f'to {BPMNEnum.ID.value}. One cannot generate '
                                 f'edges without changing the parameter.')

            self.graph.add_edge(source=vtx_src_idx,
                                target=vtx_tgt_idx,
                                condition=sequence_flow.condition, # BPMNEnum.CONDITION.value
                                id = sequence_flow.id) # BPMNEnum.ID.value

    @staticmethod
    def find_vertex(vertices: VertexSeq, vertex_id: str) -> Vertex:
        # helper function to find a specific vertex in graph according to id
        for vertex in vertices:
            if vertex[BPMNEnum.ID.value] == vertex_id:
                return vertex

    def init_graph(self, number_of_vertices: int) -> None:
        if self.graph is None:
            self.graph = Graph()
        self.graph = self.graph.as_directed()
        self.graph.add_vertices(number_of_vertices)

    def build_graph(self) -> Graph:
        #
        # From BPMN-Python objects we construct a IGraph.Graph.
        # Args:
        #    bpmn_elements (List[BPMNElement]): List of many
        #    python objects (e.g. start-and endEvents and
        #    bpmn-activities). We treat them as vertices.
        #    sequence_flows (List[BPMNSequenceFlow]): List of
        #    many sequenceFlows that are the edges of the
        #    graph.
        #
        # Returns:
        #    IGraph.Graph graph

        if self.bpmn_model is None:
            raise ValueError(f'BPMN-Model of GraphConverter {self} is None.')

        self.init_graph(number_of_vertices=len(self.bpmn_model.bpmn_elements))

        self.put_vertices_in_graph(bpmn_elements=self.bpmn_model.bpmn_elements)
        self.put_edges_in_graph(sequence_flows=self.bpmn_model.sequence_flows)

        return self.graph
