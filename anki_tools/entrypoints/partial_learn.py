import argparse
import logging
import sys

from anki_tools.enums.anki_enums import AnkiEnum
from anki_tools.functions.tag_partial_learn import find_partials


parser = argparse.ArgumentParser(description='Deck Pre-processing')
parser.add_argument('--anki21', default=AnkiEnum.COL_PATH, type=str, 
                    help='First anki .anki2 file (pulls data including due dates)')
parser.add_argument('--deck_name', '--d', default='', type=str, 
                    help='Deck to be processed')
parser.add_argument('--debug', action="store_true",
                    help="Documents output without updating the package.")

def main():
    args = parser.parse_args()

    root_logger = logging.getLogger()
    if not root_logger.hasHandlers():
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter("[%(levelname)s] %(message)s")
        handler.setFormatter(formatter)
        root_logger.addHandler(handler)
        root_logger.setLevel(logging.INFO)

    find_partials(args.deck_name, args.anki21, args.debug)

if __name__=='__main__':
    main()