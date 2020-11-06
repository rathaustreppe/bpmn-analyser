import logging

from typing import List, Tuple

from nltk import Tree


class NoChunkFoundError(Exception):
    def __init__(self, pos_list: List[Tuple[str, str]], chunker: 'Chunker'):
        self.message = f'no chunk in text {pos_list} found. ' \
                       f'Used grammars: {chunker.grammars}'
        super().__init__(self.message)
        logging.error(self.message)


class MultipleChunksFoundError(Exception):
    def __init__(self, pos_list: List[Tuple[str, str]],
                 found_chunks: List[Tree],
                 chunker: 'Chunker'):
        self.message = f'{len(found_chunks)} chunks found in text {pos_list},' \
                       f'instead of only one. Found chunks: {found_chunks}. ' \
                       f'Used chunker: {chunker}'
        super().__init__(self.message)
        logging.error(self.message)


class EmptySynonymCloudError(Exception):
    def __init__(self, syncloud: 'SynonymCloud'):
        self.message =f' Synonymcloud {syncloud} cannot be empty'
        super().__init__(self.message)
        logging.error(self.message)


class ChunkSynonymCloudMismatch(Exception):
    def __init__(self, synonym_cloud: 'SynonymCloud', chunk: Tree):
        self.message = f'length of chunk {chunk} with length:{len(chunk)} ' \
                       f' and syncloud {synonym_cloud} with length ' \
                       f'{len(synonym_cloud)} do not match.'
        super().__init__(self.message)
        logging.error(self.message)
