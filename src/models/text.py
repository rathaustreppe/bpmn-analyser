from typing import Union


class Text:
    """
    From a object-oriented point of view it is not nice to send primitive data
    types around in the system. So a simple 'Text'-class is defined that wraps
    a string.
    We are not making this class pedantic, because it will be used for sample
    solution programming and t = Text('hehe') is nicer to write than
    t = Text(text='hehe').
    """
    def __init__(self, text: str):
        self.text = text

    def __eq__(self, other: Union[str, 'Text']) -> bool:
        if isinstance(other, str):
            return self.text == other
        else:
            return self.text == other.text

    def __repr__(self) -> str:
        return self.__str__()

    def __str__(self) -> str:
        return f'\'{self.text}\''