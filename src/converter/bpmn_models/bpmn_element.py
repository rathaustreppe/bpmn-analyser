from pedantic import pedantic_class

'''
Metaclass for BPMNEvents, BPMNActivities, BPMNSequenceflows.
Basically for everything that is in a diagram.
'''


@pedantic_class
class BPMNElement:
    def __init__(self, id_: str) -> None:
        self.id_ = id_
