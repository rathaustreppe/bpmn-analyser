import inspect
import logging
import traceback
from typing import Callable

from pedantic import pedantic

from src.exception.token_state_errors import MissingAttributeInTokenError
from src.models.running_token import RunningToken
from src.util.string_operations.format_code_string import format_code_string


class TokenStateModification:
    """
    This class defines a modification on a RunningToken and changes it via a
    defined callable function.
    """

    def __init__(self, modification: Callable[[RunningToken], None]) -> None:
        """
       TokenStateModification excepts a function that is called later.
       You can only use standard functions and no lambda function. They
       cannot perform statements (a = 3).

       Usage:
       >>> def gets_hungry(token):
       >>>      token.hungry = True
       >>> TokenStateModification(gets_hungry)
       > pay attention not to use brackets when calling the constructor!
       > it is a callback function

       Inside the modification you can have several token modifications:
       >>> def got_rich(token):
       >>>      token.hungry = False
       >>>      token.poor = False
       >>> TokenStateModification(got_rich)
       """
        self.modification = modification

    @pedantic
    def change_token(self, token: RunningToken) -> None:
        """
        Changes the RunningToken with the self.modification-callable-function.
        """
        token_before = token.copy()
        try:
            self.modification(token)
        except Exception:
            msg = f'Cannot run the modification: {self.modification}.'
            logging.error(msg)
            traceback.print_exc()

        # if you run the statement 't.haha = 42' but haha is not in the token-dict, it
        # will be added. This is not a desired functionality. We check here
        # if there have been attributes added and print an error message.
        if not token_before.keys() == token.keys():
            # find out the added attribute by using difference set
            difference = set(token.keys()).difference(set(token_before.keys()))

            logging.error(f'attribute {difference} not in token')
            raise MissingAttributeInTokenError(token=token_before,
                                               attribute=list(difference)[0])

        # for logging purposes it is nice to see what token state has changed
        # and warn the user if the data type of a token value has changed.
        diff = {}
        for key in token:
            if token[key] != token_before[key]:
                diff[key] = (token_before[key], token[key])
        logging.debug(f'Token changed: {diff}')

    def __str__(self) -> str:
        # Print sourcecode of the defined modification. But remove \n
        # and appending spaces and tabs
        src = inspect.getsource(self.modification)
        src = format_code_string(text=src)
        return f'TokenStateCondition: {src}'

    def __repr__(self) -> str:
        return self.__str__()
