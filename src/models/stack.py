from typing import List
from typing import TypeVar, Generic

from pedantic import pedantic_class

T = TypeVar('T')


@pedantic_class
class Stack(Generic[T]):
    def __init__(self) -> None:
        self.items: List[T] = []

    def push(self, item: T) -> None:
        self.items.append(item)

    def pop(self) -> T:
        return self.items.pop()

    def empty(self) -> bool:
        return not self.items

    def top(self) -> T:
        if len(self.items) > 0:
            return self.items[len(self.items)-1]
        else:
            return None