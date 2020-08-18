import pytest

from src.models.token import Token


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