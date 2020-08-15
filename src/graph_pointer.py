from igraph import Edge, Graph
from pedantic import pedantic, validate_args, \
    needs_refactoring, pedantic_class

# local file imports
from src.models.tokenstaterule import TokenStateRule
from src.models.token import Token
from src.models.graphtext import GraphText


@pedantic_class
class Graph_Pointer:
    """
    Graph_Pointer is the object that points to a
    single vertex in the BPMN-graph and reads its values
    to change the token attributes --> the tokens current
    state.
    """
    def __init__(self, graph:'Graph', token:'Token') -> None:
        self.graph = graph
        self.token = token
        self.__pointer = -1

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
        if self.__pointer < -1:
            raise RuntimeError(
                f'GraphPointer.__pointer {self.__pointer} '
                f'is set horribly wrong.')

        if self.__pointer == -1:
            # case: init, first call of runstep_graph
            # set pointer to first vertex of graph and
            # change the state of the token
            self.__set_start_vertex()
            self.__change_token_state()
            return 0

        # all other cases: decide what to to by outgoing edges
        edges_ids = self.graph.incident(self.__pointer, mode='OUT')

        # if there are no edges left, we are done
        if len(edges_ids) == 0:
            return 1

        # if there is one outgoing edge, set pointer to it
        # and change token state
        if len(edges_ids) == 1:
            # get the vertex the edge points to
            edge: Edge = self.graph.es[edges_ids[0]]
            vertex_id = edge.target

            self.change_pointer(vertex_id=vertex_id)
            self.__change_token_state()
            return 0

    def __set_start_vertex(self) -> None:
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
        if (incidence_list.count([])) != 1:
            raise RuntimeError(
                'ERROR: graph has multiple starting points')
        vertex_id = incidence_list.index([])

        # set inner pointer to starting vertex
        self.change_pointer(vertex_id=vertex_id)


    def change_pointer(self, vertex_id:int) -> None:
        """
        Changes the pointer to another vertex.
        Args:
            vertex_id (int): The ID of the vertex given by igraph-lib.
        """
        if vertex_id is None or vertex_id < 0:
            raise RuntimeError(
                'ERROR: vertex_id is invalid'
                '(None or smaller than 0')
        self.__pointer = vertex_id

    def __change_token_state(self) -> None:
        # we call this function whenever the pointer has
        # changed
        # Step 1: analyze the text
        # Step 2: change token state
        vertex = self.graph.vs[self.__pointer]
        vertex_text:GraphText = vertex['text']

        # make text analysis
        unterschrift = 'Unterschrift'
        ML = 'ML'
        if unterschrift in vertex_text and ML in vertex_text:
            # rule: Ort == Görlitz
            rule = TokenStateRule(tok_attribute='Ort',
                                  operator='=',
                                  tok_value='Görlitz')
            if rule.apply_rule(token=self.token):
                self.token.change_value(key='Unterschrift ML', value=True)
                return

        zittau = 'Zittau'
        schicken = 'schicken'
        if zittau in vertex_text and schicken in vertex_text:
            # no rules applied
            self.token.change_value(key='Ort', value=zittau)
            return

        vertragspruefung = 'Vertragsprüfung'
        if vertragspruefung in vertex_text:
            # rule: 'Ort' == 'Zittau'
            rule = TokenStateRule(tok_attribute='Ort',
                                  operator='=',
                                  tok_value='Zittau')
            if rule.apply_rule(token=self.token):
                self.token.change_value(key="Fachlich geprüft", value=True)
                return

        if unterschrift in vertex_text and \
                zittau in vertex_text:
                # rule: 'Ort' == 'Zittau' and
                # 'fachlich geprüft' = True
            rule1 = TokenStateRule(tok_attribute='Ort',
                                   operator='=',
                                   tok_value='Zittau')
            rule2 = TokenStateRule(tok_attribute='Fachlich geprüft',
                                   operator='=',
                                   tok_value=True)

            if rule1.apply_rule(token=self.token) and \
                    rule2.apply_rule(token=self.token):
                self.token.change_value\
                    (key='Unterschrift Zittau', value=True)
                return

        dresden = 'Dresden'
        if dresden in vertex_text and schicken in vertex_text:
            # no rule applied
            self.token.change_value(key='Ort', value=dresden)
            return

        goerlitz = 'Görlitz'
        if goerlitz in vertex_text and schicken in vertex_text:
            # no rule applied
            self.token.change_value(key='Ort', value=goerlitz)
            return



