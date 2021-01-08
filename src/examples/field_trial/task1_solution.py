from typing import List

from pedantic import pedantic_class

from src.models.i_solution import ISolution
from src.models.running_token import RunningToken
from src.models.scenario import Scenario
from src.models.text import Text
from src.models.token import Token
from src.models.token_state_condition import TokenStateCondition
from src.models.token_state_modification import TokenStateModification
from src.models.token_state_rule import TokenStateRule


@pedantic_class
class Task1Solution(ISolution):

    def get_scenarios(self) -> List[Scenario]:

        # idea = Token(attributes={
        #     # Attribut --Szenario-Startwert - erwarteter Endwert
        #     'vorgelegter Entwurf': (False, True),
        #     'geprüfter Entwurf': (False, True),
        #     'korrigierter_Entwurf': (False, False)
        # })
        #





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
        running_token.Serveranmeldung = False
        running_token.Dokument_freigegeben = False
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
        text_1 = Text('Verfasser benachrichtigen')

        cond_r1 = TokenStateCondition(lambda t: t.Dokument_freigegeben == True)
        def m(t): t.Verfasser_benachrichtigt = True
        modification_r1 = TokenStateModification(m)
        tsr_1 = TokenStateRule(condition=cond_r1,
                               modification=modification_r1,
                               text=text_1)

        # Dokument freigegeben, wenn auf Server angemeldet und
        # überprüfter Entwurf fehlerfrei
        text_r2 = Text('Dokument hochladen')
        cond_r21 = TokenStateCondition(lambda t: t.Serveranmeldung and
                                                 t.fehlerfreier_Entwurf and
                                                 t.geprüfter_Entwurf)


        def m(t): t.Dokument_freigegeben = True
        modification_r2 = TokenStateModification(m)
        tsr_2 = TokenStateRule(condition=cond_r21,
                               modification=modification_r2,
                               text=text_r2)

        # Serveranmeldung
        text_r3 = Text('Anmelden beim Server')
        def m(t): t.Serveranmeldung = True
        modification_r3 = TokenStateModification(m)
        tsr_3 = TokenStateRule(modification=modification_r3,
                               text=text_r3)

        # Entwurf prüfen Szenario 1: ist fehlerfrei
        text_r4 = Text('Berechtigter prüft Entwurf')
        cond_r41 = TokenStateCondition(lambda t: t.vorgelegter_Entwurf == True)
        def m(t): t.geprüfter_Entwurf = True
        modification_r4 = TokenStateModification(m)
        tsr_4 = TokenStateRule(condition=cond_r41,
                               modification=modification_r4,
                               text=text_r4)

        # Entwurf prüfen, Szenario 2: musste korrigiert werden, dann nehmen wir
        # an, dass er fehlerfrei wurde
        text_r4_2 = Text('Berechigter prüft Entwurf')
        cond_r41_2 = TokenStateCondition(lambda t: t.korrigierter_Entwurf == True)
        def m(t): t.fehlerfreier_Entwurf = True
        modification_r4_2 = TokenStateModification(m)
        tsr_4_2 = TokenStateRule(condition=cond_r41_2,
                                 modification=modification_r4_2,
                                 text=text_r4_2)

        # Entwurf korrigiert, wenn gerüft und nicht fehlerfreip
        text_r5 = Text('Verfasser korrigiert Entwurf')
        cond_r51 = TokenStateCondition(lambda t: t.geprüfter_Entwurf == True and
                                                 t.fehlerfreier_Entwurf == False)
        def m(t):
            t.geprüfter_Entwurf = False
            t.fehlerfreier_Entwurf = True
            t.korrigierter_Entwurf = True
        modification_r51 = TokenStateModification(m)
        tsr_5 = TokenStateRule(condition=cond_r51,
                               modification=modification_r51,
                               text=text_r5)

        return [tsr_1, tsr_2, tsr_3, tsr_4, tsr_4_2, tsr_5]
