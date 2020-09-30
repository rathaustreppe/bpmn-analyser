from typing import List, Tuple, Optional
from xml.etree.ElementTree import Element

from pedantic import pedantic_class

from src.converter.bpmn_models.bpmn_activity import \
    BPMNActivity
from src.converter.bpmn_models.bpmn_element import \
    BPMNElement
from src.converter.bpmn_models.bpmn_enum import BPMNEnum
from src.converter.bpmn_models.bpmn_sequenceflow import \
    BPMNSequenceFlow
from src.converter.bpmn_models.event.bpmn_endevent import \
    BPMNEndEvent
from src.converter.bpmn_models.event.bpmn_startevent import \
    BPMNStartEvent
from src.converter.bpmn_models.gateway.bpmn_exclusive_gateway import \
    BPMNExclusiveGateway
from src.converter.bpmn_models.gateway.bpmn_inclusive_gateway import \
    BPMNInclusiveGateway
from src.converter.bpmn_models.gateway.bpmn_parallel_gateway import \
    BPMNParallelGateway
from src.converter.i_bpmn_factory import IBPMNFactory
from src.exception.wrong_type_errors import NotImplementedTypeError
from src.models.token_state_condition import TokenStateCondition


@pedantic_class
class BPMNFactory(IBPMNFactory):
    # Attention: BPMNFactory can only, by definition, work
    # with valid xml + valid bpmn strings and builds python objects of the data
    # in those xml files. The program is
    # designed that a factory is only instantiated when the
    # xml is conform to XML and BPMN standard. Therefore it cannot handle
    # corrupt files or file-definitions.
    # This would be okay: <task id="" condition=""></task>'
    # This not: <task></task>'
    def create_bpmn_element(self,
                            element: Element,
                            elem_type: BPMNEnum,
                            src_tgt_elements: Optional[
                                List[BPMNElement]] = None) -> BPMNElement:
        if elem_type == BPMNEnum.STARTEVENT:
            return self._create_start_event(element=element)

        elif elem_type == BPMNEnum.ENDEVENT:
            return self._create_end_event(element=element)

        elif elem_type == BPMNEnum.ACTIVITY:
            return self._create_activity(element=element)

        elif elem_type == BPMNEnum.SEQUENCEFLOW:
            return self._create_sequence_flow(sequence_flow=element,
                                              elements=src_tgt_elements)

        elif elem_type == BPMNEnum.PARALLGATEWAY:
            return self._create_parallel_gateway(element=element)

        elif elem_type == BPMNEnum.INCLGATEWAY:
            return self._create_inclusive_gateway(element=element)

        elif elem_type == BPMNEnum.EXCLGATEWAY:
            return self._create_exclusive_gateway(element=element)

        else:
            raise NotImplementedTypeError(object_=elem_type.value)

    def _create_end_event(self, element: Element) -> BPMNEndEvent:
        id_, name = self._create_bpmn_element(element=element)
        return BPMNEndEvent(id_=id_, name=name, sequence_flow=None)

    def _create_start_event(self, element: Element) -> BPMNStartEvent:
        id_, name = self._create_bpmn_element(element=element)
        return BPMNStartEvent(id_=id_, name=name, sequence_flow=None)

    def _create_bpmn_element(self, element: Element) -> Tuple[str, str]:
        id_ = element.get(BPMNEnum.ID.value)
        name = element.get(BPMNEnum.NAME.value)
        return id_, name

    def _create_activity(self, element: Element) -> BPMNActivity:
        id_, name = self._create_bpmn_element(element=element)
        return BPMNActivity(id_=id_, name=name, sequence_flow_in=None,
                            sequence_flow_out=None)

    def _create_parallel_gateway(self, element: Element) -> BPMNParallelGateway:
        id_ = element.get(BPMNEnum.ID.value)
        return BPMNParallelGateway(id_=id_, sequence_flows_in=None,
                                   sequence_flows_out=None)

    def _create_inclusive_gateway(self,
                                  element: Element) -> BPMNInclusiveGateway:
        id_ = element.get(BPMNEnum.ID.value)
        return BPMNInclusiveGateway(id_=id_, sequence_flows_in=None,
                                    sequence_flows_out=None)

    def _create_exclusive_gateway(self,
                                  element: Element) -> BPMNExclusiveGateway:
        id_ = element.get(BPMNEnum.ID.value)
        return BPMNExclusiveGateway(id_=id_, sequence_flows_in=None,
                                    sequence_flows_out=None)

    def _create_sequence_flow(self,
                              sequence_flow: Element,
                              elements: List[BPMNElement]) -> BPMNSequenceFlow:
        """
        We fully build a sequence flow here. We take the
        BPMN-elements as a list to search for the object
        references.
        """
        # ToDo: What should happen if sourceRef == '' or elements.id_ == '' ??
        # Reject earlier or raise exception?

        id_ = sequence_flow.get(BPMNEnum.ID.value)
        # name tag in xml (== the text of the element) is treated as a condition
        condition = sequence_flow.get(BPMNEnum.NAME.value)
        if condition is not None:
            condition = TokenStateCondition.from_string(condition=condition)

        source_ref = sequence_flow.get('sourceRef')
        target_ref = sequence_flow.get('targetRef')

        # Notice how a sequence flow target is incoming for
        # activities. And how outgoing for a activity means
        # source for a sequence flow!
        # If we want to check where our SequenceFlow points
        # to (our target) we look on the other side: the source-
        # attribute of our BPMN-elements.
        sequence_targets = []
        for source in elements:
            source: BPMNElement
            if target_ref == source.id_:
                sequence_targets.append(source)

        sequence_sources = []
        for target in elements:
            target: BPMNElement
            if source_ref == target.id_:
                sequence_sources.append(target)

        return BPMNSequenceFlow(id_=id_, condition=condition,
                                source=sequence_sources[0],
                                target=sequence_targets[0])
