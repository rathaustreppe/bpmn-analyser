import glob
import logging
import os
import traceback

from src.converter.converter import Converter
from src.examples.field_trial.task2_solution import Task2Solution
from src.graph_pointer import GraphPointer
from src.models.token import Token
from src.util.logger.logging_config import setup_logger_config


def run_pointer(graph_pointer: GraphPointer, solution_token: Token):
    ret = graph_pointer.iterate_model()
    if ret[0] == 0:
        logging.info('diagram processed correctly')
    else:
        logging.info('possible infinite loop detected')

    # compare tokens
    return_token = ret[1]

    logging.info(f'solution token: {solution_token}')
    logging.info(f'students token: {return_token}')

    if return_token == solution_token:
        logging.info('token equal: students solution is correct!')
    else:
        logging.info('token not equal: business process is wrong')


if __name__ == '__main__':
    setup_logger_config()

    # Execute this main.py to analyze several files in a folder and get a
    # formatted output.
    converter = Converter()

    # tell the program where all the *.bpmn-files are:
    rel_folder_path = r'../test/first_field_trial'
    abs_folder_path = os.path.abspath(rel_folder_path)

    file_mask = r'*.bpmn'

    # make solution object for task 2
    task2 = Task2Solution()

    # container for all 5 task solutions and their subfolder-names
    tasks_to_check = [(task2, 'U2')]

    # run through all tasks
    for task, task_folder_name in tasks_to_check:
        task_folder_path = os.path.join(abs_folder_path, task_folder_name)
        # runs through all the files
        for filepath in glob.glob(os.path.join(task_folder_path, file_mask)):
            logging.debug(f'>>> >>> >>> {os.path.basename(filepath)}<<< <<< <<<')
            try:
                students_bpmn_model = converter.convert(abs_file_path=filepath)

                students_graphpointer = GraphPointer(model=students_bpmn_model,
                                                     token=task.get_init_token(),
                                                     ruleset=task.get_ruleset(),
                                                     chunker=task.get_chunker())
                solution_token = task.get_solution_token()
                run_pointer(graph_pointer=students_graphpointer, solution_token=solution_token)
                logging.info(f'went trough diagram {os.path.basename(filepath)}\n')
            except Exception as e:
                logging.error(traceback.format_exc())
                logging.debug(f'Final token state: {students_graphpointer.token}\n')
                continue
