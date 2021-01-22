import logging
from typing import Dict, Optional, Union, Type

from pedantic import overrides

from src.exception.token_state_errors import MissingAttributeInTokenError


class Token(dict):
    """
    Token solve two purposes:
    1. They run through the diagram and change its state. (The state is encoded
    in the dict-attribute.) The RunningToken class is designed for this purpose.
    2. The lecturer defines a solution token. If the RunningToken after
    running through a diagram equals the solution token, we assume the diagram
    is correct.

    Token State:
    To define the state of a token it expects a dictionary with simple
    key-value pairs.
    Example:
        token = Token(attributes={'house': 'to sell', 'money': 0})

    When traversing the BPMN the token state changes. E.g. the BPMNActivity
    'sell house' can change the token state to house:sold and money: 999999.

    Token State changing:
    Refer to TokenStateCondition (the conditions when to change token),
    TokenStateModification (the modification applied to the token) and
    TokenStateRule (the rule forged of conditions and modifications) for more
    information.

    Accessing token in code:
    Token inherits from dict. Together with a special __getattr__ - method it
    is possible to directly access the dict-attributes.
    Example:
        token = Token(attributes={'house': 'sold'})
        normal python access: token.attributes['house']
        better access: token['house']
        best access: token.house

    Downside of this is token attributes cannot have spaces:
    token['mail checked'] is okay.
    >token.mail checked< cannot be coded.
    So we disallow spaces. Use underscores instead.

    copy.copy and copy.deepcopy do not work here. Please use
    token.copy() - the build-in function of every dict instead.
    Or use RunningToken.from_token().

    With the current implementation the better and best access
    version are possible. The implementation was taken from:
    https://dev.to/0xbf/use-dot-syntax-to-access-dictionary-key-python-tips-10ec

    """

    def __init__(self, attributes: Optional[Dict[str, Union[str, bool, int, float]]] = None) -> None:
        if attributes is not None:
            # Token attributes cannot have spaces because the point-operator
            # access >token.my attribute< cannot be coded.
            # So we search them here and throw an exception
            for attribute_key in attributes.keys():
                if ' ' in attribute_key:
                    msg = f'Cannot have spaces in token attribute: {attribute_key}'
                    logging.error(msg)
                    raise SyntaxError(msg)
                self.__setattr__(key=attribute_key, value=attributes[attribute_key])

    def __getattr__(self, key):
        # Method that allows direct point-access of token dict attributes:
        # e.g token.house
        # copy.copy and copy.deepcopy change the key-argument of this method
        # (somehow?) and therefore the method does not get its intended argument.
        # __deepcopy__ when using copy.deepcopy
        # __getstate__ when using copy.copy
        # So we catch them and throw an exception.
        if key == '__deepcopy__' or key == '__getstate__':
            msg = 'Cannot copy/deepcopy token class. ' \
                  'Use token.copy() or RunningToken.from_token() instead.'
            logging.error(msg)
            raise NotImplementedError
        try:
            return self[key]
        except KeyError:
            msg = f'Your defined attribute {key} is not present in the token.'
            logging.error(msg)
            raise MissingAttributeInTokenError(token=self, attribute=key)

    def __setattr__(self, key, value):
        self[key] = value

    def __delattr__(self, key):
        try:
            del self[key]
        except KeyError as k:
            raise AttributeError(k)

    def __str__(self) -> str:
        return 'token _attributes: ' + dict.__repr__(self)

    def __repr__(self) -> str:
        return self.__str__()

    @overrides(object)
    def __eq__(self, other: Type['Token']) -> bool:
        """
        Compares two tokens if they have equal dict
        Overriding __eq__ means you can use '==' syntax:
        if token1 == token2
        Args:
            other (Token): token you want to compare to

        Returns:
            bool: True if tokens are equal. Returns false otherwise

        """
        if len(self.keys()) == len(other.keys()):
            for key in self.keys():
                if key not in other.keys() or \
                        self[key] != other[key]:
                    return False
        else:
            return False
        return True


    @overrides(str)
    def __contains__(self, item: str) -> bool:
        # Enables easy syntax for in-operator:
        # Example:
        # >>> token contains 'abc in _attributes
        # >>> if 'abc' in token # True
        return item in self.keys()