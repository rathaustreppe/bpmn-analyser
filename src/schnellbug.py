from typing import Type

from pedantic import pedantic_class


@pedantic_class
class A:
    def __init__(self, val: int) -> None:
        self.val = val

    def __eq__(self, other: 'A') -> bool: # other: A and all subclasses
        return self.val == other.val

@pedantic_class
class B(A):
    def __init__(self, val: int) -> None:
        super().__init__(val=val)

@pedantic_class
class C(A):
    def __init__(self, val: int) -> None:
        super().__init__(val=val)

if __name__ == '__main__':
    a = A(val=42)
    b = B(val=42)
    c = C(val=42)

    assert a == b # works
    assert a == c # works
    assert b == c # error