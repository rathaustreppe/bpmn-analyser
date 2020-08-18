from typing import List

from src.converter.converter import Converter
from src.graph_pointer import GraphPointer
from src.models.token import Token


# solution token
init_attributes = {
    "Ort": "Dresden",
    "Unterschrift ML": True,
    "Unterschrift Zittau": True,
    "Fachlich geprüft": True
}
solution_token = Token(attributes=init_attributes)


# Graph from *.bpmn-file
path_to_xml = r'..\src\converter\bpmn-files\3-correct.bpmn'

converter = Converter()
g = converter.convert(rel_path_to_bpmn=path_to_xml)


init_attributes = {
    "Ort": "Zittau",
    "Unterschrift ML": False,
    "Unterschrift Zittau": False,
    "Fachlich geprüft": False
}
t = Token(attributes=init_attributes)
gp = GraphPointer(graph=g, token=t)


# running all graphs
graph_pointer_list: List[GraphPointer]= [gp]

for graph_pointer in graph_pointer_list:
    for i in range(100):
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
        # max 100 steps
        i += 1