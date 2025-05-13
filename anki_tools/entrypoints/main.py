import argparse

from anki_tools.enums.anki_enums import AnkiEnum

from process_japanese_deck import JapaneseProcessor
from meaning import process_meaning

parser = argparse.ArgumentParser(description='Deck Pre-processing')
parser.add_argument('--anki21', default='', type=str, 
                    help='First anki .anki2 file (pulls data including due dates)')
parser.add_argument('--deck_name', default='', type=str, 
                    help='Deck to be processed')
parser.add_argument('--debug', action="set_true",
                    help="Documents output without updating the package.")
parser.add_argument('--find', default="", 
                    help="Substring to be replaced from the --field arg")

def main():
    args = parser.parse_args()
    if args.language == 'Japanese':
        deck_processor = JapaneseProcessor()

    if args.analyze:
        deck_processor.analyze_deck(col_path=args.anki21)
    else:
        deck_processor.apply_function(note_func=process_meaning, col_path=args.anki21)


if __name__=='__main__':
    main()