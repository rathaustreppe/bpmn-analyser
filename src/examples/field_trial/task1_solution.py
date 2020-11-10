from typing import List

from src.converter.bpmn_models.bpmn_model import BPMNModel
from src.examples.i_example import IExample
from src.models.token import Token
from src.models.token_state_condition import TokenStateCondition, Operators
from src.models.token_state_modification import TokenStateModification
from src.models.token_state_rule import TokenStateRule
from src.nlp.IChunker import IChunker
from src.nlp.default_chunker import DefaultChunker
from src.nlp.synonym_cloud import SynonymCloud


class Task1Solution(IExample):

    def get_init_token(self) -> Token:
        # Scenario 1 token
        attributes = {
            'vorgelegter Entwurf': True, # should be false, and set to true by startevent
            'fehlerfreier Entwurf': True,
            'geprüfter Entwurf': False,
            'korrigierter Entwurf': False,
            'Serveranmeldung': False,
            'Dokument freigegeben': False,
            'Verfasser benachrichtigt': False,
        }
        return Token(attributes=attributes)

        # Scenario 2 token
        # attributes = {
        #     'vorgelegter Entwurf': True,# should be false, and set to true by startevent
        #     'fehlerfreier Entwurf': False,
        #     'geprüfter Entwurf': False,
        #     'korrigierter Entwurf': False,
        #     'Serveranmeldung': False,
        #     'Dokument freigegeben': False,
        #     'Verfasser benachrichtigt': False,
        # }
        # return Token(attributes=attributes)

    def get_solution_token(self) -> Token:
        # Scenario 1 token
        attributes = {
            'vorgelegter Entwurf': True, # should be false, and set to true by startevent
            'fehlerfreier Entwurf': True,
            'geprüfter Entwurf': True,
            'korrigierter Entwurf': False,
            'Serveranmeldung': True,
            'Dokument freigegeben': True,
            'Verfasser benachrichtigt': True,
        }
        return Token(attributes=attributes)

        # Scenario 2 token
        # attributes = {
        #     'vorgelegter Entwurf': True, # should be false, and set to true by startevent
        #     'fehlerfreier Entwurf': True,
        #     'geprüfter Entwurf': True,
        #     'korrigierter Entwurf': True,
        #     'Serveranmeldung': True,
        #     'Dokument freigegeben': True,
        #     'Verfasser benachrichtigt': True,
        # }
        # return Token(attributes=attributes)


    def get_ruleset(self) -> List[TokenStateRule]:
        # Verfasser benachrichtigt, wenn Dokument freigegeben:
        syncloud_r1 = SynonymCloud.from_list(text=['Verfasser benachrichtigen'])

        cond_r1 = TokenStateCondition(tok_attribute='Dokument freigegeben',
                                      operator=Operators.EQUALS,
                                      tok_value=True)
        modification_r1 = TokenStateModification(key='Verfasser benachrichtigt', value=True)
        tsr_1 = TokenStateRule(state_conditions=[cond_r1],
                               state_modifications=[modification_r1],
                               synonym_cloud=syncloud_r1)

        # Dokument freigegeben, wenn auf Server angemeldet und
        # überprüfter Entwurf fehlerfrei
        syncloud_r2 = SynonymCloud.from_list(text=['Dokument hochladen'])
        cond_r21 = TokenStateCondition(tok_attribute='Serveranmeldung',
                                      operator=Operators.EQUALS,
                                      tok_value=True)
        cond_r22 = TokenStateCondition(tok_attribute='fehlerfreier Entwurf',
                                      operator=Operators.EQUALS,
                                      tok_value=True)
        cond_r23 = TokenStateCondition(tok_attribute='geprüfter Entwurf',
                                       operator=Operators.EQUALS,
                                       tok_value=True)
        modification_r2 = TokenStateModification(key='Dokument freigegeben',
                                                 value=True)
        tsr_2 = TokenStateRule(state_conditions=[cond_r21, cond_r22, cond_r23],
                               state_modifications=[modification_r2],
                               synonym_cloud=syncloud_r2)

        # Serveranmeldung
        syncloud_r3 = SynonymCloud.from_list(text=['Anmelden beim Server'])
        modification_r3 = TokenStateModification(key='Serveranmeldung',
                                                 value=True)
        tsr_3 = TokenStateRule(state_conditions=[],
                               state_modifications=[modification_r3],
                               synonym_cloud=syncloud_r3)

        # Entwurf prüfen Szenario 1: ist fehlerfrei
        syncloud_r4 = SynonymCloud.from_list(text=['Berechtigter prüft Entwurf'])
        cond_r41 = TokenStateCondition(tok_attribute='vorgelegter Entwurf',
                                       operator=Operators.EQUALS,
                                       tok_value=True)
        modification_r4 = TokenStateModification(key='geprüfter Entwurf',
                                                 value=True)
        tsr_4 = TokenStateRule(state_conditions=[cond_r41],
                               state_modifications=[modification_r4],
                               synonym_cloud=syncloud_r4)

        # Entwurf prüfen, Szenario 2: musste korrigiert werden, dann nehmen wir
        # an, dass er fehlerfrei wurde
        syncloud_r4_2 = SynonymCloud.from_list(text=['Berechigter prüft Entwurf'])
        cond_r41_2 = TokenStateCondition(tok_attribute='korrigierter Entwurf',
                                         operator=Operators.EQUALS,
                                         tok_value=True)
        modification_r4_2 = TokenStateModification(key='fehlerfreier Entwurf',
                                                   value=True)
        tsr_4_2 = TokenStateRule(state_conditions=[cond_r41_2],
                                 state_modifications=[modification_r4_2],
                                 synonym_cloud=syncloud_r4_2)

        # Entwurf korrigiert, wenn gerüft und nicht fehlerfreip
        syncloud_r5 = SynonymCloud.from_list(text=['Verfasser korrigiert Entwurf'])
        cond_r51 = TokenStateCondition(tok_attribute='geprüfter Entwurf',
                                       operator=Operators.EQUALS,
                                       tok_value=True)
        cond_r52 = TokenStateCondition(tok_attribute='fehlerfreier Entwurf',
                                       operator=Operators.EQUALS,
                                       tok_value=False)
        modification_r51 = TokenStateModification(key='geprüfter Entwurf',
                                                 value=False)
        modification_r52 = TokenStateModification(key='fehlerfreier Entwurf',
                                                 value=True)
        modification_r53 = TokenStateModification(key='korrigierter Entwurf',
                                                  value=True)
        tsr_5 = TokenStateRule(state_conditions=[cond_r51,cond_r52],
                               state_modifications=[modification_r51,
                                                    modification_r52,
                                                    modification_r53],
                               synonym_cloud=syncloud_r5)

        return [tsr_1, tsr_2, tsr_3, tsr_4, tsr_4_2, tsr_5]

    def get_chunker(self) -> IChunker:
        # we use german in our text, which isnt supported by NLTK -> use
        # default chunker and let synonymclouds check sentences
        return DefaultChunker()

    def get_students_process(self) -> BPMNModel:
        # Students solutions are load via a file. So they dont need to be
        # programmed here
        pass


