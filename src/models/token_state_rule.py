import logging
from typing import Optional

from pedantic import pedantic_class

from src.models.running_token import RunningToken
from src.models.text import Text
from src.models.token_state_condition import \
    TokenStateCondition
from src.models.token_state_modification import \
    TokenStateModification


@pedantic_class
class TokenStateRule:
    def __init__(self, condition: Optional[TokenStateCondition] = None,
                 modification: Optional[TokenStateModification] = None,
                 text: Optional[Text] = None) -> None:
        self.text = text
        self.condition = condition
        self.modification = modification

    def _apply_modifications(self, token: RunningToken) -> RunningToken:
        if self.modification is not None:
            self.modification.change_token(token=token)
        return token

    def check_and_modify(self, token: RunningToken) -> RunningToken:
        logging.debug(f'Checking TSRule: {self}')
        if self.condition is None or self.condition.check_condition(token=token):
            token = self._apply_modifications(token=token)
        else:
            logging.debug(f'Rule not meet! Token: {token}')
        return token

    def __str__(self) -> str:
        return f'TokenStateRule:[Text:{self.text}' \
               f' Conditions: {self.condition}' \
               f' Modifications: {self.modification}]'

    def __repr__(self) -> str:
        return self.__str__()
