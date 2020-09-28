from typing import List, Union, Optional

from pedantic import pedantic_class

from src.converter.bpmn_models.bpmn_activity import BPMNActivity
from src.converter.bpmn_models.bpmn_element import BPMNElement
from src.converter.bpmn_models.bpmn_model import BPMNModel
from src.converter.bpmn_models.bpmn_sequenceflow import BPMNSequenceFlow
from src.converter.bpmn_models.event.bpmn_endevent import BPMNEndEvent
from src.converter.bpmn_models.event.bpmn_startevent import BPMNStartEvent
from src.converter.bpmn_models.gateway.bpmn_exclusive_gateway import \
    BPMNExclusiveGateway
from src.converter.bpmn_models.gateway.bpmn_gateway import BPMNGateway
from src.converter.bpmn_models.gateway.bpmn_inclusive_gateway import \
    BPMNInclusiveGateway
from src.converter.bpmn_models.gateway.bpmn_parallel_gateway import \
    BPMNParallelGateway
from src.exception.WrongTypeException import NotImplementedTypeException
from src.exception.gateway_exception import ExclusiveGatewayBranchError
from src.exception.model_exception import MultipleStartEventsError, \
    NoStartEventError
from src.models.gateway_stack_handler import GatewayStackHandler
from src.models.stack import Stack
from src.models.token import Token
from src.models.token_state_rule import TokenStateRule
from src.nlp.chunker import Chunker
from src.nlp.rule_finder import RuleFinder


