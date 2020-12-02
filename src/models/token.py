from typing import Dict, Any, Optional, Union, Type

from pedantic import overrides, pedantic_class


# @pedantic_class #activate when Type['A'] is implemented in a version > 1.2.7
# class Token(object):
#     """
#     Is the base class for tokens.
#     Refer to RunningToken and ExpectedToken to express their functionality
#     better.
#     """
#     def __init__(self, attributes: Optional[
#         Dict[str, Union[str, bool, int, float]]] = None) -> None:
#         if attributes is None:
#             self._attributes = {}
#         else:
#             self._attributes = attributes
#
#     @property
#     def attributes(self) -> Dict[str, Union[str, bool, int, float]]:
#         return self._attributes
#
#     # def new_attribute(self, key: str, value: Any) -> None:
#     #     if key not in self._attributes:
#     #         self._attributes[key] = value
#
#     def get_attribute(self, key: str) -> Any:
#          return self._attributes[key]
#
#     @overrides(str)
#     def __contains__(self, item: str) -> bool:
#         # Enables easy syntax for in-operator:
#         # Example:
#         # >>> token contains 'abc in _attributes
#         # >>> if 'abc' in token # True
#         return item in self._attributes
#
#     @overrides(object)
#     def __eq__(self, other: Type['Token']) -> bool:
#         """
#         Compares two tokens if they have equal dict-
#         _attributes.
#         Overriding __eq__ means you can use '==' syntax:
#         if token1 == token2: # do something
#         Args:
#             other (Token): token you want to compare to
#
#         Returns:
#             bool: True if tokens are equal. Returns false otherwise
#
#         """
#         if len(self._attributes) == len(other._attributes):
#             for key in self._attributes.keys():
#                 if key not in other._attributes.keys() or \
#                         self._attributes[key] != other._attributes[key]:
#                     return False
#         else:
#             return False
#         return True
#
#     def __str__(self) -> str:
#         return 'token _attributes: ' + str(self._attributes)
#
#     def __repr__(self) -> str:
#         return self.__str__()
from src.util.decorators.deprecated import deprecated


class Token(dict):
    # taken from
    # https://dev.to/0xbf/use-dot-syntax-to-access-dictionary-key-python-tips-10ec

    # direct access: token.house = sold
    # variable access: attr = 'house' --> token[attr] = sold

    def __init__(self, attributes: Optional[Dict[str, Union[str, bool, int, float]]] = None) -> None:
        if attributes is not None:
            for attribute_key in attributes.keys():
                self.__setattr__(key=attribute_key, value=attributes[attribute_key])


    def new_attribute(self, key: str, value: Any) -> None:
        self.__setattr__(key=key, value=value)

    @deprecated('Replace token.get_attribute(key) with token.key')
    def get_attribute(self, key: str) -> Any:
        return self.__getattr__(key=key)

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