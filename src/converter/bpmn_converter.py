from typing import Tuple, List, Optional, Union

from igraph import Graph, VertexSeq, Vertex
from pedantic import pedantic_class

from src.converter.bpmn_models import bpmn_model
from src.converter.bpmn_models.bpmn_activity import \
    BPMNActivity
from src.converter.bpmn_models.bpmn_element import \
    BPMNElement
from src.converter.bpmn_models.bpmn_enum import BPMNEnum
from src.converter.bpmn_models.bpmn_model import BPMNModel
from src.converter.bpmn_models.bpmn_sequenceflow import \
    BPMNSequenceFlow
from src.converter.bpmn_models.event.bpmn_endevent import \
    BPMNEndEvent
from src.converter.bpmn_models.event.bpmn_startevent import \
    BPMNStartEvent
from src.converter.bpmn_models.gateway.bpmn_exclusive_gateway import \
    BPMNExclusiveGateway
from src.converter.bpmn_models.gateway.bpmn_gateway import BPMNGateway
from src.converter.bpmn_models.gateway.bpmn_inclusive_gateway import \
    BPMNInclusiveGateway
from src.converter.bpmn_models.gateway.bpmn_parallel_gateway import \
    BPMNParallelGateway
from src.converter.i_bpmn_factory import IBPMNFactory
from src.converter.xml_reader import XMLReader
from src.models.graph_text import GraphText


@pedantic_class
class BPMNConverter:
    def __init__(self,
                 xml_reader: XMLReader,
                 bpmn_factory: IBPMNFactory,
                 graph: Optional[Graph] = None) -> None:
        self.xml_reader = xml_reader
        self.bpmn_factory = bpmn_factory
        self.graph = graph

    def make_element(self, element_type: BPMNEnum,
                     src_tgt_elements: Optional[List[BPMNElement]] = None) -> \
            List[Union[BPMNElement, BPMNSequenceFlow]]:
        # """
        # Searches all element_types in XML-DOM and returns corresponding
        # BPMN-Objects.
        # Args:
        #     element_type(BPMNEnum): abc
        #     src_tgt_elements (Optional[List[src.converter.bpmn_models.bpmn_element.BPMNElement]]): abc
        #
        # Returns:
        #     List[src.converter.bpmn_models.bpmn_element.BPMNElement]: abc
        # """
        elements = self.xml_reader.query(element_type=element_type)
        bpmn_objects = []
        for element in elements:
            element_obj = self.bpmn_factory.create_bpmn_element(element=element,
                                                                elem_type=element_type,
                                                                src_tgt_elements=src_tgt_elements)
            bpmn_objects.append(element_obj)
        return bpmn_objects

    @staticmethod
    def set_sequence_flows_references(sequence_flows: List[BPMNSequenceFlow]) -> \
            List[BPMNSequenceFlow]:
        """
        Method to tell source and target objects of sequenceflows to which
        sequenceflow they belong. (bidirectional reference)
        """
        for sequence_flow in sequence_flows:
            # check StartEvents (can only be sources) and EndEvents (can only
            # be targets)
            if isinstance(sequence_flow.source, BPMNStartEvent):
                sequence_flow.source.sequenceFlow = sequence_flow

            if isinstance(sequence_flow.target, BPMNEndEvent):
                sequence_flow.target.sequenceFlow = sequence_flow

            # check activities
            if isinstance(sequence_flow.source, BPMNActivity):
                sequence_flow.source.sequenceFlowOut = sequence_flow

            if isinstance(sequence_flow.target, BPMNActivity):
                sequence_flow.target.sequenceFlowIn = sequence_flow

            # check gateways
            if isinstance(sequence_flow.source, BPMNGateway):
                sequence_flow.source.add_sequence_flow_out(flow=sequence_flow)

            if isinstance(sequence_flow.target, BPMNGateway):
                sequence_flow.target.add_sequence_flow_in(flow=sequence_flow)

        return sequence_flows

    def create_bpmn_objects(self, bpmn_types: List[BPMNEnum]) -> List[
        BPMNElement]:
        """
        Method that creates BPMNElements (all specified in bpmn_types but no
        SequenceFlows!) by reading the XML-Reader XML-DOM.
        """
        # for this purpose we create a list that contains
        # all BPMNElements & BPMNGateways for later linking
        all_bpmn_elements: List[BPMNElement] = []

        # creating BPMN-Elements of all BPMN-Types
        for bpmn_type in bpmn_types:
            if bpmn_type != BPMNEnum.SEQUENCEFLOW:
                bpmn_elements = self.make_element(element_type=bpmn_type)
                all_bpmn_elements.extend(bpmn_elements)
            else:
                raise ValueError(f'list {bpmn_type} corrupted.'
                                 f' Must not contain sequenceflows.')
        return all_bpmn_elements

    def create_bpmn_sequence_flows(self, bpmn_elements: List[BPMNElement]) -> \
            List[BPMNSequenceFlow]:
        """
        Method that creates BPMNSequenceFlows by reading the XML-Reader XML-DOM.
        To keep bidirectional references updated we need the bpmn_elements.
        """
        sequence_flows = self.make_element(element_type=BPMNEnum.SEQUENCEFLOW,
                                           src_tgt_elements=bpmn_elements)
        # update bidirectional references of sequence flows in bpmn-elements
        return self.set_sequence_flows_references(sequence_flows=sequence_flows)

    def create_all_bpmn_objects(self, bpmn_types: List[BPMNEnum]) -> BPMNModel:
        """
        Reads the xml-dom and converts it into a list of python
        BPMN-objects. It keeps SequenceFlows and every other BPMN-Element in two
        separate lists.
        """
        bpmn_elements = self.create_bpmn_objects(bpmn_types=bpmn_types)
        bpmn_sequence_flows = self.create_bpmn_sequence_flows(
            bpmn_elements=bpmn_elements)
        return BPMNModel(bpmn_elements=bpmn_elements, sequence_flows=bpmn_sequence_flows)
