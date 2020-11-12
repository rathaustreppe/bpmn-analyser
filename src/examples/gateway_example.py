from typing import List

from src.converter.bpmn_models.bpmn_model import BPMNModel
from src.converter.converter import Converter
from src.examples.i_example import IExample
from src.models.running_token import RunningToken
from src.models.token import Token
from src.models.token_state_modification import TokenStateModification
from src.models.token_state_rule import TokenStateRule
from src.nlp.chunker import Chunker
from src.nlp.synonym_cloud import SynonymCloud


class GatewayExample(IExample):
    def get_init_token(self) -> RunningToken:
        init_attributes = {
            'v1': '1',
            'v2': '1',
            'def3': False,
            'jkl1': False,
            'jkl2': False,
            'mno1': False,
            'mno2': False,
            'pqr': False
        }
        return RunningToken(attributes=init_attributes)

    def get_solution_token(self) -> Token:
        init_attributes = {
            'v1': '1',
            'v2': '1',
            'def3': True,
            'jkl1': True,
            'jkl2': False,
            'mno1': True,
            'mno2': True,
            'pqr': True
        }
        return Token(attributes=init_attributes)

    def get_ruleset(self) -> List[TokenStateRule]:
        # ruleset for all attributes (all are the same):
        all_attributes_to_look_for = ['def3', 'jkl1', 'jkl2',
                                      'mno1', 'mno2', 'pqr']
        ruleset = []
        for attribute in all_attributes_to_look_for:
            syncloud = SynonymCloud.from_list(text=[attribute])
            mod = TokenStateModification(key=attribute, value=True)
            ruleset.append(TokenStateRule(state_conditions=[],
                                      state_modifications=[mod],
                                      synonym_cloud=syncloud))
        return ruleset


    def get_chunker(self) -> Chunker:
        grammar = r"""
            NN_Chunk:     {<NN.?>}
            """
        return Chunker(chunk_grams=grammar)

    def get_students_process(self) -> BPMNModel:
        path_to_bpmn = r'gateway_example.bpmn'
        converter = Converter()
        return converter.convert(rel_file_path=path_to_bpmn)