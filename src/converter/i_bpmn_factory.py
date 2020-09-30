from abc import ABC, abstractmethod
from typing import List, Optional
from xml.etree.ElementTree import Element

from pedantic import pedantic_class

# local imports
from src.converter.bpmn_models.bpmn_element import \
    BPMNElement
from src.converter.bpmn_models.bpmn_enum import BPMNEnum


@pedantic_class
class IBPMNFactory(ABC):

    @abstractmethod
    def create_bpmn_element(self,
                            element: Element, elem_type: BPMNEnum,
                            src_tgt_elements: Optional[
                                List[BPMNElement]] = None) -> BPMNElement:
        pass
