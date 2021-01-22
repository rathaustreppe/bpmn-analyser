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
            'für_Bewerber_entschieden': False,
            'Stelle_besetzt': False
        })


        ##############################################
        ############ SZENARIO 1 ######################
        ##############################################

        description_1 = 'Bewerber wird sofort abgelehnt'

        expected_token_1 = Token(attributes={
            'ungeeignete_Bewerbung': True,
            'ungeeigneter_Bewerber': True,

            'Bewerbung_eingegangen': True,
            'Bewerbung_gesichtet': True,
            'Bewerbung_abgelehnt': True,
            'Einladung_Vorstellungsgespräch': False,
            'Vorstellungsgespräch': False,
            'für_Bewerber_entschieden': False,
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
        scenarios.append(scen1)

        ##############################################
        ############ SZENARIO 2 ######################
        ##############################################

        description_2 = 'Bewerber nach dem Vorstellungsgespräch abelehnt'

        expected_token_2 = Token(attributes={
            'ungeeignete_Bewerbung': False,
            'ungeeigneter_Bewerber': True,

            'Bewerbung_eingegangen': True,
            'Bewerbung_gesichtet': True,
            'Bewerbung_abgelehnt': False,
            'Einladung_Vorstellungsgespräch': True,
            'Vorstellungsgespräch': True,
            'für_Bewerber_entschieden': False,
            'Stelle_besetzt': False
        })

        running_token_2 = RunningToken.from_token(token=default_token)
        running_token_2.ungeeignete_Bewerbung = False
        running_token_2.ungeeigneter_Bewerber = True

        scen2 = Scenario(running_token=running_token_2,
                         expected_token=expected_token_2,
                         description=description_2)
        scenarios.append(scen2)

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
            'für_Bewerber_entschieden': True,
            'Stelle_besetzt': True
        })

        running_token_3 = RunningToken.from_token(token=default_token)

        scen3 = Scenario(running_token=running_token_3,
                         expected_token=expected_token_3,
                         description=description_3)
        # hier die Tokens und Szenarien
        # ...

        return [scen1, scen2, scen3]

    def get_ruleset(self) -> List[TokenStateRule]:

        text_einladen= Text('Bewerber zum Vorstellungsgespräch einladen')
        cond_einladen = TokenStateCondition(
            lambda t: t.ungeeignete_Bewerbung is False and
                      t.Bewerbung_eingegangen is True and
                      t.Bewerbung_gesichtet is True and
                      t.Bewerbung_abgelehnt is False)


        def m(t): t.Einladung_Vorstellungsgespräch = True
        mod_einladung = TokenStateModification(m)


        tsr_einladung = TokenStateRule(condition=cond_einladen,
                                       modification=mod_einladung,
                                       text=text_einladen)

        return [tsr_einladung]