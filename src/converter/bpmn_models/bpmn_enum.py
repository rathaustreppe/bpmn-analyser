from enum import Enum


class BPMNEnum(Enum):
    STARTEVENT = 'startEvent'
    ACTIVITY = 'task'
    SEQUENCEFLOW = 'sequenceFlow'
    ENDEVENT = 'endEvent'
    PARALLGATEWAY = 'parallelGateway'
    EXCLGATEWAY = 'exclusiveGateway'
    INCLGATEWAY = 'inclusiveGateway'
    ID = 'id'
    NAME = 'name'
    PROCESS = 'process'
