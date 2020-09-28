from typing import List

from src.examples.bill_process_example import BillProcessExample
from src.examples.gateway_example import GatewayExample
from src.graph_pointer import GraphPointer



def run_pointer(graph_pointer: GraphPointer):
    for i in range(100):
        ret = graph_pointer.iterate_model()
        if ret == 1:
            # compare tokens
            return_token = graph_pointer.token

            print(return_token)
            print(solution_token)

            if return_token == solution_token:
                print('token equal: students solution is correct!\n')
            else:
                print('token not equal: business process is wrong\n')

            break
        # max 100 steps
        i += 1

# >>> >>> >>>  B I L L   P R O C E S S   E X A M P L E  <<< <<< <<<
bill_example = BillProcessExample()
graph_pointer = GraphPointer(model=bill_example.get_students_process(),
                             token=bill_example.get_init_token(),
                             ruleset=bill_example.get_ruleset(),
                             chunker=bill_example.get_chunker())
solution_token = bill_example.get_solution_token()
run_pointer(graph_pointer=graph_pointer)



# >>> >>> >>> G A T E W A Y    E X A M P L E <<< <<< <<<
# gateway_example = GatewayExample()
# graph_pointer = GraphPointer(model=gateway_example.get_students_process(),
#                              token=gateway_example.get_init_token(),
#                              ruleset=gateway_example.get_ruleset(),
#                              chunker=gateway_example.get_chunker())
# solution_token = gateway_example.get_solution_token()
# run_pointer(graph_pointer=graph_pointer)
