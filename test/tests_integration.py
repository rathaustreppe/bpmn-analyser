import os
import unittest

from src.converter.converter import Converter
from src.graph_pointer import GraphPointer
from src.models.token import Token
from src.models.token_state_modification import TokenStateModification
from src.models.token_state_rule import TokenStateRule
from src.nlp.synonym_cloud import SynonymCloud


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
                        chunker,
                        ruleset,
                        init_token) -> Token:

        xml_file_path = os.path.join(xml_folders_path, filename)

        converter = Converter()
        model = converter.convert(rel_path_to_bpmn=xml_file_path)

        graph_pointer = GraphPointer(model=model,
                                     token=init_token,
                                     ruleset=ruleset,
                                     chunker=chunker)

        return self.run_pointer(graph_pointer=graph_pointer)


    def test_bill_process_system_test(self, xml_folders_path,
                                      bill_process_chunker,
                                      bill_process_ruleset,
                                      bill_process_init_token,
                                      bill_process_solution_token):

        file = os.path.join('bill process', 'bill_process_with_def.bpmn')
        return_token = self.execute_process(filename=file,
                                            xml_folders_path=xml_folders_path,
                                            chunker=bill_process_chunker,
                                            ruleset=bill_process_ruleset,
                                            init_token=bill_process_init_token)

        assert return_token == bill_process_solution_token

    def test_bill_process_from_graph2(self, xml_folders_path,
                                      bill_process_chunker,
                                      bill_process_ruleset,
                                      bill_process_init_token,
                                      bill_process_solution_token):
        # bill first arrives in goerlitz
        modification = TokenStateModification(key='place',value='Goerlitz')
        bill_process_init_token.change_value(modification=modification)

        file = os.path.join('bill process', 'bill_process_2.bpmn')
        return_token = self.execute_process(filename=file,
                                            xml_folders_path=xml_folders_path,
                                            chunker=bill_process_chunker,
                                            ruleset=bill_process_ruleset,
                                            init_token=bill_process_init_token)
        assert return_token == bill_process_solution_token


    def test_bill_process_from_graph3(self, xml_folders_path,
                                      bill_process_chunker,
                                      bill_process_ruleset,
                                      bill_process_init_token,
                                      bill_process_solution_token):

        file = os.path.join('bill process', 'bill_process_3.bpmn')
        return_token = self.execute_process(filename=file,
                                            xml_folders_path=xml_folders_path,
                                            chunker=bill_process_chunker,
                                            ruleset=bill_process_ruleset,
                                            init_token=bill_process_init_token)
        assert return_token == bill_process_solution_token


    def test_bill_process_from_graph4(self, xml_folders_path,
                                      bill_process_chunker,
                                      bill_process_ruleset,
                                      bill_process_init_token,
                                      bill_process_solution_token):

        file = os.path.join('bill process', 'bill_process_4.bpmn')
        return_token = self.execute_process(filename=file,
                                            xml_folders_path=xml_folders_path,
                                            chunker=bill_process_chunker,
                                            ruleset=bill_process_ruleset,
                                            init_token=bill_process_init_token)
        assert return_token == bill_process_solution_token


    def test_bill_process_from_graph5(self, xml_folders_path,
                                      bill_process_chunker,
                                      bill_process_ruleset,
                                      bill_process_init_token,
                                      bill_process_solution_token):
        # business process doesnt work
        # ML cant sign in Zittau
        file = os.path.join('bill process', 'bill_process_5.bpmn')
        return_token = self.execute_process(filename=file,
                                            xml_folders_path=xml_folders_path,
                                            chunker=bill_process_chunker,
                                            ruleset=bill_process_ruleset,
                                            init_token=bill_process_init_token)

        assert return_token != bill_process_solution_token
        assert return_token.get_attribute(key='signature ML') == False

    def test_interlaced_gateways(self, xml_folders_path,
                                 nn_chunker):

        # define the rules
        # when finding 'act1' change act1-attribute of token to true
        # same with 'act2' and 'act3'
        ruleset = []
        for act in ['act1', 'act2', 'act3']:
            syncloud = SynonymCloud.from_list(text=[act])
            modification = TokenStateModification(key=act, value=True)
            tsr_act = TokenStateRule(state_conditions=[],
                                    state_modifications=[modification],
                                    synonym_cloud=syncloud)
            ruleset.append(tsr_act)

        # define the token
        init_attibutes = {
            'act1': False,
            'act2': False,
            'act3': False,
            'k1': 'v1' # used for branch condition of XOR
        }
        token = Token(attributes=init_attibutes)

        file = os.path.join('converter', 'exclusive_in_parallel_gateway.bpmn')
        return_token = self.execute_process(filename=file,
                                            xml_folders_path=xml_folders_path,
                                            chunker=nn_chunker,
                                            ruleset=ruleset,
                                            init_token=token)

        # define solution token
        init_attibutes = {
            'act1': True, # True, because XOR branches into act1.
            'act2': False, # False, because XOR branches into act1 instead of act2
            'act3': True # True, because AND branches into act3.
        }
        solution_token = Token(attributes=init_attibutes)

        assert return_token == solution_token