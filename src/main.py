from src.examples.bill_process_example import BillProcessExample
from src.examples.gateway_example import GatewayExample
from src.graph_pointer import GraphPointer
from src.models.token import Token


def run_pointer(graph_pointer: GraphPointer, solution_token: Token):
    ret = graph_pointer.iterate_model()
    if ret[0] == 0:
        print('diagram processed correctly')
    else:
        print('possible infinite loop detected')

    # compare tokens
    return_token = ret[1]

    print(f'solution token: {solution_token}')
    print(f'students token: {return_token}')

    if return_token == solution_token:
        print('token equal: students solution is correct!\n')
    else:
        print('token not equal: business process is wrong\n')


if __name__ == '__main__':
    # >>> >>> >>>  B I L L   P R O C E S S   E X A M P L E  <<< <<< <<<
    print('\n>>> >>> >>>  B I L L   P R O C E S S   E X A M P L E  <<< <<< <<<')
    bill_example = BillProcessExample()
    bill_pointer = GraphPointer(model=bill_example.get_students_process(),
                                token=bill_example.get_init_token(),
                                ruleset=bill_example.get_ruleset(),
                                chunker=bill_example.get_chunker())
    bill_solution_token = bill_example.get_solution_token()
    run_pointer(graph_pointer=bill_pointer, solution_token=bill_solution_token)

    # >>> >>> >>> G A T E W A Y    E X A M P L E <<< <<< <<<
    print('\n >>> >>> >>> G A T E W A Y    E X A M P L E <<< <<< <<<')
    gateway_example = GatewayExample()
    gateway_pointer = GraphPointer(model=gateway_example.get_students_process(),
                                   token=gateway_example.get_init_token(),
                                   ruleset=gateway_example.get_ruleset(),
                                   chunker=gateway_example.get_chunker())
    gw_solution_token = gateway_example.get_solution_token()
    run_pointer(graph_pointer=gateway_pointer, solution_token=gw_solution_token)
