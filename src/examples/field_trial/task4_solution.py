from typing import List

from src.models.i_solution import ISolution
from src.models.running_token import RunningToken
from src.models.scenario import Scenario
from src.models.token import Token
from src.models.token_state_condition import TokenStateCondition, Operators
from src.models.token_state_modification import TokenStateModification
from src.models.token_state_rule import TokenStateRule
from src.nlp.chunker import Chunker
from src.nlp.synonym_cloud import SynonymCloud


class Task4Solution(ISolution):

    def get_scenarios(self) -> List[Scenario]:
        scenarios = []

        description = 'cash withdrawal'
        running_token = RunningToken(attributes={
            'card inserted': False,
            'withdraw cash': True,
            'deposit cash': False,
            'correct pin': False,
            'amount choosen': False,
            'cash inserted': False,
            'card taken': False,
            'cash taken': False,
            'receipt taken': False
        })

        expected_token = Token(attributes={
            'card inserted': True,
            'withdraw cash': True,
            'deposit cash': False,
            'correct pin': True,
            'amount choosen': True,
            'cash inserted': False,
            'card taken': True,
            'cash taken': True,
            'receipt taken': False

        })

        scen1 = Scenario(running_token=running_token,
                         expected_token=expected_token,
                         description=description)
        scenarios.append(scen1)

        description = 'cash deposit'
        running_token = RunningToken(attributes={
            'card inserted': False,
            'deposit cash': True,
            'withdraw cash': False,
            'correct pin': False,
            'amount choosen': False,
            'cash inserted': True,
            'card taken': False,
            'cash taken': False,
            'receipt taken': False
        })

        expected_token = Token(attributes={
            'card inserted': True,
            'deposit cash': True,
            'withdraw cash': False,
            'correct pin': True,
            'amount choosen': False,
            'cash inserted': True,
            'card taken': True,
            'cash taken': True,
            'receipt taken': True
        })

        scen2 = Scenario(running_token=running_token,
                         expected_token=expected_token,
                         description=description)
        scenarios.append(scen2)

        return scenarios

    def get_ruleset(self) -> List[TokenStateRule]:
        # card inserted
        syncloud_r1 = SynonymCloud.from_list(text=['insert card'])

        modification_r1 = TokenStateModification(key='card inserted',
                                                 value=True)
        tsr_1 = TokenStateRule(state_conditions=[],
                               state_modifications=[modification_r1],
                               synonym_cloud=syncloud_r1)

        # enter pin only when card is in atm and cash withdrawal is selected
        # >>>> Are there ATMS where you have to enter your PIN to deposit cash?
        syncloud_r2 = SynonymCloud.from_list(text=['enter pin'])

        cond_r21 = TokenStateCondition(tok_attribute='card inserted',
                                      operator=Operators.EQUALS,
                                      tok_value=True)
        # cond_r22 = TokenStateCondition(tok_attribute='deposit cash',
        #                               operator=Operators.EQUALS,
        #                               tok_value=True)
        modification_r2 = TokenStateModification(key='correct pin',
                                                 value=True)
        tsr_2 = TokenStateRule(state_conditions=[cond_r21],#, cond_r22],
                               state_modifications=[modification_r2],
                               synonym_cloud=syncloud_r2)

        # choose amount of money to withdraw only when PIN is correct
        syncloud_r3 = SynonymCloud.from_list(text=['choose amount'])

        cond_r3 = TokenStateCondition(tok_attribute='correct pin',
                                      operator=Operators.EQUALS,
                                      tok_value=True)

        modification_r3 = TokenStateModification(key='amount choosen',
                                                 value=False)
        tsr_3 = TokenStateRule(state_conditions=[cond_r3],
                               state_modifications=[modification_r3],
                               synonym_cloud=syncloud_r3)

        # take card after amount choosen
        syncloud_r4 = SynonymCloud.from_list(text=['take card'])

        cond_r4 = TokenStateCondition(tok_attribute='amount choosen',
                                      operator=Operators.EQUALS,
                                      tok_value=True)

        modification_r4 = TokenStateModification(key='card taken',
                                                 value=True)
        tsr_4 = TokenStateRule(state_conditions=[cond_r4],
                               state_modifications=[modification_r4],
                               synonym_cloud=syncloud_r4)

        # or take card, after inserting cash
        syncloud_r5 = SynonymCloud.from_list(text=['take card'])

        cond_r5 = TokenStateCondition(tok_attribute='cash inserted',
                                      operator=Operators.EQUALS,
                                      tok_value=True)

        modification_r5 = TokenStateModification(key='card taken',
                                                 value=True)
        tsr_5 = TokenStateRule(state_conditions=[cond_r5],
                               state_modifications=[modification_r5],
                               synonym_cloud=syncloud_r5)

        # take cash after amount choosen
        syncloud_r6 = SynonymCloud.from_list(text=['take cash'])

        cond_r6 = TokenStateCondition(tok_attribute='amount choosen',
                                      operator=Operators.EQUALS,
                                      tok_value=True)

        modification_r6 = TokenStateModification(key='card taken',
                                                 value=True)
        tsr_6 = TokenStateRule(state_conditions=[cond_r6],
                               state_modifications=[modification_r6],
                               synonym_cloud=syncloud_r6)

        # take receipt after inserting cash
        syncloud_r7 = SynonymCloud.from_list(text=['take receipt'])

        cond_r7 = TokenStateCondition(tok_attribute='cash inserted',
                                      operator=Operators.EQUALS,
                                      tok_value=True)

        modification_r7 = TokenStateModification(key='receipt taken',
                                                 value=True)
        tsr_7 = TokenStateRule(state_conditions=[cond_r7],
                               state_modifications=[modification_r7],
                               synonym_cloud=syncloud_r7)

        return [tsr_1, tsr_2, tsr_3, tsr_4, tsr_5, tsr_6, tsr_7]

    def get_chunker(self) -> Chunker:
        # https://stackoverflow.com/questions/15388831/what-are-all-possible-pos-tags-of-nltk
        grammar = r"""
        VB_XX_NN:       {<NN><VB.><TO>?<IN>?<PRP>?<DT>?<NN>}
        """
        return Chunker(chunk_grams=grammar)
