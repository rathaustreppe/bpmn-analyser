from typing import Optional

from pedantic import pedantic_class

# local imports
from src.converter.bpmn_models.bpmn_element import \
    BPMNElement
from src.converter.bpmn_models.bpmn_flow_object import BPMNFlowObject
from src.converter.bpmn_models.gateway.branch_condition import BranchCondition


@pedantic_class
class BPMNSequenceFlow(BPMNElement):
    def __init__(self, id_: str,
                 condition: Optional[BranchCondition] = None,
                 source: Optional[BPMNFlowObject] = None,
                 target: Optional[BPMNFlowObject] = None) -> None:
        super().__init__(id_=id_)
        self.condition = condition
        self.source = source
        self.target = target

    def __str__(self) -> str:
        return f'SequenceFlow[src <{self.source}>' \
               f'| tgt <{self.target}' \
               f'| condition <{self.condition}>]'

    def __repr__(self) -> str:
        return self.__str__()