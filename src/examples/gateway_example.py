from typing import List

from src.converter.bpmn_models.bpmn_model import BPMNModel
from src.examples.i_example import IExample
from src.models.token import Token
from src.models.token_state_rule import TokenStateRule
from src.nlp.chunker import Chunker


class GatewayExample(IExample):
    def get_init_token(self) -> Token:
        pass

    def get_solution_token(self) -> Token:
        pass

    def get_ruleset(self) -> List[TokenStateRule]:
        pass

    def get_chunker(self) -> Chunker:
        pass

    def get_students_process(self) -> BPMNModel:
        pass