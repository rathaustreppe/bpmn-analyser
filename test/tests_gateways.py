import os
from typing import List

import pytest

from src.converter.converter import Converter
from src.exception.gateway_errors import BranchingGatewayError
from src.graph_pointer import GraphPointer
from src.models.running_token import RunningToken
from src.models.text import Text
from src.models.token import Token
from src.models.token_state_modification import TokenStateModification
from src.models.token_state_rule import TokenStateRule


class TestGateway:
    """
    Containing tests for all different kinds of gateways and gateway-combinations
    """

    def run_pointer(self, graph_pointer: GraphPointer) -> RunningToken:
        ret = graph_pointer.iterate_model()
        if ret[0] == 0:
            return graph_pointer.token
        else:
            # infinite loop
            assert False

    def execute_process(self, filename: str,
                        xml_folders_path,
                        ruleset,
                        init_token) -> RunningToken:

        xml_file_path = os.path.join(xml_folders_path, 'gateway', filename)

        converter = Converter()
        model = converter.convert(rel_file_path=xml_file_path)

        graph_pointer = GraphPointer(model=model,
                                     token=init_token,
                                     ruleset=ruleset)

        return self.run_pointer(graph_pointer=graph_pointer)

    def test_interlaced_gateways(self, xml_folders_path):

        # define the rules
        # when finding 'act1' change act1-attribute of token to true
        # same with 'act2' and 'act3'
        text_act1 = Text('act1')
        def m(t): t.act1 = True
        tsm_1 = TokenStateModification(m)
        tsr_act1 = TokenStateRule(modification=tsm_1,
                                  text=text_act1)

        text_act2 = Text('act2')
        def m(t): t.act2 = True
        tsm_2 = TokenStateModification(m)
        tsr_act2 = TokenStateRule(modification=tsm_2,
                                  text=text_act2)

        text_act3 = Text('act3')
        def m(t): t.act3 = True
        tsm_3 = TokenStateModification(m)
        tsr_act3 = TokenStateRule(modification=tsm_3,
                                  text=text_act3)

        ruleset = [tsr_act1, tsr_act2, tsr_act3]

        # define the token
        init_attibutes = {
            'act1': False,
            'act2': False,
            'act3': False,
            'k1': 'v1' # used for branch condition of XOR
        }
        token = RunningToken(attributes=init_attibutes)

        file = os.path.join('exclusive_in_parallel_gateway.bpmn')
        return_token = self.execute_process(filename=file,
                                            xml_folders_path=xml_folders_path,
                                            ruleset=ruleset,
                                            init_token=token)

        # define solution token
        init_attibutes = {
            'act1': True, # True, because XOR branches into act1.
            'act2': False, # False, because XOR branches into act1 instead of act2
            'act3': True, # True, because AND branches into act3.
            'k1': 'v1' # part of init_token, therefore of solution_token as well
        }
        solution_token = Token(attributes=init_attibutes)

        assert return_token == solution_token

    def test_interlaced_gateways_2(self, xml_folders_path):
        init_token = RunningToken(attributes={
            'v1': 1,
            'v2': 1,
            'def3': False,
            'jkl1': False,
            'jkl2': False,
            'mno1': False,
            'mno2': False,
            'pqr': False
            }
        )

        solution_token = Token(attributes={
            'v1': 1,
            'v2': 1,
            'def3': True,
            'jkl1': True,
            'jkl2': False,
            'mno1': True,
            'mno2': True,
            'pqr': True
            }
        )

        ruleset = []

        # modification-functions for every BPMNActivity
        # in this test: BPMNActivity == function name == token attribute
        # set token attribute to True to see if algorithm reached the BPMNAcitivity
        def def3(t): t.def3 = True
        def jkl1(t): t.jkl1 = True
        def jkl2(t): t.jkl2 = True
        def mno1(t): t.mno1 = True
        def mno2(t): t.mno2 = True
        def pqr(t): t.pqr = True

        all_attributes_to_look_for = [('def3',def3), ('jkl1',jkl1),
                                      ('jkl2',jkl2), ('mno1',mno1),
                                      ('mno2',mno2), ('pqr', pqr)]

        for attribute in all_attributes_to_look_for:
            text = Text(attribute[0])
            tsm = TokenStateModification(modification=attribute[1])
            ruleset.append(TokenStateRule(modification=tsm,
                                          text=text))

        return_token = self.execute_process(filename='gateway_example.bpmn',
                                            xml_folders_path=xml_folders_path,
                                            ruleset=ruleset,
                                            init_token=init_token)

        assert solution_token == return_token


    def test_3_gateways(self, xml_folders_path):

        def get_init_token() -> RunningToken:
            init_attributes = {
                'abc': False,
                'ghi1': False,
                'ghi2': False
            }
            return RunningToken(attributes=init_attributes)

        def get_solution_token() -> Token:
            init_attributes = {
                'abc': True,
                'ghi1': True,
                'ghi2': True
            }
            return Token(attributes=init_attributes)

        def get_ruleset() -> List[TokenStateRule]:
            # ruleset for all attributes (all are the same):
            ruleset = []

            # modification-functions for every BPMNActivity
            # in this test: BPMNActivity == function name == token attribute
            # set token attribute to True to see if algorithm reached the BPMNAcitivity
            def abc(t): t.abc = True
            def ghi1(t): t.ghi1 = True
            def ghi2(t): t.ghi2 = True

            all_attributes_to_look_for = [('abc', abc), ('ghi1',ghi1), ('ghi2',ghi2)]
            for attribute in all_attributes_to_look_for:
                text = Text(attribute[0])
                tsm = TokenStateModification(modification=attribute[1])
                ruleset.append(TokenStateRule(modification=tsm,
                                              text=text))
            return ruleset

        solution_token = get_solution_token()
        return_token = self.execute_process(filename='3_gateways_see.bpmn',
                                            xml_folders_path=xml_folders_path,
                                            ruleset=get_ruleset(),
                                            init_token=get_init_token())
        assert solution_token == return_token


    def test_inclusive_gateway(self, xml_folders_path):
        # test an inclusive gateway with 3 branches where 2 are true
        # checks if both branches are beeing processed and the gateway
        # switches to output

        def get_init_token() -> RunningToken:
            init_attributes = {
                'a': 0,
                'b': 0,
                'c': -1
            }
            return RunningToken(attributes=init_attributes)

        def get_solution_token() -> Token:
            init_attributes = {
                'a': 1,
                'b': 1,
                'c': -1
            }
            return Token(attributes=init_attributes)

        solution_token = get_solution_token()
        return_token = self.execute_process(filename='inclusive_gateway.bpmn',
                                            xml_folders_path=xml_folders_path,
                                            ruleset=[],
                                            init_token=get_init_token())
        assert solution_token == return_token




    def test_dying_xor(self, xml_folders_path):
        # test what happens when an XOR with 2 branches but cannot
        # branch anywhere because of the conditions on the flow.
        # And to see how the adjacent inclusive gateway reacts.
        init_attributes = {
            'a': '0',
            'b':'0'
        }
        init_token = RunningToken(attributes=init_attributes)

        with pytest.raises(BranchingGatewayError):
            self.execute_process(filename='dying_xor.bpmn',
                                xml_folders_path=xml_folders_path,
                                ruleset=[],
                                init_token=init_token)

    def test_dying_xor_changed_order(self, xml_folders_path):
        # Because the order of processing depends on where the elements are in
        # the xml file, we rearrange in a second test the order of the branches.
        init_attributes = {
            'a': '0',
            'b': '0'
        }
        init_token = RunningToken(attributes=init_attributes)

        with pytest.raises(BranchingGatewayError):
            self.execute_process(filename='dying_xor_changed_order.bpmn',
                                xml_folders_path=xml_folders_path,
                                ruleset=[],
                                init_token=init_token)
