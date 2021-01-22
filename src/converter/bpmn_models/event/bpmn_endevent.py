from typing import Optional

from pedantic import pedantic_class

from src.converter.bpmn_models.flows.bpmn_sequenceflow import \
    BPMNSequenceFlow
from src.converter.bpmn_models.event.bpmn_event import \
    BPMNEvent


@pedantic_class
class BPMNEndEvent(BPMNEvent):
    def __init__(self, id_: str, text: str,
                 sequence_flow: Optional[BPMNSequenceFlow] = None) -> None:
        super().__init__(id_=id_, text=text, sequence_flow=sequence_flow)
