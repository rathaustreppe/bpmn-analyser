import nltk as nltk

from src.models.graph_text import GraphText


class TextAnalyzer:

    def analyze(self, text: GraphText):
        """
        Gets text, preprocesses text, does chunking,
        returns tokenstaterule(s) to apply
        """
        text = self.preprocess(text=text.get_text())

        # chunking

        # chunk to (synonymcloud, TSR)

        # return TSR

    def chunking(self):
        """
        Analyzes preprocessed text and finds chunks.
        Returns chunks e.g. 'weather is good' in the text
        'the weather is good on mondays'
        """


    def preprocess(self, text: str):
        # Sentence Tokenizing
        # from "long sentence1. long sentence2" to
        # [["long sentence1], ["long sentence2"]]
        sentences = nltk.sent_tokenize(text)

        # Word Tokenizing
        # from [["long sentence"]] to [["long", "sentence"]]
        sentences = [nltk.wordpunct_tokenize(sentence) for
                     sentence in sentences]

        # Lowercase Normalisation
        # from [["Long", "Sentence"]] to [["long", "sentence"]]
        def lower_sentence(sentence):
            return [word.lower() for word in sentence]

        sentences = [lower_sentence(sent) for sent in
                     sentences]

        # Optional: Stop word removal
        # # from [["long", "to", "bar"]] to [["long", "bar"]]
        # def stopword_removal(sentence):
        #     return [word for word in sentence if word not in stopwords]
        # sentences = [stopword_removal(sent) for sent in sentences]

        # POS Tagging
        sentences = [nltk.pos_tag(sent) for sent in
                     sentences]

        # # Lemmatize   - might be useful for more advanced
        # nlp in near future. So I leave it here.
        # # # from [["longer", "bar"]] to [["long", "bar"]]
        # def lemmatize_sentence(sentence, lemmatizer):
        #     return [lemmatizer.lemmatize(word=word) for word in sentence]
        # lemmatizer = nltk.stem.WordNetLemmatizer()
        # sentences = [lemmatize_sentence(sent,lemmatizer) for sent in sentences]

        print(f'Preprocessed sentences:', sentences)
        return sentences
