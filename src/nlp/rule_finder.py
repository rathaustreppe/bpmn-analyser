from typing import List

from pedantic import pedantic_class

from src.converter.bpmn_models.gateway.branch_condition import Operators
from src.models.token_state_modification import TokenStateModification
from src.models.token_state_rule import TokenStateRule


@pedantic_class
class RuleFinder:
    def __init__(self, ruleset: List[TokenStateRule]) -> None:
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

        # if an BPMNActitivy contains text like 'a++' it means, the
        # token attribute 'a' should be increment by 1. We will generate such a
        # modification on the fly right now.
        if text.endswith('++'):
            return [self._make_increment_rule(text=text)]

        matching_rules = []
        for rule in self.ruleset:
            try:
                if rule.text == text:
                    matching_rules.append(rule)
            except Exception:
                continue

        return matching_rules

    def _make_increment_rule(self, text:str) -> TokenStateRule:
        # converts 'haha++' to executable statement 't.haha += 1'

        # remove increment and space to have only the name
        token_attribute = text
        token_attribute = token_attribute.replace(Operators.INCREMENT.value, '')
        token_attribute = token_attribute.replace(' ', '')


        # This block of code is a closure. To change the specific token attribute
        # we need to know the token and the attribute. Right now, we know the
        # attribute but not the token. Later, we will know the token but not
        # the attribute. So we define a closure to store the attribute inside
        # the function and later we can call this function with the token-paramter.
        def increment_function(a):
            attribute = a
            def increment_template(t):
                t[attribute] += 1
            return increment_template

        tsm = TokenStateModification(modification=increment_function(a=token_attribute))

        return TokenStateRule(modification=tsm)
