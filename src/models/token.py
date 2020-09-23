from typing import Dict, Any, Optional

from pedantic import overrides, pedantic_class

from src.models.token_state_modification import \
    TokenStateModification


@pedantic_class
class Token:
    """
    Is the class for a token-object to be passed through
    the business-process-graphs.
    """

    def __init__(self,
                 attributes: Optional[
                     Dict[str, Any]] = None) -> None:
        if attributes is None:
            self.attributes = {}
        else:
            self.attributes = attributes

    def new_attribute(self, key: str, value: Any) -> None:
        if key not in self.attributes:
            self.attributes[key] = value

    def change_value(self, modification: TokenStateModification) -> None:
        key = modification.get_key()
        value = modification.get_value()

        if key in self.attributes.keys():
            val_before = self.attributes[key]
            self.attributes[key] = value
            print(f'Token changed: {key}: {val_before} -> {value}')
        else:
            raise RuntimeError(
                f'ERROR: key {key} not in token attributes')

    def get_attribute(self, key: str) -> Any:
        return self.attributes[key]

    @overrides(str)
    def __contains__(self, item: str) -> bool:
        # Enables easy syntax for in-operator:
        # Example:
        # >>> token contains 'abc in attributes
        # >>> if 'abc' in token # True
        if item in self.attributes:
            return True
        else:
            return False

    @overrides(object)
    def __eq__(self, other: 'Token') -> bool:
        """
        Compares two tokens if they have equal dict-
        attributes.
        Overriding __eq__ means you can use '==' syntax.
        >>> if token1 == token2: # do something
        Args:
            other (Token): token you want to compare to

        Returns:
            bool: True if tokens are equal. Returns false otherwise

        """
        if len(self.attributes) == len(other.attributes):
            for key in self.attributes.keys():
                if key not in other.attributes.keys() or \
                        self.attributes[key] != other.attributes[key]:
                    return False
        else:
            return False
        return True

    def __str__(self) -> str:
        return "token attributes: " + str(self.attributes)

    def __repr__(self) -> str:
        return self.__str__()
