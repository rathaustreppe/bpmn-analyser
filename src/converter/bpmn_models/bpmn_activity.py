from typing import Optional

from pedantic import pedantic_class


from src.converter.bpmn_models.bpmn_flow_object import BPMNFlowObject
from src.converter.bpmn_models.bpmn_sequenceflow import \
    BPMNSequenceFlow


@pedantic_class
class BPMNActivity(BPMNFlowObject):
    def __init__(self, id_: str, name: str,
                 sequence_flow_in: Optional[BPMNSequenceFlow] = None,
                 sequence_flow_out: Optional[BPMNSequenceFlow] = None) -> None:
        super().__init__(id_=id_, name=name)
        self.sequence_flow_in = sequence_flow_in
        self.sequence_flow_out = sequence_flow_out

        if self.sequence_flow_in is not None:
            self.sequence_flow_in.target = self

        if self.sequence_flow_out is not None:
            self.sequence_flow_out.source = self

    def __str__(self) -> str:
        return f'BPMNActivity\'{self.name}>\''

    def __repr__(self) -> str:
        return self.__str__()