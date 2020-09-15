from typing import Optional

from pedantic import pedantic_class

# local imports
from src.converter.bpmn_models.bpmn_sequenceflow import \
    BPMNSequenceFlow
from src.converter.bpmn_models.event.bpmn_event import \
    BPMNEvent


@pedantic_class
class BPMNStartEvent(BPMNEvent):
    def __init__(self, id:str, name: str, sequenceFlow: Optional[BPMNSequenceFlow] = None) -> None:
        super().__init__(name=name, id=id, sequenceFlow=sequenceFlow)
