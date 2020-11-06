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
        # check synonyms via simple text compare
        if self.word is not None:
            return tagged_word[0] == self.word

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

    def __str__(self) -> str:
        if self.synset is not None:
            return self.synset.__str__()
        else:
            return self.word

    def __repr__(self) -> str:
        return self.__str__()
