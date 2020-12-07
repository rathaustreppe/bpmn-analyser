from typing import List

from pedantic import pedantic_class

from src.models.i_solution import ISolution
from src.models.running_token import RunningToken
from src.models.scenario import Scenario
from src.models.token import Token
from src.models.token_state_condition import TokenStateCondition, Operators
from src.models.token_state_modification import TokenStateModification
from src.models.token_state_rule import TokenStateRule
from src.nlp.IChunker import IChunker
from src.nlp.default_chunker import DefaultChunker
from src.nlp.synonym_cloud import SynonymCloud

@pedantic_class
class Task1Solution(ISolution):

    def get_scenarios(self) -> List[Scenario]:
        scenarios = []

        # Scnario 1 of task 1: Entwurf ist fehlerfrei
        description = 'ein fehlerfreier Entwurf wird vorgelegt'
        expected_token = Token(attributes={
            'vorgelegter_Entwurf': True,
            # should be false, and set to true by startevent
            'fehlerfreier_Entwurf': True,
            'geprüfter_Entwurf': True,
            'korrigierter_Entwurf': False,
            # note that this never changed to True
            'Serveranmeldung': True,
            'Dokument_freigegeben': True,
            'Verfasser_benachrichtigt': True
        })

        running_token = RunningToken.from_token(token=expected_token)
        running_token.geprüfter_Entwurf = False
        running_token.Serveranmeldung = False,
        running_token.Dokument_freigegeben = False,
        running_token.Verfasser_benachrichtigt = False

        scen1 = Scenario(running_token=running_token,
                         expected_token=expected_token,
                         description=description)
        scenarios.append(scen1)

        # Scenario 2 of task1: Entwurf ist nicht fehlerfrei
        description = 'Entwurf ist nicht fehlerfrei. Korrekturschleife nötig'

        expected_token = Token(attributes={
            'vorgelegter_Entwurf': True,
            # should be false, and set to true by startevent
            'fehlerfreier_Entwurf': True,
            'geprüfter_Entwurf': True,
            'korrigierter_Entwurf': True,
            'Serveranmeldung': True,
            'Dokument_freigegeben': True,
            'Verfasser_benachrichtigt': True
        })

        running_token = RunningToken.from_token(token=expected_token)
        running_token.fehlerfreier_Entwurf = False
        running_token.geprüfter_Entwurf = False
        running_token.korrigierter_Entwurf = False
        running_token.Serveranmeldung = False
        running_token.Dokument_freigegeben = False
        running_token.Verfasser_benachrichtigt = False

        scen2 = Scenario(running_token=running_token,
                         expected_token=expected_token,
                         description=description)
        scenarios.append(scen2)

        return scenarios

    def get_ruleset(self) -> List[TokenStateRule]:
        # Verfasser benachrichtigt, wenn Dokument_freigegeben:
        syncloud_r1 = SynonymCloud.from_list(text=['Verfasser benachrichtigen'])

        cond_r1 = TokenStateCondition("t.Dokument_freigegeben == True")
        modification_r1 = TokenStateModification('t.Verfasser_benachrichtigt = True')
        tsr_1 = TokenStateRule(state_conditions=[cond_r1],
                               state_modifications=[modification_r1],
                               synonym_cloud=syncloud_r1)

        # Dokument freigegeben, wenn auf Server angemeldet und
        # überprüfter Entwurf fehlerfrei
        syncloud_r2 = SynonymCloud.from_list(text=['Dokument hochladen'])
        cond_r21 = TokenStateCondition("t.Serveranmeldung == True and "
                                                 "t.fehlerfreier_Entwurf == True and "
                                                 "t.geprüfter_Entwurf == True")
        modification_r2 = TokenStateModification('t.Dokument_freigegeben =True')
        tsr_2 = TokenStateRule(state_conditions=[cond_r21],
                               state_modifications=[modification_r2],
                               synonym_cloud=syncloud_r2)

        # Serveranmeldung
        syncloud_r3 = SynonymCloud.from_list(text=['Anmelden beim Server'])
        modification_r3 = TokenStateModification('t.Serveranmeldung = True')
        tsr_3 = TokenStateRule(state_conditions=[],
                               state_modifications=[modification_r3],
                               synonym_cloud=syncloud_r3)

        # Entwurf prüfen Szenario 1: ist fehlerfrei
        syncloud_r4 = SynonymCloud.from_list(
            text=['Berechtigter prüft Entwurf'])
        cond_r41 = TokenStateCondition("t.vorgelegter_Entwurf == True")
        modification_r4 = TokenStateModification('t.geprüfter_Entwurf = True')
        tsr_4 = TokenStateRule(state_conditions=[cond_r41],
                               state_modifications=[modification_r4],
                               synonym_cloud=syncloud_r4)

        # Entwurf prüfen, Szenario 2: musste korrigiert werden, dann nehmen wir
        # an, dass er fehlerfrei wurde
        syncloud_r4_2 = SynonymCloud.from_list(
            text=['Berechigter prüft Entwurf'])
        cond_r41_2 = TokenStateCondition("t.korrigierter_Entwurf == True")
        modification_r4_2 = TokenStateModification('t.fehlerfreier_Entwurf = True')
        tsr_4_2 = TokenStateRule(state_conditions=[cond_r41_2],
                                 state_modifications=[modification_r4_2],
                                 synonym_cloud=syncloud_r4_2)

        # Entwurf korrigiert, wenn gerüft und nicht fehlerfreip
        syncloud_r5 = SynonymCloud.from_list(
            text=['Verfasser korrigiert Entwurf'])
        cond_r51 = TokenStateCondition("t.geprüfter_Entwurf == True and t.fehlerfreier_Entwurf == False")
        modification_r51 = TokenStateModification('t.geprüfter_Entwurf = False')
        modification_r52 = TokenStateModification('t.fehlerfreier_Entwurf = True')
        modification_r53 = TokenStateModification('t.korrigierter_Entwurf =True')
        tsr_5 = TokenStateRule(state_conditions=[cond_r51],
                               state_modifications=[modification_r51,
                                                    modification_r52,
                                                    modification_r53],
                               synonym_cloud=syncloud_r5)

        return [tsr_1, tsr_2, tsr_3, tsr_4, tsr_4_2, tsr_5]

    def get_chunker(self) -> IChunker:
        # we use german in our text, which isn't supported by NLTK -> use
        # default chunker and let synonymclouds check sentences
        return DefaultChunker()
