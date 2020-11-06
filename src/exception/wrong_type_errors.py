from typing import Any


class WrongTypeError(Exception):
    def __init__(self, object_: Any, expected: str, given: str):
        self.message = f'Expected type: {expected}. ' \
                       f'Got: {given}. Object: {object_} '
        super().__init__(self.message)
        logging.error(self.message)


class NotImplementedTypeError(Exception):
    def __init__(self, object_):
        self.message = f'object {object_} of type ' \
                       f'{type(object_)} is not supported' \
                       f' in this function'
        super().__init__(self.message)
        logging.error(self.message)
