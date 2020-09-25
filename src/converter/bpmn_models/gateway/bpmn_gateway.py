from typing import List, Optional

from pedantic import pedantic_class

from src.converter.bpmn_models.bpmn_element import BPMNElement
from src.converter.bpmn_models.bpmn_sequenceflow import BPMNSequenceFlow

'''
Metaclass for all BPMNGateways
'''


@pedantic_class
class BPMNGateway(BPMNElement):
    def __init__(self, id: str,
                 sequence_flows_in: Optional[List[BPMNSequenceFlow]] = None,
                 sequence_flows_out: Optional[List[BPMNSequenceFlow]] = None) -> None:
        super().__init__(id=id)#
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

    def is_opening_gateway(self) -> bool:
        # BPMN specifies two identical gateways with the same symbol: the first
        # gateway splits into multiple branches and the second gateway collects
        # the branches. We refer to them as 'opening' and 'closing' gateways.
        # Call this method to check whether a gateway is opening or closing.
        # Internally checks the number of incoming and outgoing branch_vertices.
        num_outflows = len(self.sequence_flows_out)
        num_inflows = len(self.sequence_flows_in)
        return num_inflows < num_outflows