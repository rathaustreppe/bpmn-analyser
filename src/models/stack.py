from typing import List, Optional, Union
from typing import TypeVar, Generic

from pedantic import pedantic_class

from src.exception.stack_exception import EmptyStackPopException

T = TypeVar('T')


@pedantic_class
class Stack(Generic[T]):
    def __init__(self) -> None:
        self.items: List[T] = []

    def push(self, item: T) -> None:
        self.items.append(item)

    def pop(self) -> T:
        if len(self.items) > 0:
            return self.items.pop()
        else:
            raise EmptyStackPopException()

    def empty(self) -> bool:
        return not self.items

    def top(self) -> Optional[T]:
        if len(self.items) > 0:
            return self.items[len(self.items)-1]
        else:
            return None