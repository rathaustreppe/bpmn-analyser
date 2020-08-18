import os

import pytest

from src.converter.converter import Converter
from src.graph_pointer import GraphPointer
from src.models.token import Token


class TestIntegration:

    def run_pointer(self,
                    graph_pointer: GraphPointer) -> Token:
        for i in range(100):
            ret = graph_pointer.runstep_graph()
            if ret == 1:
                return graph_pointer.get_token()
            i += 1
        # if graph_pointer does not hold after 100 steps
        return Token(attributes=None)

    def test_bill_process(self, bill_process_solution_token):

        # solution token
        init_attributes = {
            "Ort": "Dresden",
            "Unterschrift ML": True,
            "Unterschrift Zittau": True,
            "Fachlich geprüft": True
        }
        solution_token = Token(attributes=init_attributes)

        # Graph from *.bpmn-file
        pytest_root = os.path.dirname(os.path.abspath(__file__))
        working_dict = os.path.join(pytest_root,
                                    'test_files',
                                    'xml')
        xml_file_path = os.path.join(working_dict,
                                     'bill_process_no_def.bpmn')

        converter = Converter()
        g = converter.convert(rel_path_to_bpmn=xml_file_path)

        init_attributes = {
            "Ort": "Zittau",
            "Unterschrift ML": False,
            "Unterschrift Zittau": False,
            "Fachlich geprüft": False
        }
        t = Token(attributes=init_attributes)

        gp = GraphPointer(graph=g, token=t)
        return_token = self.run_pointer(graph_pointer=gp)
        assert return_token == bill_process_solution_token