import os

import igraph

from src.converter.bpmn_models.bpmn_enum import BPMNEnum
from src.converter.converter import Converter
from src.converter.xml_reader import XMLReader
from src.graph_pointer import GraphPointer
from src.models.token import Token
from src.models.token_state_modification import TokenStateModification


class TestIntegration:

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
                return graph_pointer.token
        # if graph_pointer does not hold after 100 steps
        return Token(attributes=None)

    def execute_process(self, filename: str,
                        xml_folders_path,
                        bill_process_chunker,
                        bill_process_ruleset,
                        bill_process_init_token) -> Token:

        xml_file_path = os.path.join(xml_folders_path, 'bill process', filename)

        converter = Converter()
        graph = converter.convert(rel_path_to_bpmn=xml_file_path)

        graph_pointer = GraphPointer(graph=graph, token=bill_process_init_token,
                                     ruleset=bill_process_ruleset,
                                     chunker=bill_process_chunker)

        return self.run_pointer(graph_pointer=graph_pointer)


    def test_bill_process_system_test(self, xml_folders_path,
                                      bill_process_chunker,
                                      bill_process_ruleset,
                                      bill_process_init_token,
                                      bill_process_solution_token):

        return_token = self.execute_process(filename='bill_process_with_def.bpmn',
                                            xml_folders_path=xml_folders_path,
                                            bill_process_chunker=bill_process_chunker,
                                            bill_process_ruleset=bill_process_ruleset,
                                            bill_process_init_token=bill_process_init_token)

        assert return_token == bill_process_solution_token

    def test_bill_process_from_graph2(self, xml_folders_path,
                                      bill_process_chunker,
                                      bill_process_ruleset,
                                      bill_process_init_token,
                                      bill_process_solution_token):
        # bill first arrives in goerlitz
        modification = TokenStateModification(key='place',value='Goerlitz')
        bill_process_init_token.change_value(modification=modification)

        return_token = self.execute_process(filename='bill_process_2.bpmn',
                                            xml_folders_path=xml_folders_path,
                                            bill_process_chunker=bill_process_chunker,
                                            bill_process_ruleset=bill_process_ruleset,
                                            bill_process_init_token=bill_process_init_token)
        assert return_token == bill_process_solution_token


    def test_bill_process_from_graph3(self, xml_folders_path,
                                      bill_process_chunker,
                                      bill_process_ruleset,
                                      bill_process_init_token,
                                      bill_process_solution_token):

        return_token = self.execute_process(filename='bill_process_3.bpmn',
                                            xml_folders_path=xml_folders_path,
                                            bill_process_chunker=bill_process_chunker,
                                            bill_process_ruleset=bill_process_ruleset,
                                            bill_process_init_token=bill_process_init_token)
        assert return_token == bill_process_solution_token


    def test_bill_process_from_graph4(self, xml_folders_path,
                                      bill_process_chunker,
                                      bill_process_ruleset,
                                      bill_process_init_token,
                                      bill_process_solution_token):

        return_token = self.execute_process(filename='bill_process_4.bpmn',
                                            xml_folders_path=xml_folders_path,
                                            bill_process_chunker=bill_process_chunker,
                                            bill_process_ruleset=bill_process_ruleset,
                                            bill_process_init_token=bill_process_init_token)
        assert return_token == bill_process_solution_token


    def test_bill_process_from_graph5(self, xml_folders_path,
                                      bill_process_chunker,
                                      bill_process_ruleset,
                                      bill_process_init_token,
                                      bill_process_solution_token):
        # business process doesnt work
        # ML cant sign in Zittau
        return_token = self.execute_process(filename='bill_process_5.bpmn',
                                            xml_folders_path=xml_folders_path,
                                            bill_process_chunker=bill_process_chunker,
                                            bill_process_ruleset=bill_process_ruleset,
                                            bill_process_init_token=bill_process_init_token)

        assert return_token != bill_process_solution_token
        assert return_token.get_attribute(key='signature ML') == False

