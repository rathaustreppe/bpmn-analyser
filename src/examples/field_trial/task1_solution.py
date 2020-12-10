from typing import List

from pedantic import pedantic_class

from src.models.i_solution import ISolution
from src.models.running_token import RunningToken
from src.models.scenario import Scenario
from src.models.token import Token
from src.models.token_state_condition import TokenStateCondition
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

        cond_r1 = TokenStateCondition(lambda t: t.Dokument_freigegeben == True)
        def m(t): t.Verfasser_benachrichtigt = True
        modification_r1 = TokenStateModification(m)
        tsr_1 = TokenStateRule(condition=cond_r1,
                               modification=modification_r1,
                               synonym_cloud=syncloud_r1)

        # Dokument freigegeben, wenn auf Server angemeldet und
        # überprüfter Entwurf fehlerfrei
        syncloud_r2 = SynonymCloud.from_list(text=['Dokument hochladen'])
        cond_r21 = TokenStateCondition(lambda t: t.Serveranmeldung and
                                                 t.fehlerfreier_Entwurf and
                                                 t.geprüfter_Entwurf)


        def m(t): t.Dokument_freigegeben = True
        modification_r2 = TokenStateModification(m)
        tsr_2 = TokenStateRule(condition=cond_r21,
                               modification=modification_r2,
                               synonym_cloud=syncloud_r2)

        # Serveranmeldung
        syncloud_r3 = SynonymCloud.from_list(text=['Anmelden beim Server'])
        def m(t): t.Serveranmeldung = True
        modification_r3 = TokenStateModification(m)
        tsr_3 = TokenStateRule(modification=modification_r3,
                               synonym_cloud=syncloud_r3)

        # Entwurf prüfen Szenario 1: ist fehlerfrei
        syncloud_r4 = SynonymCloud.from_list(
            text=['Berechtigter prüft Entwurf'])
        cond_r41 = TokenStateCondition(lambda t: t.vorgelegter_Entwurf == True)
        def m(t): t.geprüfter_Entwurf = True
        modification_r4 = TokenStateModification(m)
        tsr_4 = TokenStateRule(condition=cond_r41,
                               modification=modification_r4,
                               synonym_cloud=syncloud_r4)

        # Entwurf prüfen, Szenario 2: musste korrigiert werden, dann nehmen wir
        # an, dass er fehlerfrei wurde
        syncloud_r4_2 = SynonymCloud.from_list(
            text=['Berechigter prüft Entwurf'])
        cond_r41_2 = TokenStateCondition(lambda t: t.korrigierter_Entwurf == True)
        def m(t): t.fehlerfreier_Entwurf = True
        modification_r4_2 = TokenStateModification(m)
        tsr_4_2 = TokenStateRule(condition=cond_r41_2,
                                 modification=modification_r4_2,
                                 synonym_cloud=syncloud_r4_2)

        # Entwurf korrigiert, wenn gerüft und nicht fehlerfreip
        syncloud_r5 = SynonymCloud.from_list(
            text=['Verfasser korrigiert Entwurf'])
        cond_r51 = TokenStateCondition(lambda t: t.geprüfter_Entwurf == True and
                                                 t.fehlerfreier_Entwurf == False)
        def m(t):
            t.geprüfter_Entwurf = False
            t.fehlerfreier_Entwurf = True
            t.korrigierter_Entwurf = True
        modification_r51 = TokenStateModification(m)
        tsr_5 = TokenStateRule(condition=cond_r51,
                               modification=modification_r51,
                               synonym_cloud=syncloud_r5)

        return [tsr_1, tsr_2, tsr_3, tsr_4, tsr_4_2, tsr_5]

    def get_chunker(self) -> IChunker:
        # we use german in our text, which isn't supported by NLTK -> use
        # default chunker and let synonymclouds check sentences
        return DefaultChunker()
