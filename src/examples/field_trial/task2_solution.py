from typing import List

from src.converter.bpmn_models.bpmn_model import BPMNModel
from src.examples.i_example import IExample
from src.models.token import Token
from src.models.token_state_condition import TokenStateCondition, Operators
from src.models.token_state_modification import TokenStateModification
from src.models.token_state_rule import TokenStateRule
from src.nlp.chunker import Chunker
from src.nlp.synonym_cloud import SynonymCloud


class Task2Solution(IExample):

    def get_init_token(self) -> Token:
        attributes = {
            'Lagerbestand kontrolliert': False,
            'Fremdteilebedarf geprüft': False,
            'Eigenteilebedarf geprüft': False,
            'Fremdteile bestellt': False,
            'Eigenteile gefertigt': False,
            'Schubkarren zusammengebaut': False,
            'Schubkarren ausgeliefert': False,
            'Rechnung ausgestellt': False,
        }
        return Token(attributes=attributes)

    def get_solution_token(self) -> Token:
        attributes = {
            'Lagerbestand kontrolliert': True,
            'Fremdteilebedarf geprüft': True,
            'Eigenteilebedarf geprüft': True,
            'Fremdteile bestellt': True,
            'Eigenteile gefertigt': True,
            'Schubkarren zusammengebaut': True,
            'Schubkarren ausgeliefert': True,
            'Rechnung ausgestellt': True,
        }
        return Token(attributes=attributes)


    def get_ruleset(self) -> List[TokenStateRule]:
        # Rechnung ausstellen, nur wenn Schubkarren geliefert wurden
        syncloud_r1 = SynonymCloud.from_list(text=['Rechnung austellen'])

        cond_r1 = TokenStateCondition(tok_attribute='Schubkarren ausgeliefert',
                                      operator=Operators.EQUALS,
                                      tok_value=True)
        modification_r1 = TokenStateModification(key='Rechnung ausgestellt', value=True)
        tsr_1 = TokenStateRule(state_conditions=[cond_r1],
                               state_modifications=[modification_r1],
                               synonym_cloud=syncloud_r1)

        # Schubkarren nur ausliefern, wenn Schubkarren zusammengebaut
        syncloud_r2 = SynonymCloud.from_list(text=['Schubkarren mit Lieferschein ausliefern '])

        cond_r2 = TokenStateCondition(tok_attribute='Schubkarren zusammengebaut',
                                      operator=Operators.EQUALS,
                                      tok_value=True)
        modification_r2 = TokenStateModification(key='Schubkarren ausgeliefert',
                                                 value=True)
        tsr_2 = TokenStateRule(state_conditions=[cond_r2],
                               state_modifications=[modification_r2],
                               synonym_cloud=syncloud_r2)

        # Schubkarren nur zusammengebauen, wenn Eigenteile gefertigt und Fremdteile bestellt
        syncloud_r3 = SynonymCloud.from_list(text=['Schubkarren zusammenbauen'])

        cond_r3 = TokenStateCondition(
            tok_attribute='Eigenteile gefertigt',
            operator=Operators.EQUALS,
            tok_value=True)

        cond_r3 = TokenStateCondition(
            tok_attribute='Fremdteile bestellt',
            operator=Operators.EQUALS,
            tok_value=True)

        modification_r3 = TokenStateModification(key='Schubkarren zusammengebaut',
                                                 value=True)
        tsr_3 = TokenStateRule(state_conditions=[cond_r3, cond_r3],
                               state_modifications=[modification_r3],
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

        tsr_4 = TokenStateRule(state_conditions=[cond_r4],
                               state_modifications=[modification_r4],
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

        tsr_5 = TokenStateRule(state_conditions=[cond_r5],
                               state_modifications=[modification_r5],
                               synonym_cloud=syncloud_r5)

        # Lagerbestand wird kontrolliert
        syncloud_r6 = SynonymCloud.from_list(text=['Lagerbestand an Schubkarren kontrollieren'])

        modification_r6 = TokenStateModification(key='Lagerbestand kontrolliert', value=True)
        tsr_6 = TokenStateRule(state_conditions=[],
                               state_modifications=[modification_r6],
                               synonym_cloud=syncloud_r6)


        return [tsr_1, tsr_2, tsr_3, tsr_4, tsr_5, tsr_6]

    def get_chunker(self) -> Chunker:
        # we use german in our text, which isnt supported by NLTK -> use
        # default chunker and let synonymclouds check sentences
        grammar = r"""
        Chunk:     {}
        """
        return Chunker(chunk_grams=grammar)

    def get_students_process(self) -> BPMNModel:
        pass


