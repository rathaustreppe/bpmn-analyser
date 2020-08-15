from typing import Optional

from pedantic import pedantic_class

# local imports
from src.converter.bpmn_models.bpmn_element import \
    BPMNElement
from src.converter.bpmn_models.bpmn_sequenceflow import \
    BPMNSequenceFlow

@pedantic_class
class BPMNStartEndEvent(BPMNElement):
    def __init__(self, id:str, name: str, sequenceFlow: Optional[BPMNSequenceFlow] = None) -> None:
        super().__init__(name=name, id=id)
        self.__sequenceFlow = sequenceFlow

    def get_sequenceFlow(self) -> BPMNSequenceFlow:
        return self.__sequenceFlow

    def set_sequenceFlow(self, sequence_flow: BPMNSequenceFlow) -> None:
        self.__sequenceFlow = sequence_flow
