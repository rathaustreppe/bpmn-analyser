import copy
import logging

from pedantic import pedantic

from src.exception.token_state_errors import MissingAttributeInTokenError
from src.models.running_token import RunningToken


class TokenStateModification:
    # a python interpretable statement to change a token value
    # Examples:
    # 't.key == 0' --> changes attribute >key< to int 0
    # "t.key == 'apple'" --> changes attribute >key< to string 'apple'
    # ''.join(['t.place=','"' , place, '"'] == f't.place = {place}'
    # -> changes place to a pre-defined value of the variable >place<
    # Sadly we cannot use f-strings!
    # Because the {xy}-term in an f-string is evaluated inside TokenStateModification
    # and not on declaration of this string. And TSM doesnt know about this variable.
    def __init__(self, modification: str = '') -> None:
        self.modification = modification

    @pedantic
    def change_token(self, token: RunningToken) -> None:
        t = token #used to have statements like 't.haha = 32'.
        token_before = copy.copy(token)
        exec(self.modification)

        # if you run exec('t.haha = 42) but haha is not in the token-dict, it
        # will be added. This is not a desired functionality. We check here
        # if there were attributes added and print an error message.
        if not token_before.keys() == token.keys():
            # find out the added attribute by using difference set
            difference = set(token.keys()).difference(set(token_before.keys()))

            logging.error(f'attribute {difference} not in token')
            raise MissingAttributeInTokenError(token=token_before, attribute=list(difference)[0])


