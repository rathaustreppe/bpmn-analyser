from typing import List

import igraph


class ExclusiveGatewayBranchError(Exception):
    def __init__(self, gateway: igraph.Vertex, edges: List[igraph.Edge]):
        self.message = f'exclusive gateway {gateway} can only branch into 1 ' \
                       f'branch. Wanted to branch into: {edges} ' \
                       f'which are {len(edges)} branches.'
        super().__init__(self.message)
