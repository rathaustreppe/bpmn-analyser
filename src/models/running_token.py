import logging
from typing import Optional, Dict, Union

from pedantic import pedantic_class

from src.models.token import Token
from src.models.token_state_modification import TokenStateModification


#@pedantic_class
class RunningToken(Token):
    def __init__(self,
                 attributes: Optional[Dict[str, Union[str, bool, int, float]]] = None) -> None:
        super().__init__(attributes=attributes)

    @classmethod
    def from_token(cls, token:Token) -> 'RunningToken':
        # Sometimes you have a Token and want an identical RunningToken of
        # this Token. Then you use this function. Changes made to one are NOT
        # reflected to the other.
        return RunningToken(attributes=dict(token.items()))


    def change_value(self, modification: TokenStateModification) -> None:
        key = modification.get_key()

        if key not in self.keys():
            msg = f'Key >{key}< not in token attributes. Token: {self}'
            logging.error(msg)
            raise RuntimeError(msg)

        token_value_before = self[key]
        value = modification.get_value()

        if value == '++':
            # try to add 1 to token value
            try:
                int_value = int(token_value_before)
                int_value += 1
            except ValueError:
                msg = f'Tried to add 1 to a non-integer string: {token_value_before}'
                logging.error(msg)
                raise ValueError(msg)

            # convert back to string if it was a string
            if isinstance(token_value_before, str):
                self[key] = str(int_value)
            else:
                self[key] = int_value

        else:
            # simply set the string to new value
            self[key] = value

        logging.info(f'Token changed: {key}: {token_value_before} -> {value}')