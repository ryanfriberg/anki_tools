from enums.automation_enum import AutomationEnum
from gtts import gTTS
import json
import os
import pandas as pd
import shutil
import subprocess


def check_for_repeat(word):
    db_words = set(pd.read_csv(AutomationEnum.DB_FILE).iloc[:, 0].to_list())

    if (word in db_words):
        return True

    new_data = pd.DataFrame([word])
    new_data.to_csv(AutomationEnum.DB_FILE, mode="a", header=False, index=False)

    return False


def filter_seen(input_csv=AutomationEnum.INPUT_FILE, 
                database_csv=AutomationEnum.DB_FILE):
    input_words = set(pd.read_csv(input_csv).iloc[:, 0].to_list())
    db_words = set(pd.read_csv(database_csv).iloc[:, 0].to_list())

    shared_words = input_words & db_words
    new_input = list(input_words - shared_words)

    df = pd.DataFrame(new_input)
    df.to_csv(input_csv)


def get_and_update_audio_id():
    with open(AutomationEnum.ID_FILE, 'r') as file:
        data = json.load(file)

    id = data["id"]
    data['id'] = id + 1

    with open(AutomationEnum.ID_FILE, 'w') as file:
        json.dump(data, file, indent=4)
    
    return "{:07d}".format(id)


def generate_audio(word, sentence, id):
    word_file = "/Users/ryanfriberg/dev/anki_tools/automation/audio_files/word_audio_" + id + ".mp3"
    sent_file = "/Users/ryanfriberg/dev/anki_tools/automation/audio_files/sentence_audio_" + id + ".mp3"
    
    if not os.path.exists(AutomationEnum.SILENCE_PATH):
        os.system(f"sox -n -r 24000 -c 1 {AutomationEnum.SILENCE_PATH} trim 0.0 0.5")

    obj = gTTS(text=word, lang="ja", slow=False)
    obj.save(word_file)

    completed = subprocess.run(["sox", word_file, AutomationEnum.SILENCE_PATH, word_file], shell=True)

    obj = gTTS(text=sentence, lang="ja", slow=False)
    obj.save(sent_file)

    return word_file, sent_file


def move_audio_file_to_col(audio_file):
    anki_user_dir = os.path.dirname(AutomationEnum.COL_PATH)
    anki_media_dir = os.path.join(anki_user_dir, "collection.media")
    shutil.move(audio_file, anki_media_dir)