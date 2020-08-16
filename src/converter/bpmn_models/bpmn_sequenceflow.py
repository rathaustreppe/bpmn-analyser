from typing import Optional

from pedantic import pedantic_class

# local imports
from src.converter.bpmn_models.bpmn_element import \
    BPMNElement


@pedantic_class
class BPMNSequenceFlow:
    def __init__(self, id: str, source: Optional[BPMNElement] = None,
                 target: Optional[BPMNElement] = None) -> None:
        self.__id = id
        self.__source = source
        self.__target = target

    def get_id(self) -> str:
        return self.__id

    def get_source(self) -> BPMNElement:
        return self.__source

    def get_target(self) -> BPMNElement:
        return self.__target

    def set_source(self, source: BPMNElement) -> None:
        self.__source = source

    def set_target(self, target: BPMNElement) -> None:
        self.__target = target