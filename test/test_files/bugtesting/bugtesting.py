from typing import List

from src import main
from src.converter.bpmn_models.bpmn_model import BPMNModel
from src.converter.converter import Converter
from src.examples.i_example import IExample
from src.graph_pointer import GraphPointer
from src.models.token import Token
from src.models.token_state_modification import TokenStateModification
from src.models.token_state_rule import TokenStateRule
from src.nlp.chunker import Chunker
from src.nlp.synonym_cloud import SynonymCloud


class Test4Gateways(IExample):

    def get_init_token(self) -> Token:
        init_attributes = {
            'abc': False,
            'ghi1': False,
            'ghi2': False
        }
        return Token(attributes=init_attributes)

    def get_solution_token(self) -> Token:
        init_attributes = {
            'abc': True,
            'ghi1': True,
            'ghi2': True
        }
        return Token(attributes=init_attributes)

    def get_ruleset(self) -> List[TokenStateRule]:
        # ruleset for all attributes (all are the same):
        all_attributes_to_look_for = ['abc', 'ghi1', 'ghi2']
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

    def get_students_process_4gateways(self) -> BPMNModel:
        path_to_bpmn = r'4_gateways_should_work.bpmn'
        converter = Converter()
        return converter.convert(rel_path_to_bpmn=path_to_bpmn)

    def get_students_process(self) -> BPMNModel:
        pass

if __name__ == '__main__':
    print('>>> >>> >>> 4 Gateways should work <<< <<< <<<')
    gw_work = Test4Gateways()
    gw_work_pointer = GraphPointer(model=gw_work.get_students_process_4gateways(),
                                token=gw_work.get_init_token(),
                                ruleset=gw_work.get_ruleset(),
                                chunker=gw_work.get_chunker())
    solution_token = gw_work.get_solution_token()
    main.run_pointer(graph_pointer=gw_work_pointer, solution_token=solution_token)
    print(f'stack after:{gw_work_pointer.stack.items}')
