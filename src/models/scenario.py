from pedantic import pedantic_class

from src.models.running_token import RunningToken
from src.models.token import Token


@pedantic_class
class Scenario():
    """
    When running a business process that contains gateways, there are one
    or more decisions to make at each gateway - especially at exclusive
    and inclusive gateways.
    So a singleton token cannot run trough the >entire< graph.

    It is also not possible to duplicate the token at each gateway: the gateway
    decides where to branch next by checking the token state. And this state
    is always the same no matter how often you run the program. This will
    leads to the problem that parts of the diagram will never be checked by
    this software. For an explanation of the XOR-problem with an example see:
    https://github.com/rathaustreppe/bpmn-analyser/issues/10

    Scenarios are a class to solve this issue. They allow to define different
    >>scenarios<< of different business-process-cases.
    Example:In real-life you have modelled the business process of
    an ATM in a single diagram.
    Then the first scenario would be: the customer wants to withdraw cash.
    And the second scenario would be: another customer wants to deposit cash.
    Those are two different paths you could go in your diagram.
    And >>Scenario<< is a class to define exactly this one path in your diagram.

    Scenarios make it possible to 'walk' different paths of a diagram and
    perform analysis on them. This way you can 'test' the students diagrams
    and how handle different cases. And if a diagram can handle all scenarios
    well, we can assume that this diagram is correct!

    A single scenario can be enough for simple linear processes. On the other
    side it might be difficult to test all different combinations of decisions
    in a complex business process. So you may need to find a balanced way.
    """

    def __init__(self, running_token: RunningToken,
                 expected_token: Token,
                 description: str) -> None:
        self.running_token = running_token
        self.expected_token = expected_token
        self.description = description

    def __str__(self) -> str:
        return self.description

    def __repr__(self) -> str:
        return self.__str__()
