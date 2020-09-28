from typing import List, Union

import nltk
from nltk.corpus.reader import Synset
from pedantic import pedantic_class

from src.exception.language_processing_errors import EmptySynonymCloudError, \
    ChunkSynonymCloudMismatch
from src.nlp.synonym_composite import SynonymComposite


@pedantic_class
class SynonymCloud:
    """
    A class where all synonyms of a word are grouped together.
    Imaging the word 'sign a contract'. If you use synonyms and say
    'underwrite an agreement' you are basically saying the same.
    'sign an agreement' and 'underwrite a contract' would be correct too.
    In a SynonymCloud we hold all these combinations of a text.
    It behaves like a power set but we implement it via wordnet.
    A SynonymCloud knows best if another text snippet is synonym to the syncloud
    """

    def __init__(self, syncloud: List[SynonymComposite]) -> None:
        self.syncloud = syncloud

    @classmethod
    def from_list(cls, text: List[Union[str, Synset]]) -> 'SynonymCloud':
        syn_composites = []
        for word in text:
            if isinstance(word, str):
                syn_comp = SynonymComposite.from_str(word=word)
                syn_composites.append(syn_comp)
            else:
                # word is synset
                syn_comp = SynonymComposite.from_synset(synset=word)
                syn_composites.append(syn_comp)
        return cls(syncloud=syn_composites)

    def are_synonyms(self, chunk: nltk.tree.Tree) -> bool:

        if len(self.syncloud) == 0:
            raise EmptySynonymCloudError(syncloud=self)

        chunk_len = len(chunk.leaves())
        if chunk_len != len(self.syncloud):
            raise ChunkSynonymCloudMismatch(synonym_cloud=self, chunk=chunk)

        # check for syonyms
        for idx, composite in enumerate(self.syncloud):
            chunk_word = chunk.leaves()[idx]
            if not composite.are_synonyms(
                    tagged_word=chunk_word):
                return False

        return True

    def __str__(self) -> str:
        return self.syncloud.__str__()

    def __repr__(self) -> str:
        return self.__str__()
