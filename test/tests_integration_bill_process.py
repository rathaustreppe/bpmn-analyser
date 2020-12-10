import os
from typing import List

from nltk.corpus import wordnet as wn

from src.converter.converter import Converter
from src.graph_pointer import GraphPointer
from src.models.running_token import RunningToken
from src.models.token import Token
from src.models.token_state_condition import TokenStateCondition
from src.converter.bpmn_models.gateway.branch_condition import Operators
from src.models.token_state_modification import TokenStateModification
from src.models.token_state_rule import TokenStateRule
from src.nlp.chunker import Chunker
from src.nlp.synonym_cloud import SynonymCloud


class TestIntegrationBillProcess:
    # define some often used texts as variables
    ml_signs_bill = 'ML signs bill'
    send_bill_to_zittau = 'send bill to Zittau'
    zittau_checks_contract = 'Zittau checks contract'
    zittau_signs_bill = 'Zittau signs bill'
    send_bill_to_dresden = 'send bill to Dresden'
    startendevent_placeholder = 'startendevent'

    @staticmethod
    def solution_token() -> RunningToken:
        attributes_solution = {
            'place': 'Dresden',
            'signature_ML': True,
            'signature_Zittau': True,
            'contract_checked': True
        }
        return RunningToken(attributes=attributes_solution)

    @staticmethod
    def ruleset() -> List[TokenStateRule]:
        wn_synset_bill = wn.synset('bill.n.02')

        # Ruleset for modifying a token. These are real-life constraints.
        # E.g. you can
        # only sign a (physical) paper, if it is in front of you.
        # Rule 1: ML signs: only in Goerlitz
        # synonymcloud: 'ML' is fixed, 'signs' has synonyms
        syncloud_r1 = SynonymCloud.from_list(text=['ML',
                                                   wn.synset('sign.v.01'),
                                                   wn_synset_bill,
                                                   ])
        cond_r1 = TokenStateCondition(lambda t: t.place == 'Goerlitz')
        def m(t): t.signature_ML = True
        modification_r1 = TokenStateModification(m)
        tsr_1 = TokenStateRule(condition=cond_r1,
                               modification=modification_r1,
                               synonym_cloud=syncloud_r1)

        # Rule 2: send to <places>: no condition, but change 'place' to a value
        # of <places>
        # synonymcloud: '<place> is fixed', 'send' has synonyms,
        # 'bill' has synonyms, 'to' is mandatory

        def zittau(t): t.place = 'Zittau'
        def goerlitz(t): t.place = 'Goerlitz'
        def dresden(t): t.place = 'Dresden'

        places = [('Zittau',zittau), ('Goerlitz', goerlitz), ('Dresden', dresden)]
        tsr_2 = []
        for place in places:
            syncloud = SynonymCloud.from_list(text=[wn.synset('send.v.03'),
                                                    wn_synset_bill,
                                                    'to', place[0]])
            modification = TokenStateModification(modification=place[1])
            tsr = TokenStateRule(modification=modification,
                                 synonym_cloud=syncloud)
            tsr_2.append(tsr)

        # Rule 3: checking contract: only in Zittau
        # synonymcloud: 'Zittau' is fixed, 'checks' and 'contract' have synonyms
        syncloud_r3 = SynonymCloud.from_list(text=['Zittau',
                                                   wn.synset('check.v.03'),
                                                   wn.synset('contract.n.01')])
        cond_r3 = TokenStateCondition(lambda t: t.place == 'Zittau')
        def m(t): t.contract_checked = True
        modification_r3 = TokenStateModification(m)
        tsr_3 = TokenStateRule(condition=cond_r3,
                               modification=modification_r3,
                               synonym_cloud=syncloud_r3)

        # Rule 4: Zittau signs: only in Zittau and with a ckecked contract
        # synonymcloud: 'Zittau' is fixed, 'signs' has synonyms
        syncloud_r4 = SynonymCloud.from_list(text=['Zittau',
                                                   wn.synset('sign.v.01'),
                                                   wn_synset_bill,
                                                   ])
        cond1_r4 = TokenStateCondition(lambda t: t.place == 'Zittau' and t.contract_checked == True)
        def m(t): t.signature_Zittau = True
        modification_r4 = TokenStateModification(modification=m)
        tsr_4 = TokenStateRule(condition=cond1_r4,
                               modification=modification_r4,
                               synonym_cloud=syncloud_r4)

        ruleset = [tsr_1, tsr_3, tsr_4]
        ruleset.extend(tsr_2)
        return ruleset

    @staticmethod
    def chunker() -> Chunker:
        # required ChunkGrams to match synonymclouds:
        chunk_grams = r"""
                VB_NN_TO_NN:    {<VB.?>+<NN.?><TO>?<NN.?>+}
                NN_VB_NN:       {<NN.?><VB.?><NN.?>}
                VB_NN:          {<VB.?><NN.?>}
                """

        # sadly there are words, that a pos tagger always classifies wrong.
        # we define them here correctly and pass them to the chunker.
        tagged_words_bypass = [('Goerlitz', 'NN'), ('Zittau', 'NN'),
                               ('Dresden', 'NN'),
                               ('signs', 'VB'), ('checks', 'VB')]
        return Chunker(chunk_grams=chunk_grams,
                       tagged_words_bypass=tagged_words_bypass)

    @staticmethod
    def init_token() -> RunningToken:
        # important to have scope='function' on this fixture. Init-token will
        # change its attributes in GraphPointer.
        # Perhaps copy.copy or copy.deepcopy may work aswell.
        init_attributes = {
            "place": "Zittau",
            "signature_ML": False,
            "signature_Zittau": False,
            "contract_checked": False
        }
        return RunningToken(attributes=init_attributes)

    @staticmethod
    def run_pointer(graph_pointer: GraphPointer) -> RunningToken:
        ret = graph_pointer.iterate_model()
        if ret[0] == 0:
            return graph_pointer.token
        else:
            # infinite loop
            assert False

    def execute_process(self, filename: str,
                        xml_folders_path,
                        chunker,
                        ruleset,
                        init_token:RunningToken) -> RunningToken:

        xml_file_path = os.path.join(xml_folders_path, filename)

        converter = Converter()
        model = converter.convert(rel_file_path=xml_file_path)

        graph_pointer = GraphPointer(model=model,
                                     token=init_token,
                                     ruleset=ruleset,
                                     chunker=chunker)

        return self.run_pointer(graph_pointer=graph_pointer)

    def test_bill_process_system_test(self, xml_folders_path):

        file = os.path.join('bill process', 'bill_process_with_def.bpmn')
        return_token = self.execute_process(filename=file,
                                            xml_folders_path=xml_folders_path,
                                            chunker=self.chunker(),
                                            ruleset=self.ruleset(),
                                            init_token=self.init_token())

        assert return_token == self.solution_token()

    def test_bill_process_from_graph2(self, xml_folders_path):
        # bill first arrives in goerlitz
        def m(t): t.place = 'Goerlitz'
        modification = TokenStateModification(m)
        bill_process_init_token = self.init_token()
        modification.change_token(token=bill_process_init_token)

        file = os.path.join('bill process', 'bill_process_2.bpmn')
        return_token = self.execute_process(filename=file,
                                            xml_folders_path=xml_folders_path,
                                            chunker=self.chunker(),
                                            ruleset=self.ruleset(),
                                            init_token=bill_process_init_token)
        assert return_token == self.solution_token()

    def test_bill_process_from_graph3(self, xml_folders_path):

        file = os.path.join('bill process', 'bill_process_3.bpmn')
        return_token = self.execute_process(filename=file,
                                            xml_folders_path=xml_folders_path,
                                            chunker=self.chunker(),
                                            ruleset=self.ruleset(),
                                            init_token=self.init_token())
        assert return_token == self.solution_token()

    def test_bill_process_from_graph4(self, xml_folders_path):

        file = os.path.join('bill process', 'bill_process_4.bpmn')
        return_token = self.execute_process(filename=file,
                                            xml_folders_path=xml_folders_path,
                                            chunker=self.chunker(),
                                            ruleset=self.ruleset(),
                                            init_token=self.init_token())
        assert return_token == self.solution_token()

    def test_bill_process_from_graph5(self, xml_folders_path):
        # business process doesnt work
        # ML cant sign in Zittau
        file = os.path.join('bill process', 'bill_process_5.bpmn')
        return_token = self.execute_process(filename=file,
                                            xml_folders_path=xml_folders_path,
                                            chunker=self.chunker(),
                                            ruleset=self.ruleset(),
                                            init_token=self.init_token())

        assert return_token != self.solution_token()
        assert return_token['signature_ML'] is False
