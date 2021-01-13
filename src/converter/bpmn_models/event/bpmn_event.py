from typing import Optional

from pedantic import pedantic_class

from src.converter.bpmn_models.bpmn_flow_object import BPMNFlowObject
from src.converter.bpmn_models.flows.bpmn_sequenceflow import \
    BPMNSequenceFlow


@pedantic_class
class BPMNEvent(BPMNFlowObject):
    def __init__(self, id_: str, text: str,
                 sequence_flow: Optional[BPMNSequenceFlow] = None) -> None:
        super().__init__(id_=id_, text=text)
        self.name = text
        self.sequence_flow = sequence_flow
