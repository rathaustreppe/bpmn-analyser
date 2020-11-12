from typing import List

from pedantic import pedantic_class

from src.models.token_state_condition import Operators
from src.models.token_state_modification import TokenStateModification
from src.models.token_state_rule import TokenStateRule
from src.nlp.IChunker import IChunker


@pedantic_class
class RuleFinder:
    def __init__(self, chunker: IChunker, ruleset: List[TokenStateRule]) -> None:
        self.chunker = chunker
        self.ruleset = ruleset

    def find_rules(self, text: str) -> List[TokenStateRule]:
        """
        With a given text, this function finds TokenStateRules that have a
        SynonymCloud that is synonym to the given text. This means, the given
        text matches the pre-defined solution of the BPMN-diagram. It returns
        the TokenStateRules that >may< be applied to the Token -> you still need
        to check the TokenStateConditions beforehand.
        """

        # no handling of start and end events implemented yet, skip them by
        # finding no rule per default
        # ToDo: No handling of start and end events implemented
        if text == 'startendevent':
            return []

        if text.endswith('++'):
            return [self._make_increment_rule(text=text)]


        chunk = self.chunker.find_chunk(text=text)

        matching_rules = []
        for rule in self.ruleset:
            try:
                if rule.synonym_cloud.are_synonyms(chunk=chunk):
                    matching_rules.append(rule)
            except Exception:
                continue

        return matching_rules

    def _make_increment_rule(self, text:str) -> TokenStateRule:
        # needs sth. like "a ++" or "a++" (without space)

        # remove increment and space to have only the name
        token_attribute = text
        token_attribute = token_attribute.replace(Operators.INCREMENT.value, '')
        token_attribute = token_attribute.replace(' ', '')

        modification = TokenStateModification(key=token_attribute, value='++')

        return TokenStateRule(state_conditions=[],
                             state_modifications=[modification])
