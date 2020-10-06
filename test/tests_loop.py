import os
from typing import List

from src.converter.converter import Converter
from src.graph_pointer import GraphPointer
from src.models.token import Token
from src.models.token_state_rule import TokenStateRule
from src.nlp.chunker import Chunker


class TestLoop:
    """
    Contains all tests for testing different loops in the diagram.
    """

    def run_pointer(self, graph_pointer: GraphPointer) -> Token:
        ret = graph_pointer.iterate_model()
        if ret[0] == 0:
            return graph_pointer.token
        else:
            # infinite loop
            assert False

    def execute_process(self, filename: str,
                        xml_folders_path,
                        chunker,
                        ruleset,
                        init_token) -> Token:

        xml_file_path = os.path.join(xml_folders_path, 'loop', filename)

        converter = Converter()
        model = converter.convert(rel_path_to_bpmn=xml_file_path)

        graph_pointer = GraphPointer(model=model,
                                     token=init_token,
                                     ruleset=ruleset,
                                     chunker=chunker)

        return self.run_pointer(graph_pointer=graph_pointer)

    def test_simple_increment_loop(self, xml_folders_path, nn_chunker):
        def get_init_token() -> Token:
            init_attributes = {
                'a' :'0'
            }
            return Token(attributes=init_attributes)

        def get_solution_token() -> Token:
            init_attributes = {
                'a' :'2'
            }
            return Token(attributes=init_attributes)

        def get_ruleset() -> List[TokenStateRule]:
            # empty ruleset, because RuleFinder generates rule for increment
            return []

        def get_chunker() -> Chunker:
            # just return any chunker, because increments bypass Chunker
            return nn_chunker

        solution_token = get_solution_token()
        return_token = self.execute_process(filename='simple_increment_loop.bpmn',
                                            xml_folders_path=xml_folders_path,
                                            chunker=get_chunker(),
                                            ruleset=get_ruleset(),
                                            init_token=get_init_token())
        assert solution_token == return_token


    def test_two_simple_increment_loops(self, xml_folders_path, nn_chunker):
        def get_init_token() -> Token:
            init_attributes = {
                'a' :'0',
                'b' :'0'
            }
            return Token(attributes=init_attributes)

        def get_solution_token() -> Token:
            init_attributes = {
                'a' :'2',
                'b' :'2'
            }
            return Token(attributes=init_attributes)

        def get_ruleset() -> List[TokenStateRule]:
            # empty ruleset, because RuleFinder generates rule for increment
            return []

        def get_chunker() -> Chunker:
            # just return any chunker, because increments bypass Chunker
            return nn_chunker

        solution_token = get_solution_token()
        return_token = self.execute_process \
            (filename='two_simple_increment_loops.bpmn',
                                            xml_folders_path=xml_folders_path,
                                            chunker=get_chunker(),
                                            ruleset=get_ruleset(),
                                            init_token=get_init_token())
        assert solution_token == return_token

    def test_two_interlaced_loops(self, xml_folders_path, nn_chunker):
        def get_init_token() -> Token:
            init_attributes = {
                'a' :'0',
                'b' :'0'
            }
            return Token(attributes=init_attributes)

        def get_solution_token() -> Token:
            init_attributes = {
                'a' :'3',
                'b' :'1'
            }
            return Token(attributes=init_attributes)

        def get_ruleset() -> List[TokenStateRule]:
            # empty ruleset, because RuleFinder generates rule for increment
            return []

        def get_chunker() -> Chunker:
            # just return any chunker, because increments bypass Chunker
            return nn_chunker

        solution_token = get_solution_token()
        return_token = self.execute_process(filename='two_interlaced_loops.bpmn',
                                            xml_folders_path=xml_folders_path,
                                            chunker=get_chunker(),
                                            ruleset=get_ruleset(),
                                            init_token=get_init_token())
        assert solution_token == return_token

    def test_generator_loop(self, xml_folders_path, nn_chunker):
        # This loop increments b twice but while doing it, it is connected
        # to a parallel gateway which branches twice into incrementing a.
        # So while looping b, a is modified as well. (Side effects)
        def get_init_token() -> Token:
            init_attributes = {
                'a' :'0',
                'b' :'0'
            }
            return Token(attributes=init_attributes)

        def get_solution_token() -> Token:
            init_attributes = {
                'a' :'2',
                'b' :'2'
            }
            return Token(attributes=init_attributes)

        def get_ruleset() -> List[TokenStateRule]:
            # empty ruleset, because RuleFinder generates rule for increment
            return []

        def get_chunker() -> Chunker:
            # just return any chunker, because increments bypass Chunker
            return nn_chunker

        solution_token = get_solution_token()
        return_token = self.execute_process(filename='generator_loop.bpmn',
                                            xml_folders_path=xml_folders_path,
                                            chunker=get_chunker(),
                                            ruleset=get_ruleset(),
                                            init_token=get_init_token())
        assert solution_token == return_token

    def test_generator_loop_different_order(self, xml_folders_path,
                            nn_chunker):
        # in the generator_loop test a is modified first,
        # then b. In this test we changed the order, so
        # b is modified first, then a.
        def get_init_token() -> Token:
            init_attributes = {
                'a': '0',
                'b': '0'
            }
            return Token(attributes=init_attributes)

        def get_solution_token() -> Token:
            init_attributes = {
                'a': '2',
                'b': '2'
            }
            return Token(attributes=init_attributes)

        def get_ruleset() -> List[TokenStateRule]:
            # empty ruleset, because RuleFinder generates rule for increment
            return []

        def get_chunker() -> Chunker:
            # just return any chunker, because increments bypass Chunker
            return nn_chunker

        solution_token = get_solution_token()
        return_token = self.execute_process(
            filename='generator_loop_different_order.bpmn',
            xml_folders_path=xml_folders_path,
            chunker=get_chunker(),
            ruleset=get_ruleset(),
            init_token=get_init_token())
        assert solution_token == return_token