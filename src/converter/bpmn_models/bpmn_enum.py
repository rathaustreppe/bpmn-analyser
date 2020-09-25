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
    CONDITION = 'condition'


    # needs to be one chunk for chunker
    PARALLGATEWAY_TEXT = 'AND'
    EXCLGATEWAY_TEXT = 'XOR'
    INCLGATEWAY_TEXT = 'OR'

    # enhanced readability of string-checking of multiple gateways
    GATEWAY_TEXTS = [PARALLGATEWAY_TEXT,
                     EXCLGATEWAY_TEXT,
                     INCLGATEWAY_TEXT]
    TYPE = 'type'

    # use it as a true/false value. True = gateway is opening, false = gateway
    # is closing
    GATEWAY_OPEN = 'gateway_open'
