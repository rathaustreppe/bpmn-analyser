from typing import List, Tuple

from nltk.corpus import wordnet as wn
from nltk.corpus.reader import Synset

from src.nlp.synonym_cloud import SynonymCloud


class TestSynonymCloud:

    wn_synset_mail = wn.synset('mail.v.02')
    wn_synset_contract = wn.synset('contract.n.01')
    wn_synset_cluster = wn.synset('cluster.n.01')
    wn_synset_package = wn.synset('package.n.01')

    @staticmethod
    def tuple_to_str(tuple_list: List[Tuple[str, str]]):
        text = []
        for elem in tuple_list:
            text.append(elem[0])
        return ' '.join(text)

    def test_constructor_single_str(self):
        word = 'sending'
        list_words = [word]
        syncl = SynonymCloud.from_list(text=list_words)
        assert len(syncl.syncloud) == 1
        assert isinstance(syncl.syncloud[0].word, str)
        assert syncl.syncloud[0].word == word
        assert syncl.syncloud[0].synset is None

    def test_constructor_double_str(self):
        word1, word2 = 'sending', 'world'
        list_words = [word1, word2]
        syncl = SynonymCloud.from_list(text=list_words)
        assert len(syncl.syncloud) == 2

        assert isinstance(syncl.syncloud[0].word, str)
        assert syncl.syncloud[0].word == word1
        assert syncl.syncloud[0].synset is None

        assert isinstance(syncl.syncloud[1].word, str)
        assert syncl.syncloud[1].word == word2
        assert syncl.syncloud[1].synset is None

    def test_constructor_empty(self):
        list_words = []
        syncl = SynonymCloud.from_list(text=list_words)
        assert len(syncl.syncloud) == 0

    def test_constructor_single_synset(self):
        synset = [self.wn_synset_mail]
        syncl = SynonymCloud.from_list(text=synset)

        assert len(syncl.syncloud) == 1

        assert isinstance(syncl.syncloud[0].synset, Synset)
        assert syncl.syncloud[0].synset == self.wn_synset_mail
        assert syncl.syncloud[0].word == ''

    def test_constructor_double_synset(self):
        synset1 = self.wn_synset_mail
        synset2 = self.wn_synset_contract
        list_words = [synset1, synset2]
        syncl = SynonymCloud.from_list(text=list_words)

        assert len(syncl.syncloud) == 2

        assert isinstance(syncl.syncloud[0].synset, Synset)
        assert syncl.syncloud[0].synset == synset1
        assert syncl.syncloud[0].word == ''

        assert isinstance(syncl.syncloud[1].synset, Synset)
        assert syncl.syncloud[1].synset == synset2
        assert syncl.syncloud[1].word == ''

    def test_constructor_mix(self):
        word1 = 'hello'
        synset = self.wn_synset_contract
        word2 = 'checking'
        list_words = [word1, synset, word2]
        syncl = SynonymCloud.from_list(text=list_words)

        assert len(syncl.syncloud) == 3

        assert isinstance(syncl.syncloud[0].word, str)
        assert syncl.syncloud[0].word == word1
        assert syncl.syncloud[0].synset is None

        assert isinstance(syncl.syncloud[1].synset, Synset)
        assert syncl.syncloud[1].synset == synset
        assert syncl.syncloud[1].word == ''

        assert isinstance(syncl.syncloud[2].word, str)
        assert syncl.syncloud[2].word == word2
        assert syncl.syncloud[2].synset is None

    def test_synonyms(self, adj_chunker, adj_word):
        # compares 'bright' (predefined solution) with
        # 'smart' (chunk found in text)
        synset = wn.synset('bright.a.03')
        syncl = SynonymCloud.from_list(text=[synset])
        text = self.tuple_to_str(adj_word)
        chunk = adj_chunker.find_chunk(text=text)
        assert syncl.are_synonyms(chunk=chunk)

    def test_no_synonyms(self, adj_chunker, adj_word):
        # compares 'green' (predefined solution) with
        # 'smart' (chunk found in text)
        synset = wn.synset('green.a.01')
        syncl = SynonymCloud.from_list(text=[synset])
        text = self.tuple_to_str(adj_word)
        chunk = adj_chunker.find_chunk(text=text)
        assert syncl.are_synonyms(chunk=chunk) is False

    def test_equal_synonyms(self, nn_word, nn_chunker):
        synset = self.wn_synset_contract
        syncl = SynonymCloud.from_list(text=[synset])
        text = self.tuple_to_str(nn_word)
        chunk = nn_chunker.find_chunk(text=text)
        assert syncl.are_synonyms(chunk=chunk)

    def test_synonyms_in_longer_text(self, xx_nn_xx_sentence, adj_chunker):
        synset = wn.synset('greenish.a.01')
        syncl = SynonymCloud.from_list(text=[synset])
        text = self.tuple_to_str(xx_nn_xx_sentence)
        chunk = adj_chunker.find_chunk(text=text)
        assert syncl.are_synonyms(chunk=chunk)

    def test_multiple_synoynms(self, nn_vb_nn_chunker):
        # every word is synonym and is in one chunk
        synsets = [self.wn_synset_cluster,
                   wn.synset('permit.v.01'),
                   self.wn_synset_package]
        syncl = SynonymCloud.from_list(text=synsets)
        text = self.tuple_to_str([('bunch', 'NN'),
                                  ('allow', 'VB'),
                                  ('parcel', 'NN')])
        chunk = nn_vb_nn_chunker.find_chunk(text=text)
        assert syncl.are_synonyms(chunk=chunk)

    def test_multiple_synonyms_bi(self, nn_vb_nn_chunker):
        # same test as 'test_multiple_synoynms' but reversed lists
        synsets = [wn.synset('bunch.n.01'),
                   wn.synset('allow.v.01'),
                   wn.synset('parcel.n.01')]
        syncl = SynonymCloud.from_list(text=synsets)
        text = self.tuple_to_str([('cluster', 'NN'),
                                  ('permiting', 'VBG'),
                                  ('package', 'NN')])
        chunk = nn_vb_nn_chunker.find_chunk(text=text)
        assert syncl.are_synonyms(chunk=chunk)

    def test_fixed_word(self, nn_word, nn_chunker):
        # using a string in SynCloud (instead of Synset) and comparing equality
        # with the equal string found in chunk
        text = self.tuple_to_str(tuple_list=nn_word)
        syncl = SynonymCloud.from_list(text=[text])
        chunk = nn_chunker.find_chunk(text=text)
        assert syncl.are_synonyms(chunk=chunk)

    def test_fixed_word_not_equal(self, adj_chunker, adj_word):
        # comparing 'yellow' (predefined solution) with another non-synonym-adj
        fixed_word = 'yellow'
        syncl = SynonymCloud.from_list(text=[fixed_word])
        text = self.tuple_to_str(tuple_list=adj_word)
        chunk = adj_chunker.find_chunk(text=text)
        assert syncl.are_synonyms(chunk=chunk) is False

    def test_fixed_words_and_synonyms_in_complex_chunk(self, nn_vb_nn_chunker):
        # mix of synonyms and fixed words
        synsets = [self.wn_synset_cluster,
                   'permit',
                   self.wn_synset_package]
        syncl = SynonymCloud.from_list(text=synsets)
        text = self.tuple_to_str([('bunch', 'NN'),
                                  ('running', 'VB'),
                                  ('parcel', 'NN')])
        chunk = nn_vb_nn_chunker.find_chunk(text=text)
        assert syncl.are_synonyms(chunk=chunk) is False

    def test_fixed_words_and_synonyms_in_complex_chunk2(self, nn_vb_nn_chunker):
        synsets = [self.wn_synset_cluster,
                   'allow',
                   self.wn_synset_package]
        syncl = SynonymCloud.from_list(text=synsets)
        text = self.tuple_to_str([('bunch', 'NN'),
                                  ('allow', 'VB'),
                                  ('parcel', 'NN')])
        chunk = nn_vb_nn_chunker.find_chunk(text=text)
        assert syncl.are_synonyms(chunk=chunk)
