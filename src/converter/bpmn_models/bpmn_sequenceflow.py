from typing import Optional

from pedantic import pedantic_class

# local imports
from src.converter.bpmn_models.bpmn_element import \
    BPMNElement
from src.models.token_state_condition import TokenStateCondition


@pedantic_class
class BPMNSequenceFlow(BPMNElement):
    def __init__(self, id_: str,
                 condition: Optional[TokenStateCondition] = None,
                 source: Optional[BPMNElement] = None,
                 target: Optional[BPMNElement] = None) -> None:
        super().__init__(id_=id_)
        self.condition = condition
        self.source = source
        self.target = target
