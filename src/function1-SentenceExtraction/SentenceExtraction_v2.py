import numpy as np
import pandas as pd
import spacy
import re
from spacy.language import Language


@Language.component("set_custom_boundaries")
def set_custom_boundaries(doc):
    for i, token in enumerate(doc[:-2]): 
        if re.search('\.', doc[i - 1].text) and re.search('^\s+', doc[i].text) and doc[i + 1].is_alpha:
            doc[i + 1].is_sent_start = True
            if re.search('^\s+', doc.text):
                doc[i].is_sent_start = False
        elif re.search('^\s{2,}', doc[i].text) and doc[i + 1].is_alpha:
            doc[i + 1].is_sent_start = True
    return doc


# Defines the strings that can be used as section titles.
section_list = ['HISTORY OF PRESENT ILLNESS', 'PHYSICAL EXAMINATION', 'LABORATORY DATA', 'ASSESSMENT AND PLAN', 'NARRATIVE']

def extract_sentences(notesId, notesText, sections=section_list):
    
    # Find the existing sections in the current text and arrange them in order of appearance.
    sections_order = []
    for section in sections:
        start = notesText.find(section)
        if start != -1:
            sections_order.append((start, section))
    sections_order = sorted(sections_order)

    # Divide the entire text with the section title as the boundary
    if sections_order:
        # Divide the entire text in the same order with the existing sections.
        sections_split = '|'.join([section_order[1] for section_order in sections_order])
        split_text = re.split(sections_split, notesText)
        # Combine the title of sections with corresponding divided texts.
        sections_text = {'No Section':split_text[0]}
        for i in range(len(sections_order)):
            sections_text[sections_order[i][1]] = split_text[i+1]

    # If no existing sections, consider the entire text as "No Section".
    else:
        sections_text = {'No Section':notesText}

    # Use spacy divide text into sentence.
    nlp = spacy.load("en_core_web_sm")
    nlp.add_pipe("set_custom_boundaries", before="parser")
    for section in sections_text.keys():
        res = nlp(sections_text[section])
        sections_text[section] = [sent.text.strip() for sent in res.sents if not re.search('^\s+$', sent.text)]
    
    # Construct DataFrame from nested lists.
    res_list = []
    start_id = 1
    num_ids = len([text for texts in sections_text.values() for text in texts])
    for section,texts in sections_text.items():
        for text in texts:
            SentenceId = notesId + '_' + str(start_id)
            Sentence = text
            Start = notesText.find(text)
            End = Start + len(text)
            Section = section
            if start_id == 1:
                PrevSentId = np.nan
            else:
                PrevSentId = notesId + '_' + str(start_id - 1)
            if start_id == num_ids:
                NextSentId = np.nan
            else:
                NextSentId = notesId + '_' + str(start_id + 1)
            res_list.append([notesId, SentenceId, Sentence, Start, End, Section, PrevSentId, NextSentId])
            start_id += 1

    # Output: a DataFrame with columns 
    column = ['NotesId', 'SentenceId', 'Sentence', 'Start', 'End', 'Section', 'PrevSentId', 'NextSentId']
    df = pd.DataFrame(res_list, columns=column)

    return df