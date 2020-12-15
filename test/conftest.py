import os
import shutil
from typing import List, Tuple

import pytest
from nltk.corpus import wordnet as wn

from src.models.running_token import RunningToken
from src.models.token import Token

contract_checked = 'contract checked'
wn_synset_bill = wn.synset('bill.n.02')

test_files_folder_name = 'test_files'
xml_files_folder_name = 'xml'
temp_xml_files_folder_name = 'temp_xml'


def pytest_sessionstart():
    """
    Called after the Session object has been created and
    before performing collection and entering the run test loop.

    When working with xml files, we copy all files to
    a new directory to prevent overwriting of test files.
    All tests are performed there.

    We copy all xml-files from test/test_files/xml to test/test_files/temp_xml
    """

    pytest_root = os.path.dirname(os.path.abspath(__file__))
    xml_folder = os.path.join(pytest_root,
                              test_files_folder_name,
                              xml_files_folder_name)
    temp_xml_folder = os.path.join(pytest_root,
                                   test_files_folder_name,
                                   temp_xml_files_folder_name)

    try:
        shutil.copytree(xml_folder, temp_xml_folder)
    except FileExistsError:
        pass


def pytest_sessionfinish():
    """
    Called after whole test run finished, right before
    returning the exit status to the system.

    We use this timing to delete the temporary xml folder.
    """
    pytest_root = os.path.dirname(os.path.abspath(__file__))
    temp_xml_folder = os.path.join(pytest_root,
                                   test_files_folder_name,
                                   temp_xml_files_folder_name)
    shutil.rmtree(temp_xml_folder)


@pytest.fixture(scope='module', autouse=True)
def xml_folders_path():
    """
    Fixture to access all the xml test files.
    Returns the path to the temporary ones to use. Doesnt return the path to
    the original ones to prevent overwriting.
    """
    pytest_root = os.path.dirname(os.path.abspath(__file__))
    temp_xml_folder = os.path.join(pytest_root,
                                   test_files_folder_name,
                                   temp_xml_files_folder_name)
    return temp_xml_folder


@pytest.fixture(scope='function', autouse=True)
def empty_token() -> Token:
    return Token(attributes=None)


@pytest.fixture(scope='function', autouse=True)
def empty_running_token() -> RunningToken:
    return RunningToken(attributes=None)


@pytest.fixture(scope='function', autouse=True)
def example_token() -> Token:
    attributes = {'k1': 'v1', 'k2': 'v2', 'k3': 'v3'}
    return Token(attributes=attributes)


@pytest.fixture(scope='function', autouse=True)
def example_running_token() -> RunningToken:
    attributes = {'k1': 'v1', 'k2': 'v2', 'k3': 'v3'}
    return RunningToken(attributes=attributes)


@pytest.fixture(scope='module', autouse=True)
def nn_word() -> List[Tuple[str, str]]:
    return [('contract', 'NN')]


@pytest.fixture(scope='module', autouse=True)
def adj_word() -> List[Tuple[str, str]]:
    return [('to', 'TO'), ('be', 'VB'), ('smart', 'JJ')]


@pytest.fixture(scope='module', autouse=True)
def nn_vb_nn_sentence() -> List[Tuple[str, str]]:
    return [('contract', 'NN'), ('sending', 'VBG'), ('agreement', 'NN')]


@pytest.fixture(scope='module', autouse=True)
def xx_nn_xx_sentence() -> List[Tuple[str, str]]:
    return [('sending', 'VBG'), ('contract', 'NN'), ('green', 'ADJ')]
