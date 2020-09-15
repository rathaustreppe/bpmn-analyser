from typing import Optional

from pedantic import pedantic_class

# local imports
from src.converter.bpmn_models.bpmn_element import \
    BPMNElement


@pedantic_class
class BPMNSequenceFlow(BPMNElement):
    def __init__(self, id: str, name: str = '', source: Optional[BPMNElement] = None,
                 target: Optional[BPMNElement] = None) -> None:
        super().__init__(id=id)
        self.name = name
        self.source = source
        self.target = target
