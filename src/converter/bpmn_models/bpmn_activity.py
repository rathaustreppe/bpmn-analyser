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
                 sequenceFlowIn: Optional[BPMNSequenceFlow] = None,
                 sequenceFlowOut: Optional[BPMNSequenceFlow] = None) -> None:
        super().__init__(id=id, name=name)
        self.__sequenceFlowIn = sequenceFlowIn
        self.__sequenceFlowOut = sequenceFlowOut

        if self.__sequenceFlowIn is not None:
            self.__sequenceFlowIn.set_target(target=self)

        if self.__sequenceFlowOut is not None:
            self.__sequenceFlowOut.set_source(source=self)

    def set_sequenceFlowIn(self, sequenceFlow:BPMNSequenceFlow) -> None:
        self.__sequenceFlowIn = sequenceFlow

    def set_sequenceFlowOut(self,sequenceFlow: BPMNSequenceFlow) -> None:
        self.__sequenceFlowOut = sequenceFlow

