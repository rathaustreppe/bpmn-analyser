from typing import List

from src.converter.bpmn_models.bpmn_element import BPMNElement
from src.converter.bpmn_models.bpmn_sequenceflow import BPMNSequenceFlow


class BPMNModel:
    def __init__(self, bpmn_elements: List[BPMNElement],
                 sequence_flows: List[BPMNSequenceFlow]) -> None:
        for element in bpmn_elements:
            if isinstance(element, BPMNSequenceFlow):
                raise ValueError(f'list of bpmn_elements cannot contain '
                                 f'sequenceflows. Use >sequence_flow< attribute instead.')
        self.bpmn_elements = bpmn_elements
        self.sequence_flows = sequence_flows