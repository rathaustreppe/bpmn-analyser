from typing import List

from src.examples.bill_process_example import BillProcessExample
from src.examples.gateway_example import GatewayExample
from src.graph_pointer import GraphPointer
from src.models.token import Token


def run_pointer(graph_pointer: GraphPointer, solution_token: Token):
    for i in range(100):
        ret = graph_pointer.iterate_model()
        print(f'stepped {i}x')
        if ret == 1:
            # compare tokens
            return_token = graph_pointer.token

            print(f'solution token: {solution_token}')
            print(f'students token: {return_token}')

            if return_token == solution_token:
                print('token equal: students solution is correct!\n')
            else:
                print('token not equal: business process is wrong\n')

            break

# >>> >>> >>>  B I L L   P R O C E S S   E X A M P L E  <<< <<< <<<
print('\n>>> >>> >>>  B I L L   P R O C E S S   E X A M P L E  <<< <<< <<<')
bill_example = BillProcessExample()
bill_pointer = GraphPointer(model=bill_example.get_students_process(),
                             token=bill_example.get_init_token(),
                             ruleset=bill_example.get_ruleset(),
                             chunker=bill_example.get_chunker())
solution_token = bill_example.get_solution_token()
run_pointer(graph_pointer=bill_pointer, solution_token=solution_token)



# >>> >>> >>> G A T E W A Y    E X A M P L E <<< <<< <<<
print('\n >>> >>> >>> G A T E W A Y    E X A M P L E <<< <<< <<<')
gateway_example = GatewayExample()
gateway_pointer = GraphPointer(model=gateway_example.get_students_process(),
                             token=gateway_example.get_init_token(),
                             ruleset=gateway_example.get_ruleset(),
                             chunker=gateway_example.get_chunker())
solution_token = gateway_example.get_solution_token()
run_pointer(graph_pointer=gateway_pointer, solution_token=solution_token)
