from typing import Tuple, List
from xml.etree.ElementTree import Element

from src.converter.bpmn_models.bpmn_element import \
    BPMNElement
from src.converter.bpmn_models.bpmn_sequenceflow import \
    BPMNSequenceFlow
from src.converter.bpmn_models.bpmn_startevent import \
    BPMNStartEvent


class ModelBuilder:
    """
    Static class that converts XML-elements into BPMN-objects
    """
    @staticmethod
    def make_startevent(element: Tuple[Element, List[Element]]) -> BPMNStartEvent:
        # [(element, sequenceflow), (element, sequenceflow, sequenceflow)]
        id, name = ModelBuilder.make_bpmn_element(element=element[0])

        # so far only 1 sequence flow going from startevent
        # is implemented. So we can directly access the sequence
        # flow in the tuple.
        sequence_flow = element[1][0]
        sequence_flow = ModelBuilder.make_sequenceflow(element=sequence_flow)
        return BPMNStartEvent(id=id, name=name, sequenceFlow=sequence_flow)

    @staticmethod
    def make_empty_sequenceflow(element: Element) -> BPMNSequenceFlow:
        """
        Creates a sequenceflow without target and source.
        Only with id.
        Args:
            element (Element):

        Returns:

        """
        return BPMNSequenceFlow(id=element.text)

    @staticmethod
    def make_sequenceflow(element: Element) -> BPMNSequenceFlow:
        id = element.get('id')
        #source = element.get('sourceRef')
        #target = element.get('targetRef')
        return BPMNSequenceFlow(id=id, source=None, target=None)

    @staticmethod
    def make_bpmn_element(element: Element) -> (str, str):
        id = element.get('id')
        name = element.get('name')
        return id, name