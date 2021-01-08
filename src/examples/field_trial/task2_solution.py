from typing import List

from src.models.i_solution import ISolution
from src.models.running_token import RunningToken
from src.models.scenario import Scenario
from src.models.token import Token
from src.models.token_state_condition import TokenStateCondition
from src.converter.bpmn_models.gateway.branch_condition import Operators
from src.models.token_state_modification import TokenStateModification
from src.models.token_state_rule import TokenStateRule


class Task2Solution(ISolution):

    def get_scenarios(self) -> List[Scenario]:
        scenarios = []

        description = 'Von allem nix da'
        running_token = RunningToken(attributes = {
            'Lagerbestand kontrolliert': False,
            'Fremdteilebedarf geprüft': False,
            'Eigenteilebedarf geprüft': False,
            'Fremdteile bestellt': False,
            'Eigenteile gefertigt': False,
            'Schubkarren zusammengebaut': False,
            'Schubkarren ausgeliefert': False,
            'Rechnung ausgestellt': False,
            'nix da': True,
        })

        expected_token = Token(attributes = {
            'Lagerbestand kontrolliert': True,
            'Fremdteilebedarf geprüft': True,
            'Eigenteilebedarf geprüft': True,
            'Fremdteile bestellt': True,
            'Eigenteile gefertigt': True,
            'Schubkarren zusammengebaut': True,
            'Schubkarren ausgeliefert': True,
            'Rechnung ausgestellt': True,
            'nix da': True
        })
        scen1 = Scenario(running_token=running_token,
                         expected_token=expected_token,
                         description=description)
        scenarios.append(scen1)

        return scenarios

    def get_ruleset(self) -> List[TokenStateRule]:
        # Rechnung ausstellen, nur wenn Schubkarren geliefert wurden
        syncloud_r1 = SynonymCloud.from_list(text=['Rechnung austellen'])

        cond_r1 = TokenStateCondition('Schubkarren ausgeliefert',Operators.EQUALS,True)
        modification_r1 = TokenStateModification(key='Rechnung ausgestellt', value=True)
        tsr_1 = TokenStateRule(condition=[cond_r1],
                               modification=[modification_r1],
                               synonym_cloud=syncloud_r1)

        # Schubkarren nur ausliefern, wenn Schubkarren zusammengebaut
        syncloud_r2 = SynonymCloud.from_list(text=['Schubkarren mit Lieferschein ausliefern '])

        cond_r2 = TokenStateCondition(tok_attribute='Schubkarren zusammengebaut',
                                      operator=Operators.EQUALS,
                                      tok_value=True)
        modification_r2 = TokenStateModification(key='Schubkarren ausgeliefert',
                                                 value=True)
        tsr_2 = TokenStateRule(condition=[cond_r2],
                               modification=[modification_r2],
                               synonym_cloud=syncloud_r2)

        # Schubkarren nur zusammengebauen, wenn Eigenteile gefertigt und Fremdteile bestellt
        syncloud_r3 = SynonymCloud.from_list(text=['Schubkarren zusammenbauen'])

        cond_r31 = TokenStateCondition(
            tok_attribute='Eigenteile gefertigt',
            operator=Operators.EQUALS,
            tok_value=True)

        cond_r32 = TokenStateCondition(
            tok_attribute='Fremdteile bestellt',
            operator=Operators.EQUALS,
            tok_value=True)

        modification_r3 = TokenStateModification(key='Schubkarren zusammengebaut',
                                                 value=True)
        tsr_3 = TokenStateRule(condition=[cond_r31, cond_r32],
                               modification=[modification_r3],
                               synonym_cloud=syncloud_r3)

        # Fremdteile nur bestellen, wenn Bedarf geprüft wurde
        syncloud_r4 = SynonymCloud.from_list(text=['Bestellungen für fremdbezogene Teile aufgeben'])

        cond_r4 = TokenStateCondition(
            tok_attribute='Fremdteilebedarf geprüft',
            operator=Operators.EQUALS,
            tok_value=True)

        modification_r4 = TokenStateModification(
            key='Fremdteile bestellt',
            value=True)

        tsr_4 = TokenStateRule(condition=[cond_r4],
                               modification=[modification_r4],
                               synonym_cloud=syncloud_r4)

        # Eigenteile nur fertigen, wenn Bedarf geprüft wurde
        syncloud_r5 = SynonymCloud.from_list(
            text=['Fertigung für eigengefertigte Teile anstoßen'])

        cond_r5 = TokenStateCondition(
            tok_attribute='Eigenteilebedarf geprüft',
            operator=Operators.EQUALS,
            tok_value=True)

        modification_r5 = TokenStateModification(
            key='Eigenteile gefertigt',
            value=True)

        tsr_5 = TokenStateRule(condition=[cond_r5],
                               modification=[modification_r5],
                               synonym_cloud=syncloud_r5)

        # Lagerbestand wird kontrolliert
        syncloud_r6 = SynonymCloud.from_list(text=['Lagerbestand an Schubkarren kontrollieren'])

        modification_r6 = TokenStateModification(key='Lagerbestand kontrolliert', value=True)
        tsr_6 = TokenStateRule(condition=[],
                               modification=[modification_r6],
                               synonym_cloud=syncloud_r6)


        # Bedarf fremder Teile wird geprüft, nur wenn Lager vorher kontrolliert wurde
        syncloud_r7 = SynonymCloud.from_list(
            text=['Bedarf an fremdbezogenen Teilen ermitteln'])

        cond_r7 = TokenStateCondition(
            tok_attribute='Lagerbestand kontrolliert',
            operator=Operators.EQUALS,
            tok_value=True)

        modification_r7 = TokenStateModification(
            key='Fremdteilebedarf geprüft',
            value=True)

        tsr_7 = TokenStateRule(condition=[cond_r7],
                               modification=[modification_r7],
                               synonym_cloud=syncloud_r7)

        # Bedarf eigener Teile wird geprüft, nur wenn Lager vorher kontrolliert wurde
        syncloud_r8 = SynonymCloud.from_list(
            text=['Bedarf an eigengefertigten Teilen ermitteln'])

        cond_r8 = TokenStateCondition(
            tok_attribute='Lagerbestand kontrolliert',
            operator=Operators.EQUALS,
            tok_value=True)

        modification_r8 = TokenStateModification(
            key='Eigenteilebedarf geprüft',
            value=True)

        tsr_8 = TokenStateRule(condition=[cond_r8],
                               modification=[modification_r8],
                               synonym_cloud=syncloud_r8)



        return [tsr_1, tsr_2, tsr_3, tsr_4, tsr_5, tsr_6, tsr_7, tsr_8]

    def get_chunker(self) -> Chunker:
        # we use german in our text, which isnt supported by NLTK -> use
        # default chunker and let synonymclouds check sentences
        return DefaultChunker()

