from copy import deepcopy
from CoreServices import DictionaryServices
from enums.automation_enum import AutomationEnum

import os
import re
import sys
import utils


def main():
    try:
        searchword = sys.argv[1]
    except IndexError:
        errmsg = 'Empty Query'
        print(errmsg)
        sys.exit()
    
    if utils.check_for_repeat(searchword):
        raise ValueError("Word already in database.")

    wordrange = (0, len(searchword))
    dictresult = DictionaryServices.DCSCopyTextDefinition(None, searchword, wordrange)

    formated_result = ""
    
    if not dictresult:
        formated_result = "'%s' not found in Dictionary." % (searchword)
    else:
        formated_result = dictresult

    idx = formated_result.find("〈子項目〉")
    if (idx != -1):
        formated_result = formated_result[:idx]

    pattern = r'[\u2460-\u2473]'
    substring = "<br><br>"
    definition = re.sub(pattern, lambda match: f"{substring}{match.group(0)}", formated_result)
    
    with open(AutomationEnum.SENTENCES_FILE) as s_csv:
        latest_sentence = s_csv.readlines()[-1].strip()

    if ((searchword not in latest_sentence) or (searchword == latest_sentence)):
        raise ValueError
    else:
        cloze = "{{c1::" + searchword + "}}"
        tts_sentence = deepcopy(latest_sentence)
        latest_sentence = latest_sentence.replace(searchword, cloze)

    audio_id = utils.get_and_update_audio_id()
    word_file, sent_file = utils.generate_audio(searchword, tts_sentence, audio_id)

    sent_audio_file = f"[sound:{os.path.basename(word_file)}.mp3]"
    word_audio_file = f"[sound:{os.path.basename(sent_file)}.mp3]"

    utils.move_audio_file_to_col(word_file)
    utils.move_audio_file_to_col(sent_file)

    with open(AutomationEnum.DATA_FILE,'a') as c_csv:
        c_csv.write("\n"+",".join([latest_sentence, searchword, definition, word_audio_file, sent_audio_file]))


if __name__ == '__main__':
    main()