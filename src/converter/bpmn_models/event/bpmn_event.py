from typing import Optional

from pedantic import pedantic_class

from src.converter.bpmn_models.bpmn_flow_object import BPMNFlowObject
from src.converter.bpmn_models.bpmn_sequenceflow import \
    BPMNSequenceFlow


@pedantic_class
class BPMNEvent(BPMNFlowObject):
    def __init__(self, id_: str, name: str,
                 sequence_flow: Optional[BPMNSequenceFlow] = None) -> None:
        super().__init__(id_=id_, name=name)
        self.name = name
        self.sequence_flow = sequence_flow
