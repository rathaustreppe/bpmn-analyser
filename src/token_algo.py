from typing import List

import igraph as ig

# local file imports
from src.converter.bpmn_models.bpmn_enum import BPMNEnum
from src.converter.converter import Converter
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
solution_token = Token(attributes=init_attributes)


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

g.vs[0][BPMNEnum.NAME.value] = GraphText(text="ML Unterschrift")
g.vs[1][BPMNEnum.NAME.value] = GraphText(text="Nach Zittau schicken")
g.vs[2][BPMNEnum.NAME.value] = GraphText(text='Vertragsprüfung')
g.vs[3][BPMNEnum.NAME.value] = GraphText(text='Zittau Unterschrift')
g.vs[4][BPMNEnum.NAME.value] = GraphText(text='Nach Dresden schicken')

gp = Graph_Pointer(graph=g,token=t)
#ig.Graph.write_svg(g, "printed_graph.svg", labels=BPMNEnum.NAME.value)


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

g2.vs[0][BPMNEnum.NAME.value] = 'Vertragsprüfung'
g2.vs[1][BPMNEnum.NAME.value] = 'Zittau Unterschrift'
g2.vs[2][BPMNEnum.NAME.value] = "Nach Görlitz schicken"
g2.vs[3][BPMNEnum.NAME.value] = "ML Unterschrift"
g2.vs[4][BPMNEnum.NAME.value] = 'Nach Dresden schicken'


# GraphPointer
gp2 = Graph_Pointer(graph=g2,token=t2)


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

g3.vs[0][BPMNEnum.NAME.value] = 'Vertragsprüfung'
g3.vs[1][BPMNEnum.NAME.value] = 'Zittau Unterschrift'
g3.vs[2][BPMNEnum.NAME.value] = "Nach Görlitz schicken"
g3.vs[3][BPMNEnum.NAME.value] = "ML Unterschrift"
g3.vs[4][BPMNEnum.NAME.value] = "Nach Zittau schicken"
g3.vs[5][BPMNEnum.NAME.value] = 'Nach Dresden schicken'


# GraphPointer
gp3 = Graph_Pointer(graph=g3,token=t3)

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

g4.vs[0][BPMNEnum.NAME.value] = 'Vertragsprüfung'
g4.vs[1][BPMNEnum.NAME.value] = 'Zittau Unterschrift'
g4.vs[2][BPMNEnum.NAME.value] = 'ML Unterschrift'
g4.vs[3][BPMNEnum.NAME.value] = 'Nach Dresden schicken'


# GraphPointer
gp4 = Graph_Pointer(graph=g4,token=t4)


# Graph from *.bpmn-file
path_to_xml = r'..\src\converter\bpmn-files\3-correct.bpmn'

converter = Converter()
g5 = converter.convert(path_to_bpmn=path_to_xml)


init_attributes = {
    "Ort": "Zittau",
    "Unterschrift ML": False,
    "Unterschrift Zittau": False,
    "Fachlich geprüft": False
}
t5 = Token(attributes=init_attributes)
gp5 = Graph_Pointer(graph=g5,token=t5)


# running all graphs
graph_pointer_list: List[Graph_Pointer]= []
graph_pointer_list.extend((gp,gp2,gp3,gp4,gp5))

for graph_pointer in graph_pointer_list:
    while (True):
        # max 1000 steps, otherwise loop
        ret = graph_pointer.runstep_graph()
        if ret == 1:
            # comparing tokens
            return_token = graph_pointer.get_token()

            print(return_token)
            print(solution_token)

            if return_token == solution_token:
                print('token equal: very nice!\n')
            else:
                print('business process is wrong\n')

            break