from typing import List

from pedantic import pedantic_class

from src.converter.bpmn_factory import BPMNFactory
from src.converter.bpmn_models.bpmn_activity import \
    BPMNActivity
from src.converter.bpmn_models.bpmn_element import \
    BPMNElement
from src.converter.bpmn_models.bpmn_enum import BPMNEnum
from src.converter.bpmn_models.bpmn_model import BPMNModel
from src.converter.bpmn_models.flows.bpmn_sequenceflow import \
    BPMNSequenceFlow
from src.converter.bpmn_models.event.bpmn_endevent import \
    BPMNEndEvent
from src.converter.bpmn_models.event.bpmn_startevent import \
    BPMNStartEvent
from src.converter.bpmn_models.gateway.bpmn_gateway import BPMNGateway
from src.converter.xml_reader import XMLReader


@pedantic_class
class BPMNConverter:
    """
    Queries the XML-Reader and builds BPMN-objects and BPMNModel.
    """

    def __init__(self,
                 xml_reader: XMLReader,
                 bpmn_factory: BPMNFactory) -> None:
        self.xml_reader = xml_reader
        self.bpmn_factory = bpmn_factory

    def create_bpmn_model(self) -> BPMNModel:
        """
        Reads the xml-dom and converts it into a list of python
        BPMN-objects. It keeps separates connecting objects
        (e.g BPMNSequenceFlows) and BPMNFlowObjects separate and returns the
        BPMNModel
        """
        bpmn_flow_objects = self.create_bpmn_flow_objects()
        bpmn_sequence_flows = self.create_bpmn_sequence_flows(
            bpmn_elements=bpmn_flow_objects)
        return BPMNModel(bpmn_elements=bpmn_flow_objects,
                         sequence_flows=bpmn_sequence_flows)

    def create_bpmn_flow_objects(self) -> List[BPMNElement]:
        """
        Creates objects of all classes that inherit from BPMNFlowObject
        by querying the XMLReader and using the BPMNFactory.

        BPMNConverter knows all implemented types of flow-objects.
        For each type there can be multiple BPMNElements e.g multiple
        BPMNActivity's in every diagram.
        For all those objects their constructor is called.
        """
        bpmn_elements: List[BPMNElement] = []
        for bpmn_type in self.all_bpmn_flow_object_types():
            xml_elements = self.xml_reader.query(element_type=bpmn_type)
            for xml_element in xml_elements:
                element_obj = self.bpmn_factory.create_bpmn_flow_object(
                    element=xml_element,
                    elem_type=bpmn_type)
                bpmn_elements.append(element_obj)

        return bpmn_elements

    def create_bpmn_sequence_flows(self, bpmn_elements: List[BPMNElement]) -> \
            List[BPMNSequenceFlow]:
        """
        Method that creates BPMNSequenceFlows by reading the XML-Reader XML-DOM.
        To keep bidirectional references updated we need the bpmn_elements.

        When introducing new types of flows you could generalize this method
        similar to self.create_bpmn_flow_objects() with two for-loops.
        """

        xml_sequence_flows = self.xml_reader.query(
            element_type=BPMNEnum.SEQUENCEFLOW)
        sequence_flows: List[BPMNSequenceFlow] = []
        for xml_flow in xml_sequence_flows:
            sequence_flow = self.bpmn_factory.create_bpmn_connecting_object(
                element=xml_flow,
                elem_type=BPMNEnum.SEQUENCEFLOW,
                src_tgt_elements=bpmn_elements)

            sequence_flows.append(sequence_flow)

        # update bidirectional references of sequence flows in bpmn-elements
        return self.set_sequence_flows_references(sequence_flows=sequence_flows)

    @staticmethod
    def set_sequence_flows_references(sequence_flows: List[BPMNSequenceFlow]) ->\
            List[BPMNSequenceFlow]:
        """
        Method to tell source and target objects of sequenceflows to which
        sequence_flow they belong.
        Example:
            BPMNActivity A   ---f--l--o--w--->    BPMNActivity B
            A is the source of flow.
            B is the target of flow.
            flow is the target of A.
            flow is the source of B.
        This method updates source & target attributes of A and B
        """
        for sequence_flow in sequence_flows:
            # check StartEvents (can only be sources) and EndEvents (can only
            # be targets)
            if isinstance(sequence_flow.source, BPMNStartEvent):
                sequence_flow.source.sequence_flow = sequence_flow

            if isinstance(sequence_flow.target, BPMNEndEvent):
                sequence_flow.target.sequence_flow = sequence_flow

            # check activities
            if isinstance(sequence_flow.source, BPMNActivity):
                sequence_flow.source.sequence_flow_out = sequence_flow

            if isinstance(sequence_flow.target, BPMNActivity):
                sequence_flow.target.sequence_flow_in = sequence_flow

            # check gateways
            if isinstance(sequence_flow.source, BPMNGateway):
                sequence_flow.source.add_sequence_flow_out(flow=sequence_flow)

            if isinstance(sequence_flow.target, BPMNGateway):
                sequence_flow.target.add_sequence_flow_in(flow=sequence_flow)

        return sequence_flows

    @staticmethod
    def all_bpmn_flow_object_types() -> List[BPMNEnum]:
        """
        A list of all classes that inherit from BPMNFlowObject.
        In near future it should be refactored to store classes directly
        instead of their strings. Then this manual notation of subclasses
        can be replaced with:
        https://stackoverflow.com/questions/3862310/how-to-find-all-the-subclasses-of-a-class-given-its-name
        """
        return [BPMNEnum.ACTIVITY, BPMNEnum.STARTEVENT,
                BPMNEnum.ENDEVENT, BPMNEnum.PARALLGATEWAY,
                BPMNEnum.EXCLGATEWAY, BPMNEnum.INCLGATEWAY]
