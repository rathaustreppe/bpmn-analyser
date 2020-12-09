import logging
from typing import List, Optional

from pedantic import pedantic_class

from src.models.running_token import RunningToken
from src.models.token_state_condition import \
    TokenStateCondition
from src.models.token_state_modification import \
    TokenStateModification
from src.nlp.synonym_cloud import SynonymCloud


@pedantic_class
class TokenStateRule:
    def __init__(self, condition: Optional[TokenStateCondition] = None,
                 modification: Optional[TokenStateModification] = None,
                 synonym_cloud: Optional[SynonymCloud] = None) -> None:
        self.synonym_cloud = synonym_cloud
        self.condition = condition
        self.modification = modification

    def _check_conditions(self, token: RunningToken) -> bool:
        if self.condition is not None:
            if not self.condition.check_condition(token=token):
                logging.debug(f'Rule not meet! Token: {token}')
                return False
        return True

    def _apply_modifications(self, token: RunningToken) -> RunningToken:
        if self.modification is not None:
            self.modification.change_token(token=token)
        return token

    def check_and_modify(self, token: RunningToken) -> RunningToken:
        logging.debug(f'Checking TSRule: {self}')
        if self._check_conditions(token=token):
            token = self._apply_modifications(token=token)
        return token

    def __str__(self) -> str:
        return f'TokenStateRule:[SynCloud:{self.synonym_cloud}' \
               f' Conditions: {self.condition}' \
               f' Modifications: {self.modification}]'

    def __repr__(self) -> str:
        return self.__str__()
