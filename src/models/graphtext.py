from pedantic import pedantic


class GraphText:
    """
    Stores the text from a single vertex
    = business process activity
    used for better object structure in code
    """

    @pedantic
    def __init__(self, text: str = "") -> None:
        self.__text = text
        self.__text_iter = self.__text.__iter__()

    def set_text(self, text: str) -> None:
        self.__text = text

    def get_text(self) -> str:
        return self.__text

    # @pedantic # not working with op-oveload yet :(
    def __contains__(self, item: str) -> bool:
        """
        Checks if GraphText contains substring.
        Overriding __contains__ build in functions allows
        to use the 'in' - operator for GraphText-objects
        thus enhances readability
        Example:
        my_graph_text = GraphText(text='abcd')
        if 'ab' in my_graph_text -> True
        Args:
            item: substring you want to check

        Returns: True if item is stored in GraphText. False
        if otherwise.
        """
        if item in self.__text:
            return True
        else:
            return False
