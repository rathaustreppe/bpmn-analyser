from abc import ABC, abstractmethod
from typing import List

from pedantic import pedantic_class

from src.models.scenario import Scenario
from src.models.token_state_rule import TokenStateRule


@pedantic_class
class ISolution(ABC):

    @abstractmethod
    def get_scenarios(self) -> List[Scenario]:
        pass

    @abstractmethod
    def get_ruleset(self) -> List[TokenStateRule]:
        pass
