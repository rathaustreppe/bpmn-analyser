from typing import List

from nltk.corpus import wordnet as wn

from src.converter.converter import Converter
from src.graph_pointer import GraphPointer
from src.models.token import Token

# solution token
from src.models.token_state_condition import TokenStateCondition, Operators
from src.models.token_state_modification import TokenStateModification
from src.models.token_state_rule import TokenStateRule
from src.nlp.chunker import Chunker
from src.nlp.synonym_cloud import SynonymCloud

# solution token
init_attributes = {
    'place': 'Dresden',
    'signature ML': True,
    'signature Zittau': True,
    'contract checked': True
}
solution_token = Token(attributes=init_attributes)

# Ruleset for modifying a token. These are real-life constraints. E.g. you can
# only sign a (physical) paper, if it is in front of you.
# Rule 1: ML signs: only in Goerlitz
# synonymcloud: 'ML' is fixed, 'signs' has synonyms
syncloud_r1 = SynonymCloud.from_list(text=['ML',
                                           wn.synset('sign.v.01'),
                                           wn.synset('bill.n.02'),
                                           ])
cond_r1 = TokenStateCondition(tok_attribute='place',
                              operator=Operators.EQUALS,
                              tok_value='Goerlitz')
modification_r1 = TokenStateModification(key='signature ML', value=True)
tsr_1 = TokenStateRule(state_conditions=[cond_r1],
                       state_modifications=[modification_r1],
                       synonym_cloud=syncloud_r1)

# Rule 1.1: Zittau signs: only in Zittau and with a ckecked contract
# synonymcloud: 'Zittau' is fixed, 'signs' has synonyms
syncloud_r11 = SynonymCloud.from_list(text=['Zittau',
                                            wn.synset('sign.v.01'),
                                            wn.synset('bill.n.02'),
                                            ])
cond1_r11 = TokenStateCondition(tok_attribute='place',
                                operator=Operators.EQUALS,
                                tok_value='Zittau')
cond2_r11 = TokenStateCondition(tok_attribute='contract checked',
                                operator=Operators.EQUALS,
                                tok_value=True)
modification_r11 = TokenStateModification(key='signature Zittau', value=True)
tsr_11 = TokenStateRule(state_conditions=[cond1_r11, cond2_r11],
                        state_modifications=[modification_r11],
                        synonym_cloud=syncloud_r11)

# Rule 2: send to <places>
places = ['Zittau', 'Goerlitz', 'Dresden']
# synonymcloud: 'Zittau is fixed', 'send' has synonyms, 'to' optional
syncloud_r2 = SynonymCloud.from_list(text=[wn.synset('send.v.03'),
                                           wn.synset('bill.n.02'),
                                           'to',
                                           'Zittau'])
modification_r2 = TokenStateModification(key='place', value='Zittau')
tsr_2 = TokenStateRule(state_conditions=[],
                       state_modifications=[modification_r2],
                       synonym_cloud=syncloud_r2)

# Rule 2.1:
syncloud_r21 = SynonymCloud.from_list(text=[wn.synset('send.v.03'),
                                            wn.synset('bill.n.02'),
                                            'to',
                                            'Goerlitz'])
modification_r21 = TokenStateModification(key='place', value='Goerlitz')
tsr_21 = TokenStateRule(state_conditions=[],
                        state_modifications=[modification_r21],
                        synonym_cloud=syncloud_r21)

# Rule 2.2:
syncloud_r22 = SynonymCloud.from_list(text=[wn.synset('send.v.03'),
                                            wn.synset('bill.n.02'),
                                            'to',
                                            'Dresden'])
modification_r22 = TokenStateModification(key='place', value='Dresden')
tsr_22 = TokenStateRule(state_conditions=[],
                        state_modifications=[modification_r22],
                        synonym_cloud=syncloud_r22)

# Rule 3: checking contract: only in Zittau
# synonymcloud: 'Zittau' is fixed, 'checks' and 'contract' have synonyms
syncloud_r3 = SynonymCloud.from_list(text=['Zittau',
                                           wn.synset('check.v.03'),
                                           wn.synset('contract.n.01')])
cond_r3 = TokenStateCondition(tok_attribute='place',
                              operator=Operators.EQUALS,
                              tok_value='Zittau')
modification_r3 = TokenStateModification(key='contract checked', value=True)
tsr_3 = TokenStateRule(state_conditions=[cond_r3],
                       state_modifications=[modification_r3],
                       synonym_cloud=syncloud_r3)

ruleset = [tsr_1, tsr_11, tsr_2, tsr_21, tsr_22, tsr_3]

# required ChunkGrams to match synonymclouds:
chunk_grams = r"""
VB_NN_TO_NN:    {<VB.?>+<NN.?><TO>?<NN.?>+}
NN_VB_NN:       {<NN.?><VB.?><NN.?>}
VB_NN:          {<VB.?><NN.?>}
"""

# sadly there are words, that a pos tagger always classifies wrong.
# we define them here correctly and pass them to the chunker.
tagged_words_bypass = [('Goerlitz', 'NN'), ('Zittau', 'NN'), ('Dresden', 'NN'),
                       ('signs', 'VB'), ('checks', 'VB')]
chunker = Chunker(chunk_grams=chunk_grams,
                  tagged_words_bypass=tagged_words_bypass)

# This is the students solution. We want to check if this BPMN-Graph is correct.
# Graph from *.bpmn-file
path_to_bpmn = r'..\src\converter\bpmn-files\3-correct.bpmn'

converter = Converter()
g = converter.convert(rel_path_to_bpmn=path_to_bpmn)

init_attributes = {
    "place": "Zittau",
    "signature ML": False,
    "signature Zittau": False,
    "contract checked": False
}
t = Token(attributes=init_attributes)
gp = GraphPointer(graph=g, token=t, ruleset=ruleset, chunker=chunker)

# checking students solution
graph_pointer_list: List[GraphPointer] = [gp]

for graph_pointer in graph_pointer_list:
    for i in range(100):
        ret = graph_pointer.runstep_graph()
        if ret == 1:
            # compare tokens
            return_token = graph_pointer.get_token()

            print(return_token)
            print(solution_token)

            if return_token == solution_token:
                print('token equal: students solution is correct!\n')
            else:
                print('token not equal: business process is wrong\n')

            break
        # max 100 steps
        i += 1
