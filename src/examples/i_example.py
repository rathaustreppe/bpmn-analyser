from abc import ABC, abstractmethod
from typing import List

from pedantic import pedantic_class

from src.converter.bpmn_models.bpmn_model import BPMNModel
from src.models.token import Token
from src.models.token_state_rule import TokenStateRule
from src.nlp.chunker import Chunker


@pedantic_class
class IExample(ABC):

    @abstractmethod
    def get_init_token(self) -> Token:
        pass

    @abstractmethod
    def get_solution_token(self) -> Token:
        pass

    @abstractmethod
    def get_ruleset(self) -> List[TokenStateRule]:
        pass

    @abstractmethod
    def get_chunker(self) -> Chunker:
        pass

    @abstractmethod
    def get_students_process(self) -> BPMNModel:
        pass
