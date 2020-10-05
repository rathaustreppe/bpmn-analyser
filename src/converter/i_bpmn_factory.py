from abc import ABC, abstractmethod
from typing import List, Optional
from xml.etree.ElementTree import Element

from pedantic import pedantic_class

from src.converter.bpmn_models.bpmn_element import \
    BPMNFlowObject
from src.converter.bpmn_models.bpmn_enum import BPMNEnum
from src.converter.bpmn_models.bpmn_sequenceflow import BPMNSequenceFlow


@pedantic_class
class IBPMNFactory(ABC):

    @abstractmethod
    def create_bpmn_flow_object(self,
                                element: Element,
                                elem_type: BPMNEnum) -> BPMNFlowObject:
        """
        Method to create BPMNFlowObjects (e.g Gateways, Activities, Events) but
        no connecting objects (e.g. SequenceFlows).
        """
        pass

    @abstractmethod
    def create_bpmn_connecting_object(self,
                                      element: Element,
                                      elem_type: BPMNEnum,
                                      src_tgt_elements:
                                      Optional[List[BPMNFlowObject]] = None) \
            -> BPMNSequenceFlow:
        """
        Method to create connecting objects in BPMN. Currently only 
        SequenceFlows are implemented.Change the signature to parent class 
        BPMNConnectingObject (or similar) in future when new flows are 
        implemented. 
        """
        pass
