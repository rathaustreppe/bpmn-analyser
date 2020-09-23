from typing import Optional

from pedantic import pedantic_class


# local import
from src.converter.bpmn_models.bpmn_element import \
    BPMNElement
from src.converter.bpmn_models.bpmn_sequenceflow import \
    BPMNSequenceFlow


@pedantic_class
class BPMNActivity(BPMNElement):
    def __init__(self, id: str, name: str,
                 sequence_flow_in: Optional[BPMNSequenceFlow] = None,
                 sequence_flow_out: Optional[BPMNSequenceFlow] = None) -> None:
        super().__init__(id=id)
        self.name = name
        self.sequenceFlowIn = sequence_flow_in
        self.sequenceFlowOut = sequence_flow_out

        if self.sequenceFlowIn is not None:
            self.sequenceFlowIn.target = self

        if self.sequenceFlowOut is not None:
            self.sequenceFlowOut.source = self
