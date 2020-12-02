import logging
import re
from enum import Enum
from typing import Any, Union

from pedantic import pedantic_class

from src.exception.token_state_errors import \
    MissingOperatorInConditionError, \
    MissingAttributeInConditionError, MissingValueInConditionError, \
    MissingAttributeInTokenError
from src.exception.wrong_type_errors import WrongTypeError
from src.models.token import Token


class Operators(Enum):
    # list of operators that python can evaluate
    EQUALS = '=='
    GREATER_THEN = '>'
    SMALLER_THEN = '<'
    INCREMENT = '++'


@pedantic_class
class TokenStateCondition:
    """
    This class defines a single condition that is checked
    before a RunningToken state can change.
    """

    def __init__(self, tok_attribute: str = '',
                 operator: Operators = Operators.EQUALS,
                 tok_value: Union[str, int, float] = '') -> None:
        """
        Example: If you want to define the condition, where
        the token attribute foo has to be bar, then you
        define the condition:
        TokenStateCondition(tok_attribute = 'foo',
            operator = '=', tok_value='bar')
        Args:
            tok_attribute (str): is the key of the attribute dict of a token
            operator (Operators): '==' compares equality.
            tok_value (Union[str,int,float]): Defines the value the _tok_attribute has to have.
        """
        self._tok_attribute = tok_attribute
        self._operator = operator
        self._tok_value = tok_value

    @classmethod
    def from_string(cls, condition: str) -> 'TokenStateCondition':
        """
        parses conditions on BPMNConnectingObjects (e.g. sequenceFlows) to
        constructor call of TokenStateConditions.
        Example: 'attr>42' ==> token_attribute = attr, operator = >, value = 42
        We pay attention to white spaces: '    attr   > 42'.
        """
        operator = ''
        # find operator
        for op in Operators:
            if condition.find(op.value) != -1:
                operator = op
        if operator == '':
            raise MissingOperatorInConditionError(text=condition,
                                                  valid_operators=[op.value for op in Operators])

        # find attr
        op_pos = condition.find(operator.value)
        attribute = condition[0:op_pos]
        # delete whitespaces
        attribute = attribute.rstrip()
        attribute = attribute.lstrip()

        if attribute == '':
            raise MissingAttributeInConditionError(text=condition)

        # find value
        op_str_ending = op_pos + len(operator.value)
        value = condition[op_str_ending:len(condition)]
        if value == '':
            raise MissingValueInConditionError(text=condition)
        # delete whitespaces
        value = value.rstrip()
        value = value.lstrip()

        return TokenStateCondition(tok_attribute=attribute,
                                   operator=operator,
                                   tok_value=value)

    def check_condition(self, token: Token) -> bool:
        """
        Takes a token and checks if its pre-defined
        condition is true or false wth the given token.
        Args:
            token (Token): a Token object you want to check

        Returns:
             bool: True if condition applied to token is okay.
             False if token does not comply with condition
        """
        if self._tok_attribute not in token or self._tok_attribute == '':
            raise MissingAttributeInTokenError(
                attribute=self._tok_attribute,
                token=token)

        token_val = token[self._tok_attribute]

        if self._operator == Operators.EQUALS:
            # pay attention to True/False values:
            # SequenceFlows contain strings and they can be matched
            # to text and bool.
            # Token values can be bool and strings. And those strings can be
            # matched to text and boolean.

            if isinstance(token_val, bool):
                if isinstance(self._tok_value, bool):
                    # bool - bool
                    return token_val == self._tok_value
                elif self.__string_is_bool(string=self._tok_value):
                    # bool - 'True' or 'False'
                    return token_val == self.__string_to_bool(string=self._tok_value)
                else:
                    # bool - 'sth else'
                    msg = f'Conditions tok_value <{self._tok_value}> ' \
                          f'is neither <True> nor <False> ' \
                          f'and is compared to a Token attribute ' \
                          f'of type bool!'
                    logging.error(msg)
                    raise TypeError(msg)

            elif isinstance(token_val, str):
                # str - str
                return token_val == self._tok_value

            else:
                raise WrongTypeError(expected='str or bool',
                                     given=type(token_val),
                                     object_=token_val)

        elif self._operator == Operators.GREATER_THEN:
            return token_val > self._tok_value
        elif self._operator == Operators.SMALLER_THEN:
            return token_val < self._tok_value
        else:
            msg = f'Operator {self._operator} not implemented. ' \
                  f'Currently implemented: {Operators.value}'
            logging.error(msg)
            raise NotImplementedError(msg)

    def __string_is_bool(self, string:str) -> bool:
        return (string == 'True' or string == 'False')

    def __string_to_bool(self, string:str) -> bool:
        if string == 'True':
            return True
        elif string == 'False':
            return False
        else:
            msg = 'String <{string}> cannot be converted to bool'
            logging.error(msg)
            raise TypeError(msg)

    def __str__(self) -> str:
        return f'{self._tok_attribute}{self._operator.value}{self._tok_value}'

    def __repr__(self) -> str:
        return self.__str__()

    def __eq__(self, other: 'TokenStateCondition') -> bool:
        return self._tok_attribute == other._tok_attribute and \
               self._operator == other._operator and \
               self._tok_value == other._tok_value
