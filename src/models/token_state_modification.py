from typing import Any

from pedantic import pedantic_class


@pedantic_class
class TokenStateModification:
    """
    E.g. Saves token state e.g. 'weather is good' --> 'weather' = 'good'
    Simple key - value to keep things organized
    """

    def __init__(self, key: str = '', value: Any = '') -> None:
        self.key = key
        self.value = value

    def get_key(self) -> str:
        return self.key

    def get_value(self) -> Any:
        return self.value

    def __str__(self) -> str:
        return f'{self.key}=={self.value}'

    def __repr__(self) -> str:
        return self.__str__()
