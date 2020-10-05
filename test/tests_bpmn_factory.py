import pytest

from src.converter.bpmn_factory import BPMNFactory
from src.converter.bpmn_models.bpmn_enum import BPMNEnum
from src.converter.bpmn_models.gateway.bpmn_exclusive_gateway import \
    BPMNExclusiveGateway
from src.converter.bpmn_models.gateway.bpmn_inclusive_gateway import \
    BPMNInclusiveGateway
from src.converter.bpmn_models.gateway.bpmn_parallel_gateway import \
    BPMNParallelGateway


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
        bpmn = self.factory.create_bpmn_flow_object(element=elem,
                                                    elem_type=BPMNEnum.ACTIVITY)
        assert bpmn.name == ''
        assert bpmn.id_ == ''

    def test_activity_normal_no_flow(self):
        string = r'<task id="1" name="a"></task>'
        elem = self.read_xml(string)
        bpmn = self.factory.create_bpmn_flow_object(element=elem,
                                                    elem_type=BPMNEnum.ACTIVITY)
        assert bpmn.name == 'a'
        assert bpmn.id_ == '1'

    def test_flow_normal(self):
        string_act1 = r'<task id="1" name="a"></task>'
        string_act2 = r'<task id="2" name="b"></task>'
        string_flow = r'<sequenceFlow id="f" sourceRef="1" targetRef="2"/>'
        act1 = self.factory.create_bpmn_flow_object(
            element=self.read_xml(string_act1), elem_type=BPMNEnum.ACTIVITY)
        act2 = self.factory.create_bpmn_flow_object(
            element=self.read_xml(string_act2), elem_type=BPMNEnum.ACTIVITY)
        flow = self.factory.create_bpmn_connecting_object(
            element=self.read_xml(string_flow),
            elem_type=BPMNEnum.SEQUENCEFLOW,
            src_tgt_elements=[act1, act2])

        assert flow.id_ == 'f'
        assert flow.source.id_ == '1'
        assert flow.target.id_ == '2'

    def test_flow_empty_id(self):
        string_act1 = r'<task id="" name="a"></task>'
        string_act2 = r'<task id="2" name="b"></task>'
        string_flow = r'<sequenceFlow id="f" sourceRef="" targetRef="2"/>'
        act1 = self.factory.create_bpmn_flow_object(
            element=self.read_xml(string_act1), elem_type=BPMNEnum.ACTIVITY)
        act2 = self.factory.create_bpmn_flow_object(
            element=self.read_xml(string_act2), elem_type=BPMNEnum.ACTIVITY)
        flow = self.factory.create_bpmn_connecting_object(
            element=self.read_xml(string_flow),
            elem_type=BPMNEnum.SEQUENCEFLOW,
            src_tgt_elements=[act1, act2])

        assert flow.id_ == 'f'
        assert flow.source.id_ == ''
        assert flow.target.id_ == '2'

    def test_start_event_normal(self):
        string = '<startEvent id="1" name="a"></startEvent>'
        start = self.factory.create_bpmn_flow_object(
            element=self.read_xml(string), elem_type=BPMNEnum.STARTEVENT)

        assert start.id_ == '1'
        assert start.name == 'a'

    def test_endevent_normal(self):
        string = '<startEvent id="1" name="a"></startEvent>'
        start = self.factory.create_bpmn_flow_object(
            element=self.read_xml(string), elem_type=BPMNEnum.ENDEVENT)

        assert start.id_ == '1'
        assert start.name == 'a'

    def test_parallel_gateway_constructor(self):
        string = '<parallelGateway id="1"></parallelGateway>'
        gateway = self.factory.create_bpmn_flow_object(
            element=self.read_xml(string), elem_type=BPMNEnum.PARALLGATEWAY)

        assert isinstance(gateway, BPMNParallelGateway)
        assert gateway.id_ == '1'

    def test_inclusive_gateway_constructor(self):
        string = '<inclusiveGateway id="1"></inclusiveGateway>'
        gateway = self.factory.create_bpmn_flow_object(
            element=self.read_xml(string), elem_type=BPMNEnum.INCLGATEWAY)

        assert isinstance(gateway, BPMNInclusiveGateway)
        assert gateway.id_ == '1'

    def test_exclusive_gateway_constructor(self):
        string = '<exclusiveGateway id="1"></exclusiveGateway>'
        gateway = self.factory.create_bpmn_flow_object(
            element=self.read_xml(string), elem_type=BPMNEnum.EXCLGATEWAY)

        assert isinstance(gateway, BPMNExclusiveGateway)
        assert gateway.id_ == '1'
