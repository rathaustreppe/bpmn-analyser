import igraph

from src.converter.bpmn_models.bpmn_model import BPMNModel


# class GraphNotDirectedError(Exception):
#     def __init__(self, graph: igraph.Graph):
#         self.message = f'graph: {graph} is not directed'
#         super().__init__(self.message)


class NoStartEventError(Exception):
    def __init__(self, model: BPMNModel):
        self.message = f'model: {model} has no starting point'
        super().__init__(self.message)


class MultipleStartEventsError(Exception):
    def __init__(self, model: BPMNModel):
        self.message = f'model: {model} has multiple start events'
        super().__init__(self.message)
