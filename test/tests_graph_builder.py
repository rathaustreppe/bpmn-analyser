import os
from typing import List

import pytest

from src.converter.bpmn_factory import BPMNFactory
from src.converter.bpmn_models.bpmn_activity import BPMNActivity
from src.converter.bpmn_models.bpmn_element import BPMNElement
from src.converter.bpmn_models.bpmn_enum import BPMNEnum
from src.converter.bpmn_models.bpmn_sequenceflow import BPMNSequenceFlow
from src.converter.bpmn_models.event.bpmn_endevent import BPMNEndEvent
from src.converter.bpmn_models.event.bpmn_startevent import BPMNStartEvent
from src.converter.bpmn_models.gateway.bpmn_parallel_gateway import \
    BPMNParallelGateway
from src.converter.graph_builder import GraphBuilder
from src.converter.xml_reader import XMLReader


class TestGraphBuilder:
    @pytest.fixture(scope='module', autouse=True)
    def graph_builder(self):
        return GraphBuilder(xml_reader=XMLReader(),bpmn_factory=BPMNFactory())

    @pytest.fixture(scope='module', autouse=True)
    def graph_builder_xmls(self):
        pytest_root = os.path.dirname(os.path.abspath(__file__))
        working_dict = os.path.join(pytest_root, 'test_files', 'xml', 'graphbuilder')
        return working_dict

    def find_elems(self, elements: List[BPMNElement], type):
        return [elem for elem in elements if isinstance(elem, type)]

    def find_by_id(self, elements: List[BPMNElement], id) -> BPMNElement:
        elements = [elem for elem in elements if elem.id == id]

        if len(elements) == 0:
            raise ValueError(f'no elements with id={id} in {elements} found')

        if len(elements) > 1:
            raise ValueError(f'Error in testdata.'
                             f'Multiple used IDs detected: {id}')

        return elements[0]






    def test_start_end(self, graph_builder, graph_builder_xmls):
        file_path = os.path.join(graph_builder_xmls, 'S_to_E.bpmn')
        graph_builder.xml_reader.parse_to_dom(abs_path=file_path)
        bpmn_elements, sequence_flows = graph_builder.create_bpmn_objects()

        assert len(bpmn_elements) == 2
        assert len(sequence_flows) == 1

        startEvent = self.find_elems(elements=bpmn_elements, type=BPMNStartEvent)
        assert len(startEvent) == 1
        assert startEvent[0].id == 'S'
        assert startEvent[0].name == 'SE'
        assert startEvent[0].sequenceFlow.id == 'F'

        endEvent = self.find_elems(elements=bpmn_elements, type=BPMNEndEvent)
        assert len(endEvent) == 1
        assert endEvent[0].id == 'E'
        assert endEvent[0].name == 'EE'
        assert endEvent[0].sequenceFlow.id == 'F'

        assert len(sequence_flows) == 1
        assert sequence_flows[0].id == 'F'
        assert sequence_flows[0].source.id == 'S'
        assert sequence_flows[0].target.id == 'E'

    def test_start_act_end(self, graph_builder, graph_builder_xmls):
        file_path = os.path.join(graph_builder_xmls, 'S_A_E.bpmn')
        graph_builder.xml_reader.parse_to_dom(abs_path=file_path)
        bpmn_elements, sequence_flows = graph_builder.create_bpmn_objects()

        assert len(bpmn_elements) == 3
        assert len(sequence_flows) == 2

        startEvent = self.find_elems(elements=bpmn_elements,
                                     type=BPMNStartEvent)
        assert len(startEvent) == 1
        assert startEvent[0].id == 'S'
        assert startEvent[0].name == 'SE'
        assert startEvent[0].sequenceFlow.id == 'F1'

        endEvent = self.find_elems(elements=bpmn_elements, type=BPMNEndEvent)
        assert len(endEvent) == 1
        assert endEvent[0].id == 'E'
        assert endEvent[0].name == 'EE'
        assert endEvent[0].sequenceFlow.id == 'F2'

        activity = self.find_elems(elements=bpmn_elements, type=BPMNActivity)
        assert len(activity) == 1
        assert activity[0].id == 'A'
        assert activity[0].name == 'Act'

        assert len(sequence_flows) == 2
        flow_1 = self.find_by_id(elements=sequence_flows, id='F1')
        assert flow_1.source.id == 'S'
        assert flow_1.target.id == 'A'

        flow_2 = self.find_by_id(elements=sequence_flows, id='F2')
        assert flow_2.source.id == 'A'
        assert flow_2.target.id == 'E'

    def test_parallel_gateway(self, graph_builder, graph_builder_xmls):
        file_path = os.path.join(graph_builder_xmls, 'min_parallel_gateway.bpmn')
        graph_builder.xml_reader.parse_to_dom(abs_path=file_path)
        bpmn_elements, sequence_flows = graph_builder.create_bpmn_objects()

        assert len(bpmn_elements) == 6
        assert len(sequence_flows) == 6

        gateways = self.find_elems(elements=bpmn_elements, type=BPMNParallelGateway)
        assert len(gateways) == 2

        gateway_1 = self.find_by_id(elements=gateways, id='GW1')
        assert len(gateway_1.sequence_flows_in) == 1
        assert len(gateway_1.sequence_flows_out) == 2

        #naming flows by their ids
        flow_1 = self.find_by_id(elements=sequence_flows, id='F1')
        assert flow_1.source.id == 'S'
        assert flow_1.target.id == 'GW1'

        flow_2 = self.find_by_id(elements=sequence_flows, id='F2')
        assert flow_2.name == 'cond1'
        assert flow_2.source.id == 'GW1'
        assert flow_2.target.id == 'A1'

        flow_3 = self.find_by_id(elements=sequence_flows, id='F3')
        assert flow_3.name == 'cond2'
        assert flow_3.source.id == 'GW1'
        assert flow_3.target.id == 'A2'

        flow_4 = self.find_by_id(elements=sequence_flows, id='F4')
        assert flow_4.source.id == 'A1'
        assert flow_4.target.id == 'GW2'

        flow_5 = self.find_by_id(elements=sequence_flows, id='F5')
        assert flow_5.source.id == 'A2'
        assert flow_5.target.id == 'GW2'

        flow_6 = self.find_by_id(elements=sequence_flows, id='F6')
        assert flow_6.source.id == 'GW2'
        assert flow_6.target.id == 'E'

        gateway_2 = self.find_by_id(elements=gateways, id='GW2')
        assert len(gateway_2.sequence_flows_in) == 2
        assert len(gateway_2.sequence_flows_out) == 1
