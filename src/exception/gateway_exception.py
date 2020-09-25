from typing import List

from src.converter.bpmn_models.bpmn_element import BPMNElement
from src.converter.bpmn_models.bpmn_sequenceflow import BPMNSequenceFlow
from src.converter.bpmn_models.gateway.bpmn_gateway import BPMNGateway


class ExclusiveGatewayBranchError(Exception):
    def __init__(self, gateway: BPMNGateway, flows: List[BPMNSequenceFlow]):
        self.message = f'exclusive gateway {gateway} can only branch into 1 ' \
                       f'branch. Wanted to branch into: {flows} ' \
                       f'which are {len(flows)} branches.'
        super().__init__(self.message)

class OpeningGatewayBranchError(Exception):
    def __init__(self, gateway: BPMNGateway):
        self.message = f'The opening gateway: {gateway} cannot have ' \
                        f'0 outgoing sequence_flows. This contradicts ' \
                        f'BPMN-specification.'
        super().__init__(self.message)


class ClosingGatewayBranchError(Exception):
    def __init__(self, gateway: BPMNGateway, branch_elements: List[BPMNElement]):
        self.message = f'Closing gateway {gateway} has not exactly 1 outgoing ' \
                       f'branch vertex. Found: {len(branch_elements)}. ' \
                       f'This contradicts BPMN-specification.'
        super().__init__(self.message)
