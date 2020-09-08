from typing import List

from src.models.token import Token
from src.nlp.chunks import SynonymCloud
from src.nlp.token_state_condition import \
    TokenStateCondition
from src.nlp.token_state_modification import \
    TokenStateModification


class TokenStateRule:
    def __init__(self, synonym_cloud: SynonymCloud,
                 state_conditions: List[TokenStateCondition],
                 state_modifcations: List[TokenStateModification]) -> None:
        self.synonym_cloud = synonym_cloud
        self.token_state_conditions = state_conditions
        self.token_state_modifications = state_modifcations

    def apply_rule(self, token: Token) -> Token:
        # if all conditions == True:
            # apply all modifications to token
        pass