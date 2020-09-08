from typing import Tuple

from nltk.corpus.reader import Synset
import nltk
from nltk.corpus import wordnet
from nltk.corpus.reader import Synset
from pedantic import pedantic_class


@pedantic_class
class SynonymComposite:
    def __init__(self, text: str = '', synset: Synset = None) -> None:
        if text == '' and synset is None:
            raise ValueError('text and synset parameter cannot be empty or None')

        self.text = text
        self.synset = synset


    def are_synonyms(self,tagged_word: Tuple[str, str]) -> bool:
        """
        Checks if the tagged_word is a synonym of solutions_synset.
        tagged_word: (word, tag by NLTK-Tagger)
        """

        # Assumption: If the list of all Synsets of tagged_word
        # contains the solution_synset, then tagged_word is
        # closely (at least close enough) to solution_synset and
        # therefore it is a synonym.
        # Requires the exact Synset. E.g 'mail.v.02'. 'mail' is
        # not enough.
        word = tagged_word[0]
        word_type = self.get_wordnet_pos(tagged_word[1])
        synset_words = wordnet.synsets(word, word_type)

        if self.text == '':
            if self.synset in synset_words:
                return True
            else:
                return False
        else:
            Exception('STRING CHECKING NOT YET IMPLEMENTED')


    def get_wordnet_pos(self, treebank_tag):
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