@pedantic_class
class GraphPointer:
    """
    GraphPointer is the object that points to a
    single vertex in the BPMN-graph and reads its values
    to change the token attributes --> the tokens current
    state. It knows how to deal with gateways.
    """

    def __init__(self,
                 token: Token,
                 ruleset: List[TokenStateRule],
                 chunker: Chunker,
                 model: BPMNModel,
                 stack: Optional[Stack] = None) -> None:
        self.model = model
        self.token = token
        self.rule_finder = RuleFinder(chunker=chunker, ruleset=ruleset)
        self.previous_element: Optional[Union[BPMNGateway, BPMNActivity]] = None
        self.stack_handler = GatewayStackHandler()
        self.stack = stack
        self._model_start = None

        if self.stack is None:
            self.stack = Stack()

    def runstep_graph(self) -> int:
        """
        With each call, it iterates one step through the
        BPMNModel (= changes and self.previous),
        analyses the text (= bpmn activity) and performs state transitions
        on token.
        Returns:
            int:
            1 if the end of the graph is reached
            0 if the the step was performed successfully but
            the end of the graph is not reached yet
        """
        if self._model_start is None:
            # init
            self._model_start = self.find_start_event()
            self.next_step_no_gateway(element=self._model_start)

        if not self.reached_end_event():
            self.next_step_switch_by_type()
            return 0
        else:
            # make text analysis of endevent, empty stack and
            # quit with return 1
            self.next_step_switch_by_type()
            self.stack.empty()
            return 1

    def reached_end_event(self) -> bool:
        return isinstance(self.stack.top(), BPMNEndEvent)

    def find_start_event(self) -> BPMNStartEvent:
        """
        Find the entry point of the BPMNModel from where
        the BPMNModel is read. This is usually the BPMNStartEvent.
        """
        start = self.model.find_elements_by_type(type_to_find=BPMNStartEvent)
        if len(start) == 1:
            return start[0]
        elif len(start) == 0:
            raise NoStartEventError(model=self.model)
        else:
            raise MultipleStartEventsError(model=self.model)

    def _text_analysis(self, activity: Union[
        BPMNActivity, BPMNStartEvent, BPMNEndEvent]) -> List[TokenStateRule]:
        """
        Applies NLP on BPMNActivity and finds all the rules where
        their SynonymCloud is synonym to the given vertex text.
        """
        matching_rules = self.rule_finder.find_rules(text=activity.name)

        print(f'TEXT: {activity.name}')
        print(f'MATCHING RULES: {matching_rules}')

        return matching_rules

    def _modify_token_with_rules(self,
                                 matching_rules: List[TokenStateRule]) -> Token:
        """
        We apply rules (==change token state), when their SynonymClouds are
        matching and their conditions are true.
        """
        for rule in matching_rules:
            self.token = rule.check_and_modify(token=self.token)
        return self.token


    def first_element_of_all_branches(self,
                                      branches: List[BPMNSequenceFlow]) -> \
            List[Union[BPMNActivity, BPMNGateway, BPMNElement]]:
        return [flow.target for flow in branches]

    def condition_fulfilling_sequence_flows(self, flows_to_check: List[
        BPMNSequenceFlow]) -> List[BPMNSequenceFlow]:
        flows = []
        for flow in flows_to_check:
            if flow.condition is None or flow.condition.check_condition(
                    token=self.token):
                # we treat flows without conditions as fulfilled flows
                flows.append(flow)
        return flows

    def collect_conditional_sequence_flows_of_gateway(self,
                                                      gateway: BPMNGateway) -> \
            List[BPMNSequenceFlow]:
        """
        Method that makes a distinction of different gateway types and returns
        the corresponding sequence_flows that fulfill the conditions.
        Parallel-Gateway: returns all sequence_flows
        Inclusive-Gateway: returns all sequence_flows that meet the condition
        Exclusive-Gateway: checks that only one sequence_flow
        fullfills the condition
        """
        flows = gateway.sequence_flows_out

        if isinstance(gateway, BPMNParallelGateway):
            return flows

        elif isinstance(gateway, BPMNInclusiveGateway):
            return self.condition_fulfilling_sequence_flows(
                flows_to_check=flows)

        elif isinstance(gateway, BPMNExclusiveGateway):
            cond_flows = self.condition_fulfilling_sequence_flows(
                flows_to_check=flows)
            if len(cond_flows) == 1:
                return cond_flows
            else:
                raise ExclusiveGatewayBranchError(gateway=gateway,
                                                  flows=flows)

    def text_analysis(self, current: Union[
        BPMNActivity, BPMNStartEvent, BPMNEndEvent]) -> None:
        matching_rules = self.rule_finder.find_rules(text=current.name)
        self._modify_token_with_rules(matching_rules=matching_rules)

    def is_opening_gateway(self, element: BPMNElement) -> bool:
        return isinstance(element, BPMNGateway) and element.is_opening_gateway()

    def is_closing_gateway(self, element: BPMNElement) -> bool:
        return isinstance(element,
                          BPMNGateway) and not element.is_opening_gateway()



    def next_step_no_gateway(self, element: Union[
        BPMNActivity, BPMNStartEvent, BPMNEndEvent]) -> None:
        def push(to_push: Union[
            BPMNActivity, BPMNStartEvent, BPMNEndEvent, BPMNElement]):
            self.stack.push(item=to_push)

        self.text_analysis(current=element)

        if isinstance(element, BPMNActivity):
            push(to_push=element.sequence_flow_out.target)

        elif isinstance(element, BPMNStartEvent):
            push(to_push=element.sequence_flow.target)

        elif isinstance(element, BPMNEndEvent):
            # BPMNEndEvent on top of stack is treated as ending in next
            # iteration
            push(to_push=element)

    def next_step_opening_gateway(self, gateway: BPMNGateway) -> None:
        if self.is_opening_gateway(element=gateway):
            conditions_meet_flows = \
                self.collect_conditional_sequence_flows_of_gateway(
                    gateway=gateway)
            branch_elements = self.first_element_of_all_branches(
                branches=conditions_meet_flows)

            self.stack.push(gateway)

            #reverse list order to put it 1:1 on stack (because stack is LIFO,
            #but first list element should be on top of stack, because easier
            # to debug)
            branch_elements.reverse()

            for element in branch_elements:
                self.stack.push(element)

    def next_step_closing_gateway(self, gateway: BPMNGateway) -> None:
        if self.is_closing_gateway(element=gateway):
            tos = self.stack.top()
            if self.is_opening_gateway(element=tos):
                # annihilate
                self.stack.pop()
                # closing gateway can have only 1 outgoing sequence_flow
                # therefore direct access
                self.stack.push(gateway.sequence_flows_out[0].target)
            elif self.is_closing_gateway(element=tos):
                raise ValueError('Stack Exception')
            elif isinstance(tos, BPMNActivity) or isinstance(tos,
                                                             BPMNStartEvent):
                #there is another branch to process
                return

    def next_step_switch_by_type(self) -> None:
        """
        Current = stack.pop()
        Current is StartEvent oder Activity
            nlp auf current
            stack.push(current.sequence_flow.out.target)
        Current is Opening Gateway:
            conditions meet flows herausfinden
            push gateway
            push conditions meet flows
        current is closing gateway:
            check top of stack:
                if tos is opening gateway of same type
                    annhilate: stack.pop ins nichts
                    push gateway.sequenceflow_out.target (length = 1)
                elif tos is closing gateway
                    error
                elif tos is activity oder startevent
                    kein annihalte
                    warten zum nächsten aufruf, der popt dann die activity
        
        """

        current = self.stack.pop()
        if self.is_opening_gateway(element=current):
            self.next_step_opening_gateway(gateway=current)

        elif self.is_closing_gateway(element=current):
            self.next_step_closing_gateway(gateway=current)

        else:
            self.next_step_no_gateway(element=current)
