from typing import Optional

from pedantic import pedantic_class

from src.converter.bpmn_models.flows.bpmn_connecting_object import \
    BPMNConnectingObject
from src.converter.bpmn_models.bpmn_flow_object import BPMNFlowObject
from src.converter.bpmn_models.gateway.branch_condition import BranchCondition


@pedantic_class
class BPMNSequenceFlow(BPMNConnectingObject):
    """
    SequenceFlows are directed edges in a bpmn-diagram.

    source and target attributes are optional so you can fill them later and
    to make them testable without specifying a whole diagram.
    """
    def __init__(self, id_: str,
                 condition: Optional[BranchCondition] = None,
                 source: Optional[BPMNFlowObject] = None,
                 target: Optional[BPMNFlowObject] = None) -> None:
        super().__init__(id_=id_, source=source, target=target)
        self.condition = condition

    def __str__(self) -> str:
        return f'SequenceFlow[src <{self.source}>' \
               f'| tgt <{self.target}' \
               f'| condition <{self.condition}>]'

    def __repr__(self) -> str:
        return self.__str__()