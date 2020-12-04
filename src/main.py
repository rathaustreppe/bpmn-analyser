import os

from src.examples.field_trial.task1_solution import Task1Solution
from src.examples.field_trial.task2_solution import Task2Solution
from src.examples.field_trial.task4_solution import Task4Solution
from src.models.solution_coordinator import SolutionCoordinator
from src.util.logger.logging_config import setup_logger_config


if __name__ == '__main__':
    setup_logger_config()

    # the path where all bpmn_files are you want to check
    folder_path = r'../test/first_field_trial'

    # check all *.bpmn-files
    file_mask = r'*.bpmn'

    # the sample_solution you want to apply and the subfolder
    solution = Task1Solution()
    subfolder = 'U1'
    #file_mask = r'*corrected.bpmn'
    file_mask = r'*.bpmn'

    # check all diagrams
    folder_path = os.path.join(folder_path, subfolder)
    coordinator = SolutionCoordinator(folder_path=folder_path,
                                      sample_solution=solution,
                                      file_mask=file_mask)
    coordinator.run_all_solution_checking()
