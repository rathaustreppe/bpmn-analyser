import os

from src.examples.field_trial.task1_solution import Task1Solution
from src.models.solution_coordinator import SolutionCoordinator
from src.util.logger.logging_config import setup_logger_config


if __name__ == '__main__':
    setup_logger_config()

    # the path where all bpmn_files are you want to check
    # can be a relative path if the bpmn-files are inside the
    # bpmn-analyzer-project
    # or can be an absolute path
    # Example:
    # >>> folder_path = r'../test/first_field_trial'
    # >>> folder_path = r'C:/Users/Anon/Desktop'
    folder_path = r'../test/first_field_trial'

    # in case you have multiple folders in folder_path, you can specify one
    # folder here that is used. If not used, leave it as empty string.
    subfolder = ''

    # file-mask. Is a regular expression to match all the files with a specific
    # file name.
    # Example:
    # >>> file_mask = r'*.bpmn'     matches all bpmn-files. is the default mask
    # >>> file_mask = r'*corrected.bpmn'       matches all files that end with
    # 'corrected' e.g. my_house_corrected.bpmn
    file_mask = r'*.bpmn'
    file_mask = r'*corrected.bpmn'

    # the sample_solution you want to apply
    # this is the class where you wrote your sample solution
    # put the file in src and import it here
    solution = Task1Solution()

    # check all diagrams. leave code as it is
    folder_path = os.path.join(folder_path, subfolder)
    coordinator = SolutionCoordinator(folder_path=folder_path,
                                      sample_solution=solution,
                                      file_mask=file_mask)
    coordinator.run_all_solution_checking()
