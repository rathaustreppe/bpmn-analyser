from typing import List

import igraph
from pedantic import pedantic_class


@pedantic_class
class Stack:
    def __init__(self, stack: List[igraph.Vertex]) -> None:
        self.stack = stack

    def push(self, element: igraph.Vertex) -> None:
        self.stack.push(element)

    def pop(self) -> igraph.Vertex:
        return self.stack.pop()

    def top(self) -> igraph.Vertex:
        return self.stack[len(self.stack) - 1]

    def empty(self) -> None:
        self.stack = []
