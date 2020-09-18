from typing import List, TypeVar, Generic
from pedantic import pedantic_class

T = TypeVar('T')


@pedantic_class
class Stack:
    def __init__(self, stack: List[Generic[T]]) -> None:
        self.stack = stack

    def push(self, element: T) -> None:
        self.stack.push(element)

    def pop(self) -> T:
        return self.stack.pop()

    def top(self) -> T:
        if len(self.stack) > 0:
            return self.stack[len(self.stack) - 1]

    def empty(self) -> None:
        self.stack = []
