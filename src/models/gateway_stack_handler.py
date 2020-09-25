from typing import List, Optional

import igraph
from pedantic import pedantic_class

from src.converter.bpmn_models.bpmn_enum import BPMNEnum
from src.converter.bpmn_models.gateway.bpmn_gateway import BPMNGateway
from src.models.stack import Stack


@pedantic_class
class GatewayStackHandler:
    """
    Class that knows how to put BPMN-Gateways (or their respective vertices)
    in a stack. Used to keep track of multiple branches that split up after each
    gateway and come together in a closing gateway.
    """

    def __init__(self) -> None:
        self.stack: Stack[igraph.Vertex] = Stack()

    def check_gateway_stack(self, gateway: igraph.Vertex,
                            branch_vertices: List[igraph.Vertex]) -> None:
        """
        Checks the type of gateway and proceeds with stack operations.
        <branch_vertices> contains first vertex of all branches where
        the conditions are meet/true to branch into them.
        """

        # BPMN specifies two identical gateways with the same symbol: the first
        # gateway splits into multiple branches and the second gateway collects
        # the branches. We refer to them as 'opening' and 'closing' gateways.
        # To check whether a gateway is opening or closing, we check the number
        # of incoming and outgoing branch_vertices.

        num_incoming = len(gateway.in_edges())
        num_outgoing = len(gateway.out_edges())

        if num_outgoing > num_incoming:
            # opening gateway
            # We need to push them and their branches on the stack.
            self.push_gateway(gateway=gateway, branch_vertices=branch_vertices)

        elif num_incoming > num_outgoing:
            # closing gateway
            # If it is a closing gateway, we check if we can take it
            # from the stack.
            # If we can take it from the stack, we put the following branch_vertex
            # onto the stack. Because BPMN-Specification, only one vertex
            # follows a closing gateway.
            if len(branch_vertices) == 1:
                self.pop_gateway(branch_vertex=branch_vertices[0])
            else:
                raise ValueError(
                    f'Closing gateway {gateway} has not exactly 1 outgoing '
                    f'branch vertex. Found: {len(branch_vertices)}. '
                    f'This contradicts BPMN-specification.')

        else:
            raise ValueError(f'Gateway {gateway} has same number of incoming '
                             f'and outgoing branch_vertices ({num_incoming}/{num_outgoing}). '
                             f'This contradicts BPMN-specification.')

    def push_gateway(self, gateway: igraph.Vertex,
                     branch_vertices: List[igraph.Vertex]) -> None:
        """
        Pushes an opening gateway and its branches on the stack. Before a
        gateway can be removed again, all of its branches must be removed before.
        So in the stack, the gateway is below its branches. This way we make
        sure every branch is processed before removing the gateway.
        """
        if len(branch_vertices) <= 1:
            raise ValueError(f'The opening gateway: {gateway} cannot have '
                             f'only 1 or 0 outgoing edges. This contradicts '
                             f'BPMN-specification.')
        self.stack.push(item=gateway)
        for vertex in branch_vertices:
            self.stack.push(item=vertex)

    def pop_gateway(self, branch_vertex: igraph.Vertex) -> None:
        """
        Tries to remove a gateway from the stack. This only works, when every
        branch_vertex of this gateway is processed and removed first.
        Still, we need the vertex that comes after the gateway to push it on
        the stack after removing the gateway. So every calling class (e.g.
        GraphPointer) knows what comes next after removing a closing gateway.
        If top of stack is not a gateway, not all branches of a gateway were
        processed. Call GatewayStackHandler.next_stack_element() to get the vertex.
        """
        top_of_stack = self.stack.top()

        if top_of_stack is None:
            raise IndexError(f'cannot pop from an empty stack')

        if top_of_stack[BPMNEnum.TYPE.value] == BPMNGateway.__name__ and \
            top_of_stack[BPMNEnum.GATEWAY_OPEN.value]:
            # remove opening gateway from stack
            self.stack.pop()
            # add following vertex on stack
            self.stack.push(item=branch_vertex)


    def next_stack_element(self) -> Optional[igraph.Vertex]:
        if self.stack.top() is not None:
            return self.stack.pop()
        else:
            return None