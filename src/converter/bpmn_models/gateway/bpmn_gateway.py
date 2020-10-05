from typing import List, Optional

from pedantic import pedantic_class

from src.converter.bpmn_models.bpmn_flow_object import BPMNFlowObject
from src.converter.bpmn_models.bpmn_sequenceflow import BPMNSequenceFlow
from src.exception.gateway_errors import BranchJoiningGatewayError

'''
Metaclass for all BPMNGateways
'''


@pedantic_class
class BPMNGateway(BPMNFlowObject):
    def __init__(self, id_: str, name: Optional[str] = '',
                 sequence_flows_in: Optional[List[BPMNSequenceFlow]] = None,
                 sequence_flows_out: Optional[List[BPMNSequenceFlow]] = None) -> None:
        super().__init__(id_=id_, name=name)
        self.sequence_flows_in = sequence_flows_in
        self.sequence_flows_out = sequence_flows_out

        if sequence_flows_in is None:
            self.sequence_flows_in = []

        if sequence_flows_out is None:
            self.sequence_flows_out = []

    def add_sequence_flow_in(self, flow: BPMNSequenceFlow) -> None:
        self.sequence_flows_in.append(flow)

    def add_sequence_flow_out(self, flow: BPMNSequenceFlow) -> None:
        self.sequence_flows_out.append(flow)

    def is_branching_gateway(self) -> bool:
        """
        BPMN specifies two identical gateways with the same symbol: the first
        gateway splits into multiple branches and the second gateway collects
        the branches. We refer to them as 'branching' and 'joining' gateways.
        Call this method to check whether a gateway is branching or joining.
        Internally checks the number of incoming and outgoing branch_vertices.
        If it has only one outgoing branch, then it is by BPMN-Specification
        a joining gateway.
        If it has only one incoming branch, then it is a branching gateway.
        If both are equal then the gateway is a branching and joining gateway
        at the same time. This would make things highly complicated, so we
        leave this case.
        """
        num_inflows = len(self.sequence_flows_in)
        num_outflows = len(self.sequence_flows_out)

        if num_inflows == num_outflows:
            raise BranchJoiningGatewayError(gateway=self)
        elif num_inflows == 1 and num_outflows > 1:
            return True
        else:
            return False