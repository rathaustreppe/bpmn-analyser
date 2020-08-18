from xml.etree.ElementTree import Element

import pytest

from src.converter.bpmn_factory import BPMNFactory
from src.converter.bpmn_models.bpmn_enum import BPMNEnum


class TestBPMNFactory:

    @pytest.fixture(autouse=True)
    def factory(self):
        self.factory = BPMNFactory()

    def read_xml(self, string):
        import xml.etree.ElementTree as ET
        xml_tree = ET.fromstring(string)
        return xml_tree

    def test_empty_activity_no_flow(self):
        string = r'<task id="" name=""></task>'
        elem = self.read_xml(string)
        bpmn = self.factory.create_bpmn_element(element=elem, elem_type=BPMNEnum.ACTIVITY)
        assert bpmn.get_name() == ''
        assert bpmn.get_id() == ''

    def test_activity_normal_no_flow(self):
        string = r'<task id="1" name="a"></task>'
        elem = self.read_xml(string)
        bpmn = self.factory.create_bpmn_element(element=elem, elem_type=BPMNEnum.ACTIVITY)
        assert bpmn.get_name() == 'a'
        assert bpmn.get_id() == '1'

    def test_flow_normal(self):
        string_act1 = r'<task id="1" name="a"></task>'
        string_act2 = r'<task id="2" name="b"></task>'
        string_flow = r'<sequenceFlow id="f" sourceRef="1" targetRef="2"/>'
        act1 = self.factory.create_bpmn_element(element=self.read_xml(string_act1), elem_type=BPMNEnum.ACTIVITY)
        act2 = self.factory.create_bpmn_element(element=self.read_xml(string_act2), elem_type=BPMNEnum.ACTIVITY)
        flow = self.factory.create_bpmn_flow(flow=self.read_xml(string_flow), elem_type=BPMNEnum.SEQUENCEFLOW, elements=[act1,act2])

        assert flow.get_id() == 'f'
        assert flow.get_source().get_id() == '1'
        assert flow.get_target().get_id() == '2'

    def test_flow_empty_id(self):
        string_act1 = r'<task id="" name="a"></task>'
        string_act2 = r'<task id="2" name="b"></task>'
        string_flow = r'<sequenceFlow id="f" sourceRef="" targetRef="2"/>'
        act1 = self.factory.create_bpmn_element(element=self.read_xml(string_act1), elem_type=BPMNEnum.ACTIVITY)
        act2 = self.factory.create_bpmn_element(element=self.read_xml(string_act2), elem_type=BPMNEnum.ACTIVITY)
        flow = self.factory.create_bpmn_flow(flow=self.read_xml(string_flow), elem_type=BPMNEnum.SEQUENCEFLOW, elements=[act1,act2])

        assert flow.get_id() == 'f'
        assert flow.get_source().get_id() == ''
        assert flow.get_target().get_id() == '2'

    def test_start_event_normal(self):
        string = '<startEvent id="1" name="a"></startEvent>'
        start = self.factory.create_bpmn_element(element=self.read_xml(string), elem_type=BPMNEnum.STARTEVENT)

        assert start.get_id() == '1'
        assert start.get_name() == 'a'

    def test_endevent_normal(self):
        string = '<startEvent id="1" name="a"></startEvent>'
        start = self.factory.create_bpmn_element(element=self.read_xml(string), elem_type=BPMNEnum.ENDEVENT)

        assert start.get_id() == '1'
        assert start.get_name() == 'a'
