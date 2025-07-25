from copy import deepcopy
from CoreServices import DictionaryServices

import logging
import re
import subprocess
import sys


'''
TODO:
 - migrate the automation codebase to this directory
 - allow for an entrypoint that takes in a CSV and generates the dictionary
   reponses
 - add a reset method that clears the csv data (run after importing to anki)
 - switch audio counter to JSON
 - re-direct audio files to the collection path
   
COMMANDS:
 - found in system settings > keyboards > shortcuts > services > general

Sentence_to_CSV       -> control + shift + N
Dictionary_Automation -> control + shift + M

'''

class CardBuilder:
    def __init__(self):
        pass
