from typing import Optional

from pedantic import pedantic_class

# local imports
from src.converter.bpmn_models.bpmn_element import \
    BPMNFlowObject
from src.models.token_state_condition import TokenStateCondition


@pedantic_class
class BPMNSequenceFlow(BPMNFlowObject):
    def __init__(self, id_: str,
                 condition: Optional[TokenStateCondition] = None,
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