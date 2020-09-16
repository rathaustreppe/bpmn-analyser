import pytest
from igraph import EdgeSeq, Vertex, VertexSeq, Edge


class TestGraphConverter:

    def find_edge_by_id(self, edges: EdgeSeq, id: str) -> Edge:
        edges = [edge for edge in edges if edge['id'] == id]

        if len(edges) == 0:
            raise ValueError(f'no elements with id={id} in {edges} found')

        if len(edges) > 1:
            raise ValueError(f'Error in testdata.'
                             f'Multiple used IDs detected: {id}')
        return edges[0]

    def find_vertex_by_id(self, vertices: VertexSeq, id:str) -> Vertex:
        vertices = [vertex for vertex in vertices if vertex['id'] == id]

        if len(vertices) == 0:
            raise ValueError(f'no elements with id={id} in {vertices} found')

        if len(vertices) > 1:
            raise ValueError(f'Error in testdata.'
                             f'Multiple used IDs detected: {id}')
        return vertices[0]


    def test_1(self):
        pass