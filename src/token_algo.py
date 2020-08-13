from typing import List

import igraph as ig

# local file imports
from src.models.graphtext import GraphText
from src.graph_pointer import Graph_Pointer
from src.models.token import Token


# solution token
init_attributes = {
    "Ort": "Dresden",
    "Unterschrift ML": True,
    "Unterschrift Zittau": True,
    "Fachlich geprüft": True
}
sol_t = Token(attributes=init_attributes)


# Graph 1:
# ML Unterschrift -> nach Zittau -> Vertragsprüfung ->
# Unterschrift Zittau -> nach Dresden
# ==> funktioniert

#  g1
init_attributes = {
    "Ort": "Görlitz",
    "Unterschrift ML": False,
    "Unterschrift Zittau": False,
    "Fachlich geprüft": False
}
t = Token(attributes=init_attributes)

# Graph Nr 1: business process works
g = ig.Graph()
g = g.as_directed()

g.add_vertices(5)
g.add_edges([(0,1), (1,2), (2,3), (3,4)])

g.vs[0]["text"] = GraphText(text="ML Unterschrift")
g.vs[1]["text"] = GraphText(text="Nach Zittau schicken")
g.vs[2]['text'] = GraphText(text='Vertragsprüfung')
g.vs[3]['text'] = GraphText(text='Zittau Unterschrift')
g.vs[4]['text'] = GraphText(text='Nach Dresden schicken')

gp = Graph_Pointer(g,t)
ig.Graph.write_svg(g, "printed_graph.svg", labels="text")

# at this point we know the starting point of the graph
# so now change the state of the token
while(True):
    ret = gp.runstep_graph()
    print('Graph-Runstep:', ret)
    if ret == 2:
        break


# Graph 2:
# Vertragsprüfung -> Zittau Unterschrift -> Nach Görlitz ->
# ML Unterschrift -> nach Dresden
# ==> funktioniert


# Token g2
init_attributes = {
    "Ort": "Zittau",
    "Unterschrift ML": False,
    "Unterschrift Zittau": False,
    "Fachlich geprüft": False
}

t2 = Token(attributes=init_attributes)
# Graph Nr 2: business process works
g2 = ig.Graph()
g2 = g2.as_directed()
g2.add_vertices(5)
g2.add_edges([(0,1), (1,2), (2,3), (3,4)])

g2.vs[0]['text'] = 'Vertragsprüfung'
g2.vs[1]['text'] = 'Zittau Unterschrift'
g2.vs[2]["text"] = "Nach Görlitz schicken"
g2.vs[3]["text"] = "ML Unterschrift"
g2.vs[4]['text'] = 'Nach Dresden schicken'


# GraphPointer
gp2 = Graph_Pointer(g2,t2)

while(True):
    ret = gp2.runstep_graph()
    print('Graph-Runstep:', ret)
    if ret == 2:
        break


init_attributes = {
    "Ort": "Zittau",
    "Unterschrift ML": False,
    "Unterschrift Zittau": False,
    "Fachlich geprüft": False
}

t3 = Token(attributes=init_attributes)
# Graph Nr 3: business process works. Sending back to Zittau
g3 = ig.Graph()
g3 = g3.as_directed()
g3.add_vertices(6)
g3.add_edges([(0,1), (1,2), (2,3), (3,4),(4,5)])

g3.vs[0]['text'] = 'Vertragsprüfung'
g3.vs[1]['text'] = 'Zittau Unterschrift'
g3.vs[2]["text"] = "Nach Görlitz schicken"
g3.vs[3]["text"] = "ML Unterschrift"
g3.vs[4]["text"] = "Nach Zittau schicken"
g3.vs[5]['text'] = 'Nach Dresden schicken'


# GraphPointer
gp3 = Graph_Pointer(g3,t3)

while(True):
    ret = gp3.runstep_graph()
    print('Graph-Runstep:', ret)
    if ret == 2:
        break

init_attributes = {
    "Ort": "Zittau",
    "Unterschrift ML": False,
    "Unterschrift Zittau": False,
    "Fachlich geprüft": False
}

t4 = Token(attributes=init_attributes)
# Graph Nr 4: ML Unterschrift in Zittau
g4 = ig.Graph()
g4 = g4.as_directed()
g4.add_vertices(4)
g4.add_edges([(0,1), (1,2), (2,3)])

g4.vs[0]['text'] = 'Vertragsprüfung'
g4.vs[1]['text'] = 'Zittau Unterschrift'
g4.vs[2]['text'] = 'ML Unterschrift'
g4.vs[3]['text'] = 'Nach Dresden schicken'


# GraphPointer
gp4 = Graph_Pointer(g4,t4)

while(True):
    ret = gp4.runstep_graph()
    print('Graph-Runstep:', ret)
    if ret == 2:
        break


#
# # Token Comparisons
token_list: List[Token] = [t, t2, t3, t4]
for tok in token_list:
    print(tok)
    print(sol_t)
    if sol_t == tok:
        print('token equal: very nice!')
    else:
        print('business process is wrong')
#
# # ToDo: Tests entwickeln für alle Methoden
# # ToDo: Tests für fehlgeschlagene Business Processes entwickeln
# # ToDo: Text-Analyse-Funktionen überarbeiten
# # ToDo: BPMN-Einlesefunktion entwickeln
# # ToDo: Parallele Tokens entwickeln
# # ToDo: Start-und Ende des Diagramms entwickeln
#
# # test tests
# g3 = ig.Graph()
# g3 = g3.as_directed()
#
# g3.add_vertices(2)
# g3.add_edges([(0,1)])
#
# gt = GraphText("ML Unterschrift Graph-Text")
#
# g3.vs[0]["text"] = gt
#
# print(g3.vs[0]["text"].get_text())
