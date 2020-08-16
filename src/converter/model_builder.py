from typing import List, Tuple
from xml.etree.ElementTree import Element

from pedantic import pedantic_class, for_all_methods, \
    combine, pedantic

from src.converter.bpmn_models.bpmn_activity import \
    BPMNActivity
from src.converter.bpmn_models.bpmn_element import \
    BPMNElement
from src.converter.bpmn_models.bpmn_endevent import \
    BPMNEndEvent
from src.converter.bpmn_models.bpmn_sequenceflow import \
    BPMNSequenceFlow
from src.converter.bpmn_models.bpmn_startevent import \
    BPMNStartEvent

@pedantic_class
@for_all_methods(staticmethod)
class ModelBuilder:
    """
    Static class that converts XML-elements into BPMN-objects
    """

    def make_startevent(element: Element) -> BPMNStartEvent:
        id, name = ModelBuilder.make_bpmn_element(element=element)
        return BPMNStartEvent(id=id, name=name, sequenceFlow=None)


    def make_end_event(element:Element) -> BPMNEndEvent:
        id, name = ModelBuilder.make_bpmn_element(element=element)
        return BPMNEndEvent(id=id, name=name, sequenceFlow=None)


    def make_sequenceflow(sequence_flow: Element, elements: List[BPMNElement]) -> BPMNSequenceFlow:
        """
        We fully build a sequence flow here. We take the
        BPMN-elements as a list to search for the object
        references.
        Args:
            sequence_flow:
            elements:

        Returns:

        """
        id = sequence_flow.get('id')
        source_ref = sequence_flow.get('sourceRef')
        target_ref = sequence_flow.get('targetRef')

        # Notice how a sequence flow target is incomming for
        # activities. And how outgoing for a activity means
        # source for a sequence flow!
        # If we want to check where our SequenceFlow points
        # to (our target) we look on the other side: the source-
        # attribute of our BPMN-elements.
        sequence_targets = []
        for source in elements:
            source: BPMNElement
            if target_ref == source.get_id():
                sequence_targets.append(source)

        sequence_sources = []
        for target in elements:
            target: BPMNElement
            if source_ref == target.get_id():
                sequence_sources.append(target)

        # Sequence Flow can only point to one source and target
        # so far!
        return BPMNSequenceFlow(id=id, source=sequence_sources[0], target=sequence_targets[0])


    def make_bpmn_element(element: Element) -> Tuple[str, str]:
        id = element.get('id')
        name = element.get('name')
        return id, name

    def make_activity(element:Element) -> BPMNActivity:
        id, name = ModelBuilder.make_bpmn_element(element=element)
        return BPMNActivity(id=id, name=name, sequenceFlowIn=None, sequenceFlowOut=None)
