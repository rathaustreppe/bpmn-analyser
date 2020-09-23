from abc import ABC, abstractmethod
from typing import List, Optional
from xml.etree.ElementTree import Element

from pedantic import pedantic_class

# local imports
from src.converter.bpmn_models.bpmn_element import \
    BPMNElement
from src.converter.bpmn_models.bpmn_enum import BPMNEnum
from src.converter.bpmn_models.bpmn_sequenceflow import \
    BPMNSequenceFlow


@pedantic_class
class IBPMNFactory(ABC):
    # Attention: BPMNFactory can only, by definition, work
    # with valid xml + valid bpmn strings.The program is
    # designed that a factory is only instantiated when the
    # xml is conform to XML and BPMN standard.
    # This is okay: <task id="" condition=""></task>'
    # This not: <task></task>'
    @abstractmethod
    def create_bpmn_element(self,
                            element: Element, elem_type: BPMNEnum,
                            src_tgt_elements: Optional[List[BPMNElement]] = None) -> BPMNElement:
        pass