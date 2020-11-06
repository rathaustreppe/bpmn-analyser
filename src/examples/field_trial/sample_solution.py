from typing import List

from nltk.corpus import wordnet as wn

from src.converter.bpmn_models.bpmn_model import BPMNModel
from src.examples.i_example import IExample
from src.models.token import Token
from src.models.token_state_condition import TokenStateCondition, Operators
from src.models.token_state_modification import TokenStateModification
from src.models.token_state_rule import TokenStateRule
from src.nlp.chunker import Chunker
from src.nlp.synonym_cloud import SynonymCloud


class SampleSolution(IExample):
    def get_students_process(self) -> BPMNModel:
        # not implemented because bpmn-files are read in the main files
        # there are multiple files to read, this method only allows file
        # to be read
        pass

    # File that contains the sample solution of the first field trial (Oct, Nov 2020).

    def get_init_token(self) -> Token:
        # Specify the initial state of the token right before a diagram is executed.
        # Use it as a dict-like structure. Integers, booleans and strings are allowed.
        attributes = {
            "place": "Zittau",
        }
        return Token(attributes=attributes)

    def get_solution_token(self) -> Token:
        # Specify the initial state of the token right after a diagram is executed.
        # This token will be compared with the token of the students solution.
        attributes = {
            "place": "Zittau",
        }
        return Token(attributes=attributes)

    def get_ruleset(self) -> List[TokenStateRule]:
        # Define the real-life-constraints that limit your process here.
        syncloud_r1 = SynonymCloud.from_list(text=['ML',
                                                   wn.synset('sign.v.01'),
                                                   wn.synset('bill.n.02')
                                                   ])
        cond_r1 = TokenStateCondition(tok_attribute='place',
                                      operator=Operators.EQUALS,
                                      tok_value='Goerlitz')
        modification_r1 = TokenStateModification(key='signature ML', value=True)
        tsr_1 = TokenStateRule(state_conditions=[cond_r1],
                               state_modifications=[modification_r1],
                               synonym_cloud=syncloud_r1)

        return [tsr_1]

    def get_chunker(self) -> Chunker:
            # define the format of the sentences the texts in the students solution
            # should have. Make sure it is conform to the Synclouds defined above.
            chunk_grams = r"""
            VB_NN_TO_NN:    {<VB.?>+<NN.?><TO>?<NN.?>+}
            NN_VB_NN:       {<NN.?><VB.?><NN.?>}
            VB_NN:          {<VB.?><NN.?>}
            """
            # sadly there are words, that a pos tagger always classifies wrong.
            # we define them here correctly and pass them to the chunker.
            tagged_words_bypass = [('Goerlitz', 'NN'), ('Zittau', 'NN'), ('Dresden', 'NN'),
                                   ('signs', 'VB'), ('checks', 'VB')]
            return Chunker(chunk_grams=chunk_grams,
                              tagged_words_bypass=tagged_words_bypass)
