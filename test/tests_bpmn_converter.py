import os
from typing import List, Generic, TypeVar

import pytest

from src.converter.bpmn_converter import BPMNConverter
from src.converter.bpmn_factory import BPMNFactory
from src.converter.bpmn_models.bpmn_activity import BPMNActivity
from src.converter.bpmn_models.bpmn_element import BPMNElement
from src.converter.bpmn_models.bpmn_enum import BPMNEnum
from src.converter.bpmn_models.bpmn_model import BPMNModel
from src.converter.bpmn_models.event.bpmn_endevent import BPMNEndEvent
from src.converter.bpmn_models.event.bpmn_startevent import BPMNStartEvent
from src.converter.bpmn_models.gateway.bpmn_exclusive_gateway import \
    BPMNExclusiveGateway
from src.converter.bpmn_models.gateway.bpmn_inclusive_gateway import \
    BPMNInclusiveGateway
from src.converter.bpmn_models.gateway.bpmn_parallel_gateway import \
    BPMNParallelGateway
from src.converter.xml_reader import XMLReader
from src.models.token_state_condition import TokenStateCondition


class TestBPMNConverter:

    def converter_xmls(self) -> str:
        pytest_root = os.path.dirname(os.path.abspath(__file__))
        working_dict = os.path.join(pytest_root, 'test_files', 'xml','converter')
        return working_dict

    def all_bpmn_types(self) -> List[BPMNEnum]:
        return [BPMNEnum.STARTEVENT, BPMNEnum.ENDEVENT, BPMNEnum.ACTIVITY,
                BPMNEnum.PARALLGATEWAY, BPMNEnum.EXCLGATEWAY,
                BPMNEnum.INCLGATEWAY]

    def create_model(self, filename:str) -> BPMNModel:
        bpmn_converter = BPMNConverter(xml_reader=XMLReader(), bpmn_factory=BPMNFactory())
        file_path = os.path.join(self.converter_xmls(), filename)
        bpmn_converter.xml_reader.parse_to_dom(abs_path=file_path)
        return bpmn_converter.create_all_bpmn_objects(bpmn_types=self.all_bpmn_types())

    def find_elems(self, elements: List[BPMNElement], type):
        return [elem for elem in elements if isinstance(elem, type)]

    def find_by_id(self, elements: List[BPMNElement], id: str) -> BPMNElement:
        elements = [elem for elem in elements if elem.id == id]

        if len(elements) == 0:
            raise ValueError(f'no elements with id={id} in {elements} found')

        if len(elements) > 1:
            raise ValueError(f'Error in testdata.'
                             f'Multiple used IDs detected: {id}')
        return elements[0]


    def test_single_start_event(self):
        model = self.create_model(filename='S.bpmn')
        assert len(model.bpmn_elements) == 1
        assert len(model.sequence_flows) == 0

        start_event = model.bpmn_elements[0]
        assert type(start_event) == BPMNStartEvent
        assert start_event.id == 'S'
        assert start_event.name == 'SE'

    def test_single_end_event(self):
        model = self.create_model(filename='E.bpmn')
        assert len(model.bpmn_elements) == 1
        assert len(model.sequence_flows) == 0

        send_event = model.bpmn_elements[0]
        assert type(send_event) == BPMNEndEvent

        assert send_event.id == 'E'
        assert send_event.name == 'EE'

    def test_single_activity(self):
        model = self.create_model(filename='A.bpmn')
        assert len(model.bpmn_elements) == 1
        assert len(model.sequence_flows) == 0

        activity = model.bpmn_elements[0]
        assert type(activity) == BPMNActivity
        assert activity.id == 'a'
        assert activity.name == 'act'


    def test_single_to_end_event(self):
        model = self.create_model(filename='S_to_E.bpmn')
        assert len(model.bpmn_elements) == 2
        assert len(model.sequence_flows) == 1

        startEvent = self.find_elems(elements=model.bpmn_elements, type=BPMNStartEvent)
        assert len(startEvent) == 1
        assert startEvent[0].id == 'S'
        assert startEvent[0].name == 'SE'
        assert startEvent[0].sequenceFlow.id == 'F'

        endEvent = self.find_elems(elements=model.bpmn_elements,
                                   type=BPMNEndEvent)
        assert len(endEvent) == 1
        assert endEvent[0].id == 'E'
        assert endEvent[0].name == 'EE'
        assert endEvent[0].sequenceFlow.id == 'F'

        assert len(model.sequence_flows) == 1
        assert model.sequence_flows[0].id == 'F'
        assert model.sequence_flows[0].source.id == 'S'
        assert model.sequence_flows[0].target.id == 'E'

    def test_start_activity_end(self):
        model = self.create_model(filename='S_A_E.bpmn')

        assert len(model.bpmn_elements) == 3
        assert len(model.sequence_flows) == 2

        startEvent = self.find_elems(elements=model.bpmn_elements,
                                     type=BPMNStartEvent)
        assert len(startEvent) == 1
        assert startEvent[0].id == 'S'
        assert startEvent[0].name == 'SE'
        assert startEvent[0].sequenceFlow.id == 'F1'

        endEvent = self.find_elems(elements=model.bpmn_elements,
                                   type=BPMNEndEvent)
        assert len(endEvent) == 1
        assert endEvent[0].id == 'E'
        assert endEvent[0].name == 'EE'
        assert endEvent[0].sequenceFlow.id == 'F2'

        activity = self.find_elems(elements=model.bpmn_elements,
                                   type=BPMNActivity)
        assert len(activity) == 1
        assert activity[0].id == 'A'
        assert activity[0].name == 'Act'
        assert activity[0].sequenceFlowIn.id == 'F1'
        assert activity[0].sequenceFlowOut.id == 'F2'

        assert len(model.sequence_flows) == 2
        flow_1 = self.find_by_id(elements=model.sequence_flows, id='F1')
        assert flow_1.source.id == 'S'
        assert flow_1.target.id == 'A'

        flow_2 = self.find_by_id(elements=model.sequence_flows, id='F2')
        assert flow_2.source.id == 'A'
        assert flow_2.target.id == 'E'

    def test_three_activities(self):
        model = self.create_model(filename='S_A_A_A_E.bpmn')

        assert len(model.bpmn_elements) == 5
        assert len(model.sequence_flows) == 4

        startEvent = self.find_elems(elements=model.bpmn_elements,
                                     type=BPMNStartEvent)
        assert len(startEvent) == 1
        assert startEvent[0].id == 'S'
        assert startEvent[0].name == 'SE'
        assert startEvent[0].sequenceFlow.id == 'F1'

        endEvent = self.find_elems(elements=model.bpmn_elements,
                                   type=BPMNEndEvent)
        assert len(endEvent) == 1
        assert endEvent[0].id == 'E'
        assert endEvent[0].name == 'EE'
        assert endEvent[0].sequenceFlow.id == 'F4'

        activities = self.find_elems(elements=model.bpmn_elements,
                                     type=BPMNActivity)
        assert len(activities) == 3

        activity_1 = self.find_by_id(elements=activities, id='a1')
        assert activity_1.name == 'A1'
        assert activity_1.sequenceFlowIn.id == 'F1'
        assert activity_1.sequenceFlowOut.id == 'F2'

        activity_2 = self.find_by_id(elements=activities, id='a2')
        assert activity_2.name == 'A2'
        assert activity_2.sequenceFlowIn.id == 'F2'
        assert activity_2.sequenceFlowOut.id == 'F3'

        activity_3 = self.find_by_id(elements=activities, id='a3')
        assert activity_3.name == 'A3'
        assert activity_3.sequenceFlowIn.id == 'F3'
        assert activity_3.sequenceFlowOut.id == 'F4'

        assert len(model.sequence_flows) == 4
        flow_1 = self.find_by_id(elements=model.sequence_flows, id='F1')
        assert flow_1.source.id == 'S'
        assert flow_1.target.id == 'a1'

        flow_2 = self.find_by_id(elements=model.sequence_flows, id='F2')
        assert flow_2.source.id == 'a1'
        assert flow_2.target.id == 'a2'

        flow_3 = self.find_by_id(elements=model.sequence_flows, id='F3')
        assert flow_3.source.id == 'a2'
        assert flow_3.target.id == 'a3'

        flow_4 = self.find_by_id(elements=model.sequence_flows, id='F4')
        assert flow_4.source.id == 'a3'
        assert flow_4.target.id == 'E'

    def test_single_parallel_gateway(self):
        model = self.create_model(filename='parallel_gateway.bpmn')

        assert len(model.bpmn_elements) == 1
        assert len(model.sequence_flows) == 0

        gateway = model.bpmn_elements[0]
        assert type(gateway) == BPMNParallelGateway
        assert gateway.id == 'gw1'

    def test_single_exclusive_gateway(self):
        model = self.create_model(filename='exclusive_gateway.bpmn')

        assert len(model.bpmn_elements) == 1
        assert len(model.sequence_flows) == 0

        gateway = model.bpmn_elements[0]
        assert type(gateway) == BPMNExclusiveGateway
        assert gateway.id == 'gw1'

    def test_single_inclusive_gateway(self):
        model = self.create_model(filename='inclusive_gateway.bpmn')

        assert len(model.bpmn_elements) == 1
        assert len(model.sequence_flows) == 0

        gateway = model.bpmn_elements[0]
        assert type(gateway) == BPMNInclusiveGateway
        assert gateway.id == 'gw1'

    def test_parallel_gateway(self):
        model = self.create_model(filename='min_parallel_gateway.bpmn')
        
        assert len(model.bpmn_elements) == 6
        assert len(model.sequence_flows) == 6

        gateways = self.find_elems(elements=model.bpmn_elements,
                                   type=BPMNParallelGateway)
        assert len(gateways) == 2

        gateway_1 = self.find_by_id(elements=gateways, id='GW1')
        assert len(gateway_1.sequence_flows_in) == 1
        assert len(gateway_1.sequence_flows_out) == 2

        # naming flows by their ids
        flow_1 = self.find_by_id(elements=model.sequence_flows, id='F1')
        assert flow_1.source.id == 'S'
        assert flow_1.target.id == 'GW1'

        flow_2 = self.find_by_id(elements=model.sequence_flows, id='F2')
        assert flow_2.condition is None
        assert flow_2.source.id == 'GW1'
        assert flow_2.target.id == 'A1'

        flow_3 = self.find_by_id(elements=model.sequence_flows, id='F3')
        assert flow_3.condition is None
        assert flow_3.source.id == 'GW1'
        assert flow_3.target.id == 'A2'

        flow_4 = self.find_by_id(elements=model.sequence_flows, id='F4')
        assert flow_4.source.id == 'A1'
        assert flow_4.target.id == 'GW2'

        flow_5 = self.find_by_id(elements=model.sequence_flows, id='F5')
        assert flow_5.source.id == 'A2'
        assert flow_5.target.id == 'GW2'

        flow_6 = self.find_by_id(elements=model.sequence_flows, id='F6')
        assert flow_6.source.id == 'GW2'
        assert flow_6.target.id == 'E'

        gateway_2 = self.find_by_id(elements=gateways, id='GW2')
        assert len(gateway_2.sequence_flows_in) == 2
        assert len(gateway_2.sequence_flows_out) == 1

    def test_exclusive_gateway(self):
        model = self.create_model(filename='min_exclusive_gateway.bpmn')


        assert len(model.bpmn_elements) == 6
        assert len(model.sequence_flows) == 6

        gateways = self.find_elems(elements=model.bpmn_elements,
                                   type=BPMNExclusiveGateway)
        assert len(gateways) == 2

        gateway_1 = self.find_by_id(elements=gateways, id='GW1')
        assert len(gateway_1.sequence_flows_in) == 1
        assert len(gateway_1.sequence_flows_out) == 2

        # naming flows by their ids
        flow_1 = self.find_by_id(elements=model.sequence_flows, id='F1')
        assert flow_1.source.id == 'S'
        assert flow_1.target.id == 'GW1'

        flow_2 = self.find_by_id(elements=model.sequence_flows, id='F2')
        assert flow_2.condition is None
        assert flow_2.source.id == 'GW1'
        assert flow_2.target.id == 'A1'

        flow_3 = self.find_by_id(elements=model.sequence_flows, id='F3')
        assert flow_3.condition is None
        assert flow_3.source.id == 'GW1'
        assert flow_3.target.id == 'A2'

        flow_4 = self.find_by_id(elements=model.sequence_flows, id='F4')
        assert flow_4.source.id == 'A1'
        assert flow_4.target.id == 'GW2'

        flow_5 = self.find_by_id(elements=model.sequence_flows, id='F5')
        assert flow_5.source.id == 'A2'
        assert flow_5.target.id == 'GW2'

        flow_6 = self.find_by_id(elements=model.sequence_flows, id='F6')
        assert flow_6.source.id == 'GW2'
        assert flow_6.target.id == 'E'

        gateway_2 = self.find_by_id(elements=gateways, id='GW2')
        assert len(gateway_2.sequence_flows_in) == 2
        assert len(gateway_2.sequence_flows_out) == 1

    def test_min_inclusive_gateway(self):
        model = self.create_model(filename='min_inclusive_gateway.bpmn')

        assert len(model.bpmn_elements) == 6
        assert len(model.sequence_flows) == 6

        gateways = self.find_elems(elements=model.bpmn_elements,
                                   type=BPMNInclusiveGateway)
        assert len(gateways) == 2

        gateway_1 = self.find_by_id(elements=gateways, id='GW1')
        assert len(gateway_1.sequence_flows_in) == 1
        assert len(gateway_1.sequence_flows_out) == 2

        # naming flows by their ids
        flow_1 = self.find_by_id(elements=model.sequence_flows, id='F1')
        assert flow_1.source.id == 'S'
        assert flow_1.target.id == 'GW1'

        flow_2 = self.find_by_id(elements=model.sequence_flows, id='F2')
        assert flow_2.condition is None
        assert flow_2.source.id == 'GW1'
        assert flow_2.target.id == 'A1'

        flow_3 = self.find_by_id(elements=model.sequence_flows, id='F3')
        assert flow_3.condition is None
        assert flow_3.source.id == 'GW1'
        assert flow_3.target.id == 'A2'

        flow_4 = self.find_by_id(elements=model.sequence_flows, id='F4')
        assert flow_4.source.id == 'A1'
        assert flow_4.target.id == 'GW2'

        flow_5 = self.find_by_id(elements=model.sequence_flows, id='F5')
        assert flow_5.source.id == 'A2'
        assert flow_5.target.id == 'GW2'

        flow_6 = self.find_by_id(elements=model.sequence_flows, id='F6')
        assert flow_6.source.id == 'GW2'
        assert flow_6.target.id == 'E'

        gateway_2 = self.find_by_id(elements=gateways, id='GW2')
        assert len(gateway_2.sequence_flows_in) == 2
        assert len(gateway_2.sequence_flows_out) == 1

    def test_conditional_edge(self):
        model = self.create_model(filename='S_to_E_named_edge.bpmn')

        bpmn_elements = model.bpmn_elements
        sequene_flows = model.sequence_flows

        assert len(bpmn_elements) == 2
        assert len(sequene_flows) == 1

        assert sequene_flows[0].condition ==\
               TokenStateCondition.from_string(condition='attr==42')

    def test_conditional_edge_gateway(self):
        model = self.create_model(filename='conditional_edge_exclusive_gateway.bpmn')

        sequence_flows = model.sequence_flows
        assert len(sequence_flows) == 6

        cond_flow_1 = self.find_by_id(elements=sequence_flows, id='F2')
        cond_flow_2 = self.find_by_id(elements=sequence_flows, id='F3')

        assert cond_flow_1.condition == TokenStateCondition.from_string(condition='k1==v1')
        assert cond_flow_2.condition == TokenStateCondition.from_string(condition='k1==v2')

