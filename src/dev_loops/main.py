

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
    visited = []
    queue = MyQueue()

    visited.append(first_edge)
    queue.queue(first_edge)

    print(queue)
    while queue.not_empty():
        edge = queue.dequeue()
        print(f'dequeued edge: {edge}')

        # find all edges after target vertex of any_edge
        edges_after_vertex = graph.edges_after_vertex(edge)

        # check conditions...
        edges_with_passed_conditions = edges_after_vertex

        # my_queue edges when they are not visited
        for edge in edges_with_passed_conditions:
            if edge not in visited:
                visited.append(edge)
                print(f'append visited:{edge}')
                queue.queue(edge)

                # visited ist nicht richtig.
                # eher drehen auf abgearbeitet
                # wenn abgearbeitet, dann auf die liste
                # und wenn dequeued wird, wird gerprüft ob es schon abgearbeitet wurde