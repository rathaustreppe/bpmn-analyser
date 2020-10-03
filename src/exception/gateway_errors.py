from typing import List

from src.converter.bpmn_models.bpmn_sequenceflow import BPMNSequenceFlow


class ExclusiveGatewayBranchError(Exception):
    def __init__(self, gateway: 'BPMNGateway', flows: List[BPMNSequenceFlow]):
        self.message = f'exclusive gateway {gateway} can only branch into 1 ' \
                       f'branch. Wanted to branch into: {flows} ' \
                       f'which are {len(flows)} branches.'
        super().__init__(self.message)

class BranchingGatewayError(Exception):
    def __init__(self, gateway: 'BPMNGateway'):
        self.message = f'The branching gateway: {gateway} cannot have ' \
                        f'0 outgoing sequence_flows. This contradicts ' \
                        f'BPMN-specification.'
        super().__init__(self.message)


class JoiningGatewayError(Exception):
    def __init__(self, gateway: 'BPMNGateway'):
        self.message = f'Joining gateway {gateway} has not exactly 1 outgoing ' \
                       f'sequence flow. Found: {len(gateway.sequence_flows_out)}. ' \
                       f'This contradicts BPMN-specification.'
        super().__init__(self.message)

class BranchJoiningGatewayError(Exception):
    def __init__(self, gateway: 'BPMNGateway'):
        self.message = f'Gateway {gateway} is a branching and joining gateway.' \
                       f'This is not allowed. Use two gateways to join first' \
                       f'and then branch.'