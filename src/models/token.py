import logging
from typing import Dict, Optional, Union, Type

from pedantic import overrides


class Token(dict):
    # taken from
    # https://dev.to/0xbf/use-dot-syntax-to-access-dictionary-key-python-tips-10ec

    # direct access: token.house = sold
    # variable access: attr = 'house' --> token[attr] = sold

    def __init__(self, attributes: Optional[Dict[str, Union[str, bool, int, float]]] = None) -> None:
        if attributes is not None:
            for attribute_key in attributes.keys():
                # We use eval() in TokenStateConditions. Eval() cannot handle
                # spaces in attribute names:
                # token = Token(attributes={'my attribute': 42})
                # TokenStateCondition(condition='t.my attribute == 42')
                # this will break.
                # So there are two options: use []-brackets notation:
                # TokenStateCondition(condition="t['my attribute'] == 42")
                # or disallow spaces in attribute names.
                # We decided for disallowing spaces, because we want the
                # syntax of conditions easy. And using _ instead of space
                # is better.
                # We could automatically replace space with underscore. But we
                # would have to do this in the TokenStateConditions as well.
                # This is not so easy, so we decided just to warn the user
                # about spaces in token-attributes.
                if ' ' in attribute_key:
                    msg = f'Cannot have spaces in token attribute: {attribute_key}'
                    logging.error(msg)
                    raise SyntaxError(msg)
                self.__setattr__(key=attribute_key, value=attributes[attribute_key])

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError as k:
            raise AttributeError(k)

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
        if token1 == token2: # do something
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