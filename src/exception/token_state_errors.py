import logging


class MissingOperatorInConditionError(Exception):
    def __init__(self, text: str, valid_operators: 'Operators'):
        self.message = f'operator in string >{text}< is not implemented. ' \
                       f'Valid operators: {valid_operators}'
        super().__init__(self.message)
        logging.error(self.message)


class MissingAttributeInConditionError(Exception):
    def __init__(self, text: str):
        self.message = f'attribute before operator in string >{text}< not found'
        super().__init__(self.message)
        logging.error(self.message)


class MissingValueInConditionError(Exception):
    def __init__(self, text: str):
        self.message = f'value after operator in string >{text}< not found'
        super().__init__(self.message)
        logging.error(self.message)


class MissingAttributeInTokenError(Exception):
    def __init__(self, token: 'Token', attribute: str):
        self.message = f'attribute >{attribute}< in token {token} is either ' \
                       f'empty, none or non-existing.'
        super().__init__(self.message)
        logging.error(self.message)
