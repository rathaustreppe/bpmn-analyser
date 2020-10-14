import glob
import os

from src.converter.converter import Converter
from src.examples.field_trial.sample_solution import SampleSolution
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
    # Execute this main.py to analyze several files in a folder and get a
    # formatted output.
    converter = Converter()

    # tell the program where all the *.bpmn-files are:
    abs_folder_path = r'.....................\files'


    file_mask = r'*.bpmn'

    # runs through all the files
    for filepath in glob.glob(os.path.join(abs_folder_path, file_mask)):
        print(f'\n>>> >>> >>> {os.path.basename(filepath)}<<< <<< <<<')
        try:
            students_bpmn_model = converter.convert(abs_file_path=filepath)
            sample_solution = SampleSolution()

            students_graphpointer = GraphPointer(model=students_bpmn_model,
                                                 token=sample_solution.get_init_token(),
                                                 ruleset=sample_solution.get_ruleset(),
                                                 chunker=sample_solution.get_chunker())
            sample_solution_token = sample_solution.get_solution_token()
            run_pointer(graph_pointer=students_graphpointer, solution_token=sample_solution_token)
        except Exception as e:
            print(f'while processing an error occurred: \n {e}')
            print(f'{students_graphpointer.token}')
            continue
