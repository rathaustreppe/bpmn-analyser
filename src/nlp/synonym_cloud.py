from typing import Tuple, List

import nltk
from nltk.corpus import wordnet
from nltk.corpus.reader import Synset
from pedantic import pedantic_class

from src.nlp.synonym_composite import SynonymComposite


@pedantic_class
class SynonymCloud:
    """
    A class where all synonyms of a text are grouped together.
    Imaging the text 'sign a contract'. If you use synonyms and say
    'underwrite an agreement' you are basically saying the same.
    'sign an agreement' and 'underwrite a contract' would be correct too.
    In a SynonymCloud we hold all these combinations of a text snippet -> chunk.
    It behaves like a power set but we implement it via wordnet.
    A SynonymCloud knows best if other chunks are synonym to the syncloud.
    """
    def __init__(self, syncloud: List[SynonymComposite]) -> None:
        self.syncloud = syncloud


    def are_synonyms(self, chunk: nltk.tree.Tree) -> bool:
        # chunk length == syncloud length?
        chunk_len = len(chunk.leaves())
        if chunk_len != len(self.syncloud):
            raise Exception(f'length of chunk {chunk} (length:{chunk_len})'
                            f' and syncloud {self.syncloud}  '
                            f'(length:{len(self.syncloud)}) do not match.')

        # access chunk words
        list_chunk_words = []
        for leave in chunk.leaves():
            list_chunk_words.append(leave[0])

        # check for syonyms
        for idx, composite in enumerate(self.syncloud):
            chunk_word = chunk.leaves()[idx]
            if not composite.are_synonyms(tagged_word=chunk_word):
                return False

        return True




