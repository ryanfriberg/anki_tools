# from anki.notes import Note
import anki.collection as collection
import logging

from anki_tools.enums.anki_enums import AnkiEnum


_logger = logging.getLogger(__name__)
_logger.addHandler(logging.NullHandler())


def find_partials(deck_name: str, col_path: str = AnkiEnum.COL_PATH, debug: bool = False):
    col = collection.Collection(col_path) 

    _logger.info("Searching deck [" + deck_name + "]...")
    deck = col.decks.by_name(deck_name)
    
    if (deck is None):
        _logger.error("Deck not found.")
        col.close()

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
            
            if (not debug):
                col.update_note(note)

    _logger.info("# paritally learned: " + str(len(partials)))

    col.close()
