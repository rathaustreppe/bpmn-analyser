from typing import List

import igraph
from igraph import Graph
from pedantic import pedantic_class

from src.converter.bpmn_models.bpmn_activity import BPMNActivity
from src.converter.bpmn_models.bpmn_enum import BPMNEnum
from src.converter.bpmn_models.gateway.bpmn_gateway import BPMNGateway
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
    state.
    """

    def __init__(self, graph: Graph,
                 token: Token,
                 ruleset: List[TokenStateRule],
                 chunker: Chunker) -> None:
        self.graph = graph
        self.token = token
        self.rule_finder = RuleFinder(chunker=chunker, ruleset=ruleset)
        self.previous_element: igraph.Vertex = None
        self.current: igraph.Vertex = None
        self.stackhandler = GatewayStackHandler()

    def get_token(self) -> Token:
        return self.token

    def runstep_graph(self) -> int:
        """
        With each call, it iterates one step through the
        graph (= changes pointer), analyses the text (= bpmn
        activity) and performs state transitions on token.
        Returns:
            int:
            1 if the end of the graph is reached
            0 if the the step was performed successfully but
            the end of the graph is not reached yet
        """

        if self.previous_element is None:
            # case: init, first call of runstep_graph
            # We know it must be a BPMNStartEvent (otherwise contradicting
            # BPMNSpecification) so we can perform text analysis on it.
            # ToDo: implement text analysis on start-and endevents
            self.current = self.__find_start_vertex()
            # matching_rules = self._text_analysis(current=self.current)
            # self._modify_token_with_rules(matching_rules=matching_rules)
            self.previous_element = self.current
        else:
            self._next_step()

        # if current element is a endEvent, we reached the end of the graph
        # endEvents are the only BPMN-Element with no outgoing edges
        # (compare to activities, gateways and startEvents)
        return 1 if len(self.current.out_edges()) == 0 else 0

    def __find_start_vertex(self) -> igraph.Vertex:
        """
        Define the entry point of the graph from where
        the graph is read. Can only process directed graphs
        and only graphs with one start vertex.
        Start vertex have no prior (incident) vertex.
        Returns: None, but changes inner pointer of GraphPointer

        """
        if not self.graph.is_directed():
            raise RuntimeError(
                'ERROR: graph is not directed')

        # get the incidence list of all verticies
        # if one and only one vertices has no incident edge,
        # it is the start vertex
        incidence_list = (self.graph.get_inclist(mode="IN"))

        # now we got something like
        # >>> [[], [0], [1], [2], [3]]
        # and want to check that there is only one empty
        # list and we want to get the position of the list
        # because this is equal to the vertex_id (see
        # documentation of igraph.graph.get_inclist)
        if (incidence_list.count([])) == 0:
            raise RuntimeError(
                'ERROR: graph has no starting point')

        if (incidence_list.count([])) > 1:
            raise RuntimeError(
                'ERROR: graph has multiple starting points')

        vertex_id_in_graph = incidence_list.index([])

        # treat this vertex as current vertex
        return self.graph.vs[vertex_id_in_graph]


    def _text_analysis(self, current: igraph.Vertex) -> List[TokenStateRule]:
        # analyzes text and updates token
        vertex_text = current[BPMNEnum.NAME.value]

        # no handling of start and end events implemented yet, skip them by
        # finding no rule per default
        if vertex_text == 'startendevent':
            return []

        matching_rules = self.rule_finder.find_rules(text=vertex_text)

        print(f'TEXT: {vertex_text}')
        print(f'MATCHING RULES: {matching_rules}')

        return matching_rules

    def _modify_token_with_rules(self,
                                 matching_rules: List[TokenStateRule]) -> Token:
        # we apply rules (==change token state), when their synonymclouds are
        # matching and their conditions are true
        for rule in matching_rules:
            self.token = rule.check_and_modify(token=self.token)
        return self.token

    def _next_step(self) -> None:
        gateway_texts = [BPMNEnum.PARALLGATEWAY_TEXT.value,
                         BPMNEnum.EXCLGATEWAY_TEXT.value,
                         BPMNEnum.INCLGATEWAY_TEXT.value]
        if self.previous_element[BPMNEnum.NAME.value] in gateway_texts:
            # previous_element was gateway
            self.current = self.stackhandler.next_stack_element()

        else:
            # previous_element was activity or startEvent
            next_edges = self.previous_element.out_edges()
            if len(next_edges) == 1:
                self.current = self.graph.vs[next_edges[0].target]

        # check current type
        if self.current[BPMNEnum.NAME.value] in gateway_texts:
            # current is gateway
            # collect branch_vertices and check their conditions
            outgoing_edges = self.current.out_edges()
            conditions_meet_edges = []
            for edge in outgoing_edges:
                if edge[BPMNEnum.CONDITION.value].check_condition(
                        token=self.token):
                    conditions_meet_edges.append(edge)

            # get first vertex of edges
            branch_vertices = [self.graph.vs[edge.target] for edge in conditions_meet_edges]

            # tell stackhandler to modify stack according to gateway
            self.stackhandler.check_gateway_stack(gateway=self.current,
                                                  branch_vertices=branch_vertices)
        else:
            # current is no gateway --> is activity
            # text analysis & rule checking & token changing
            matching_rules = self._text_analysis(current=self.current)
            self._modify_token_with_rules(matching_rules=matching_rules)

        self.previous_element = self.current

