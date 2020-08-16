from typing import Optional

from pedantic import pedantic_class

# local imports
from src.converter.bpmn_models.bpmn_sequenceflow import \
    BPMNSequenceFlow
from src.converter.bpmn_models.bpmn_start_end_event import \
    BPMNStartEndEvent


@pedantic_class
class BPMNEndEvent(BPMNStartEndEvent):
    def __init__(self, id:str, name: str, sequenceFlow: Optional[BPMNSequenceFlow] = None) -> None:
        super().__init__(name=name, id=id, sequenceFlow=sequenceFlow)
