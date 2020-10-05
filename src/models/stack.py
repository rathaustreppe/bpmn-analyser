from typing import List, Optional
from typing import TypeVar, Generic

from pedantic import pedantic_class

from src.exception.stack_errors import EmptyStackPopError

T = TypeVar('T')


@pedantic_class
class Stack(Generic[T]):
    def __init__(self) -> None:
        self.items: List[T] = []

    def len(self) -> int:
        return len(self.items)

    def push(self, item: T) -> None:
        self.items.append(item)

    def pop(self) -> T:
        if len(self.items) > 0:
            return self.items.pop()
        else:
            raise EmptyStackPopError()

    def empty(self) -> bool:
        return not self.items

    def top(self) -> Optional[T]:
        if len(self.items) > 0:
            return self.items[len(self.items) - 1]
        else:
            return None

    # def __len__(self) -> int:
    #     return self.len()
