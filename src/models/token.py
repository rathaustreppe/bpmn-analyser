from typing import Dict, Any

from pedantic import pedantic


class Token:
    """
    Is the class for a token-object to be passed through
    the business-process-graphs.
    """

    @pedantic
    def __init__(self,
                 attributes: Dict[str, Any] = None) -> None:
        if attributes is None:
            self.attributes = {}
        else:
            self.attributes = attributes

    @pedantic
    def __change_value(self, key: str, value: Any) -> None:
        if key in self.attributes.keys():
            val_before = self.attributes[key]
            self.attributes[key] = value
            print('{}: {} -> {}'
                  .format(key, val_before, value))
        else:
            raise RuntimeError(
                'ERROR: key {} not '
                'in token attributes'.format(key))

    @pedantic
    def new_attribute(self, key: str, value: Any) -> None:
        self.attributes[key] = value

    @pedantic
    def change_value(self, key: str, value: Any) -> None:
        self.__change_value(key=key, value=value)

    @pedantic
    def get_attribute(self, key: str) -> Any:
        return self.attributes[key]

    # @pedantic #does not yet work with TypeHint 'Token'
    def compare_token(self, other: 'Token') -> bool:
        """
        Compares two tokens if they have equal dict-
        attributes.
        Args:
            other: Token of class Token

        Returns: True if tokens are equal.
        Returns false otherwise

        """
        if len(self.attributes) == len(other.attributes):
            for key in self.attributes.keys():
                if key in other.attributes.keys() and \
                        self.attributes[key] == \
                        other.attributes[key]:
                    pass
                else:
                    return False
        else:
            return False
        return True

    @pedantic
    def __str__(self) -> str:
        return "token attribues: " + str(self.attributes)
