import anki.collection as collection
import logging


class CollectionProcessor:
    def __init__(col_path: str):
        pass

    def replace_str_from_field(field_name: str, 
                               substring: str, 
                               replacement: str):
        pass


'''

def post_process(col_path: str):
    col = collection.Collection(col_path) 
    deck = col.decks.by_name("korean::vocab::common")
    card_ids = col.find_cards(f'deck:"{deck["name"]}"')

    seen_notes = set()
    count1 = 0
    count2 = 0
    for card_id in card_ids:
        card = col.get_card(card_id)
        note = col.get_note(card.nid)
        if (card.nid in seen_notes):
            continue
        else:
            seen_notes.add(card.nid)
        # suspended = card.queue

        meaning = note["Vocab-English"]
        
        meaning = meaning.replace("<br><br>", ", ")
        meaning = meaning.replace(" / ", "<br><br>")
        
        note["Vocab-English"] = meaning
        print(meaning)

        col.update_note(note)
    col.close()
    return

'''