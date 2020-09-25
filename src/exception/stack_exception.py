
class EmptyStackPopException(Exception):
    def __init__(self):
        self.message = f'cannot pop from an empty stack.'
        super().__init__(self.message)
