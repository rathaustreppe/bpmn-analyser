import igraph as ig
from igraph import Edge

from classes.token_state_rule import Token_State_Rule
from classes.token import Token
from classes.graph_text import Graph_Text

# Graph_Pointer is the object that points to a
# single vertex in the BPMN-graph and reads its values
# to change the token attributes --> the tokens current
# state.
class Graph_Pointer:

    def __init__(self, graph:ig.Graph, token:Token):
        self.graph = graph
        self.token = token
        self.__pointer = -1

    def runstep_graph(self):
        # goes through the graph and changes token state
        # call it multiple times. First time calling it will
        # put the pointer to the start of the graph
        if self.__pointer == -1:
            self.__set_start_verticy()
            return 0

        # all outgoing edges from vertex pointed by __pointer
        edges_ids = self.graph.incident(self.__pointer, mode='OUT')

        # if there are no edges left, return 2
        if len(edges_ids) == 0:
            return 2

        # if vertex the pointer points to has one
        # outgoing edge:
        if len(edges_ids) == 1:
            # get the vertex the edge points to and set
            # the pointer
            edge: Edge = self.graph.es[edges_ids[0]]
            vertex_id = edge.target
            self.change_pointer(vertex_id)
            return 1


    def __set_start_verticy(self):
        # define the entry point of the graph from where
        # the graph is read
        # can only process directed graphs
        if not self.graph.is_directed():
            print("ERROR: graph is not directed")
            return -1

        # get the incidence list of all verteces
        # if one and only one vertices has no incident edge,
        # it is the start vertex
        inclist = (self.graph.get_inclist(mode="IN"))

        # check for only one empty list and return index
        # position of it
        starting_points = []
        for idx, list in enumerate(inclist, start=0):
            if len(list) == 0:
                starting_points.append(idx)
            else:
                continue

        if len(starting_points) != 1:
            print("ERROR: graph has multiple "
                  "starting points")
            return -1
        else:
            self.change_pointer(starting_points[0])


    def change_pointer(self, vertex_id):
        if vertex_id is None:
            print('ERROR: vertex id is none!')
            return -1
        else:
            self.__pointer = vertex_id
            # the pointer has changed. So we now change the
            # token state according to the content of the vertex
            self.__change_token_state()

    def __change_token_state(self):
        # we call this function whenever the pointer has
        # changed
        # Step 1: analyze the text
        # Step 2: change token state
        vertex = self.graph.vs[self.__pointer]
        vertex_text:Graph_Text = vertex['text']

        # make text analysis
        unterschrift = 'Unterschrift'
        ML = 'ML'
        if unterschrift in vertex_text and ML in vertex_text:
            # rule: Ort == Görlitz
            rule = Token_State_Rule(tok_attribute='Ort', operator='=',
                                    tok_value='Görlitz')
            if rule.apply_rule(t=self.token):
                self.token.change_value('Unterschrift ML', True)
                return

        zittau = 'Zittau'
        schicken = 'schicken'
        if zittau in vertex_text and schicken in vertex_text:
            # no rules applied
            self.token.change_value('Ort', zittau)
            return

        vertragspruefung = 'Vertragsprüfung'
        if vertragspruefung in vertex_text:
            # rule: 'Ort' == 'Zittau'
            rule = Token_State_Rule(tok_attribute='Ort', operator='=',
                                    tok_value='Zittau')
            if rule.apply_rule(t=self.token):
                self.token.change_value("Fachlich geprüft", True)
                return

        if unterschrift in vertex_text and \
                zittau in vertex_text:
                # rule: 'Ort' == 'Zittau' and
                # 'fachlich geprüft' = True
            rule1 = Token_State_Rule(tok_attribute='Ort',
                                     operator='=',
                                     tok_value='Zittau')
            rule2 = Token_State_Rule(tok_attribute='Fachlich geprüft',
                                     operator='=',
                                     tok_value=True)

            if rule1.apply_rule(self.token) and \
                    rule2.apply_rule(self.token):
                self.token.change_value\
                    ('Unterschrift Zittau', True)
                return

        dresden = 'Dresden'
        if dresden in vertex_text and schicken in vertex_text:
            # no rule applied
            self.token.change_value('Ort', dresden)
            return

        goerlitz = 'Görlitz'
        if goerlitz in vertex_text and schicken in vertex_text:
            # no rule applied
            self.token.change_value('Ort', goerlitz)
            return



