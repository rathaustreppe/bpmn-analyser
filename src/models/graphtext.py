import inspect

from pedantic import pedantic, pedantic_class, overrides
from pyparsing import unicode
import string


@pedantic_class
class GraphText:
    """
    Stores the text from a single vertex
    = business process activity
    used for better object structure in code
    """
    def __init__(self, text: str = "") -> None:
        self.__text = text
        self.__text_iter = self.__text.__iter__()

    def set_text(self, text: str) -> None:
        self.__text = text

    def get_text(self) -> str:
        return self.__text

    @overrides(str)
    def __contains__(self, item: str = '') -> bool:
        """
        Checks if GraphText contains substring.
        Overriding __contains__ build in functions allows
        to use the 'in' - operator for GraphText-objects
        thus enhances readability
        Example:
        >>> my_graph_text = GraphText(text='abcd')
        >>> if 'ab' in my_graph_text -> True
        Args:
            item: substring you want to check

        Returns: True if item is stored in GraphText. False
        if otherwise.
        """
        if item in self.__text:
            return True
        else:
            return False

    def __str__(self) -> str:
        """
        When printing svg with igraph lib there is a utf-8
        error. ß, ä,ü... are not correctly written in the
        svg-file. And therefore the text is not displayed.
        We workaround this problem if we check the calling
        stack. If write_svg calls this function here, we
        give back an ascii-representation of the text.
        Returns:
            str: Ascii if called with write_svg function,
            otherwise standard python string representation.
        """
        stack = inspect.stack()
        for caller in stack:
            if caller.function == 'write_svg':
                return self.__text.encode("ascii", errors="ignore").decode()
        return self.__text


