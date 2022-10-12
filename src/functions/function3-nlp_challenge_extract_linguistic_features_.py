# -*- coding: utf-8 -*-
"""NLP Challenge extract linguistic features .ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1JLDBS0IgqFjx7ysBTkpN85BEmz74SFmm
"""

import pandas as pd
import spacy
nlp = spacy.load("en_core_web_sm")

def extract_word_linguistic_features(extracted_df):
  tokens_info=[]
  df_to_dict = extracted_df.to_dict(orient='index')
  for i in range(len(df_to_dict)):
    Extracted_sentence = nlp(df_to_dict[i]["Sentence"])
    Sentence_Id = df_to_dict[i]["SentenceId"]
    for token in Extracted_sentence:
      tokens_info.append([Sentence_Id, token.text, token.lemma_, token.pos_, token.tag_, token.dep_, token.shape_, token.is_alpha, token.is_stop])
  token_df = pd.DataFrame(tokens_info, columns = ['SentenceId', 'Token', 'Lemma', 'POS','TAG', 'DEP', 'Shape', 'Is_Alpha', 'Is_Stop'])
  return token_df
