from typing import List, Tuple

import pytest

from src.models.token import Token
from src.nlp.chunker import Chunker


@pytest.fixture(scope='function', autouse=True)
def empty_token() -> Token:
    return Token(attributes=None)


@pytest.fixture(scope='function', autouse=True)
def example_token() -> Token:
    attributes = {'k1': 'v1', 'k2': 'v2', 'k3': 'v3'}
    return Token(attributes=attributes)


@pytest.fixture(scope='module', autouse=True)
def bill_process_solution_token() -> Token:
    attributes_solution = {
        "Ort": "Dresden",
        "Unterschrift ML": True,
        "Unterschrift Zittau": True,
        "Fachlich geprüft": True
    }
    return Token(attributes=attributes_solution)


@pytest.fixture(scope='module', autouse=True)
def nn_vb_nn_chunker() -> Chunker:
    grammar = r"""
    NN_VB_NN:     {<NN.?><VB.?><NN.?>}
    """
    return Chunker(chunk_grams=grammar)


@pytest.fixture(scope='module', autouse=True)
def nn_chunker() -> Chunker:
    grammar = r"""
    NN_Chunk:     {<NN.?>}
    """
    return Chunker(chunk_grams=grammar)


@pytest.fixture(scope='module', autouse=True)
def adj_chunker() -> Chunker:
    grammar = r"""
    ADJ_Chunk:      {<JJ.?>}
    """
    return Chunker(chunk_grams=grammar)


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
