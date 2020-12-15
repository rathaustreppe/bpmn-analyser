from typing import List, Optional

from pedantic import pedantic_class

from src.converter.bpmn_models.gateway.bpmn_gateway import BPMNGateway
from src.converter.bpmn_models.bpmn_sequenceflow import BPMNSequenceFlow


@pedantic_class
class BPMNParallelGateway(BPMNGateway):
    def __init__(self, id_: str,
                 sequence_flows_in: Optional[List[BPMNSequenceFlow]] = None,
                 sequence_flows_out: Optional[List[BPMNSequenceFlow]] = None) -> None:
        super().__init__(id_=id_, sequence_flows_in=sequence_flows_in,
                         sequence_flows_out=sequence_flows_out)

    def __str__(self) -> str:
        return 'BPMNParallelGateway'

    def __repr__(self) -> str:
        return self.__str__()