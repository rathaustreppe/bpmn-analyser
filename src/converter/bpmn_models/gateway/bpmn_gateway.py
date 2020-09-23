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
                 sequence_flows_in: Optional[List[BPMNSequenceFlow]],
                 sequence_flows_out: Optional[List[BPMNSequenceFlow]]) -> None:
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
