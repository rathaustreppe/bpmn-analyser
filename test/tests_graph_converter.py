import os
from typing import List

import pytest
from igraph import EdgeSeq, Vertex, VertexSeq, Edge

from src.converter.bpmn_converter import BPMNConverter
from src.converter.bpmn_factory import BPMNFactory
from src.converter.bpmn_models.bpmn_enum import BPMNEnum
from src.converter.bpmn_models.bpmn_model import BPMNModel
from src.converter.graph_converter import GraphConverter
from src.converter.xml_reader import XMLReader


class TestGraphConverter:

    def converter_xmls(self) -> str:
        pytest_root = os.path.dirname(os.path.abspath(__file__))
        working_dict = os.path.join(pytest_root, 'test_files', 'xml',
                                    'converter')
        return working_dict

    def all_bpmn_types(self) -> List[BPMNEnum]:
        return [BPMNEnum.STARTEVENT, BPMNEnum.ENDEVENT, BPMNEnum.ACTIVITY,
                BPMNEnum.PARALLGATEWAY, BPMNEnum.EXCLGATEWAY,
                BPMNEnum.INCLGATEWAY]

    def create_model(self, filename: str) -> BPMNModel:
        bpmn_converter = BPMNConverter(xml_reader=XMLReader(),
                                       bpmn_factory=BPMNFactory())
        file_path = os.path.join(self.converter_xmls(), filename)
        bpmn_converter.xml_reader.parse_to_dom(abs_path=file_path)
        return bpmn_converter.create_all_bpmn_objects(
            bpmn_types=self.all_bpmn_types())

    def create_converter(self, bpmn_model: BPMNModel) -> GraphConverter:
        return GraphConverter(bpmn_model=bpmn_model)

    def find_edge_by_id(self, edges: EdgeSeq, id: str) -> Edge:
        edges = [edge for edge in edges if edge[BPMNEnum.ID.value] == id]

        if len(edges) == 0:
            raise ValueError(f'no elements with id={id} in {edges} found')

        if len(edges) > 1:
            raise ValueError(f'Error in testdata.'
                             f'Multiple used IDs detected: {id}')
        return edges[0]

    def find_vertex_by_id(self, vertices: VertexSeq, id: str) -> Vertex:
        vertices = [vertex for vertex in vertices if vertex[BPMNEnum.ID.value] == id]

        if len(vertices) == 0:
            raise ValueError(f'no elements with id={id} in {vertices} found')

        if len(vertices) > 1:
            raise ValueError(f'Error in testdata.'
                             f'Multiple used IDs detected: {id}')
        return vertices[0]

    def test_put_activity_in_graph(self):
        model = self.create_model(filename='A.bpmn')
        gc = self.create_converter(bpmn_model=model)

        gc.init_graph(number_of_vertices=len(model.bpmn_elements))

        assert len(model.bpmn_elements) == 1
        activity = model.bpmn_elements[0]

        gc.put_vertex_in_graph(element=activity, idx=0)
        assert len(gc.graph.vs) == 1

        vertex = gc.graph.vs[0]
        assert vertex[BPMNEnum.ID.value] == activity.id
        assert vertex[BPMNEnum.NAME.value].get_text() == activity.name

    def test_overwrite_existing_vertex(self):
        model = self.create_model(filename='A.bpmn')
        gc = self.create_converter(bpmn_model=model)

        assert len(model.bpmn_elements) == 1
        gc.init_graph(number_of_vertices=len(model.bpmn_elements))

        activity = model.bpmn_elements[0]
        gc.put_vertex_in_graph(element=activity, idx=0)
        with pytest.raises(IndexError):
            gc.put_vertex_in_graph(element=activity, idx=0)

    def test_put_start_event_in_graph(self):
        model = self.create_model(filename='S.bpmn')
        gc = self.create_converter(bpmn_model=model)

        assert len(model.bpmn_elements) == 1
        gc.init_graph(number_of_vertices=len(model.bpmn_elements))

        start_event = model.bpmn_elements[0]
        gc.put_vertex_in_graph(element=start_event, idx=0)

        vertex = gc.graph.vs[0]
        assert vertex[BPMNEnum.ID.value] == start_event.id
        assert vertex[BPMNEnum.NAME.value].get_text() == start_event.name

    def test_put_end_event_in_graph(self):
        model = self.create_model(filename='E.bpmn')
        gc = self.create_converter(bpmn_model=model)

        assert len(model.bpmn_elements) == 1
        gc.init_graph(number_of_vertices=len(model.bpmn_elements))

        end_event = model.bpmn_elements[0]
        gc.put_vertex_in_graph(element=end_event, idx=0)

        vertex = gc.graph.vs[0]
        assert vertex[BPMNEnum.ID.value] == end_event.id
        assert vertex[BPMNEnum.NAME.value].get_text() == end_event.name

    def test_put_parallel_gateway_in_graph(self):
        model = self.create_model(filename='parallel_gateway.bpmn')
        gc = self.create_converter(bpmn_model=model)

        assert len(model.bpmn_elements) == 1
        gc.init_graph(number_of_vertices=len(model.bpmn_elements))

        gateway = model.bpmn_elements[0]
        gc.put_vertex_in_graph(element=gateway, idx=0)

        vertex = gc.graph.vs[0]
        assert vertex[BPMNEnum.ID.value] == gateway.id
        assert vertex[BPMNEnum.NAME.value].get_text() == BPMNEnum.PARALLGATEWAY_TEXT.value

    def test_put_exclusive_gateway_in_graph(self):
        model = self.create_model(filename='exclusive_gateway.bpmn')
        gc = self.create_converter(bpmn_model=model)

        assert len(model.bpmn_elements) == 1
        gc.init_graph(number_of_vertices=len(model.bpmn_elements))

        gateway = model.bpmn_elements[0]
        gc.put_vertex_in_graph(element=gateway, idx=0)

        vertex = gc.graph.vs[0]
        assert vertex[BPMNEnum.ID.value] == gateway.id
        assert vertex[BPMNEnum.NAME.value].get_text() == BPMNEnum.EXCLGATEWAY_TEXT.value

    def test_put_inclusive_gateway_in_graph(self):
        model = self.create_model(filename='inclusive_gateway.bpmn')
        gc = self.create_converter(bpmn_model=model)

        assert len(model.bpmn_elements) == 1
        gc.init_graph(number_of_vertices=len(model.bpmn_elements))

        gateway = model.bpmn_elements[0]
        gc.put_vertex_in_graph(element=gateway, idx=0)

        vertex = gc.graph.vs[0]
        assert vertex[BPMNEnum.ID.value] == gateway.id
        assert vertex[BPMNEnum.NAME.value].get_text() == BPMNEnum.INCLGATEWAY_TEXT.value

    def test_put_edge_in_graph(self):
        model = self.create_model(filename='S_to_E.bpmn')
        gc = self.create_converter(bpmn_model=model)

        assert len(model.bpmn_elements) == 2
        gc.init_graph(number_of_vertices=len(model.bpmn_elements))

        assert len(model.sequence_flows) == 1
        flow = model.sequence_flows[0]

        gc.put_vertex_in_graph(element=model.bpmn_elements[0], idx=0) #startEvent
        gc.put_vertex_in_graph(element=model.bpmn_elements[1], idx=1) #endEvent
        gc.put_edges_in_graph(sequence_flows=[flow])

        assert len(gc.graph.es) == 1
        edge = gc.graph.es[0]

        start_event_idx = gc.find_vertex(vertices=gc.graph.vs,
                                         vertex_id=model.bpmn_elements[0].id).index
        end_event_idx = gc.find_vertex(vertices=gc.graph.vs,
                                       vertex_id=model.bpmn_elements[1].id).index
        assert edge.source == start_event_idx
        assert edge.target == end_event_idx

    def test_put_edge_twice_in_graph(self):
        model = self.create_model(filename='S_to_E.bpmn')
        gc = self.create_converter(bpmn_model=model)

        assert len(model.bpmn_elements) == 2
        gc.init_graph(number_of_vertices=len(model.bpmn_elements))

        assert len(model.sequence_flows) == 1
        flow = model.sequence_flows[0]

        gc.put_vertex_in_graph(element=model.bpmn_elements[0],idx=0) #startEvent
        gc.put_vertex_in_graph(element=model.bpmn_elements[1],idx=1) #endEvent
        gc.put_edges_in_graph(sequence_flows=[flow])
        with pytest.raises(ValueError):
            gc.put_edges_in_graph(sequence_flows=[flow])