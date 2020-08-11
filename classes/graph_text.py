
# Graph_Text objects store the text from a single vertex
# = business process activity
# used for better object structure in code
# deliver some string util functions
# and semantic text analysis is performed with them
class Graph_Text:

    def __init__(self, text:str=""):
        self.__text = text
        self.__text_iter = self.__text.__iter__()

    def set_text(self, text:str):
        self.__text = text

    def get_text(self) -> str:
        return self.__text

    def __contains__(self, item):
    # with this function you can use the syntax:
    # graph_text = Graph_Text('abcd')
    # if 'abc' in graph_text ...
    # instead of
    # if 'abc' in graph_text.text or
    # if 'abc' in graph_text.get_text() ...
    # enhances readability
        if item in self.__text:
            return True
        else:
            return False
