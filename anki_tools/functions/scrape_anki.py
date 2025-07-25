from anki_tools.enums.anki_enums import AnkiEnum

import pandas as pd
import anki.collection as collection


def find_cloze(deck_name: str, col_path: str = AnkiEnum.COL_PATH, debug: bool = False):
    col = collection.Collection(col_path) 

    deck = col.decks.by_name(deck_name)

    if (deck is None):
        col.close()

    note_ids = col.find_notes(f'deck:"{deck["name"]}"')

    clozes = []
    for nid in note_ids:
        note = col.get_note(nid)
        
        sentence = note["Sentence"]

        start_string = "{{c1::"
        end_string = "}}"
        start_index = sentence.find(start_string)
        start_of_substring = start_index + len(start_string)
        end_index = sentence.find(end_string, start_of_substring)

        cloze = sentence[start_of_substring:end_index]
        clozes.append(cloze)
    

    df = pd.DataFrame(set(clozes))
    df.to_csv('words_database.csv', mode='a', header=False, index=False)
    
    col.close()


find_cloze("japanese::sentences::vocab")