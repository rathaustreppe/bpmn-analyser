from typing import List, Union

import nltk
from nltk.corpus.reader import Synset
from pedantic import pedantic_class

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
    def from_list(cls, text:List[Union[str,Synset]]):
        syn_composites = []
        for word in text:
            if isinstance(word, str):
                syn_comp = SynonymComposite.from_str(word=word)
                syn_composites.append(syn_comp)
            elif isinstance(word, Synset):
                syn_comp = SynonymComposite.from_synset(synset=word)
                syn_composites.append(syn_comp)
            else:
                raise ValueError(f'bad data type in list {text}: '
                                 f'{word} has type {type(word)}.')

    def are_synonyms(self, chunk: nltk.tree.Tree) -> bool:

        if len(self.syncloud) == 0:
            raise ValueError(f'syncloud {self} cannot be empty')

        chunk_len = len(chunk.leaves())
        if chunk_len != len(self.syncloud):
            raise Exception(f'length of chunk {chunk} with length:{chunk_len} '
                            f' and syncloud {self.syncloud} with length'
                            f' {len(self.syncloud)}) do not match.')

        # check for syonyms
        for idx, composite in enumerate(self.syncloud):
            chunk_word = chunk.leaves()[idx]
            if not composite.are_synonyms(tagged_word=chunk_word): # may not work? not tagged enough
                return False

        return True
