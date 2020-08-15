from pedantic import pedantic_class


'''
Metaclass for BPMN-Event, BPMN-Activities, basicly for
everything that isnt a flow/arrow
'''


@pedantic_class
class BPMNElement():
    def __init__(self, id:str, name: str) -> None:
        self.__id = id
        self.__name = name

    def get_name(self) -> str:
        return self.__name

    def set_name(self, name: str) -> None:
        self.__name = name

    def get_id(self) -> str:
        return self.__id

    def set_id(self, id:str) ->None:
        self.__id = id
