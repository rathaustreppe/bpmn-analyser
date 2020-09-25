from typing import List, Union

from igraph import Graph
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
from src.exception.gateway_exception import ExclusiveGatewayBranchError
from src.exception.model_exception import MultipleStartEventsError, \
    NoStartEventError
from src.models.gateway_stack_handler import GatewayStackHandler
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
                 # graph: Graph,
                 token: Token,
                 ruleset: List[TokenStateRule],
                 chunker: Chunker,
                 model: BPMNModel) -> None:
        # self.graph = graph
        self.model = model
        self.token = token
        self.rule_finder = RuleFinder(chunker=chunker, ruleset=ruleset)
        # self.previous_element: igraph.Vertex = None
        self.previous_element: Union[BPMNGateway, BPMNActivity] = None
        self.stack_handler = GatewayStackHandler()

    def runstep_graph(self) -> int:
        """
        With each call, it iterates one step through the
        graph (= changes self.current and self.previous),
        analyses the text (= bpmn activity) and performs state transitions on token.
        Returns:
            int:
            1 if the end of the graph is reached
            0 if the the step was performed successfully but
            the end of the graph is not reached yet
        """
        if not self.reached_end_event():
            self._next_step()
            return 0
        else:
            return 1

    def reached_end_event(self) -> bool:
        if self.previous_element is None:
            return False

        # if self.previous_element[BPMNEnum.TYPE.value] == BPMNEndEvent.__name__:
        return isinstance(self.previous_element, BPMNEndEvent)

    def find_start_event(self) -> BPMNStartEvent:
        """
        Find the entry point of the graph from where
        the graph is read. Can only process directed graphs
        and only graphs with exactly one start vertex. We treat a vertex as
        start vertex if the vertex has no incident edges.
        """
        start = self.model.find_elements_by_type(type_to_find=BPMNStartEvent)
        if len(start) == 1:
            return start[0]
        elif len(start) == 0:
            raise NoStartEventError(model=self.model)
        else:
            raise MultipleStartEventsError(model=self.model)

    # def find_start_vertex(self) -> igraph.Vertex:
    #     """
    #     Find the entry point of the graph from where
    #     the graph is read. Can only process directed graphs
    #     and only graphs with exactly one start vertex. We treat a vertex as
    #     start vertex if the vertex has no incident edges.
    #     """
    #
    #     if not self.graph.is_directed():
    #         raise GraphNotDirectedError(graph=self.graph)
    #
    #     # get the incidence list of all vertices
    #     # if one and only one vertex has no incident edge,
    #     # it is the start vertex
    #     incidence_list = (self.graph.get_inclist(mode="IN"))
    #
    #     # now we got something like
    #     # >>> [[], [0], [1], [2], [3]]
    #     # and want to check that there is only one empty
    #     # list and we want to get the position of the list
    #     # because this is equal to the vertex_id (see
    #     # documentation of igraph.graph.get_inclist)
    #     if (incidence_list.count([])) == 0:
    #         raise GraphHasNoStartError(graph=self.graph)
    #
    #     elif (incidence_list.count([])) > 1:
    #         raise GraphHasMultipleStartsError(graph=self.graph)
    #
    #     else:
    #         vertex_id_in_graph = incidence_list.index([])
    #         return self.graph.vs[vertex_id_in_graph]

    def _text_analysis(self, activity: Union[
        BPMNActivity, BPMNStartEvent, BPMNEndEvent]) -> List[TokenStateRule]:
        """
        Applies NLP on BPMNActivity and finds all the rules where their SynonymCloud
        is synonym to the given vertex text.
        """
        matching_rules = self.rule_finder.find_rules(text=activity.name)

        print(f'TEXT: {activity.name}')
        print(f'MATCHING RULES: {matching_rules}')

        return matching_rules

    # def _text_analysis(self, vertex: igraph.Vertex) -> List[TokenStateRule]:
    #     """
    #     Applies NLP on vertex and finds all the rules where their SynonymCloud
    #     is synonym to the given vertex text.
    #     """
    #     vertex_text = vertex[BPMNEnum.NAME.value]
    #     matching_rules = self.rule_finder.find_rules(text=vertex_text)
    #
    #     print(f'TEXT: {vertex_text}')
    #     print(f'MATCHING RULES: {matching_rules}')
    #
    #     return matching_rules

    def _modify_token_with_rules(self,
                                 matching_rules: List[TokenStateRule]) -> Token:
        """
        We apply rules (==change token state), when their SynonymClouds are
        matching and their conditions are true.
        """
        for rule in matching_rules:
            self.token = rule.check_and_modify(token=self.token)
        return self.token

    # def is_previous_gateway(self) -> bool:
    #     gateway_texts = BPMNEnum.GATEWAY_TEXTS.value
    #     return self.previous_element[BPMNEnum.NAME.value] in gateway_texts

    def is_previous_gateway(self) -> bool:
        return isinstance(self.previous_element, BPMNGateway)

    def is_previous_activity(self) -> bool:
        return isinstance(self.previous_element, BPMNActivity)

    def is_previous_start_event(self) -> bool:
        return isinstance(self.previous_element, BPMNStartEvent)

    def find_current_element(self) -> Union[
        BPMNElement, BPMNGateway, BPMNActivity, BPMNStartEvent, BPMNEndEvent]:
        """
        Finds out what is meant to be the current element by looking back
        and checking the type of the previous element.
        """
        if self.previous_element is None:
            # has no previous_element means graph_pointer never started its
            # algorithm. So we new need to find the starting point.
            return self.find_start_event()

        elif self.is_previous_gateway():
            # If the previous element was a gateway we need to ask the stack. It
            # tells us with which branch of the gateway we should continue the
            # processing. This will be our new current element.
            return self.stack_handler.next_stack_element()

        elif self.is_previous_activity():
            # If it was an activity we dont invoke the stack. Every BPMNActivity
            # can have only one adjacent/following element. So we can find the
            # adjacent element by asking the BPMN-object. The adjacent element
            # of the previous element is therefore our new current element.
            return self.previous_element.sequence_flow_out.target

        elif self.is_previous_start_event():
            # same as BPMNActivity but different access on outgoing sequence_flows
            return self.previous_element.sequence_flow.target

        else:
            raise ValueError('not implmemented case')

    # def find_current_element(self) -> igraph.Vertex:
    #     """
    #     Finds out what is meant to be the current element by looking back
    #     and checking the type of the previous element.
    #     """
    #     if self.previous_element is None:
    #         # has no previous_element means graph_pointer never started its
    #         # algorithm. So we new need to find the starting point.
    #         return self.find_start_vertex()
    #
    #     elif self.is_previous_gateway():
    #         # If the previous element was a gateway we need to ask the stack. It
    #         # tells us with which branch of the gateway we should continue the
    #         # processing. This will be our new current element.
    #         return self.stack_handler.next_stack_element()
    #     else:
    #         # If it was an activity we dont invoke the stack. Every BPMNActivity
    #         # can have only one adjacent/following element. So we can find the
    #         # adjacent element by asking the graph library. The adjacent element
    #         # of the previous element is therefore our new current element.
    #         next_edges = self.previous_element.out_edges()
    #         if len(next_edges) == 1:
    #             return self.graph.vs[next_edges[0].target]

    def get_first_element_of_all_branches(self,
                                          branches: List[BPMNSequenceFlow]) -> \
    List[Union[BPMNActivity, BPMNGateway, BPMNElement]]:
        return [flow.target for flow in branches]

    # def get_first_vertex_of_all_branches(self, branches: List[igraph.Edge]) -> \
    # List[igraph.Vertex]:
    #     return [self.graph.vs[edge.target] for edge in branches]

    def get_condition_fulfilling_sequence_flows(self, flows_to_check: List[
        BPMNSequenceFlow]) -> List[BPMNSequenceFlow]:
        flows = []
        for flow in flows_to_check:
            if flow.condition is None or flow.condition.check_condition(
                    token=self.token):
                # we treat flows without conditions as fulfilled flows per default
                flows.append(flow)
        return flows

    # def get_condition_fulfilling_edges(self,
    #                                    edges_to_check: List[igraph.Edge]) -> \
    # List[igraph.Edge]:
    #     edges = []
    #     for edge in edges_to_check:
    #         if BPMNEnum.CONDITION.value in edge.attributes() and \
    #                 edge[BPMNEnum.CONDITION.value].check_condition(
    #                     token=self.token):
    #             edges.append(edge)
    #     return edges

    # @staticmethod
    # def is_gateway(gateway: igraph.Vertex) -> bool:
    #     gateway_types = [BPMNParallelGateway.__name__,
    #                      BPMNInclusiveGateway.__name__,
    #                      BPMNExclusiveGateway.__name__]
    #     return gateway[BPMNEnum.TYPE.value] in gateway_types

    def collect_conditional_sequence_flows_of_gateway(self, gateway: BPMNGateway) -> \
    List[BPMNSequenceFlow]:
        """
        Method that makes a distinction of different gateway types and returns
        the corresponding sequence_flows that fulfill the conditions.
        Parallel-Gateway: returns all sequence_flows
        Inclusive-Gateway: returns all sequence_flows that meet the condition
        Exclusive-Gateway: checks that only one sequence_flow fullfills the condition
        """
        flows = gateway.sequence_flows_out

        if isinstance(gateway, BPMNParallelGateway):
            return flows

        elif isinstance(gateway, BPMNInclusiveGateway):
            return self.get_condition_fulfilling_sequence_flows(
                flows_to_check=flows)

        elif isinstance(gateway, BPMNExclusiveGateway):
            cond_flows = self.get_condition_fulfilling_sequence_flows(
                flows_to_check=flows)
            if len(cond_flows) == 1:
                return cond_flows
            else:
                raise ExclusiveGatewayBranchError(gateway=gateway,
                                                  flows=flows)

    # def collect_conditional_edges_of_gateway(self, gateway: igraph.Vertex) -> \
    # List[igraph.Edge]:
    #     """
    #     Method that makes a distinction of different gateway types and returns
    #     the corresponding edges that fullfill the conditions.
    #     Parallel-Gateway: returns all edges
    #     Inclusive-Gateway: returns all edges that meet the condition
    #     Exclusive-Gateway: checks that only one edge fullfills the condition
    #     """
    #     if not self.is_gateway(gateway=gateway):
    #         raise WrongTypeException(object=gateway,
    #                                  expected='instance of BPMNGateway',
    #                                  given=gateway[BPMNEnum.TYPE.value])
    #     else:
    #         gateway_type = gateway[BPMNEnum.TYPE.value]
    #         edges = gateway.out_edges()
    #
    #         if gateway_type == BPMNParallelGateway.__name__:
    #             return edges
    #         elif gateway_type == BPMNInclusiveGateway.__name__:
    #             return self.get_condition_fulfilling_edges(edges_to_check=edges)
    #         elif gateway_type == BPMNExclusiveGateway.__name__:
    #             cond_edges = self.get_condition_fulfilling_edges(
    #                 edges_to_check=edges)
    #             if len(cond_edges) == 1:
    #                 return cond_edges
    #             else:
    #                 raise ExclusiveGatewayBranchError(gateway=gateway,
    #                                                   flows=cond_edges)

    def _next_step(self) -> None:
        """
        Single-Steps through the BPMNModel with each call. Deals with consecutively
        BPMNActivities and knows how to split at BPMNGateways. Uses a
        StackHandler to keep track of processed gateway branches.
        """
        current = self.find_current_element()

        if isinstance(current, BPMNGateway):
            # current is gateway:
            # Collect all the branches a gateway branches into it and check
            # their conditions. If they are true, we can branch into them.
            # All those BPMNElements that meet the condition will be put on the stack.
            # This way we make sure to process all branches.
            conditions_meet_flows = self.collect_conditional_sequence_flows_of_gateway(
                gateway=current)
            branch_elements = self.get_first_element_of_all_branches(
                branches=conditions_meet_flows)

            self.stack_handler.check_gateway_stack(gateway=current,
                                                   branch_elements=branch_elements)

        else:
            # current is no gateway, therefore perform text analysis &
            # rule checking & token changing
            matching_rules = self._text_analysis(activity=current)
            self._modify_token_with_rules(matching_rules=matching_rules)

        self.previous_element = current

    # def _next_step(self) -> None:
    #     """
    #     Single-Steps through the graph with each call. Deals with consecutively
    #     BPMNActivities and knows how to split at BPMNGateways. Uses a
    #     StackHandler to keep track of processed gateway branches.
    #     """
    #     gateway_texts = BPMNEnum.GATEWAY_TEXTS.value
    #
    #     current = self.find_current_element()
    #     current_name_tag = current[BPMNEnum.NAME.value]
    #
    #     if current_name_tag in gateway_texts:
    #         # current is gateway
    #         # Collect all the branches a gateway branches into it and check
    #         # their conditions. If they are true, we can branch into them.
    #         # All those edges that meet the condition will be put on the stack.
    #         # This way we make sure to process all branches.
    #         conditions_meet_edges = self.collect_conditional_edges_of_gateway(
    #             gateway=current)
    #
    #         branch_vertices = self.get_first_vertex_of_all_branches(
    #             branches=conditions_meet_edges)
    #
    #         self.stack_handler.check_gateway_stack(gateway=current,
    #                                                branch_vertices=branch_vertices)
    #     else:
    #         # current is no gateway, therefore perform text analysis &
    #         # rule checking & token changing
    #         matching_rules = self._text_analysis(vertex=current)
    #         self._modify_token_with_rules(matching_rules=matching_rules)
    #
    #     self.previous_element = current
