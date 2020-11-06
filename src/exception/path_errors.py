import logging

class NoPathError(Exception):
    def __init__(self):
        self.message = f'Not a single path was given that day.'
        super().__init__(self.message)
        logging.error(self.message)