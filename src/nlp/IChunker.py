from abc import ABC, abstractmethod
from typing import List, Tuple

import nltk
from pedantic import pedantic_class

from src.exception.language_processing_errors import NoChunkFoundError, \
    MultipleChunksFoundError


@pedantic_class
class IChunker(ABC):

    @abstractmethod
    def preprocess(self, text:str) -> List[Tuple[str, str]]:
        # Implements all preprocessing of a text that is necessary for the
        # chunker to find chunks.
        pass

    @abstractmethod
    def find_chunk(self, text: str) -> nltk.tree.Tree:
        # Returns the chunk that is found in the text.
        preprocessed_text = self.preprocess(text=text)
        parser = nltk.RegexpParser(self.grammars)
        parsed = parser.parse(preprocessed_text)

        # S is the root terminal of every tree per default by NLTK.
        # So it is the root of every chunk. And if no chunk was found,
        # then it is the root of the text.
        # So to decide if sth. is a real chunk, it has a different label
        # then 'S' and is a tree.
        chunks = [chunk for chunk in parsed if
                  isinstance(chunk, nltk.tree.Tree)
                  and chunk.label() != 'S']

        if len(chunks) == 0:
            raise NoChunkFoundError(pos_list=preprocessed_text, chunker=self)

        elif len(chunks) > 1:
            raise MultipleChunksFoundError(pos_list=preprocessed_text,
                                           found_chunks=chunks,
                                           chunker=self)
        else:
            return chunks[0]

    @abstractmethod
    def set_regex_grammars(self, grammars: str = '') -> str:
        # Regex-grammars are used to find chunks in preprocessed text.
        # Think about it as simple pattern matching with Regex.

        # Uses default empty string as parameter, so you can define
        # default grammars in this function or give them as a parameter.

        # When defining multiple chunk-grammars, make sure
        # they have no space before them (except tab-spaces) - and are correctly
        # aligned with tabulator
        # Example:
        # grammars = r"""
        #       VB_NN_TO_NN:    {<VB.?>+<NN.?><TO><NN.?>+}
        #       NN_VB_NN:       {<NN.?><VB.?><NN.?>}
        #       """
        pass
