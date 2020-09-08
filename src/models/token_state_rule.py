from typing import List, Optional

from src.models.token import Token
from src.models.token_state_condition import \
    TokenStateCondition
from src.models.token_state_modification import \
    TokenStateModification
from src.nlp.synonym_cloud import SynonymCloud


class TokenStateRule:
    def __init__(self, state_conditions: List[TokenStateCondition],
                 state_modifications: List[TokenStateModification],
                 synonym_cloud: Optional[SynonymCloud] = None)-> None:
        self.synonym_cloud = synonym_cloud
        self.token_state_conditions = state_conditions
        self.token_state_modifications = state_modifications

    def _check_conditions(self, token: Token) -> bool:
        for condition in self.token_state_conditions:
            if not condition.check_condition(token=token):
                return False
        return True

    def _apply_modifications(self, token: Token) -> Token:
        for modification in self.token_state_modifications:
            token.change_value(modification=modification)
        return token

    def check_and_modify(self, token:Token) -> Token:
        if self._check_conditions(token):
            token = self._apply_modifications(token=token)
        return token