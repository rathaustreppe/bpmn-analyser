import pytest

from src.exception.stack_errors import EmptyStackPopError
from src.models.stack import Stack


class TestStack:
    def test_stack_empty(self):
        stack = Stack[int]()
        assert stack.empty()

    def test_push_pop(self):
        stack = Stack[int]()
        stack.push(item=1)
        stack.push(item=2)
        stack.push(item=3)
        assert stack.pop() == 3
        assert stack.pop() == 2
        assert stack.pop() == 1
        assert stack.empty

    def test_pop_empty_stack(self):
        stack = Stack[int]()
        with pytest.raises(EmptyStackPopError):
            stack.pop()

    def test_top_empty_stack(self):
        stack = Stack[int]()
        assert stack.top() is None

    def test_top(self):
        stack = Stack[int]()
        stack.push(item=42)
        assert stack.top() == 42