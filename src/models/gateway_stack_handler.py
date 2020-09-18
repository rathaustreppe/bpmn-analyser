from typing import List

import igraph
from pedantic import pedantic_class

from src.converter.bpmn_models.bpmn_enum import BPMNEnum
from src.models.stack import Stack


@pedantic_class
class GatewayStackHandler:
    """
    Class that knows how to put BPMN-Gateways (or their respective vertices)
    in a stack. Used to keep track of multiple paths that split up after each
    gateway and come together in a closing gateway.
    """

    def __init__(self):
        self.stack = Stack(stack=[])

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
            self.pop_gateway(branch_vertices=branch_vertices)

        else:
            raise ValueError(f'Gateway {gateway} has same number of incoming '
                             f'and outgoing branch_vertices ({num_incoming}/{num_outgoing}). '
                             f'This contradicts BPMN-specification.')

    def push_gateway(self, gateway: igraph.Vertex,
                     branch_vertices: List[igraph.Vertex]) -> None:
        # gateway at bottom, branch_vertices on top
        self.stack.push(gateway)
        for vertex in branch_vertices:
            self.stack.push(vertex)

    def pop_gateway(self, branch_vertices: List[igraph.Vertex]) -> None:
        # If a opening gateway of the same type is on top of stack, this means
        # that all branches of the opening gateway were processed. So we can
        # safely delete the opening gateway. But to know which vertex follows
        # a closing gateway (it can only be one (BPMN Specification)) we put
        # the following vertex on the stack.
        # If we reach a closing gateway, but non-gateway vertices are on top of
        # the stack, this means not all branches of the opening gateway are
        # processed yet. We still return None, because GraphPointer works
        # step-wise and could not handle a returned vertex. But this method is
        # side-effect free - next time calling the
        # GatwayStackHandler.next_vertex() function you will get the vertex.
        top_of_stack = self.stack.top()
        gateway_texts = [BPMNEnum.PARALLGATEWAY_TEXT.value,
                         BPMNEnum.EXCLGATEWAY_TEXT.value,
                         BPMNEnum.INCLGATEWAY_TEXT.value]
        if top_of_stack[BPMNEnum.NAME.value] in gateway_texts:
            self.stack.pop()
            if len(branch_vertices) == 1:
                self.stack.push(branch_vertices[0])
            else:
                raise ValueError(f'BPMN-Specification-Contradiction found: '
                                 f'number of outgoing edges of a bpmn-gateway '
                                 f'can only be 1. Was: {len(branch_vertices)}')
        else:
            raise ValueError(f'you can only call this method if the top of '
                             f'the stack is a gateway type. Was: {top_of_stack}')

    def next_vertex(self) -> igraph.Vertex:
        return self.stack.pop()
