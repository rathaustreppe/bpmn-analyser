

# Simple independent program to test algorithm
# for BFS, gated gateways, strongly connected components
# and a new graph implementation to process loops
import queue

from src.dev_loops.graph import Graph
from src.dev_loops.myqueue import MyQueue

if __name__ == '__main__':

    # graph
    g = {'A': ['B'],
             'B': ['C', 'D', 'E'],
             'C': ['D', 'D'],
             'D': ['E'],
             'E': ['F'], #ohne loop E -> C
             'F': []
             }
    graph = Graph(g)

    # first node
    first_edge = ('A', 'B')

    # BFS
    processed = []
    queue = MyQueue()

    queue.queue(first_edge)

    print(queue)
    while queue.not_empty():
        edge = queue.dequeue()
        if edge in processed:
            print(f'edge already processed: {edge}')
            continue
        print(f'edge to process: {edge}')

        # find all edges after target vertex of any_edge
        edges_after_vertex = graph.edges_after_vertex(edge)

        # check conditions...
        edges_with_passed_conditions = edges_after_vertex

        # queue edges when they are not processed
        for e in edges_with_passed_conditions:
            queue.queue(e)
            print(f'edge put in queue: {e}')

        processed.append(edge)

                # processed ist nicht richtig.
                # eher drehen auf abgearbeitet
                # wenn abgearbeitet, dann auf die liste
                # und wenn dequeued wird, wird gerprüft ob es schon abgearbeitet wurde