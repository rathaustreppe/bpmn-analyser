from pedantic import pedantic_class

'''
Metaclass for everything that can be displayed graphically in a BPMNChart:
Gateways, Events, Acitivities, Flows (== edges) between those object...
'''


@pedantic_class
class BPMNFlowObject:
    def __init__(self, id_: str) -> None:
        self.id_ = id_
