from enum import Enum
from typing import Union

from pedantic import pedantic_class

from src.exception.token_state_errors import MissingOperatorInConditionError, \
    MissingAttributeInConditionError, MissingValueInConditionError, \
    MissingAttributeInTokenError


class Operators(Enum):
    # list of operators that python can evaluate
    EQUALS = '=='
    GREATER_THEN = '>'
    SMALLER_THEN = '<'
    INCREMENT = '++'


@pedantic_class
class BranchCondition:
    """
    BPMNGateways branch into several paths depending on the condition that
    is documented on the BPMNSequenceFlow. This string (it comes from BPMN-XML)
    needs to be parsed to check if this condition is true or not - i.e to branch
    a gateway into one or more paths.
    E.g.
    ExclusiveGateway A can branch into the activities X and Y, depending on
    the BranchCondition.

    Dont get confused with TokenStateConditions. They are used as part of
    rules in the sample solution creation. (Why not using them as branch
    conditions? Because they want a Callback-Function that evaluates to bool.
    But in the BPMN-Diagram we have only simple strings. And converting the
    string to callable function without using evil eval() is difficult.
    Furthermore: Having two distinct classes means that TokenStateCondition is
    not used for two different aspects of the software.
    1 Functionality = 1 Class)
    """

    def __init__(self, tok_attribute: str = '',
                 operator: Operators = Operators.EQUALS,
                 tok_value: Union[str, int, bool] = '') -> None:
        """
        Example: If you want to define the condition, where
        the token attribute foo has to be bar, then you
        define the condition:
        TokenStateCondition(tok_attribute = 'foo',
            operator = Operator.EQUALS, tok_value='bar')
        Args:
            tok_attribute (str): is the key of the attribute dict of a token
            operator (Operators): a python standard operator
            tok_value (Union[str,int,bool]): Defines the value the tok_attribute
             has to have.
        """
        self._tok_attribute = tok_attribute
        self._operator = operator
        self._tok_value = tok_value

    @classmethod
    def from_string(cls, condition: str) -> 'BranchCondition':
        """
        Parses conditions on BPMNConnectingObjects (e.g. sequenceFlows) to
        constructor call of BranchCondition.
        Example: 'attr>42' ==> token_attribute = attr, operator = >, value = 42
        We pay attention to white spaces: '    attr   > 42'.

        The value (e.g 42) comes from BPMN-XMLs. They contain only strings.
        It automatically parses everything to string. (True/False, 42, hehe are
        all strings). The person defining the sample solution defines the token
        as well. He probably defines True/False-values as booleans and uses int.
        So it is very handy if those strings coming from the diagram can be
        converted to a more appropriate data type.
        """

        operator = ''
        # find operator
        for op in Operators:
            if condition.find(op.value) != -1:
                operator = op
        if operator == '':
            raise MissingOperatorInConditionError(text=condition,
                                                  valid_operators=[op.value for
                                                                   op in
                                                                   Operators])

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

        # convert data types
        value = cls._str_to_data_type(text=value)

        return BranchCondition(tok_attribute=attribute,
                               operator=operator,
                               tok_value=value)

    @staticmethod
    def _str_to_data_type(text: str) -> Union[str, int, bool]:
        # check int
        try:
            return int(text)
        except ValueError:
            pass
        # check bool. Remark: bool(text) doesnt work here.
        if text == 'True':
            return True
        elif text == 'False':
            return False
        else:
            # else return str
            return text

    def check_condition(self, token: 'RunningToken') -> bool:
        """
        bool: True if condition applied to token is okay.
        False if token does not comply with condition
        """
        if self._tok_attribute not in token or self._tok_attribute == '':
            raise MissingAttributeInTokenError(
                attribute=self._tok_attribute,
                token=token)

        token_val = token[self._tok_attribute]

        if self._operator == Operators.EQUALS:
            return token_val == self._tok_value
        elif self._operator == Operators.GREATER_THEN:
            return token_val > self._tok_value
        elif self._operator == Operators.SMALLER_THEN:
            return token_val < self._tok_value
        else:
            msg = f'Operator {self._operator} not implemented. ' \
                  f'Currently implemented: {Operators.value}'
            raise NotImplementedError(msg)

    def __eq__(self, other: 'BranchCondition') -> bool:
        return self._tok_value == other._tok_value and \
               self._operator == other._operator and \
               self._tok_attribute == other._tok_attribute

    def __str__(self) -> str:
        return f'{self._tok_attribute}{self._operator.value}{self._tok_value}'

    def __repr__(self) -> str:
        return self.__str__()
