from typing import List, Type, Union

from src.converter.bpmn_models.bpmn_activity import BPMNActivity
from src.converter.bpmn_models.bpmn_element import BPMNFlowObject
from src.converter.bpmn_models.bpmn_sequenceflow import BPMNSequenceFlow
from src.converter.bpmn_models.event.bpmn_endevent import BPMNEndEvent
from src.converter.bpmn_models.event.bpmn_startevent import BPMNStartEvent


class BPMNModel:
    def __init__(self, bpmn_elements: List[BPMNFlowObject],
                 sequence_flows: List[BPMNSequenceFlow]) -> None:
        for element in bpmn_elements:
            if isinstance(element, BPMNSequenceFlow):
                raise ValueError(f'list of bpmn_elements cannot contain '
                                 f'sequenceflows. Use >sequence_flow< attribute instead.')
        self.bpmn_elements = bpmn_elements

        self.sequence_flows = sequence_flows

    def find_elements_by_type(self, type_to_find) -> List[Union[BPMNStartEvent,
                                                                BPMNEndEvent,
                                                                BPMNActivity,
                                                                BPMNFlowObject]]:
        return [elem for elem in self.bpmn_elements if isinstance(elem, type_to_find)]

