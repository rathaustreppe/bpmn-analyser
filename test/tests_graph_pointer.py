import os
import unittest
from typing import List, Tuple

import pytest

from src.converter.bpmn_models.bpmn_activity import BPMNActivity
from src.converter.bpmn_models.bpmn_element import BPMNElement
from src.converter.bpmn_models.bpmn_enum import BPMNEnum
from src.converter.bpmn_models.bpmn_model import BPMNModel
from src.converter.bpmn_models.bpmn_sequenceflow import BPMNSequenceFlow
from src.converter.bpmn_models.event.bpmn_endevent import BPMNEndEvent
from src.converter.bpmn_models.event.bpmn_event import BPMNEvent
from src.converter.bpmn_models.event.bpmn_startevent import BPMNStartEvent
from src.converter.bpmn_models.gateway.bpmn_exclusive_gateway import \
    BPMNExclusiveGateway
from src.converter.bpmn_models.gateway.bpmn_gateway import BPMNGateway
from src.converter.bpmn_models.gateway.bpmn_inclusive_gateway import \
    BPMNInclusiveGateway
from src.converter.bpmn_models.gateway.bpmn_parallel_gateway import \
    BPMNParallelGateway
from src.converter.converter import Converter
from src.exception.gateway_errors import ExclusiveGatewayBranchError
from src.exception.model_errors import NoStartEventError, \
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
                      target: BPMNElement) -> Tuple[BPMNElement, BPMNElement, BPMNSequenceFlow]:
        linking_flow = BPMNSequenceFlow(id_='f1', condition=None, source=source,
                                        target=target)

        if isinstance(source, BPMNEvent):
            source.sequence_flow = linking_flow
        elif isinstance(source, BPMNGateway):
            source.add_sequence_flow_out(flow=linking_flow)
        elif isinstance(source, BPMNActivity):
            source.sequence_flow_out = linking_flow

        if isinstance(target, BPMNEvent):
            target.sequence_flow = linking_flow
        elif isinstance(target, BPMNGateway):
            target.add_sequence_flow_in(flow=linking_flow)
        elif isinstance(target, BPMNActivity):
            target.sequence_flow_in = linking_flow

        return (source, target, linking_flow)

    def test_find_start_event_no_start(self):
        # error here: model has no start event
        activity = BPMNActivity(id_='42', name='space')
        model = self.make_model(elements=[activity], flows=[])
        graph_pointer = self.graph_pointer(model=model)

        with pytest.raises(NoStartEventError):
            graph_pointer.find_start_event()

    def test_find_start_event_multiple_starts(self):
        # error here: model has multiple start events
        start_1 = BPMNStartEvent(id_='1', name='SE1')
        start_2 = BPMNStartEvent(id_='2', name='SE2')
        model = self.make_model(elements=[start_1, start_2], flows=[])
        graph_pointer = self.graph_pointer(model=model)

        with pytest.raises(MultipleStartEventsError):
            graph_pointer.find_start_event()

    def test_find_start_event(self):
        # no error here: checks if it finds the single start event
        start = BPMNStartEvent(id_='1', name='SE')
        model = self.make_model(elements=[start], flows=[])
        graph_pointer = self.graph_pointer(model=model)

        assert graph_pointer.find_start_event() == start

    def test_reached_end_event(self):
        # no error here: checks if previous element is end_event which only happens
        # if graph_pointer reached the end of the graph
        end = BPMNEndEvent(id_='1', name='EE')
        model = self.make_model(elements=[end], flows=[])
        graph_pointer = self.graph_pointer(model=model)
        graph_pointer.stack.push(end)

        assert graph_pointer.reached_end_event()

    def test_reached_end_event_no_init(self):
        # error here: previous_element is not set yet
        model = BPMNModel(bpmn_elements=[], sequence_flows=[])
        graph_pointer = self.graph_pointer(model=model)

        assert graph_pointer.reached_end_event() is False

    def test_not_reached_end_event(self):
        # no error here: not reached end_event yet
        act = BPMNActivity(id_='1', name='act')
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
        sequence_flow_1 = BPMNSequenceFlow(id_='1', condition=condition1)
        condition2 = TokenStateCondition(tok_attribute=k2,
                                         operator=Operators.EQUALS,
                                         tok_value=v2)
        sequence_flow_2 = BPMNSequenceFlow(id_='2', condition=condition2)
        model = self.make_model(elements=[],
                                flows=[sequence_flow_1, sequence_flow_2])
        graph_pointer = self.graph_pointer(model=model, token=example_token)

        flows = graph_pointer.condition_fulfilling_sequence_flows(
            flows_to_check=model.sequence_flows)
        assert len(flows) == 2
        assert flows[0].id_ != flows[1].id_
        assert flows[0].id_ == 0 or 1

    def test_condition_fulfulling_sequence_flows_no_condition(self,
                                                              example_token):
        # no error here: check if flow without condition is accepted:
        # first flow with explicit none, second flow with implicit none.
        # just in case constructor changes
        sequence_flow_1 = BPMNSequenceFlow(id_='1', condition=None)
        sequence_flow_2 = BPMNSequenceFlow(id_='2')

        model = self.make_model(elements=[],
                                flows=[sequence_flow_1, sequence_flow_2])
        graph_pointer = self.graph_pointer(model=model, token=example_token)

        flows = graph_pointer.condition_fulfilling_sequence_flows(
            flows_to_check=model.sequence_flows)

        assert len(flows) == 2
        assert flows[0].id_ != flows[1].id_
        assert flows[0].id_ == 0 or 1

    def test_collect_conditional_sequence_flows_of_parallel_gateway(self):
        # no error here: checks if all sequence_flows make it through
        sequence_flow_1 = BPMNSequenceFlow(id_='1')
        sequence_flow_2 = BPMNSequenceFlow(id_='2')
        flows = [sequence_flow_1, sequence_flow_2]
        gateway = BPMNParallelGateway(id_='gw', sequence_flows_out=flows)
        model = self.make_model(elements=[gateway], flows=flows)
        graph_pointer = self.graph_pointer(model=model)

        flows = graph_pointer.collect_conditional_sequence_flows_of_gateway(
            gateway=gateway)
        assert len(flows) == 2
        assert flows[0].id_ != flows[1].id_
        assert flows[0].id_ == 0 or 1


    def test_collect_conditional_sequence_flows_of_inclusive_gateway(self, example_token):
        # no error here: checks if all sequence_flows make it through

        k1, v1 = 'k1', 'v1'
        k2 = 'k2'
        id_of_cond_flow = '1'
        condition1 = TokenStateCondition(tok_attribute=k1,
                                         operator=Operators.EQUALS,
                                         tok_value=v1)
        sequence_flow_1 = BPMNSequenceFlow(id_=id_of_cond_flow,
                                           condition=condition1)
        condition2 = TokenStateCondition(tok_attribute=k2,
                                         operator=Operators.EQUALS,
                                         tok_value='a value that is wrong')
        sequence_flow_2 = BPMNSequenceFlow(id_='no cond flow',
                                           condition=condition2)

        flows = [sequence_flow_1, sequence_flow_2]
        gateway = BPMNInclusiveGateway(id_='gw', sequence_flows_out=flows)
        model = self.make_model(elements=[gateway], flows=flows)
        graph_pointer = self.graph_pointer(model=model, token=example_token)

        flows = graph_pointer.collect_conditional_sequence_flows_of_gateway(
                                                            gateway=gateway)
        assert len(flows) == 1
        assert flows[0].id_ == id_of_cond_flow



    def test_collect_conditional_sequence_flows_of_exclusive_gateway_0_conditions_meet(self, example_token):
        # error here: have an exclusive gateway but 0 flows meet the conditions

        k1 = 'k1'
        condition1 = TokenStateCondition(tok_attribute=k1,
                                         operator=Operators.EQUALS,
                                         tok_value='wrong value')
        sequence_flow_1 = BPMNSequenceFlow(id_='no cond flow',
                                           condition=condition1)

        condition2 = TokenStateCondition(tok_attribute=k1,
                                         operator=Operators.EQUALS,
                                         tok_value='a value that is wrong')
        sequence_flow_2 = BPMNSequenceFlow(id_='no cond flow2',
                                           condition=condition2)
        flows = [sequence_flow_1, sequence_flow_2]

        gateway = BPMNExclusiveGateway(id_='gw', sequence_flows_out=flows)
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
        sequence_flow_1 = BPMNSequenceFlow(id_=id_of_cond_flow,
                                           condition=condition1)

        condition2 = TokenStateCondition(tok_attribute=k1,
                                         operator=Operators.EQUALS,
                                         tok_value='a value that is wrong')
        sequence_flow_2 = BPMNSequenceFlow(id_='no cond flow2',
                                           condition=condition2)
        flows = [sequence_flow_1, sequence_flow_2]

        gateway = BPMNExclusiveGateway(id_='gw', sequence_flows_out=flows)
        model = self.make_model(elements=[gateway], flows=flows)
        graph_pointer = self.graph_pointer(model=model, token=example_token)

        flows = graph_pointer.collect_conditional_sequence_flows_of_gateway(gateway=gateway)
        assert len(flows) == 1
        assert flows[0].id_ == id_of_cond_flow


    def test_next_step_no_gateway_activity(self, nn_chunker):
        # checks if adjacent element of activity is pushed on stack

        # model building
        act_1 = BPMNActivity(id_='act1', name='noun')
        act_2 = BPMNActivity(id_='act2', name='noun')
        act_1, act_2, flow = self.link_elements(source=act_1, target=act_2)
        act_1: BPMNActivity
        model = self.make_model(elements=[act_1,act_2], flows=[flow])

        # init
        graph_pointer = self.graph_pointer(model=model, chunker=nn_chunker)
        graph_pointer.stack.push(act_1)

        # test
        graph_pointer.next_step_no_gateway(element=act_1)
        assert graph_pointer.stack.top() == act_2

    def test_next_step_no_gateway_start_event(self, nn_chunker):
        # checks if adjacent element of start event is pushed on stack

        # model building
        start = BPMNStartEvent(id_='SE', name='startendevent')
        act_1 = BPMNActivity(id_='act1', name='noun')
        start, act_1, flow = self.link_elements(source=start, target=act_1)
        start: BPMNStartEvent
        model = self.make_model(elements=[start,act_1], flows=[flow])

        # init
        graph_pointer = self.graph_pointer(model=model, chunker=nn_chunker)
        graph_pointer.stack.push(start)

        # test
        graph_pointer.next_step_no_gateway(element=start)
        assert graph_pointer.stack.top() == act_1

    def test_next_step_no_gateway_end_event(self, nn_chunker):
        # checks if activity with adjacent end event is comes to a stop

        # model_building
        end = BPMNEndEvent(id_='EE', name='startendevent')
        act_1 = BPMNActivity(id_='act1', name='noun')
        act_1, end, flow = self.link_elements(source=act_1, target=end)
        act_1: BPMNActivity
        end: BPMNEndEvent
        model = self.make_model(elements=[act_1, end], flows=[flow])

        # init
        graph_pointer = self.graph_pointer(model=model, chunker=nn_chunker)
        graph_pointer.stack.push(act_1)

        # test
        graph_pointer.next_step_no_gateway(element=act_1)
        # act_1 puts endEvent on top
        assert graph_pointer.stack.top() == end
        graph_pointer.next_step_no_gateway(element=act_1)
        # end puts itself (endEvent) on top
        assert graph_pointer.stack.top() == end

    def test_next_step_opening_gateway(self, nn_chunker):
        # checks if branches of opening gateway and gateway itself are on stack
        # conditional branch checking is done by other tests

        # model building
        gateway = BPMNParallelGateway(id_='gw')
        act_1 = BPMNActivity(id_='act1', name='noun')
        act_2 = BPMNActivity(id_='act2', name='noun')

        gateway, act_1, flow_1 = self.link_elements(source=gateway, target=act_1)
        gateway, act_2, flow_2 = self.link_elements(source=gateway, target=act_2)
        model = self.make_model(elements=[gateway, act_1, act_2], flows=[flow_1, flow_2])
        gateway: BPMNParallelGateway

        # init
        graph_pointer = self.graph_pointer(model=model, chunker=nn_chunker)
        graph_pointer.stack.push(gateway)

        # test
        graph_pointer.next_step_opening_gateway(gateway=gateway)
        assert graph_pointer.stack.pop() == act_1
        assert graph_pointer.stack.pop() == act_2
        assert graph_pointer.stack.pop() == gateway


    def test_next_step_closing_gateway(self, nn_chunker):
        # checks case: annihilate opening gateway

        # model building
        in_act_1 = BPMNActivity(id_='inact1', name='noun')
        in_act_2 = BPMNActivity(id_='inact2', name='noun')
        opening_gateway = BPMNParallelGateway(id_='opgw')
        closing_gateway = BPMNParallelGateway(id_='clgw')
        out_act = BPMNActivity(id_='outact', name='noun')

        opening_gateway, in_act_1, _ = self.link_elements(source=opening_gateway,
                                                          target=in_act_1)
        opening_gateway, in_act_2, _ = self.link_elements(source=opening_gateway,
                                                          target=in_act_2)

        in_act_1, closing_gateway, _ = self.link_elements(source=in_act_1,
                                                          target=closing_gateway)
        in_act_2, closing_gateway, _ = self.link_elements(source=in_act_2,
                                                          target=closing_gateway)

        closing_gateway, out_act, _ = self.link_elements(source=closing_gateway,
                                                         target=out_act)

        closing_gateway: BPMNParallelGateway
        model = self.make_model(elements=[in_act_1, in_act_2,
                                          opening_gateway,
                                          closing_gateway,
                                          out_act], flows=[_])

        # init
        graph_pointer = self.graph_pointer(model=model, chunker=nn_chunker)
        graph_pointer.stack.push(opening_gateway)

        # asserts for test config
        assert graph_pointer.is_opening_gateway(element=opening_gateway)
        assert graph_pointer.is_closing_gateway(element=closing_gateway)
        assert type(opening_gateway) == type(closing_gateway)

        # test
        graph_pointer.next_step_closing_gateway(gateway=closing_gateway)
        assert graph_pointer.stack.top() == out_act

    def test_next_step_closing_gateway_activity(self, nn_chunker):
        # checks case: not all branches processed,
        # activity before gateway annihilation

        # model building
        in_act_1 = BPMNActivity(id_='inact1', name='noun')
        in_act_2 = BPMNActivity(id_='inact2', name='noun')
        closing_gateway = BPMNParallelGateway(id_='clgw')
        out_act = BPMNActivity(id_='outact', name='noun')

        in_act_1, closing_gateway, _ = self.link_elements(source=in_act_1,
                                                          target=closing_gateway)
        in_act_2, closing_gateway, _ = self.link_elements(source=in_act_2,
                                                          target=closing_gateway)

        closing_gateway, out_act, _ = self.link_elements(source=closing_gateway,
                                                         target=out_act)
        closing_gateway: BPMNParallelGateway
        model = self.make_model(elements=[in_act_1, in_act_2,
                                          closing_gateway,
                                          out_act], flows=[_])
        # init
        graph_pointer = self.graph_pointer(model=model, chunker=nn_chunker)
        activity_on_stack = in_act_2
        graph_pointer.stack.push(item=activity_on_stack)

        # asserts for test config
        assert graph_pointer.is_closing_gateway(element=closing_gateway)

        # test
        graph_pointer.next_step_closing_gateway(gateway=closing_gateway)
        assert graph_pointer.stack.top() == activity_on_stack