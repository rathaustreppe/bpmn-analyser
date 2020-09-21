from copy import copy

import igraph
import pytest

from src.converter.bpmn_models.bpmn_enum import BPMNEnum
from src.graph_pointer import GraphPointer
from src.models.graph_text import GraphText
from src.models.token import Token
from src.models.token_state_modification import TokenStateModification


class TestGraphPointer:

    ml_signs_bill = 'ML signs bill'
    send_bill_to_zittau = 'send bill to Zittau'
    zittau_checks_contract = 'Zittau checks contract'
    zittau_signs_bill = 'Zittau signs bill'
    send_bill_to_dresden = 'send bill to Dresden'
    startendevent_placeholder = 'startendevent'

    def run_pointer(self, graph_pointer: GraphPointer) -> Token:
        for _ in range(100):
            ret = graph_pointer.runstep_graph()
            if ret == 1:
                return graph_pointer.get_token()
        # if graph_pointer does not hold after 100 steps
        return Token(attributes=None)

    def test_bill_process1(self, bill_process_chunker,
                          bill_process_ruleset,
                          bill_process_init_token,
                          bill_process_solution_token):
        # bill first arrives in goerlitz
        pre = TokenStateModification(key='place', value='Goerlitz')
        bill_process_init_token.change_value(modification=pre)

        graph = igraph.Graph()
        graph = graph.as_directed()

        graph.add_vertices(7)
        graph.add_edges([(0, 1), (1, 2), (2, 3), (3, 4), (4,5),(5,6)])

        graph.vs[0][BPMNEnum.NAME.value] = GraphText(text=self.startendevent_placeholder)
        graph.vs[1][BPMNEnum.NAME.value] = GraphText(text=self.ml_signs_bill)
        graph.vs[2][BPMNEnum.NAME.value] = GraphText(text=self.send_bill_to_zittau)
        graph.vs[3][BPMNEnum.NAME.value] = GraphText(text=self.zittau_checks_contract)
        graph.vs[4][BPMNEnum.NAME.value] = GraphText(text=self.zittau_signs_bill)
        graph.vs[5][BPMNEnum.NAME.value] = GraphText(text=self.send_bill_to_dresden)
        graph.vs[6][BPMNEnum.NAME.value] = GraphText(text=self.startendevent_placeholder)

        graph_pointer = GraphPointer(graph=graph, token=bill_process_init_token,
                                     ruleset=bill_process_ruleset,
                                     chunker=bill_process_chunker)
        return_token = self.run_pointer(graph_pointer=graph_pointer)
        assert return_token == bill_process_solution_token

    def test_bill_process2(self, bill_process_chunker,
                          bill_process_ruleset,
                          bill_process_init_token,
                          bill_process_solution_token):
        graph = igraph.Graph()
        graph = graph.as_directed()

        graph.add_vertices(7)
        graph.add_edges([(0, 1), (1, 2), (2, 3), (3, 4), (4,5),(5,6)])

        graph.vs[0][BPMNEnum.NAME.value] = GraphText(text=self.startendevent_placeholder)
        graph.vs[1][BPMNEnum.NAME.value] = GraphText(text=self.zittau_checks_contract)
        graph.vs[2][BPMNEnum.NAME.value] = GraphText(text=self.zittau_signs_bill)
        graph.vs[3][BPMNEnum.NAME.value] = GraphText(text="send bill to Goerlitz")
        graph.vs[4][BPMNEnum.NAME.value] = GraphText(text=self.ml_signs_bill)
        graph.vs[5][BPMNEnum.NAME.value] = GraphText(text=self.send_bill_to_dresden)
        graph.vs[6][BPMNEnum.NAME.value] = GraphText(text=self.startendevent_placeholder)

        graph_pointer = GraphPointer(graph=graph, token=bill_process_init_token,
                                     ruleset=bill_process_ruleset,
                                     chunker=bill_process_chunker)
        return_token = self.run_pointer(graph_pointer=graph_pointer)
        assert return_token == bill_process_solution_token

    def test_bill_process3(self, bill_process_chunker,
                          bill_process_ruleset,
                          bill_process_init_token,
                          bill_process_solution_token):
        # business process works

        graph = igraph.Graph()
        graph = graph.as_directed()

        graph.add_vertices(8)
        graph.add_edges([(0, 1), (1, 2), (2, 3), (3, 4), (4, 5),(5, 6), (6, 7)])

        graph.vs[0][BPMNEnum.NAME.value] = GraphText(text=self.startendevent_placeholder)
        graph.vs[1][BPMNEnum.NAME.value] = GraphText(text=self.zittau_checks_contract)
        graph.vs[2][BPMNEnum.NAME.value] = GraphText(text=self.zittau_signs_bill)
        graph.vs[3][BPMNEnum.NAME.value] = GraphText(text="send bill to Goerlitz")
        graph.vs[4][BPMNEnum.NAME.value] = GraphText(text=self.ml_signs_bill)
        graph.vs[5][BPMNEnum.NAME.value] = GraphText(text=self.send_bill_to_zittau)
        graph.vs[6][BPMNEnum.NAME.value] = GraphText(text=self.send_bill_to_dresden)
        graph.vs[7][BPMNEnum.NAME.value] = GraphText(text=self.startendevent_placeholder)

        graph_pointer = GraphPointer(graph=graph, token=bill_process_init_token,
                                     ruleset=bill_process_ruleset,
                                     chunker=bill_process_chunker)
        return_token = self.run_pointer(graph_pointer=graph_pointer)
        assert return_token == bill_process_solution_token

    def test_bill_process4(self, bill_process_chunker,
                          bill_process_ruleset,
                          bill_process_init_token,
                          bill_process_solution_token):
        # business process doesnt work
        # ML cant sign in Zittau

        graph = igraph.Graph()
        graph = graph.as_directed()
        graph.add_vertices(6)
        graph.add_edges([(0, 1), (1, 2), (2, 3), (3, 4), (4, 5)])

        graph.vs[0][BPMNEnum.NAME.value] = GraphText(text=self.startendevent_placeholder)
        graph.vs[1][BPMNEnum.NAME.value] = GraphText(text=self.zittau_checks_contract)
        graph.vs[2][BPMNEnum.NAME.value] = GraphText(text=self.zittau_signs_bill)
        graph.vs[3][BPMNEnum.NAME.value] = GraphText(text=self.ml_signs_bill)
        graph.vs[4][BPMNEnum.NAME.value] = GraphText(text=self.send_bill_to_dresden)
        graph.vs[5][BPMNEnum.NAME.value] = GraphText(text=self.startendevent_placeholder)

        graph_pointer = GraphPointer(graph=graph, token=bill_process_init_token,
                                     ruleset=bill_process_ruleset,
                                     chunker=bill_process_chunker)
        return_token = self.run_pointer(graph_pointer=graph_pointer)

        assert return_token != bill_process_solution_token
        assert return_token.get_attribute(key='signature ML') == False
