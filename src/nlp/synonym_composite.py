import logging
from typing import Tuple, Optional, List

from nltk.corpus import wordnet
from nltk.corpus.reader import Synset
from pedantic import pedantic_class


@pedantic_class
class SynonymComposite:
    def __init__(self, word: str = None,
                 synset: Optional[Synset] = None) -> None:
        if (word is None or word == '') and synset is None:
            msg = 'word and synset parameter cannot both be none'
            logging.error(msg)
            raise ValueError(msg)

        self.word = word
        self.synset = synset

    @classmethod
    def from_str(cls, word: str = None) -> 'SynonymComposite':
        return cls(word=word, synset=None)

    @classmethod
    def from_synset(cls, synset: Synset) -> 'SynonymComposite':
        return cls(word='', synset=synset)

    def are_synonyms(self, tagged_word: Tuple[str, str]) -> bool:
        """
        Checks if the tagged_word is a synonym of solutions_synset.
        tagged_word: (word, TreeBank-POS-tag)
        """
        # check synonyms via synsets
        if self.synset is not None:
            synset = self.tagged_word_to_synset(tagged_word=tagged_word)
            return self._synset_comparison(synsets_to_check=synset)
        # check synonyms via simple text compare and simple distance algorithm
        # in case there are spelling mistakes
        if self.word is not None:
            accepted_distance = 0.92
            score = self.cosine_distance(word1=tagged_word[0], word2=self.word)
            return score > accepted_distance

    def tagged_word_to_synset(self,
                              tagged_word: Tuple[str, str]) -> List[Synset]:
        word = tagged_word[0]
        word_type = self.get_wordnet_pos(treebank_tag=tagged_word[1])

        if word is None or word == '':
            msg = f'Function parameter tagged_word cannot contain empty strings.'
            logging.error(msg)
            raise ValueError(msg)

        if word_type == '':
            msg = f'words in {tagged_word} have no TreeBank-POS-tag.'
            logging.error(msg)
            raise ValueError(msg)

        return wordnet.synsets(word, word_type)

    def _synset_comparison(self, synsets_to_check: List[Synset]) -> bool:
        # Assumption: If the list of all Synsets of tagged_word
        # contains the solution_synset, then tagged_word is
        # closely (at least close enough) to solution_synset and
        # therefore it is a synonym.
        # Requires the exact Synset. E.g 'mail.v.02'. 'mail' is
        # not enough.
        if self.synset is not None:
            return self.synset in synsets_to_check
        else:
            msg = f'synset attribute of synset {self} is none'
            logging.error(msg)
            raise ValueError(msg)

    @staticmethod
    def get_wordnet_pos(treebank_tag: str) -> str:
        if treebank_tag.startswith('J'):
            return wordnet.ADJ
        elif treebank_tag.startswith('V'):
            return wordnet.VERB
        elif treebank_tag.startswith('N'):
            return wordnet.NOUN
        elif treebank_tag.startswith('R'):
            return wordnet.ADV
        else:
            return ''

    def cosine_distance(self, word1: str, word2: str):
        # algorithm for calculating distance of two strings
        # Example: Word1 == Word2 == 'hello' --> score: 1.0, means exact
        # Example: Word1 == 'abc', Word2 == 'xyz' --> score: 0.0
        # Example: Word1 == 'ready', Word2 == 'reedy' --> score: 0.9
        set1 = {w for w in word1}
        set2 = {w for w in word2}

        l1 = []
        l2 = []

        # form a set containing keywords of both strings
        rvector = set1.union(set2)
        for w in rvector:
            if w in set1:
                l1.append(1)  # create a vector
            else:
                l1.append(0)
            if w in set2:
                l2.append(1)
            else:
                l2.append(0)
        c = 0

        # cosine formula
        for i in range(len(rvector)):
            c += l1[i] * l2[i]
        cosine = c / float((sum(l1) * sum(l2)) ** 0.5)
        return cosine

    def __str__(self) -> str:
        if self.synset is not None:
            return self.synset.__str__()
        else:
            return self.word

    def __repr__(self) -> str:
        return self.__str__()
