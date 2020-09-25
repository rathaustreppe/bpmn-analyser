from typing import List, Optional, Union

from pedantic import pedantic_class

from src.converter.bpmn_models.bpmn_activity import BPMNActivity
from src.converter.bpmn_models.bpmn_element import BPMNElement
from src.converter.bpmn_models.event.bpmn_endevent import BPMNEndEvent
from src.converter.bpmn_models.event.bpmn_startevent import BPMNStartEvent
from src.converter.bpmn_models.gateway.bpmn_gateway import BPMNGateway
from src.converter.bpmn_models.gateway.bpmn_parallel_gateway import \
    BPMNParallelGateway
from src.exception.gateway_exception import OpeningGatewayBranchError, \
    ClosingGatewayBranchError
from src.exception.stack_exception import EmptyStackPopException
from src.models.stack import Stack


@pedantic_class
class GatewayStackHandler:
    """
    Class that knows how to put BPMN-Gateways
    in a stack. Used to keep track of multiple branches that split up after each
    gateway and come together in a closing gateway.
    """

    def __init__(self) -> None:
        self.stack: Stack[Union[BPMNElement, BPMNParallelGateway, BPMNActivity]] = Stack()

    def check_gateway_stack(self, gateway: BPMNGateway,
                            branch_elements: List[BPMNElement]) -> None:
        """
       Checks the type of gateway and proceeds with stack operations.
       <branch_vertices> contains first element of all branches where
       the conditions are meet/true to branch into them.
       """
        if gateway.is_opening_gateway():
            # opening gateway: we need to push them and
            # their branches on the stack
            self.push_gateway(gateway=gateway, branch_elements=branch_elements)
        else:
            # If it is a closing gateway, we check if we can take it
            # from the stack.
            # If we can take it from the stack, we put
            # the following branch_vertex
            # onto the stack. Because BPMN-Specification, only one vertex
            # follows a closing gateway.
            # If we cannot take it from the stack, other branches must be
            # processed before.
            if len(branch_elements) == 1:
                self.pop_gateway(branch_element=branch_elements[0])
            else:
                raise ClosingGatewayBranchError(gateway=gateway,
                                                branch_elements=branch_elements)

    def push_gateway(self, gateway: BPMNGateway,
                     branch_elements: List[BPMNElement]) -> None:
        """
        Pushes an opening gateway and its branches on the stack. Before a
        gateway can be removed again, all of its branches must be
        removed before.
        So in the stack, the gateway is below its branches. This way we make
        sure every branch is processed before removing the gateway.
        """
        if len(branch_elements) == 0:
            raise OpeningGatewayBranchError(gateway=gateway)
        else:
            self.stack.push(item=gateway)
            for element in branch_elements:
                self.stack.push(item=element)

    def pop_gateway(self, branch_element: BPMNElement) -> None:
        """
        Tries to remove a gateway from the stack. This only works, when every
        branch_element of this gateway is processed and removed first.
        Still, we need the element that comes after the gateway to push it on
        the stack after removing the gateway. So every calling class (e.g.
        GraphPointer & BPMNModel) knows what comes next after removing
        a closing gateway.
        If top of stack is not a gateway, not all branches of a gateway were
        processed. Call GatewayStackHandler.next_stack_element()
        to get the vertex.
        """
        top_of_stack = self.stack.top()
        if top_of_stack is None:
            raise EmptyStackPopException()

        if isinstance(top_of_stack, BPMNGateway) and \
                top_of_stack.is_opening_gateway():
            # remove opening gateway from stack
            self.stack.pop()
            # add following vertex on stack
            self.stack.push(item=branch_element)


    def next_stack_element(self) -> \
            Optional[Union[BPMNGateway, BPMNActivity, BPMNStartEvent,
                           BPMNEndEvent, BPMNElement]]:
        if self.stack.top() is not None:
            return self.stack.pop()
        else:
            return None


    def top_of_stack_is_gateway(self) -> bool:
        return isinstance(self.stack.top(), BPMNGateway)

    def top_of_stack_is_activity(self) -> bool:
        return isinstance(self.stack.top(), BPMNActivity)