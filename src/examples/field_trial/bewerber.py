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
class Bewerber(ISolution):

    def get_scenarios(self) -> List[Scenario]:

        ######## default token #######
        default_token = Token(attributes={
            'ungeeignete_Bewerbung': False,
            'ungeeigneter_Bewerber': False,

            'Bewerbung_eingegangen': False,
            'Bewerbung_gesichtet': False,
            'Bewerbung_abgelehnt': False,
            'Einladung_Vorstellungsgespräch': False,
            'Vorstellungsgespräch': False,
            'Bewerber_abgelehnt': False,
            'Stelle_besetzt': False
        })


        ##############################################
        ############ SZENARIO 1 ######################
        ##############################################

        description_1 = 'Bewerbung wird sofort abgelehnt'

        expected_token_1 = Token(attributes={
            'ungeeignete_Bewerbung': True,
            'ungeeigneter_Bewerber': True,

            'Bewerbung_eingegangen': True,
            'Bewerbung_gesichtet': True,
            'Bewerbung_abgelehnt': True,
            'Einladung_Vorstellungsgespräch': False,
            'Vorstellungsgespräch': False,
            'Bewerber_abgelehnt': False,
            'Stelle_besetzt': False
        })

        # den RunningToken auf Initialwerte setzen.
        # Wir kopieren den Default-Token und setzen die Gateway-Entscheidungs-
        # Attribute manuell auf die gleichen wie beim expected Token
        running_token_1 = RunningToken.from_token(token=default_token)
        running_token_1.ungeeignete_Bewerbung = True
        running_token_1.ungeeigneter_Bewerber = True

        scen1 = Scenario(running_token=running_token_1,
                         expected_token=expected_token_1,
                         description=description_1)

        ##############################################
        ############ SZENARIO 2 ######################
        ##############################################

        description_2 = 'Bewerber nach dem Vorstellungsgespräch abgelehnt'

        expected_token_2 = Token(attributes={
            'ungeeignete_Bewerbung': False,
            'ungeeigneter_Bewerber': True,

            'Bewerbung_eingegangen': True,
            'Bewerbung_gesichtet': True,
            'Bewerbung_abgelehnt': False,
            'Einladung_Vorstellungsgespräch': True,
            'Vorstellungsgespräch': True,
            'Bewerber_abgelehnt': True,
            'Stelle_besetzt': False
        })

        running_token_2 = RunningToken.from_token(token=default_token)
        running_token_2.ungeeignete_Bewerbung = False
        running_token_2.ungeeigneter_Bewerber = True

        scen2 = Scenario(running_token=running_token_2,
                         expected_token=expected_token_2,
                         description=description_2)

        ##############################################
        ############ SZENARIO 3 ######################
        ##############################################

        description_3 = 'Bewerber bekommt die Stelle'

        expected_token_3 = Token(attributes={
            'ungeeignete_Bewerbung': False,
            'ungeeigneter_Bewerber': False,

            'Bewerbung_eingegangen': True,
            'Bewerbung_gesichtet': True,
            'Bewerbung_abgelehnt': False,
            'Einladung_Vorstellungsgespräch': True,
            'Vorstellungsgespräch': True,
            'Bewerber_abgelehnt': False,
            'Stelle_besetzt': True
        })

        running_token_3 = RunningToken.from_token(token=default_token)

        scen3 = Scenario(running_token=running_token_3,
                         expected_token=expected_token_3,
                         description=description_3)

        return [scen1, scen2, scen3]

    def get_ruleset(self) -> List[TokenStateRule]:


        # Rule: Bewerbung geht ein
        text_eingang = Text('Bewerbung geht ein')
        cond_eingang = TokenStateCondition(
            lambda t: t.Bewerbung_eingegangen == False)

        def m(t): t.Bewerbung_eingegangen = True
        mod_eingang = TokenStateModification(m)

        tsr_eingang = TokenStateRule(text=text_eingang,
                                     condition=cond_eingang,
                                     modification=mod_eingang)

        # Rule: Bewerbung sichten
        text_sichten = Text('Bewerbung sichten')
        cond_sichten = TokenStateCondition(
            lambda t: t.Bewerbung_eingegangen == True)

        def m(t): t.Bewerbung_gesichtet = True

        mod_sichten = TokenStateModification(m)

        tsr_sichten = TokenStateRule(text=text_sichten,
                                     condition=cond_sichten,
                                     modification=mod_sichten)

        # Rule: Bewerbung ablehnen
        text_ablehnen = Text('Bewerbung ablehnen')
        cond_ablehnen = TokenStateCondition(
            lambda t: t.ungeeignete_Bewerbung == True)

        def m(t): t.Bewerbung_abgelehnt = True
        mod_ablehnen = TokenStateModification(m)

        tsr_ablehnen = TokenStateRule(text=text_ablehnen,
                                      condition=cond_ablehnen,
                                      modification=mod_ablehnen)



        # Rule: Zum Vorstellungsgespräch einladen
        text_einladen = Text('Bewerber zum Vorstellungsgespräch einladen')
        cond_einladen = TokenStateCondition(
            lambda t: t.ungeeignete_Bewerbung is False and
                      t.Bewerbung_eingegangen is True and
                      t.Bewerbung_gesichtet is True and
                      t.Bewerbung_abgelehnt is False)

        def m(t): t.Einladung_Vorstellungsgespräch = True
        mod_einladung = TokenStateModification(m)

        tsr_einladung = TokenStateRule(text=text_einladen,
                                       condition=cond_einladen,
                                       modification=mod_einladung)

        # Rule: Vorstellungsgespräch führen
        text_vorstellung = Text('Vorstellungsgespräch führen')
        cond_vorstellung = TokenStateCondition(
            lambda t: t.Einladung_Vorstellungsgespräch == True)

        def m(t): t.Vorstellungsgespräch = True
        mod_vorstellung = TokenStateModification(m)

        tsr_vorstellung = TokenStateRule(text=text_vorstellung,
                                         condition=cond_vorstellung,
                                         modification=mod_vorstellung)

        # Rule: Bewerbunng abgelehnt (EndEvent)
        text_bewerber_ablehnen = Text('Bewerber ablehnen')
        cond_bewerber_ablehnen = TokenStateCondition(
            lambda t: t.ungeeigneter_Bewerber == True)

        def m(t): t.Bewerber_abgelehnt = True

        mod_bewerber_ablehnen = TokenStateModification(m)

        tsr_bewerber_ablehnen = TokenStateRule(text=text_bewerber_ablehnen,
                                      condition=cond_bewerber_ablehnen,
                                      modification=mod_bewerber_ablehnen)

        # Rule: Stelle besetzen
        text_stelle = Text('Stelle besetzen')
        cond_stelle = TokenStateCondition(
            lambda t: t.Vorstellungsgespräch == True and
                      t.ungeeigneter_Bewerber == False)

        def m(t):
            t.Bewerber_abgelehnt = False
            t.Stelle_besetzt = True
        mod_stelle = TokenStateModification(m)

        tsr_stelle = TokenStateRule(text=text_stelle,
                                    condition=cond_stelle,
                                    modification=mod_stelle)

        return [tsr_eingang, tsr_ablehnen, tsr_sichten,
                tsr_einladung, tsr_vorstellung, tsr_bewerber_ablehnen, tsr_stelle]