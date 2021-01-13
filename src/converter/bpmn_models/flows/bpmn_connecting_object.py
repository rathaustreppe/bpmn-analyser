from typing import Optional

from pedantic import pedantic_class

from src.converter.bpmn_models.bpmn_element import BPMNElement
from src.converter.bpmn_models.bpmn_flow_object import BPMNFlowObject


@pedantic_class
class BPMNConnectingObject(BPMNElement):
    """
    Metaclass for all ConnectingObjects in BPMN == all flows that connect
    BPMNFlowObjects. Dont get confused with those names ;)
    BPMNConnectingObject is the superclass of e.g. BPMNSequenceFlows and message
    flows.
    They all have in common that they have a source and a target (which makes
    them flows) and an ID. That makes them inherit from BPMNElement.

    source and target attributes are optional so you can fill them later and
    to make them testable without specifying a whole diagram.
    """
    def __init__(self, id_:str,
                 source: Optional[BPMNFlowObject],
                 target: Optional[BPMNFlowObject]) -> None:
        super().__init__(id_=id_)
        self.source = source
        self.target = target

