import inspect
from typing import Callable

from pedantic import pedantic

from src.models.running_token import RunningToken


class TokenStateCondition:
    """
    This class defines a condition that is checked
    before a RunningToken state can change. Used for sample solution generation.
    Dont get confused with BranchCondition. They are used in the BPMNModel to
    tell when a BPMNGateway has to branch.
    """

    def __init__(self, condition: Callable[[RunningToken], bool]) -> None:
        """
        TokenStateCondition excepts a function that is called later.
        You can choose between standard functions or (anonymous) lambda functions:

        Method 1
        >>> def check_if_not_hungry(token):
        >>>    return token.hungry == False
        >>> TokenStateCondition(condition=check_if_not_hungry)
        > pay attention not to use brackets when calling the constructor!
        > it is a callback function

        Method 2
        >>> TokenStateCondition(condition=lambda token: token.hungry == False)
        > this method does not pollute namespace and has less lines of code
        > recommended method

        If you have more conditions, you pass them all at once:
        >>> TokenStateCondition(condition=lambda token: token.hungry == False and
        >>>                                             token.poor == True)

        """
        self.condition = condition

    @pedantic
    def check_condition(self, token: RunningToken) -> bool:
        """
        Takes a token and checks if its pre-defined
        condition-function is true or false wth the given token.
        """
        return self.condition(token)

    def __str__(self) -> str:
        # Print sourcecode of the defined condition. But remove \n and appending
        # spaces and tabs
        src = inspect.getsource(self.condition)
        src = src.lstrip()
        src = src.rstrip()
        src = src.replace('\t', '')
        src = src.replace('\n', '')
        return f'TokenStateCondition: {src}'

    def __repr__(self) -> str:
        return self.__str__()

    def __eq__(self, other: 'TokenStateCondition') -> bool:
        # I havn't found a way to compare functions. You could compare
        # the source code with inspect, but the results were wrong?!
        # So we return always False to make no false promises.
        return False
