import pytest
from nltk.corpus import wordnet as wn

from src.nlp.synonym_composite import SynonymComposite


class TestSynonymComposite:

    @pytest.fixture(scope='module', autouse=True)
    def wordnet(self) -> wn:
        return wn

    @pytest.fixture(scope='function', autouse=True)
    def syn_comp(self) -> SynonymComposite:
        return SynonymComposite.from_synset(synset=wn.synset('mail.v.02'))

    def test_constructor_empty(self):
        with pytest.raises(ValueError):
            SynonymComposite.from_str(word='')

    def test_constructor_from_string(self):
        word = 'mail'
        sc = SynonymComposite.from_str(word=word)
        assert sc.synset is None
        assert sc.word == word

    def test_constructor_from_synset(self):
        synset = wn.synset('mail.v.02')
        sc = SynonymComposite.from_synset(synset=synset)
        assert sc.word == ''
        assert sc.synset == synset

    def test_tagged_word_empty(self, syn_comp):
        # giving an empty parameter
        tagged_word = ('', '')
        with pytest.raises(ValueError):
            syn_comp.tagged_word_to_synset(tagged_word=tagged_word)

    def test_tagged_word_empty2(self, syn_comp):
        # giving an empty parameter
        tagged_word = ('', 'NN')
        with pytest.raises(ValueError):
            syn_comp.tagged_word_to_synset(tagged_word=tagged_word)

    def test_tagged_word_empty3(self, syn_comp):
        # giving an empty parameter
        tagged_word = ('mail', '')
        with pytest.raises(ValueError):
            syn_comp.tagged_word_to_synset(tagged_word=tagged_word)

    def test_synonym_synsets(self, syn_comp):
        synonym = 'send'
        pos_tag = 'V'
        assert syn_comp.are_synonyms(tagged_word=(synonym, pos_tag))

    def test_synonym_synsets_tagged_word_changes_in_synset(self):
        # when using synset('salary.n.01') Wordnet changes it
        # to synset('wage.n.01') -> does it still identify words as synonyms?
        synonym = 'wage'
        pos_tag = 'N'
        synset = wn.synset('salary.n.01')
        sc = SynonymComposite.from_synset(synset=synset)
        assert sc.are_synonyms(tagged_word=(synonym, pos_tag))

    def test_synonym_synsets_not_synonym(self, syn_comp):
        synonym = 'awkward'
        pos_tag = 'N'
        assert syn_comp.are_synonyms(tagged_word=(synonym, pos_tag)) is False

    def test_synonyms_text(self):
        synonym = 'send'
        pos_tag = 'V'
        sc = SynonymComposite.from_str(word='send')
        assert sc.are_synonyms(tagged_word=(synonym, pos_tag))
