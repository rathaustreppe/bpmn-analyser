from typing import Optional, Dict, Union

from pedantic import pedantic_class

from src.models.token import Token

# pedantic got a bug in version 1.2.7 with RunningToken. Please reenable in
# a future version.
#@pedantic_class
class RunningToken(Token):
    """
    The token that runs through the diagram. Is mostly the same a the superclass
    token but was introduced to make it clear which token runs and which token
    is the solution token.
    """

    def __init__(self,
                 attributes: Optional[
                     Dict[str, Union[str, bool, int, float]]] = None) -> None:
        super().__init__(attributes=attributes)

    @classmethod
    def from_token(cls, token: Token) -> 'RunningToken':
        # Sometimes you have a Token and want an identical RunningToken of
        # this Token. Then you use this function. Changes made to one are NOT
        # reflected to the other.
        return RunningToken(attributes=dict(token.items()))
