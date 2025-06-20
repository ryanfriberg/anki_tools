# from anki.notes import Note
import anki.collection as collection
import re
import pandas as pd

def post_process(col_path: str, deck_name: str):
    col = collection.Collection(col_path) 

    deck = col.decks.by_name(deck_name)
    note_ids = col.find_notes(f'deck:"{deck["name"]}"')

    partials = set()
    for nid in note_ids:
        note = col.get_note(nid)
        
        card_ids = note.card_ids()
        states = []
        for cid in card_ids:
            card = col.get_card(cid)
            states.append(card.queue)
        if (0 in states) and (not all(state == 0 for state in states)):
            partials.add(note)
            note.add_tag("partially_learned")
            col.update_note(note)

    print("# paritally learned:", len(partials))
    for n in partials:
        if ("Vocab" in n.keys()):
            print(n["Vocab"])
        elif("Front" in n.keys()):
            print(n["Front"])

    col.close()


post_process(col_path="/Users/ryanfriberg/Library/Application Support/Anki2/Ryan/collection.anki2",
             deck_name="korean")
