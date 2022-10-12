import xml.etree.ElementTree
import numpy
import pandas
import spacy
import requests


class RxNormExtractor:

    def __init__(self, sentences_df, set_default_args=None, copy = True):
        self.sentences_df = sentences_df.copy() if copy else sentences_df

        # API dictionary https://lhncbc.nlm.nih.gov/RxNav/APIs/RxNormAPIs.html
        default_args = {
            # https://lhncbc.nlm.nih.gov/RxNav/APIs/api-RxNorm.filterByProperty.html
            "filterByProperty": ["REST/rxcui/rxcui/filter.xml", "propName", ".//rxcui"],

            # https://lhncbc.nlm.nih.gov/RxNav/APIs/api-RxNorm.findRxcuiByString.html
            "findRxcuiByString": ["REST/rxcui.xml", "name", ".//rxnormId"],

            # https://lhncbc.nlm.nih.gov/RxNav/APIs/api-RxNorm.getApproximateMatch.html
            "getApproximateMatch": ["REST/approximateTerm", "term", ".//rxcui"],

            # https://lhncbc.nlm.nih.gov/RxNav/APIs/api-RxNorm.getDrugs.html
            "getDrugs": ["REST/drugs", "name", ".//rxcui"],

            # https://lhncbc.nlm.nih.gov/RxNav/APIs/api-RxNorm.getSpellingSuggestions.html
            "getSpellingSuggestions": ["REST/spellingsuggestions.xml", "name", ".//suggestion"],
        }
        self.args_dict = set_default_args if set_default_args is not None else default_args
        self.nlp = spacy.load("en_core_web_sm")

        self.tokens = None
        self.features = None
        self.extract_result = None

    def tokenize(self, sentence_df):
        tokens = []
        for i, row in sentence_df.iterrows():
            t = pandas.DataFrame({
                "SentenceId": row.SentenceId,
                "words": [*self.nlp(row.Sentence.lower())]
            }, dtype="string")
            tokens.append(t)
        tokens_df = pandas.concat(tokens, axis=0).reset_index(drop=True)
        tokens_df["words_id"] = tokens_df.index
        self.tokens = tokens_df
        return self.tokens

    @staticmethod
    def single_query(word, url, par, xpath_rule, method=True):  # method: True -> GET, False -> PUT
        try:
            if method:
                message = requests.get("https://rxnav.nlm.nih.gov/" + url, params={par: word})
            else:
                message = requests.post("https://rxnav.nlm.nih.gov/" + url, params={par: word})

            if message.status_code == 200:
                return xml.etree.ElementTree.fromstring(message.text).findall(xpath_rule)[0].text
        except:
            return numpy.NaN

    # multiple features query flow
    def query(self):
        uni_words = pandas.Series(self.tokens["words"].unique())
        features = {"words": uni_words}
        for col_name in self.args_dict:
            print("Querying Feature[{}]. Please wait...".format(col_name))
            features[col_name] = uni_words.apply(
                lambda x: self.single_query(x, *self.args_dict[col_name]))
            self.features = pandas.DataFrame(features)
        return self.features

    def extract(self, args=None, drop_global_id = True):
        self.args_dict = args if args is not None else self.args_dict

        self.tokenize(self.sentences_df)
        self.query()
        self.extract_result = self.tokens.merge(self.features, on="words", )\
            .set_index("words_id").sort_index()

        if drop_global_id:
            self.extract_result.reset_index(drop=True, inplace=True)

        return self.extract_result
