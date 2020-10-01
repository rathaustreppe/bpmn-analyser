from typing import List, Tuple


class MyQueue:
    def __init__(self):
        self.item = []

    def queue(self, element: Tuple[str,str]):
        self.item.append(element)

    def queue(self, element: List[Tuple[str,str]]):
        self.item.append(element)

    def dequeue(self):
        return self.item.pop(0)

    def items(self):
        return self.items

    def not_empty(self):
        if len(self.item) == 0:
            return False
        else:
            return True

    def __str__(self):
        return self.item.__str__()