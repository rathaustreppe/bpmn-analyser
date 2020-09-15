import os

from src.converter.converter import Converter
from src.graph_pointer import GraphPointer
from src.models.token import Token


class TestIntegration:

    def run_pointer(self,
                    graph_pointer: GraphPointer) -> Token:
        for i in range(100):
            ret = graph_pointer.runstep_graph()
            if ret == 1:
                return graph_pointer.get_token()
            i += 1
        # if graph_pointer does not hold after 100 steps
        return Token(attributes=None)

    def test_bill_process(self, xml_folders_path,
                          bill_process_chunker,
                          bill_process_ruleset,
                          bill_process_init_token,
                          bill_process_solution_token):

        xml_file_path = os.path.join(xml_folders_path,
                                     'bill_process_no_def.bpmn')

        converter = Converter()
        graph = converter.convert(rel_path_to_bpmn=xml_file_path)

        graph_pointer = GraphPointer(graph=graph, token=bill_process_init_token,
                                     ruleset=bill_process_ruleset,
                                     chunker=bill_process_chunker)

        return_token = self.run_pointer(graph_pointer=graph_pointer)
        assert return_token == bill_process_solution_token
