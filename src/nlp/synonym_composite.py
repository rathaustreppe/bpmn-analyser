from typing import Tuple, Optional, List

from nltk.corpus import wordnet
from nltk.corpus.reader import Synset
from pedantic import pedantic_class


@pedantic_class
class SynonymComposite:
    def __init__(self, word: str = '', synset: Optional[Synset] = None) -> None:
        if word == '' and synset is None:
            raise ValueError(
                'word and synset parameter cannot both be empty/none')

        self.word = word
        self.synset = synset

    @classmethod
    def from_str(cls, word: str = '') -> 'SynonymComposite':
        return cls(word=word, synset=None)

    @classmethod
    def from_synset(cls, synset: Synset) -> 'SynonymComposite':
        return cls(word='', synset=synset)

    def get_word(self) -> str:
        return self.word

    def get_synset(self) -> Optional[Synset]:
        return self.synset

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
        if self.word is not '':
            return tagged_word[0] == self.word

    def tagged_word_to_synset(self,
                              tagged_word: Tuple[str, str]) -> List[Synset]:
        word = tagged_word[0]
        word_type = self.get_wordnet_pos(treebank_tag=tagged_word[1])

        if word == '':
            raise ValueError(f'tagged word cannot be '
                             f'empty when checking synonyms')

        if word_type == '':
            raise ValueError(f'word type of word  {word} '
                             f'needs to be a TreeBank-POS-tag')

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
            raise ValueError(f'synset attribute of synset {self} is none')

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
