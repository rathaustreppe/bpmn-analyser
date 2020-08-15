from enum import Enum


class BPMNEnum(Enum):
    STARTEVENT = 'startEvent'
    ACTIVITY = 'task'
    SEQUENCEFLOW = 'sequenceFlow'
