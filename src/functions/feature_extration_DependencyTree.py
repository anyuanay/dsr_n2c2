from pandas import DataFrame
import spacy

def extract_word_dep_features(input_dataframe):
    '''
    This function is used to extract features from processes sentences using dependency tree. We need to use spacy package here
    :param input_dataframe: dataframe extracted in function 1
    :return: We will get a dataframe with 6 columns.
             SentenceId to identify each token belongs to which file and which sentence.
             Token means which token we are extracting feature here.
             Relation means the relation of dependence between token and its corresponding head.
             Head_Text represents the head extracted using dependency tree for current token.
             Head_Lexical means what is the lexical form of the current head, like verb, noun and so on.
             Children_Len means the number of children related to current token.
    '''
    nlp = spacy.load("en_core_web_sm")
    Features = []
    for r, row in input_dataframe.iterrows():
        doc = nlp(row['Sentence'])

        for token in doc:
            Features.append([row["SentenceId"],str(token.text),  str(token.dep_), str(token.head.text),  token.head.pos_, len([child for child in token.children])])

    df = DataFrame(Features)
    df.columns = ["SentenceId", 'Token','Relation', 'Head_Text','Head_Lexical', 'Children_Len']

    return df


