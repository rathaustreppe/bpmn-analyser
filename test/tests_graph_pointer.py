import os
import unittest
from copy import copy
from typing import List, Tuple

import igraph
import pytest

from src.converter.bpmn_models.bpmn_activity import BPMNActivity
from src.converter.bpmn_models.bpmn_element import BPMNElement
from src.converter.bpmn_models.bpmn_enum import BPMNEnum
from src.converter.bpmn_models.bpmn_model import BPMNModel
from src.converter.bpmn_models.bpmn_sequenceflow import BPMNSequenceFlow
from src.converter.bpmn_models.event.bpmn_endevent import BPMNEndEvent
from src.converter.bpmn_models.event.bpmn_startevent import BPMNStartEvent
from src.converter.bpmn_models.gateway.bpmn_exclusive_gateway import \
    BPMNExclusiveGateway
from src.converter.bpmn_models.gateway.bpmn_inclusive_gateway import \
    BPMNInclusiveGateway
from src.converter.bpmn_models.gateway.bpmn_parallel_gateway import \
    BPMNParallelGateway
from src.converter.converter import Converter
from src.exception.WrongTypeException import WrongTypeException
from src.exception.gateway_exception import ExclusiveGatewayBranchError
from src.exception.model_exception import NoStartEventError, \
    MultipleStartEventsError
from src.graph_pointer import GraphPointer
from src.models.token import Token
from src.models.token_state_condition import TokenStateCondition, Operators
from src.nlp.chunker import Chunker


