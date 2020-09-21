from typing import List

import igraph
from igraph import Graph
from pedantic import pedantic_class

from src.converter.bpmn_models.bpmn_enum import BPMNEnum
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

    def __init__(self, graph: Graph,
                 token: Token,
                 ruleset: List[TokenStateRule],
                 chunker: Chunker) -> None:
        self.graph = graph
        self.token = token
        self.rule_finder = RuleFinder(chunker=chunker, ruleset=ruleset)
        self.previous_element: igraph.Vertex = None
        self.current: igraph.Vertex = None
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

        if self.previous_element is None:
            # case: init, first call of runstep_graph
            # We know it must be a BPMNStartEvent (otherwise contradicting
            # BPMNSpecification) so we can perform text analysis on it.
            self.current = self.__find_start_vertex()
            matching_rules = self._text_analysis(vertex=self.current)
            self._modify_token_with_rules(matching_rules=matching_rules)
            self.previous_element = self.current
            return 0
        else:
            # if previous element was a endEvent, we reached the end of the graph
            # endEvents are the only BPMN-Element with no outgoing edges
            # (compare to activities, gateways and startEvents)
            if len(self.previous_element.out_edges()) != 0:
                self._next_step()
                return 0
            else:
                return 1



    def __find_start_vertex(self) -> igraph.Vertex:
        """
        Find the entry point of the graph from where
        the graph is read. Can only process directed graphs
        and only graphs with exactly one start vertex. We treat a vertex as
        start vertex if the vertex has no incident edges.
        """

        # cannot find a start of a non-directed graph
        if not self.graph.is_directed():
            raise RuntimeError('ERROR: graph is not directed')

        # get the incidence list of all vertices
        # if one and only one vertex has no incident edge,
        # it is the start vertex
        incidence_list = (self.graph.get_inclist(mode="IN"))

        # now we got something like
        # >>> [[], [0], [1], [2], [3]]
        # and want to check that there is only one empty
        # list and we want to get the position of the list
        # because this is equal to the vertex_id (see
        # documentation of igraph.graph.get_inclist)
        if (incidence_list.count([])) == 0:
            raise RuntimeError('ERROR: graph has no starting point')

        elif (incidence_list.count([])) > 1:
            raise RuntimeError('ERROR: graph has multiple starting points')

        else:
            vertex_id_in_graph = incidence_list.index([])
            return self.graph.vs[vertex_id_in_graph]


    def _text_analysis(self, vertex: igraph.Vertex) -> List[TokenStateRule]:
        """
        Applies NLP on vertex and finds all the rules where their SynonymCloud
        is synonym to the given vertex text.
        """
        vertex_text = vertex[BPMNEnum.NAME.value]
        matching_rules = self.rule_finder.find_rules(text=vertex_text)

        print(f'TEXT: {vertex_text}')
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

    def find_current_element(self) -> igraph.Vertex:
        # We find out what is meant to be the current element by looking back
        # and checking the type of the previous element.
        # If it was an activity we dont invoke the stack. Every BPMNActivity
        # can have only one adjacent/following element. So we can find the
        # adjacent element by asking the graph library. The adjacent element
        # of the previous element is therefore our new current element.
        # If the previous element was a gateway we need to ask the stack. It
        # tells us with which branch of the gateway we should continue the
        # processing. This will be our new current element.
        gateway_texts = BPMNEnum.GATEWAY_TEXTS.value

        if self.previous_element[BPMNEnum.NAME.value] in gateway_texts:
            return self.stack_handler.next_stack_element()
        else:
            # previous_element was activity or startEvent
            next_edges = self.previous_element.out_edges()
            if len(next_edges) == 1:
                return self.graph.vs[next_edges[0].target]

    def get_first_vertex_of_all_branches(self, branches:List[igraph.Edge]):
        return [self.graph.vs[edge.target] for edge in branches]

    def _next_step(self) -> None:
        """
        Single-Steps through the graph with each call. Deals with consecutively
        BPMNActivities and knows how to split at BPMNGateways. Uses a
        StackHandler to keep track of processed gateway branches.
        """
        gateway_texts = BPMNEnum.GATEWAY_TEXTS.value

        current = self.find_current_element()

        if current[BPMNEnum.NAME.value] in gateway_texts:
            # current is gateway
            # Collect all the branches a gateway branches into it and check
            # their conditions. If they are true, we can branch into them.
            # All those edges that meet the condition will be put on the stack.
            # This way we make sure to process all branches.
            outgoing_edges = current.out_edges()
            conditions_meet_edges = [edge for edge in outgoing_edges
                                     if edge[BPMNEnum.CONDITION.value].
                                         check_condition(token=self.token)]

            branch_vertices = self.get_first_vertex_of_all_branches(
                branches=conditions_meet_edges)

            self.stack_handler.check_gateway_stack(gateway=current,
                                                   branch_vertices=branch_vertices)
        else:
            # current is no gateway, therefore perform text analysis &
            # rule checking & token changing
            matching_rules = self._text_analysis(vertex=current)
            self._modify_token_with_rules(matching_rules=matching_rules)

        self.previous_element = current

