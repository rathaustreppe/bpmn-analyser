import igraph


class GraphNotDirectedError(Exception):
    def __init__(self, graph: igraph.Graph):
        self.message = f'graph: {graph} is not directed'
        super().__init__(self.message)


class GraphHasNoStartError(Exception):
    def __init__(self, graph: igraph.Graph):
        self.message = f'graph: {graph} has no starting point'
        super().__init__(self.message)


class GraphHasMultipleStartsError(Exception):
    def __init__(self, graph: igraph.Graph):
        self.message = f'graph: {graph} has multiple starting points'
        super().__init__(self.message)
