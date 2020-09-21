import os
from copy import copy
from typing import List

import igraph
import pytest

from src.converter.bpmn_models.bpmn_enum import BPMNEnum
from src.converter.converter import Converter
from src.exception.graph_exception import GraphNotDirectedError, \
    GraphHasNoStartError, GraphHasMultipleStartsError
from src.graph_pointer import GraphPointer
from src.models.token import Token
from src.models.token_state_condition import TokenStateCondition
from src.models.token_state_modification import TokenStateModification
from src.nlp.chunker import Chunker


class TestGraphPointer:

    def graph_pointer(self, graph: igraph.Graph,
                      token: Token = Token(),
                      ruleset: List[TokenStateCondition] = [],
                      chunker: Chunker = Chunker()) -> GraphPointer:
        return GraphPointer(graph=graph, token=token,
                                     ruleset=ruleset,
                                     chunker=chunker)

    def test_find_start_vertex_not_directed_graph(self):
        graph = igraph.Graph()
        graph = graph.as_undirected()
        graph.add_vertices(2)
        graph.add_edges([(0, 1)])
        graph_pointer = self.graph_pointer(graph=graph)

        with pytest.raises(GraphNotDirectedError):
            graph_pointer.find_start_vertex()

    def test_find_start_vertex_no_start(self):
        graph = igraph.Graph()
        graph = graph.as_directed()
        graph.add_vertices(2)
        graph.add_edges([(0, 1), (1,0)]) # referencing each other -> no start
        graph_pointer = self.graph_pointer(graph=graph)

        with pytest.raises(GraphHasNoStartError):
            graph_pointer.find_start_vertex()

    def test_find_start_vertex(self):
        graph = igraph.Graph()
        graph = graph.as_directed()
        graph.add_vertices(2)
        graph.add_edges([(0, 1)])
        graph_pointer = self.graph_pointer(graph=graph)

        assert graph_pointer.find_start_vertex() == graph.vs[0]

    def test_find_start_vertex_multiple_starts(self):
        graph = igraph.Graph()
        graph = graph.as_directed()
        graph.add_vertices(3)
        # vertex 0 and 1 point to 2. So vertex 1 and 2 are starting points
        graph.add_edges([(0, 2), (1,2)])
        graph_pointer = self.graph_pointer(graph=graph)

        with pytest.raises(GraphHasMultipleStartsError):
            graph_pointer.find_start_vertex()

    def test_find_start_vertex_disconnected_multiple_starts(self):
        graph = igraph.Graph()
        graph = graph.as_directed()
        graph.add_vertices(2)
        # no edges = both vertices are starting points but are not connected
        graph_pointer = self.graph_pointer(graph=graph)

        with pytest.raises(GraphHasMultipleStartsError):
            graph_pointer.find_start_vertex()

    def test_next_step_with_gateway(self, xml_folders_path, example_token, nn_chunker):
        xml_file_path = os.path.join(xml_folders_path,
                                     'converter',
                                     'min_parallel_gateway.bpmn')
        converter = Converter()
        graph = converter.convert(rel_path_to_bpmn=xml_file_path)
        graph_pointer = self.graph_pointer(graph=graph, token=example_token, chunker=nn_chunker)

        # first call for init startevent
        graph_pointer.runstep_graph()
        assert graph_pointer.previous_element[BPMNEnum.NAME.value] == 'SE'
        assert graph_pointer.stack_handler.stack.empty()

        # next call to find opening gateway --> check stack
        graph_pointer.runstep_graph()
        assert graph_pointer.previous_element[BPMNEnum.NAME.value] == BPMNEnum.PARALLGATEWAY_TEXT.value
        assert graph_pointer.stack_handler.stack.top()[BPMNEnum.NAME.value] in ['act','Bact']

        # next call to go into first branch
        graph_pointer.runstep_graph()
        assert graph_pointer.previous_element[BPMNEnum.NAME.value] in ['act','Bact']
        assert graph_pointer.stack_handler.stack.top()[BPMNEnum.NAME.value] in ['act','Bact']

        # next call to go into adjacent of first branch == closing gateway
        graph_pointer.runstep_graph()
        assert graph_pointer.previous_element[BPMNEnum.NAME.value] == BPMNEnum.PARALLGATEWAY_TEXT.value
        assert graph_pointer.stack_handler.stack.top()[BPMNEnum.NAME.value] in ['act','Bact']

        # next call to finish first branch and ask stack to go into second branch
        graph_pointer.runstep_graph()
        assert graph_pointer.previous_element[BPMNEnum.NAME.value] in ['act','Bact']
        assert graph_pointer.stack_handler.stack.top()[BPMNEnum.NAME.value] == BPMNEnum.PARALLGATEWAY_TEXT.value

        # next call to go adjacent of second branch == closing gateway
        # but stack is empty --> finishing gateway and taking it from stack
        # but putting adjacent of closing gateway on stack
        graph_pointer.runstep_graph()
        assert graph_pointer.previous_element[BPMNEnum.NAME.value] == BPMNEnum.PARALLGATEWAY_TEXT.value
        assert graph_pointer.stack_handler.stack.top()[BPMNEnum.NAME.value] == 'EE'

        # next call to go into endevent and clear stack
        graph_pointer.runstep_graph()
        assert graph_pointer.previous_element[BPMNEnum.NAME.value] == 'EE'
        assert graph_pointer.stack_handler.stack.empty()

        # next call to to find out it reached the end of the graph (returns 1)
        assert graph_pointer.runstep_graph() == 1
