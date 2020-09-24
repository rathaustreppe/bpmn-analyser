import os
from copy import copy
from typing import List

import igraph
import pytest

from src.converter.bpmn_models.bpmn_enum import BPMNEnum
from src.converter.bpmn_models.event.bpmn_endevent import BPMNEndEvent
from src.converter.bpmn_models.event.bpmn_startevent import BPMNStartEvent
from src.converter.bpmn_models.gateway.bpmn_exclusive_gateway import \
    BPMNExclusiveGateway
from src.converter.bpmn_models.gateway.bpmn_inclusive_gateway import \
    BPMNInclusiveGateway
from src.converter.bpmn_models.gateway.bpmn_parallel_gateway import \
    BPMNParallelGateway
from src.converter.converter import Converter
from src.exception.WrongTypeException import WrongTypeException
from src.exception.gateway_exception import ExclusiveGatewayBranchError
from src.exception.graph_exception import GraphNotDirectedError, \
    GraphHasNoStartError, GraphHasMultipleStartsError
from src.graph_pointer import GraphPointer
from src.models.token import Token
from src.models.token_state_condition import TokenStateCondition, Operators
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

    def test_not_reached_end_event_no_init(self):
        graph = igraph.Graph()
        graph.add_vertices(1)
        graph_pointer = self.graph_pointer(graph=graph)

        assert graph_pointer.reached_end_event() is False

    def test_not_reached_end_event(self):
        graph = igraph.Graph()
        graph.add_vertices(1)
        graph.vs[0][BPMNEnum.TYPE.value] = BPMNStartEvent.__name__
        graph_pointer = self.graph_pointer(graph=graph)
        graph_pointer.previous_element = graph.vs[0]

        assert graph_pointer.reached_end_event() is False

    def test_reached_end_event(self):
        graph = igraph.Graph()
        graph.add_vertices(1)
        graph.vs[0][BPMNEnum.TYPE.value] = BPMNEndEvent.__name__
        graph_pointer = self.graph_pointer(graph=graph)
        graph_pointer.previous_element = graph.vs[0]

        assert graph_pointer.reached_end_event() is True

    def test_condition_fulfilling_edges_all_edges(self, example_token):
        # all edges fulfill condition
        graph = igraph.Graph()
        graph.add_vertices(2)

        k1, v1 = 'k1', 'v1'
        k2, v2 = 'k2', 'v2'
        condition1 = TokenStateCondition(tok_attribute=k1,
                                         operator=Operators.EQUALS,
                                         tok_value=v1)
        graph.add_edge(source=graph.vs[0],
                            target=graph.vs[1],
                            condition=condition1,
                            id=0)
        condition2 = TokenStateCondition(tok_attribute=k2,
                                         operator=Operators.EQUALS,
                                         tok_value=v2)
        graph.add_edge(source=graph.vs[0],
                       target=graph.vs[1],
                       condition=condition2,
                       id=1)
        graph_pointer = self.graph_pointer(graph=graph, token=example_token)
        edges_to_check = graph.vs[0].out_edges()
        edges = graph_pointer.get_condition_fulfilling_edges(edges_to_check=edges_to_check)

        assert len(edges) == 2
        assert edges[0].index != edges[1].index
        assert edges[0] == 0 or 1

    def test_condition_fulfilling_edges_none(self, example_token):
        graph = igraph.Graph()
        graph.add_vertices(2)
        graph_pointer = self.graph_pointer(graph=graph, token=example_token)
        edges_to_check = graph.vs[0].out_edges()
        edges = graph_pointer.get_condition_fulfilling_edges(edges_to_check=edges_to_check)
        assert len(edges) == 0

    def test_condition_fulfilling_edges_no_condition(self, example_token):
        graph = igraph.Graph()
        graph.add_vertices(2)
        graph.add_edge(source=graph.vs[0], target=graph.vs[1])
        graph_pointer = self.graph_pointer(graph=graph, token=example_token)
        edges_to_check = graph.vs[0].out_edges()
        edges = graph_pointer.get_condition_fulfilling_edges(edges_to_check=edges_to_check)
        assert len(edges) == 0

    def test_is_gateway(self):
        graph = igraph.Graph()
        graph.add_vertices(1)
        graph.vs[0][BPMNEnum.TYPE.value] = BPMNParallelGateway.__name__
        assert GraphPointer.is_gateway(gateway=graph.vs[0]) is True

    def test_is_not_gateway(self):
        graph = igraph.Graph()
        graph.add_vertices(1)
        graph.vs[0][BPMNEnum.TYPE.value] = BPMNStartEvent.__name__
        assert GraphPointer.is_gateway(gateway=graph.vs[0]) is False

    def test_collect_conditional_edges_of_gateway_no_gateway(self):
        graph = igraph.Graph()
        graph.add_vertices(1)
        graph.vs[0][BPMNEnum.TYPE.value] = BPMNStartEvent.__name__
        graph_pointer = self.graph_pointer(graph=graph)
        with pytest.raises(WrongTypeException):
            graph_pointer.collect_conditional_edges_of_gateway(gateway=graph.vs[0])

    def test_collect_conditional_edges_of_gateway_parallel_gateway(self):
        graph = igraph.Graph()
        graph.add_vertices(3)
        graph.add_edges([(0,1), (0,2)])
        graph.vs[0][BPMNEnum.TYPE.value] = BPMNParallelGateway.__name__
        graph_pointer = self.graph_pointer(graph=graph)
        edges = graph_pointer.collect_conditional_edges_of_gateway(gateway=
                                                                   graph.vs[0])
        assert len(edges) == 2
        assert edges[0] != edges[1]

    def test_collect_conditional_edges_of_gateway_inclusive_gateway(self, example_token):
        graph = igraph.Graph()
        graph.add_vertices(3)
        graph.vs[0][BPMNEnum.TYPE.value] = BPMNInclusiveGateway.__name__

        k1, v1 = 'k1', 'v1'
        k2 = 'k2'
        condition1 = TokenStateCondition(tok_attribute=k1,
                                         operator=Operators.EQUALS,
                                         tok_value=v1)
        graph.add_edge(source=graph.vs[0],
                       target=graph.vs[1],
                       condition=condition1,
                       id=0) # BPMNEnum.ID.value

        condition2 = TokenStateCondition(tok_attribute=k2,
                                         operator=Operators.EQUALS,
                                         tok_value='a value that is wrong')
        graph.add_edge(source=graph.vs[0],
                       target=graph.vs[2],
                       condition=condition2,
                       id=1)
        graph_pointer = self.graph_pointer(graph=graph, token=example_token)
        edges = graph_pointer.collect_conditional_edges_of_gateway(gateway=
                                                                   graph.vs[0])
        assert len(edges) == 1
        assert edges[0][BPMNEnum.ID.value] == 0

    def test_collect_conditional_edges_of_gateway_exclusive_gateway_0_conditions_meet(self, example_token):
        graph = igraph.Graph()
        graph.add_vertices(3)
        graph.vs[0][BPMNEnum.TYPE.value] = BPMNExclusiveGateway.__name__

        k1 = 'k1'
        k2 = 'k2'
        condition1 = TokenStateCondition(tok_attribute=k1,
                                         operator=Operators.EQUALS,
                                         tok_value='wrong value')
        graph.add_edge(source=graph.vs[0],
                       target=graph.vs[1],
                       condition=condition1,
                       id=0)  # BPMNEnum.ID.value

        condition2 = TokenStateCondition(tok_attribute=k2,
                                         operator=Operators.EQUALS,
                                         tok_value='a value that is wrong')
        graph.add_edge(source=graph.vs[0],
                       target=graph.vs[2],
                       condition=condition2,
                       id=1)
        graph_pointer = self.graph_pointer(graph=graph, token=example_token)
        with pytest.raises(ExclusiveGatewayBranchError):
            graph_pointer.collect_conditional_edges_of_gateway(gateway=graph.vs[0])

    def test_collect_conditional_edges_of_gateway_exclusive_gateway(self, example_token):
        graph = igraph.Graph()
        graph.add_vertices(3)
        graph.vs[0][BPMNEnum.TYPE.value] = BPMNExclusiveGateway.__name__

        k1, v1 = 'k1', 'v1'
        condition1 = TokenStateCondition(tok_attribute=k1,
                                         operator=Operators.EQUALS,
                                         tok_value=v1)

        edge_id = 42
        graph.add_edge(source=graph.vs[0],
                       target=graph.vs[1],
                       condition=condition1,
                       id=edge_id)  # BPMNEnum.ID.value

        condition2 = TokenStateCondition(tok_attribute=k1,
                                         operator=Operators.EQUALS,
                                         tok_value='a value that is wrong')
        graph.add_edge(source=graph.vs[0],
                       target=graph.vs[2],
                       condition=condition2,
                       id=0)
        graph_pointer = self.graph_pointer(graph=graph, token=example_token)
        edges = graph_pointer.collect_conditional_edges_of_gateway(gateway=
                                                                   graph.vs[0])
        assert len(edges) == 1
        assert edges[0][BPMNEnum.ID.value] == edge_id


    def test_next_step_with_parallel_gateway(self, xml_folders_path, example_token, nn_chunker):
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
