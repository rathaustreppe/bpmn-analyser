from typing import Optional, List, Tuple

import nltk

from src.nlp.IChunker import IChunker


class DefaultChunker(IChunker):
    # Default Chunker works as following:
    # original text: 'Hey there sup?'
    # preprocessed pos-tagged text: ('Hey there sup?', 'NN')
    # chunk found: ['Hey there sup?' - NN]
    def __init__(self) -> None:
        self.grammars = self.set_regex_grammars()

    def preprocess(self, text: str) -> List[Tuple[str, str]]:
        # The default chunker doesnt care about the text. It classifies
        # the whole text as one chunk. It treats the whole text as noun.
        return [(text, 'NN')]

    def find_chunk(self, text: str) -> nltk.tree.Tree:
        return super().find_chunk(text=text)

    def set_regex_grammars(self, grammars: str = '') -> str:
        # Because the whole text is treated as a single noun, we need
        # only one grammar, that checks for nouns.
        return r"""
        default_chunk:  {<NN>}
        """