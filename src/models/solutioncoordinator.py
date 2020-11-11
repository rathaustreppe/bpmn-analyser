import glob
import logging
import os
import traceback

from pedantic import pedantic_class

from src.converter.converter import Converter
from src.graph_pointer import GraphPointer
from src.models.i_solution import ISolution
from src.models.token import Token


@pedantic_class
class SolutionCoordinator():
    """
    A class that knows the location of students diagrams and
    the sample solution. It applies the sample solution (and its scenarios)
    on all of the students diagrams by instantiating GraphPointer-objects and
    using them.
    Because it knows only one sample solution it is used only to check students
    diagrams of a single task. Instantiate multiple objects to check
    multiple diagrams.
    """
    def __init__(self, folder_path: str, sample_solution: ISolution) -> None:

        if not os.path.isabs(folder_path):
            folder_path = os.path.abspath(folder_path)

        self.abs_folder_path = folder_path
        self.file_mask = r'*.bpmn' # only bpmn-files
        self.sample_solution = sample_solution

    def run_all_solution_checking(self) -> None:
        """
        Main entry point to check a folder of diagrams.
        """
        converter = Converter()

        files_path = os.path.join(self.abs_folder_path, self.file_mask)

        for filepath in glob.glob(files_path):
            # run through all files
            logging.debug(f'>>> >>> >>> {os.path.basename(filepath)}<<< <<< <<<')
            students_bpmn_model = None
            try:
                students_bpmn_model = converter.convert(abs_file_path=filepath)
            except Exception:
                logging.error(traceback.format_exc())
                logging.debug('failure in converting BPMNModel\n')
                continue #with next file

            scenarios = self.sample_solution.get_scenarios()
            ruleset = self.sample_solution.get_ruleset()
            chunker = self.sample_solution.get_chunker()

            for scenario in scenarios:
                running_token = scenario.running_token
                students_graphpointer = GraphPointer(model=students_bpmn_model,
                                                 token=running_token,
                                                 ruleset=ruleset,
                                                 chunker=chunker)
                logging.debug(f'starting scenario {scenario.description}')
                self.check_solution(graph_pointer=students_graphpointer,
                                    expected_token=scenario.expected_token)
                logging.info(f'went trough scenario <{scenario}>\n')


    def check_solution(self, graph_pointer: GraphPointer,
                       expected_token: Token) -> None:
        """
        Steps through the graph_pointer.
        """
        ret = graph_pointer.iterate_model()
        if ret[0] == 0:
            logging.info('diagram processed correctly')
        else:
            logging.info('possible infinite loop detected')

        # compare tokens
        return_token = ret[1]

        logging.info(f'solution token: {expected_token}')
        logging.info(f'students token: {return_token}')

        if return_token == expected_token:
            logging.info('token equal: students solution is correct!')
        else:
            logging.info('token not equal: business process is wrong')