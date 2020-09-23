from typing import List

import igraph
import pytest

from src.converter.bpmn_models.bpmn_enum import BPMNEnum
from src.models.gateway_stack_handler import GatewayStackHandler


class TestGatewayStackHandler:

    @pytest.fixture(scope='function', autouse=True)
    def stack_handler(self) -> GatewayStackHandler:
        return GatewayStackHandler()

    @staticmethod
    def example_graph(num_of_branches: int) -> igraph.Graph:
        graph = igraph.Graph()
        graph = graph.as_directed()
        graph.add_vertices(
            num_of_branches + 2)  # +2=opening and closing gateway

        for id in range(num_of_branches):
            idx = id + 1
            graph.add_edges([(0, idx)])  # every branch to opening gateway
            graph.add_edges(
                [(idx, num_of_branches + 1)])  # every branch to closing

        graph.vs[0][BPMNEnum.NAME.value] = 'open'

        for id in range(num_of_branches):
            idx = id + 1  # opening gateway has idx=0
            graph.vs[idx][BPMNEnum.NAME.value] = f'Vertex{idx}'

        graph.vs[num_of_branches + 1][BPMNEnum.NAME.value] = 'closing'
        return graph

    @staticmethod
    def branch_vertices_from_graph(graph: igraph.Graph) -> List[igraph.Vertex]:
        # function is closly connected to inner workings of example_graph() !!!
        num_vertices = len(graph.vs)
        branch_vertices = []
        for id in range(num_vertices - 2):  # -2=leave gateways out
            idx = id + 1
            branch_vertices.append(graph.vs[idx])
        return branch_vertices

    @staticmethod
    def find_gateway(graph: igraph.Graph,
                     gateway_text: str = 'open') -> igraph.Vertex:
        # function is closly connected to inner workings of example_graph() !!!
        if graph.vs[0][BPMNEnum.NAME.value] == gateway_text:
            return graph.vs[0]

    def test_push_gateway_0_branches(self, stack_handler):
        graph = self.example_graph(num_of_branches=0)
        branch_vertices = self.branch_vertices_from_graph(graph=graph)
        opening_gateway = self.find_gateway(graph=graph)

        with pytest.raises(ValueError):
            stack_handler.push_gateway(gateway=opening_gateway,
                                       branch_vertices=branch_vertices)

    def test_push_gateway_1_branches(self, stack_handler):
        graph = self.example_graph(num_of_branches=1)
        branch_vertices = self.branch_vertices_from_graph(graph=graph)
        opening_gateway = self.find_gateway(graph=graph)

        with pytest.raises(ValueError):
            stack_handler.push_gateway(gateway=opening_gateway,
                                       branch_vertices=branch_vertices)

    def test_push_gateway_2_branches(self, stack_handler):
        graph = self.example_graph(num_of_branches=2)
        branch_vertices = self.branch_vertices_from_graph(graph=graph)
        opening_gateway = self.find_gateway(graph=graph)

        stack_handler.push_gateway(gateway=opening_gateway,
                                   branch_vertices=branch_vertices)

        # both branches should be on top of stack = 2x pop and
        # should be different
        top1 = stack_handler.stack.pop()
        top2 = stack_handler.stack.pop()
        assert top1 in branch_vertices
        assert top2 in branch_vertices
        assert top1 != top2

        # after popping branches, opening gateway is on top
        assert stack_handler.stack.pop() == graph.vs[0]

    def test_pop_gateway_empty_stack(self, stack_handler):
        graph = self.example_graph(num_of_branches=2)
        branch_vertices = self.branch_vertices_from_graph(graph=graph)
        with pytest.raises(IndexError):
            stack_handler.pop_gateway(branch_vertex=branch_vertices[0])

    def test_pop_gateway_1_following_branch(self, stack_handler):
        graph = self.example_graph(num_of_branches=1)
        opening_gateway = self.find_gateway(graph=graph)
        opening_gateway[BPMNEnum.NAME.value] = BPMNEnum.PARALLGATEWAY_TEXT.value

        stack_handler.stack.push(item=opening_gateway)

        branch_vertex = self.branch_vertices_from_graph(graph=graph)[0]

        # using branch_vertex from the graph above makes no sense in
        # real life. But we can use them know to check if pushing the next
        # branch_vertex works.
        stack_handler.pop_gateway(branch_vertex=branch_vertex)
        assert stack_handler.next_stack_element() == branch_vertex

    def test_pop_gateway_vertex_on_top(self, stack_handler):
        graph = self.example_graph(num_of_branches=1)
        opening_gateway = self.find_gateway(graph=graph)
        opening_gateway[BPMNEnum.NAME.value] = BPMNEnum.PARALLGATEWAY_TEXT.value
        branch_vertex = self.branch_vertices_from_graph(graph=graph)[0]

        stack_handler.stack.push(item=opening_gateway)
        stack_handler.stack.push(item=branch_vertex)

        stack_handler.pop_gateway(branch_vertex=branch_vertex)

        assert stack_handler.next_stack_element() == branch_vertex

    def test_check_gateway_opening_gateway(self, stack_handler):
        # 0 incoming edges, but 2 outgoing == opening gate
        graph = self.example_graph(num_of_branches=2)
        opening_gateway = self.find_gateway(graph=graph)
        opening_gateway[BPMNEnum.NAME.value] = BPMNEnum.PARALLGATEWAY_TEXT.value
        branch_vertices = self.branch_vertices_from_graph(graph=graph)

        stack_handler.check_gateway_stack(gateway=opening_gateway,
                                          branch_vertices=branch_vertices)

        # check for both branch vertices
        assert stack_handler.next_stack_element() in branch_vertices
        assert stack_handler.next_stack_element() in branch_vertices
        # check for gateway
        assert stack_handler.next_stack_element() == opening_gateway
