from typing import List, Tuple, Optional
from xml.etree.ElementTree import Element

from pedantic import pedantic_class

from src.converter.bpmn_models.gateway.bpmn_exclusive_gateway import \
    BPMNExclusiveGateway
from src.converter.bpmn_models.gateway.bpmn_inclusive_gateway import \
    BPMNInclusiveGateway
from src.converter.bpmn_models.gateway.bpmn_parallel_gateway import \
    BPMNParallelGateway
from src.converter.i_bpmn_factory import IBPMNFactory
from src.converter.bpmn_models.bpmn_activity import \
    BPMNActivity
from src.converter.bpmn_models.bpmn_element import \
    BPMNElement
from src.converter.bpmn_models.event.bpmn_endevent import \
    BPMNEndEvent
from src.converter.bpmn_models.bpmn_enum import BPMNEnum
from src.converter.bpmn_models.bpmn_sequenceflow import \
    BPMNSequenceFlow
from src.converter.bpmn_models.event.bpmn_startevent import \
    BPMNStartEvent


@pedantic_class
class BPMNFactory(IBPMNFactory):
    def create_bpmn_element(self,
                            element: Element,
                            elem_type: BPMNEnum,
                            src_tgt_elements: Optional[List[BPMNElement]] = None) -> BPMNElement:
        if elem_type == BPMNEnum.STARTEVENT:
            return self._create_start_event(element=element)

        elif elem_type == BPMNEnum.ENDEVENT:
            return self._create_end_event(element=element)

        elif elem_type == BPMNEnum.ACTIVITY:
            return self._create_activity(element=element)

        elif elem_type == BPMNEnum.SEQUENCEFLOW:
            return self._create_sequenceflow(sequence_flow=element,
                                             elements=src_tgt_elements)

        elif elem_type == BPMNEnum.PARALLGATEWAY:
            return self._create_parallel_gateway(element=element)

        elif elem_type == BPMNEnum.INCLGATEWAY:
            return self._create_inclusive_gateway(element=element)

        elif elem_type == BPMNEnum.EXCLGATEWAY:
            return self._create_exclusive_gateway(element=element)

        else:
            raise ValueError(
                f'BPMNEnum {BPMNEnum} with value {BPMNEnum.value} is not \
                implemented'
            )

    def _create_end_event(self, element: Element) -> BPMNEndEvent:
        id, name = self._create_bpmn_element(element=element)
        return BPMNEndEvent(id=id, name=name, sequenceFlow=None)

    def _create_start_event(self, element: Element) -> BPMNStartEvent:
        id, name = self._create_bpmn_element(element=element)
        return BPMNStartEvent(id=id, name=name, sequenceFlow=None)

    def _create_bpmn_element(self, element: Element) -> Tuple[str, str]:
        id = element.get('id')
        name = element.get('name')
        return id, name

    def _create_activity(self, element: Element) -> BPMNActivity:
        id, name = self._create_bpmn_element(element=element)
        return BPMNActivity(id=id,
                            name=name,
                            sequenceFlowIn=None,
                            sequenceFlowOut=None)

    def _create_parallel_gateway(self, element: Element) -> BPMNParallelGateway:
        id = element.get('id')
        return BPMNParallelGateway(id=id,
                                   sequence_flows_in=None,
                                   sequence_flows_out=None)

    def _create_inclusive_gateway(self, element: Element) -> BPMNInclusiveGateway:
        id = element.get('id')
        return BPMNInclusiveGateway(id=id,
                                    sequence_flows_in=None,
                                    sequence_flows_out=None)

    def _create_exclusive_gateway(self, element: Element) -> BPMNExclusiveGateway:
        id = element.get('id')
        return BPMNExclusiveGateway(id=id,
                                    sequence_flows_in=None,
                                    sequence_flows_out=None)


    def _create_sequenceflow(self,
                             sequence_flow: Element,
                             elements: List[BPMNElement]) -> BPMNSequenceFlow:
        """
        We fully build a sequence flow here. We take the
        BPMN-elements as a list to search for the object
        references.
        Args:
            sequence_flow:
            elements:

        Returns:

        """
        # ToDo: What should happen if sourceRef == '' or elements.id == '' ??
        # Reject earlier or raise exception?

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
            if target_ref == source.id:
                sequence_targets.append(source)

        sequence_sources = []
        for target in elements:
            target: BPMNElement
            if source_ref == target.id:
                sequence_sources.append(target)

        # Sequence Flow can only point to one source and target
        # so far!
        return BPMNSequenceFlow(id=id,
                                source=sequence_sources[0],
                                target=sequence_targets[0])