class TestGraphPointer:

    def graph_pointer(self, model: BPMNModel,
                      token: Token = Token(),
                      ruleset: List[TokenStateCondition] = [],
                      chunker: Chunker = Chunker()) -> GraphPointer:
        return GraphPointer(model=model, token=token,
                            ruleset=ruleset,
                            chunker=chunker)

    def make_model(self, elements: List[BPMNElement],
                   flows: List[BPMNSequenceFlow]) -> BPMNModel:
        return BPMNModel(bpmn_elements=elements, sequence_flows=flows)

    def link_elements(self, source: BPMNElement,
                      target: BPMNElement) -> Tuple[BPMNElement, BPMNElement]:
        linking_flow = BPMNSequenceFlow(id='f1', condition=None,
                                        source=source, target=target)
        source.sequence_flow_out = linking_flow
        target.sequence_flow_in = linking_flow
        return (source, target)

    def test_find_start_event_no_start(self):
        # error here: model has no start event
        activity = BPMNActivity(id='42', name='space')
        model = self.make_model(elements=[activity], flows=[])
        graph_pointer = self.graph_pointer(model=model)

        with pytest.raises(NoStartEventError):
            graph_pointer.find_start_event()

    def test_find_start_event_multiple_starts(self):
        # error here: model has multiple start events
        start_1 = BPMNStartEvent(id='1', name='SE1')
        start_2 = BPMNStartEvent(id='2', name='SE2')
        model = self.make_model(elements=[start_1, start_2], flows=[])
        graph_pointer = self.graph_pointer(model=model)

        with pytest.raises(MultipleStartEventsError):
            graph_pointer.find_start_event()

    def test_find_start_event(self):
        # no error here: checks if it finds the single start event
        start = BPMNStartEvent(id='1', name='SE')
        model = self.make_model(elements=[start], flows=[])
        graph_pointer = self.graph_pointer(model=model)

        assert graph_pointer.find_start_event() == start

    def test_reached_end_event(self):
        # no error here: checks if previous element is end_event which only happens
        # if graph_pointer reached the end of the graph
        end = BPMNEndEvent(id='1', name='EE')
        model = self.make_model(elements=[end], flows=[])
        graph_pointer = self.graph_pointer(model=model)
        graph_pointer.previous_element = end

        assert graph_pointer.reached_end_event()

    def test_reached_end_event_no_init(self):
        # error here: previous_element is not set yet
        model = BPMNModel(bpmn_elements=[], sequence_flows=[])
        graph_pointer = self.graph_pointer(model=model)

        assert graph_pointer.reached_end_event() is False

    def test_not_reached_end_event(self):
        # no error here: not reached end_event yet
        act = BPMNActivity(id='1', name='act')
        model = self.make_model(elements=[act], flows=[])
        graph_pointer = self.graph_pointer(model=model)
        graph_pointer.previous_element = act

        assert graph_pointer.reached_end_event() is False

    def test_condition_fulfilling_sequence_flows(self, example_token):
        # no error here: check if all sequence_flows are treated right
        k1, v1 = 'k1', 'v1'
        k2, v2 = 'k2', 'v2'
        condition1 = TokenStateCondition(tok_attribute=k1,
                                         operator=Operators.EQUALS,
                                         tok_value=v1)
        sequence_flow_1 = BPMNSequenceFlow(id='1', condition=condition1)
        condition2 = TokenStateCondition(tok_attribute=k2,
                                         operator=Operators.EQUALS,
                                         tok_value=v2)
        sequence_flow_2 = BPMNSequenceFlow(id='2', condition=condition2)
        model = self.make_model(elements=[],
                                flows=[sequence_flow_1, sequence_flow_2])
        graph_pointer = self.graph_pointer(model=model, token=example_token)

        flows = graph_pointer.get_condition_fulfilling_sequence_flows(
            flows_to_check=model.sequence_flows)
        assert len(flows) == 2
        assert flows[0].id != flows[1].id
        assert flows[0].id == 0 or 1

    def test_condition_fulfulling_sequence_flows_no_condition(self,
                                                              example_token):
        # no error here: check if flow without condition is accepted:
        # first flow with explicit none, second flow with implicit none.
        # just in case constructor changes
        sequence_flow_1 = BPMNSequenceFlow(id='1', condition=None)
        sequence_flow_2 = BPMNSequenceFlow(id='2')

        model = self.make_model(elements=[],
                                flows=[sequence_flow_1, sequence_flow_2])
        graph_pointer = self.graph_pointer(model=model, token=example_token)

        flows = graph_pointer.get_condition_fulfilling_sequence_flows(
            flows_to_check=model.sequence_flows)

        assert len(flows) == 2
        assert flows[0].id != flows[1].id
        assert flows[0].id == 0 or 1

    def test_collect_conditional_sequence_flows_of_parallel_gateway(self):
        # no error here: checks if all sequence_flows make it through
        sequence_flow_1 = BPMNSequenceFlow(id='1')
        sequence_flow_2 = BPMNSequenceFlow(id='2')
        flows = [sequence_flow_1, sequence_flow_2]
        gateway = BPMNParallelGateway(id='gw', sequence_flows_out=flows)
        model = self.make_model(elements=[gateway], flows=flows)
        graph_pointer = self.graph_pointer(model=model)

        flows = graph_pointer.collect_conditional_sequence_flows_of_gateway(
            gateway=gateway)
        assert len(flows) == 2
        assert flows[0].id != flows[1].id
        assert flows[0].id == 0 or 1


    def test_collect_conditional_sequence_flows_of_inclusive_gateway(self, example_token):
        # no error here: checks if all sequence_flows make it through

        k1, v1 = 'k1', 'v1'
        k2 = 'k2'
        id_of_cond_flow = '1'
        condition1 = TokenStateCondition(tok_attribute=k1,
                                         operator=Operators.EQUALS,
                                         tok_value=v1)
        sequence_flow_1 = BPMNSequenceFlow(id=id_of_cond_flow, condition=condition1)
        condition2 = TokenStateCondition(tok_attribute=k2,
                                         operator=Operators.EQUALS,
                                         tok_value='a value that is wrong')
        sequence_flow_2 = BPMNSequenceFlow(id='no cond flow', condition=condition2)

        flows = [sequence_flow_1, sequence_flow_2]
        gateway = BPMNInclusiveGateway(id='gw', sequence_flows_out=flows)
        model = self.make_model(elements=[gateway], flows=flows)
        graph_pointer = self.graph_pointer(model=model, token=example_token)

        flows = graph_pointer.collect_conditional_sequence_flows_of_gateway(
                                                            gateway=gateway)
        assert len(flows) == 1
        assert flows[0].id == id_of_cond_flow



    def test_collect_conditional_sequence_flows_of_exclusive_gateway_0_conditions_meet(self, example_token):
        # error here: have an exclusive gateway but 0 flows meet the conditions

        k1 = 'k1'
        k2 = 'k2'
        condition1 = TokenStateCondition(tok_attribute=k1,
                                         operator=Operators.EQUALS,
                                         tok_value='wrong value')
        sequence_flow_1 = BPMNSequenceFlow(id='no cond flow', condition=condition1)

        condition2 = TokenStateCondition(tok_attribute=k1,
                                         operator=Operators.EQUALS,
                                         tok_value='a value that is wrong')
        sequence_flow_2 = BPMNSequenceFlow(id='no cond flow2', condition=condition2)
        flows = [sequence_flow_1, sequence_flow_2]

        gateway = BPMNExclusiveGateway(id='gw', sequence_flows_out=flows)
        model = self.make_model(elements=[gateway], flows=flows)
        graph_pointer = self.graph_pointer(model=model, token=example_token)

        with pytest.raises(ExclusiveGatewayBranchError):
            graph_pointer.collect_conditional_sequence_flows_of_gateway(gateway=
                                                                        gateway)


    def test_collect_conditional_sequence_flows_of_exclusive_gateway(self,example_token):
        # no error here: checks if exclusive gateway with 1 branch works
        k1, v1 = 'k1', 'v1'
        id_of_cond_flow = '1'
        condition1 = TokenStateCondition(tok_attribute=k1,
                                         operator=Operators.EQUALS,
                                         tok_value=v1)
        sequence_flow_1 = BPMNSequenceFlow(id=id_of_cond_flow, condition=condition1)

        condition2 = TokenStateCondition(tok_attribute=k1,
                                         operator=Operators.EQUALS,
                                         tok_value='a value that is wrong')
        sequence_flow_2 = BPMNSequenceFlow(id='no cond flow2', condition=condition2)
        flows = [sequence_flow_1, sequence_flow_2]

        gateway = BPMNExclusiveGateway(id='gw', sequence_flows_out=flows)
        model = self.make_model(elements=[gateway], flows=flows)
        graph_pointer = self.graph_pointer(model=model, token=example_token)

        flows = graph_pointer.collect_conditional_sequence_flows_of_gateway(gateway=gateway)
        assert len(flows) == 1
        assert flows[0].id == id_of_cond_flow

    @unittest.skip
    def test_next_step_with_parallel_gateway(self, xml_folders_path,
                                             example_token, nn_chunker):
        xml_file_path = os.path.join(xml_folders_path,
                                     'converter',
                                     'min_parallel_gateway.bpmn')
        converter = Converter()
        graph = converter.convert(rel_path_to_bpmn=xml_file_path)
        graph_pointer = self.graph_pointer(model=graph, token=example_token,
                                           chunker=nn_chunker)

        # first call for init startevent
        graph_pointer.runstep_graph()
        assert graph_pointer.previous_element[BPMNEnum.NAME.value] == 'SE'
        assert graph_pointer.stack_handler.stack.empty()

        # next call to find opening gateway --> check stack
        graph_pointer.runstep_graph()
        assert graph_pointer.previous_element[
                   BPMNEnum.NAME.value] == BPMNEnum.PARALLGATEWAY_TEXT.value
        assert graph_pointer.stack_handler.stack.top()[BPMNEnum.NAME.value] in [
            'act', 'Bact']

        # next call to go into first branch
        graph_pointer.runstep_graph()
        assert graph_pointer.previous_element[BPMNEnum.NAME.value] in ['act',
                                                                       'Bact']
        assert graph_pointer.stack_handler.stack.top()[BPMNEnum.NAME.value] in [
            'act', 'Bact']

        # next call to go into adjacent of first branch == closing gateway
        graph_pointer.runstep_graph()
        assert graph_pointer.previous_element[
                   BPMNEnum.NAME.value] == BPMNEnum.PARALLGATEWAY_TEXT.value
        assert graph_pointer.stack_handler.stack.top()[BPMNEnum.NAME.value] in [
            'act', 'Bact']

        # next call to finish first branch and ask stack to go into second branch
        graph_pointer.runstep_graph()
        assert graph_pointer.previous_element[BPMNEnum.NAME.value] in ['act',
                                                                       'Bact']
        assert graph_pointer.stack_handler.stack.top()[
                   BPMNEnum.NAME.value] == BPMNEnum.PARALLGATEWAY_TEXT.value

        # next call to go adjacent of second branch == closing gateway
        # but stack is empty --> finishing gateway and taking it from stack
        # but putting adjacent of closing gateway on stack
        graph_pointer.runstep_graph()
        assert graph_pointer.previous_element[
                   BPMNEnum.NAME.value] == BPMNEnum.PARALLGATEWAY_TEXT.value
        assert graph_pointer.stack_handler.stack.top()[
                   BPMNEnum.NAME.value] == 'EE'

        # next call to go into endevent and clear stack
        graph_pointer.runstep_graph()
        assert graph_pointer.previous_element[BPMNEnum.NAME.value] == 'EE'
        assert graph_pointer.stack_handler.stack.empty()

        # next call to to find out it reached the end of the graph (returns 1)
        assert graph_pointer.runstep_graph() == 1
