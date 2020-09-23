from typing import Optional

from pedantic import pedantic_class

# local imports
from src.converter.bpmn_models.bpmn_sequenceflow import \
    BPMNSequenceFlow
from src.converter.bpmn_models.event.bpmn_event import \
    BPMNEvent


@pedantic_class
class BPMNEndEvent(BPMNEvent):
    def __init__(self, id:str, name: str, sequence_flow: Optional[BPMNSequenceFlow] = None) -> None:
        super().__init__(name=name, id=id, sequence_flow=sequence_flow)
