import igraph
import pytest

from src.converter.bpmn_models.bpmn_enum import BPMNEnum
from src.graph_pointer import GraphPointer
from src.models.graph_text import GraphText
from src.models.token import Token


class TestGraphPointer:

    def run_pointer(self, graph_pointer: GraphPointer) -> Token:
        for i in range(100):
            ret = graph_pointer.runstep_graph()
            if ret == 1:
                return graph_pointer.get_token()
            i += 1
        # if graph_pointer does not hold after 100 steps
        return Token(attributes=None)


    def test_bill_process1(self, bill_process_solution_token):
        # ML Unterschrift -> nach Zittau -> Vertragsprüfung ->
        # Unterschrift Zittau -> nach Dresden
        # ==> works

        init_attributes = {
            "Ort": "Görlitz",
            "Unterschrift ML": False,
            "Unterschrift Zittau": False,
            "Fachlich geprüft": False
        }
        t = Token(attributes=init_attributes)

        g = igraph.Graph()
        g = g.as_directed()

        g.add_vertices(5)
        g.add_edges([(0, 1), (1, 2), (2, 3), (3, 4)])

        g.vs[0][BPMNEnum.NAME.value] = GraphText(
            text="ML Unterschrift")
        g.vs[1][BPMNEnum.NAME.value] = GraphText(
            text="Nach Zittau schicken")
        g.vs[2][BPMNEnum.NAME.value] = GraphText(
            text='Vertragsprüfung')
        g.vs[3][BPMNEnum.NAME.value] = GraphText(
            text='Zittau Unterschrift')
        g.vs[4][BPMNEnum.NAME.value] = GraphText(
            text='Nach Dresden schicken')

        gp = GraphPointer(graph=g, token=t)
        return_token = self.run_pointer(graph_pointer=gp)
        assert return_token == bill_process_solution_token


    def test_bill_process2(self, bill_process_solution_token):
        # Vertragsprüfung -> Zittau Unterschrift -> Nach Görlitz ->
        # ML Unterschrift -> nach Dresden
        # ==> works

        init_attributes = {
            "Ort": "Zittau",
            "Unterschrift ML": False,
            "Unterschrift Zittau": False,
            "Fachlich geprüft": False
        }
        t = Token(attributes=init_attributes)

        g = igraph.Graph()
        g = g.as_directed()

        g.add_vertices(5)
        g.add_edges([(0, 1), (1, 2), (2, 3), (3, 4)])

        g.vs[0][BPMNEnum.NAME.value] = 'Vertragsprüfung'
        g.vs[1][BPMNEnum.NAME.value] = 'Zittau Unterschrift'
        g.vs[2][
            BPMNEnum.NAME.value] = "Nach Görlitz schicken"
        g.vs[3][BPMNEnum.NAME.value] = "ML Unterschrift"
        g.vs[4][BPMNEnum.NAME.value] = 'Nach Dresden schicken'

        gp = GraphPointer(graph=g, token=t)
        return_token = self.run_pointer(graph_pointer=gp)
        assert return_token == bill_process_solution_token

    def test_bill_process3(self, bill_process_solution_token):
        # business process works

        init_attributes = {
            "Ort": "Zittau",
            "Unterschrift ML": False,
            "Unterschrift Zittau": False,
            "Fachlich geprüft": False
        }
        t = Token(attributes=init_attributes)

        g = igraph.Graph()
        g = g.as_directed()

        g.add_vertices(6)
        g.add_edges(
            [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5)])

        g.vs[0][BPMNEnum.NAME.value] = 'Vertragsprüfung'
        g.vs[1][BPMNEnum.NAME.value] = 'Zittau Unterschrift'
        g.vs[2][BPMNEnum.NAME.value] = "Nach Görlitz schicken"
        g.vs[3][BPMNEnum.NAME.value] = "ML Unterschrift"
        g.vs[4][BPMNEnum.NAME.value] = "Nach Zittau schicken"
        g.vs[5][BPMNEnum.NAME.value] = 'Nach Dresden schicken'

        gp = GraphPointer(graph=g, token=t)
        return_token = self.run_pointer(graph_pointer=gp)
        assert return_token == bill_process_solution_token

    def test_bill_process4(self, bill_process_solution_token):
        # business process doesnt work
        # ML cant sign in Zittau
        init_attributes = {
            "Ort": "Zittau",
            "Unterschrift ML": False,
            "Unterschrift Zittau": False,
            "Fachlich geprüft": False
        }
        t = Token(attributes=init_attributes)

        g = igraph.Graph()
        g = g.as_directed()
        g.add_vertices(4)
        g.add_edges([(0, 1), (1, 2), (2, 3)])

        g.vs[0][BPMNEnum.NAME.value] = 'Vertragsprüfung'
        g.vs[1][BPMNEnum.NAME.value] = 'Zittau Unterschrift'
        g.vs[2][BPMNEnum.NAME.value] = 'ML Unterschrift'
        g.vs[3][BPMNEnum.NAME.value] = 'Nach Dresden schicken'

        gp = GraphPointer(graph=g, token=t)
        return_token = self.run_pointer(graph_pointer=gp)

        assert return_token != bill_process_solution_token
        assert return_token.get_attribute(key='Unterschrift ML') == False
