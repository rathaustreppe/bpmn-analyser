from typing import List, Tuple

import igraph
import pytest

from src.converter.bpmn_models.bpmn_activity import BPMNActivity
from src.converter.bpmn_models.bpmn_element import BPMNElement
from src.converter.bpmn_models.bpmn_enum import BPMNEnum
from src.converter.bpmn_models.bpmn_model import BPMNModel
from src.converter.bpmn_models.bpmn_sequenceflow import BPMNSequenceFlow
from src.converter.bpmn_models.gateway.bpmn_gateway import BPMNGateway
from src.converter.bpmn_models.gateway.bpmn_parallel_gateway import \
    BPMNParallelGateway
from src.exception.gateway_exception import OpeningGatewayBranchError
from src.exception.stack_exception import EmptyStackPopException
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


    def link_elements(self, source: BPMNElement,
                      target: BPMNElement) -> Tuple[BPMNElement, BPMNElement]:
        linking_flow = BPMNSequenceFlow(id='f1', condition=None,
                                        source=source, target=target)
        source.sequence_flow_out = linking_flow
        target.sequence_flow_in = linking_flow
        return (source, target)

    def test_push_gateway_0_branches(self, stack_handler):
        # error here: gateway always needs at least 1 branch
        gateway = BPMNParallelGateway(id='0',
                                      sequence_flows_in=None,
                                      sequence_flows_out=None)
        with pytest.raises(OpeningGatewayBranchError):
            stack_handler.push_gateway(gateway=gateway,
                                       branch_elements=[])

    def test_push_gateway_2_branches(self, stack_handler):
        # no error here: check if pushing a correct gateway works
        # generate gateway and add two outgoing branches to it
        gateway = BPMNParallelGateway(id='0')
        element1 = BPMNActivity(id='a1', name='act1')
        element2 = BPMNActivity(id='a2', name='act2')
        gateway, element1 = self.link_elements(source=gateway, target=element1)
        gateway, element2 = self.link_elements(source=gateway, target=element2)
        branch_elements = [element1, element2]

        stack_handler.push_gateway(gateway=gateway,
                                   branch_elements=branch_elements)

        # both branches should be on top of stack = 2x pop and
        # should be different
        top1 = stack_handler.stack.pop()
        top2 = stack_handler.stack.pop()
        assert top1 in branch_elements
        assert top2 in branch_elements
        assert top1 != top2

        # after popping branches, opening gateway is on top
        assert stack_handler.stack.pop() == gateway


    def test_pop_gateway_empty_stack(self, stack_handler):
        # error here: popping from an empty stack
        branch_element = BPMNActivity(id='42', name='space')
        with pytest.raises(EmptyStackPopException):
            stack_handler.pop_gateway(branch_element=branch_element)

