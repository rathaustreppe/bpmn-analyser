"""
Metaclass for BPMNEvents, BPMNActivities and BPMNGateways.
BPMN2.0 specified a weird name for those elements. Dont get confused with
BPMNSequenceFlows or BPMNMessageFlows!!
All three (BPMNEvents, BPMNActivities and BPMNGateways) have the name attribute
in common.
"""
from pedantic import pedantic_class

from src.converter.bpmn_models.bpmn_element import BPMNElement


@pedantic_class
class BPMNFlowObject(BPMNElement):
    def __init__(self, id_: str, text: str) -> None:
        super().__init__(id_=id_)
        self.name = text
