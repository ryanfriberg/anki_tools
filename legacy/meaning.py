import re
import requests

# from anki.notes import Note
# from anki.collection import Collection

from collections import defaultdict
from bs4 import BeautifulSoup, NavigableString
from copy import deepcopy
from googletrans import Translator
from nltk.stem import WordNetLemmatizer
from typing import List, Set, Tuple
from time import sleep
from nltk.corpus import wordnet
from logging import Logger


parts_of_speech_map = {
    "Noun": ["Noun"],
    "Godan verb with 'u' ending": ["Verb", "Godan-う"],
    "Auxiliary": ["Auxiliary"],
    "Irregular nu verb": ["Verb", "Irregular-ぬ"],
    "Adverb": ["Adverb"],
    "Yodan verb with 'ru' ending (archaic)": ["Verb", "Yodan-る"],
    "Copula": ["Copula"],
    "used as a prefix": ["Prefix"],
    "Godan verb with 'nu' ending": ["Verb", "Godan-ぬ"],
    "Ichidan verb - zuru verb (alternative form of -jiru verbs)": ["Verb", "Ichidan-ずる(-じる_alt)"],
    "Godan verb with 'ru' ending": ["Verb", "Godan-る"],
    "plain form ends with -ri": ["(Plain-form:り)"],
    "used as a suffix": ["Suffix"],
    "etc.)": [],
    "Company": ["Company"],
    "Ichidan verb - kureru special class": ["Verb", "Ichidan-かれる", "Special"],
    "Verb unspecified": ["Verb"],
    "'taru' adjective": ["たる-Adj"],
    "Irregular ru verb": ["Verb", "Irregular-る"],
    "Unclassified": [],
    "Noun which may take the genitive case particle 'no'": ["Nounの"],
    "Godan verb with 'bu' ending": ["Verb", "Godan-ぶ"],
    "Godan verb with 'ru' ending (irregular verb)": ["Verb", "Irregular", "Godan-る"],
    "Godan verb with 'u' ending": ["Verb", "Godan-う"],
    "Godan verb with 'mu' ending": ["Verb", "Godan-む"],
    "Godan verb with 'su' ending": ["Verb", "Godan-す"],
    "Godan verb with 'tsu' ending": ["Verb", "Godan-つ"],
    "Godan verb with 'gu' ending": ["Verb", "Godan-ぐ"],
    "Godan verb with 'ku' ending": ["Verb", "Godan-く"],
    "Godan verb with 'u' ending (special class)": ["Verb", "Godan-う", "Special"],
    "Godan verb - Iku/Yuku special class": ["Verb", "Godan-いく/ゆく", "Special"],
    "Godan verb - -aru special class": ["Verb", "Godan-ある", "Special"],
    "Pronoun": ["Pronoun"],
    "Noun or verb acting prenominally": ["Prenominal-Noun/Verb"],
    "Suru verb": ["Verb-する"],
    "Pre-noun adjectival (rentaishi)": ["連体詞"],
    "Expressions (phrases": ["Expression/phrase"],
    "Adverb taking the 'to' particle": ["と-Adj"],
    "Adverb (fukushi)": ["Adverb"],
    "Auxiliary verb": ["Aux-Verb"],
    "Numeric": ["Numeric"],
    "Counter": ["Counter"],
    "Full name": [],
    "Na-adjective (keiyodoshi)": ["な-Adj"],
    "Place": [],
    "Jreibun": [],
    "clauses": [],
    "Conjunction": ["Conjunction"],
    "Su verb - precursor to the modern suru": ["す-Verb", "する-precursor"],
    "Kuru verb - special class": ["くる-Verb", "Special"],
    "Intransitive verb": ["Intransitive", "Verb"],
    "Suffix": ["Suffix"],
    "Suru verb - special class": ["する-verb", "Special"],
    "Organization": ["Organization"],
    "Particle": ["Particle"],
    "'ku' adjective (archaic)": ["く-Adj"],
    "Auxiliary": ["Auxiliary"],
    "I-adjective (keiyoushi)": ["い-Adj"],
    "Auxiliary adjective": ["Aux-Adj"],
    "Transitive verb": ["Transitive", "Verb"],
    "I-Adjective (keiyoushi) - yoi/ii class": ["い-Adj", "よい/いい-class"],
    "Ichidan verb": ["Ichidan"],
    "Prefix": ["Prefix"],
    "Suru verb - included": ["する-Verb"],
    "Notes": [],
    "Other forms": [],
    "Wikipedia definition": [],
    "Given name": []
}   

to_tag = {
    "derogatory": "Derogatory",
    "biology": "Biology",
    "slang": "Slang", 
    "Vulgar expression or word": "Vulgar", 
    "colloquial": "Colloquial", 
    "humble (kenjougo) language": "Humble", 
    "polite": "Polite", 
    "sports": "Sports", 
    "figurative": "Figurative", 
    "engineering": "Engineering", 
    "electricity": "Electricity", 
    "networking": "Networking", 
    "internet slang": "Internet-slang", 
    "onomatopoea": "Onomatopoea", 
    "astronomy": "Astronomy", 
    "music": "Music", 
    "chemistry": "Chemistry", 
    "physics": "Physics", 
    "physics term": "Physics", 
    "physics terminology": "Physics", 
    "statistics": "Statistics", 
    "formal or literary term": "Formal", 
    "computing": "Computing", 
    "medicine": "Medicine", 
    "grammar": "Grammar", 
    "botany": "Botany", 
    "food": "Food", 
    "cooking": "Cooking", 
    "psychology": "Psychology", 
    "honorific or respectful (sonkeigo) language": "Honorific",
    "law": "Law", 
    "logic": "Logic", 
    "linguistics": "Linguistics", 
    "sensitive": "Sensitive", 
    "counter": "Counter",
    "mathematics": "Mathematics", 
    "Familiar language": "Familiar", 
    "physiology": "Physiology", 
    "male term or language": "Male-term", 
    "female term or language": "Female-term", 
    "stock market": "Stock market", 
    "proverb": "Proverb", 
    "geology": "Geology", 
    "anatomy": "Anatomy", 
    "general term": "General-term", 
    "video games": "Video-Games", 
    "aviation": "Aviation", 
    "telecommunications": "Telecommunications", 
    "finance": "Finance",
    "geometry": "Geometry", 
    "jocular": "Jocular", 
    "humorous": "Humorous",
    "printing": "Printing",
    "onomatopoeic or mimetic word": "onomatopoea",
    "yojijukugo (four character compound)": "四字熟語",
    "euphemistic": "Euphemistic",
    "mahjong": "Mahjong",
    "children's language": "Children's-language",
    "fig.": "",
    "business": "Business",
    "sumo": "Sumo",
    "dated term": "Dated",
    "historical term": "Historical",
    "archaic": "Archaic",
    "archaism": "Archaism",
    "abuki": "Kabuki",
    "christianity": "Christianity", 
    "bhuddism": "Bhuddism", 
    "go (game)": "Go", 
    "obsolete term": "Obsolete", 
    "obsolete": "Obsolete", 
    "baseball": "Baseball",
    "poetical term": "Poetic", 
    "rare term": "Rare", 
    "horse racing": "Horse-racing", 
    "brazilian": "Brazilian", 
    "martial arts": "Martial-arts",
    "billiards slang": "Billiards-slang", 
    "shogi": "Shogi", 
    "hanafuda": "Hanafuda",
    "seldom": "Seldom",
    "shinto": "Shinto", 
    "osaka dialect": "Osaka-Dialect", 
    "kansai dialect": "Kansai-Dialect", 
    "kyuushuu dialect": "Kyuushuu-Dialect", 
    "hokkaido dialect": "Hokkaido-Dialect",
    "touhoku dialect": "Touhoku-Dialect", 
    "tsugaru dialect": "Tsugaru-Dialect", 
    "abbreviation": "Abbreviation"
}

redirect = [
    "sumo", "dated term", "historical term", "card games", "archaic", "archaism",
    "kabuki", "christianity", "bhuddism", "go (game)", "obsolete term", "baseball",
    "poetical term", "rare term", "horse racing", "brazilian", "martial arts",
    "may be the only daughter", "billiards slang", "shogi", "hanafuda", "seldom",
    "shinto", "osaka dialect", "kansai dialect", "kyuushuu dialect", "hokkaido dialect",
    "touhoku dialect", "tsugaru dialect", "abbreviation", "mahjong"
]


def count_kanji(s):
    # Define the regex pattern for kanji characters
    kanji_pattern = re.compile(
        r'[\u4E00-\u9FFF]'  # CJK Unified Ideographs
        r'|[\u3400-\u4DBF]'  # CJK Unified Ideographs Extension A
        r'|[\uF900-\uFAFF]'  # CJK Compatibility Ideographs
        r'|[\U00020000-\U0002A6DF]'  # CJK Unified Ideographs Extension B
        r'|[\U0002A700-\U0002B73F]'  # CJK Unified Ideographs Extension C
        r'|[\U0002B740-\U0002B81F]'  # CJK Unified Ideographs Extension D
        r'|[\U0002B820-\U0002CEAF]'  # CJK Unified Ideographs Extension E
        r'|[\U0002CEB0-\U0002EBEF]'  # CJK Unified Ideographs Extension F
    )
    
    # Find all kanji characters in the string
    kanji_characters = kanji_pattern.findall(s)
    
    # Return the number of kanji characters
    return len(kanji_characters)


def extract_main_japanese(word):
    '''
    Removes excess information found within a card (such as particles, 
    English text, etc.)
    '''
    kanji_range = r'\u4E00-\u9FFF\u3007々'
    na_pattern = re.compile(f'^[' + kanji_range + r']+な$')
    no_pattern = re.compile(f'^[' + kanji_range + r']+の$')
    extract_japanese = re.compile(r'[\d\u3000-\u303F\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FFF\uFF00-\uFFEF]+')
    
    # get rid of parenthesis values
    res = re.sub("[\(（].*?[\)）]", "", word)

    # get rid of non-japanese text          
    res = ''.join(extract_japanese.findall(res))
    
    # get rid of extraneous kana letters (お、な、ご、etc.)
    na = bool(re.match(na_pattern, res))
    no = bool(re.match(no_pattern, res))

    if (na or no):
        res = res[:-1]

    if res == "":
        res = word

    return str(res)


def break_up_anki_defintion(text: str) -> Tuple[List[str]]:
    '''
    Break up a card's english defintions, first by ";" then by ","
    Handles certain cases of anki cards (such as semi-colon within paranthesis)
    and weird characters that appear within defintion strings
    
    :param text: the full card backside string
    :returns : A list of the meanings, and a list of lists of the individual words
    '''
    card_front = deepcopy(text)
    card_front = card_front.replace("&#x27;", "'")
    card_front = card_front.replace("&quot;", '"')
    card_front = card_front.replace("&nbsp;", '')
    card_front = card_front.replace("<div>", '')
    card_front = card_front.replace("</div>", '')
    card_front = card_front.rstrip()
    
    if card_front[-1] == ";":
        card_front = card_front[:-1]

    paren_pattern = re.compile(r';(?![^()]*\))')

    if bool(re.search(paren_pattern, card_front)):
        meanings = [meaning.strip() for meaning in re.split(r';(?![^()]*\))', card_front)]
        meanings = [meaning.replace("<br><br>", "") if meaning.startswith("<br><br>") else meaning for meaning in meanings]
    else:
        meanings = None

    return meanings


def discard_words(input_set):
    input_set.discard("to")
    input_set.discard("in")
    input_set.discard("at")
    input_set.discard("a")
    input_set.discard("on")
    input_set.discard("by")
    input_set.discard("the")
    input_set.discard("of")
    input_set.discard("as")
    return input_set


def match_anki_to_info(anki_meanings: List[str], jisho_meanings: List[str], 
                        infos: List[str], jisho_tags: List[List]) -> Tuple[List[str], List[str], List]:
    '''
    Map the customized defintions found in anki to those present on the jisho 
    website to determine which supplemental infos apply to which definitions
    '''

    anki_meanings = [anki_meanings] if isinstance(anki_meanings, str) else anki_meanings
    original_meanings = deepcopy(anki_meanings)
    anki_meanings = [meaning.replace("<br><br>", ", ") for meaning in anki_meanings]
    
    if all(not info for info in infos):
        return anki_meanings, [[] for i in range(len(anki_meanings))], jisho_tags

    anki_info = []
    _jisho_tags = []

    for anki_meaning in anki_meanings:
        highest_score = 0.0
        best_match = ""
        found = False
        best_jisho_tags = []
        anki_words = anki_meaning.split(", ")

        for i, jisho_meaning in enumerate(jisho_meanings):
            jisho_words = jisho_meaning.split("; ")

            intersection = len(set(anki_words).intersection(set(jisho_words)))
            union = len(set(anki_words).union(set(jisho_words)))
            similarity = intersection / union

            if ((similarity >= highest_score) and (similarity != 0)):
                found = True
                highest_score = similarity
                current_info = infos[i] if (infos[i] != None) else ""

                if (best_match == ""):
                    best_match = current_info
                else:
                    best_match += ", " + current_info

                if (best_jisho_tags == []):
                    best_jisho_tags = jisho_tags[i]
                else:
                    for tag in jisho_tags[i]:
                        if (tag not in best_jisho_tags):
                            best_jisho_tags.append(tag)
            
        if (not found):
            for i, jisho_meaning in enumerate(jisho_meanings):
                jisho_words = jisho_meaning.split("; ")
                similarity = 0
                for anki_word_def in anki_words:
                    anki_word_def_set = discard_words(set(anki_word_def.split(" ")))
                    
                    for jisho_word_def in jisho_words:
                        jisho_word_def_set = discard_words(set(jisho_word_def.split(" ")))

                        intersection = len(set(anki_word_def_set).intersection(set(jisho_word_def_set)))
                        union = len(set(anki_word_def_set).union(set(jisho_word_def_set)))
                        similarity += intersection / union

                if ((similarity >= highest_score) and (similarity != 0)):
                    found = True
                    highest_score = similarity
                    current_info = infos[i] if (infos[i] != None) else ""
                    best_match = current_info
                    best_jisho_tags = jisho_tags[i]

        anki_info.append(best_match)
        _jisho_tags.append(best_jisho_tags)
                    
    return original_meanings, anki_info, _jisho_tags


def parse_jisho_html(soup: BeautifulSoup) -> Tuple[List, List, List, List, str]:
    '''
    Parse the known structure of jisho.org's html and look for specific data

    :returns: A list of the relevant defintions and a list of the supplemental 
        info for each definition (if present)
    '''
    main_div = soup.find('div', class_='meanings-wrapper')
    if (not main_div):
        return None, None, None, None, None, None, None
    elements = main_div.find_all(recursive=False)
    it = iter(elements)

    notes = ""
    definitions, info, alts, tags = [], [], [], []
    for tag_div, def_div in zip(it, it):
        definition, extra_info = None, None
        tag_list = []

        # add tags
        if "meaning-tags" in tag_div.get("class"):
            parts_of_speech = tag_div.text.strip().split(",")
            for tag in parts_of_speech:
                tag = tag.strip()
                try:
                    new_tags = parts_of_speech_map[tag]
                except:
                    new_tags = [tag]

                if not all(elem in tag_list for elem in new_tags):
                    tag_list.extend(new_tags)

            if ("Wikipedia" in '\t'.join(parts_of_speech)):
                continue
                
            if ("Notes" in '\t'.join(parts_of_speech)):
                notes = def_div.text.strip()
                continue

            if ("Other forms" in '\t'.join(parts_of_speech)):
                alternates = def_div.find_all(class_='break-unit')
                if (alternates):
                    for alt in alternates:
                        alts.append(alt.text)
                continue
            tags.append(tag_list)
        
        if ("meaning-wrapper" in def_div.get("class")):
            meaning_div = def_div.find(class_='meaning-meaning')
            if meaning_div: 
                definition = meaning_div.text.strip()
                definitions.append(definition)

            extra_info_div = def_div.find(class_='supplemental_info')
            if extra_info_div:
                extra_info = extra_info_div.text.strip()
            info.append(extra_info)

    word_div = soup.find('div', class_="concept_light-readings japanese japanese_gothic")
    kana_div = word_div.find('span', class_="furigana")
    kanji_div = word_div.find('span', class_="text")

    kana_list = []
    for element in kana_div:
        if element.name == 'span':
            kana = element.get_text(strip=True)
            if kana != "":
                kana_list.append(kana)

    num_seen_kanji = 0
    new_word, new_middle = "", ""
    for element in kanji_div:
        if isinstance(element, NavigableString):
            kanjis = element.strip()
            if (kanjis != ""):
                for kanji in kanjis:
                    new_word += kanji
                    if (num_seen_kanji < len(kana_list)):
                        new_middle += kana_list[num_seen_kanji]
                    num_seen_kanji += 1
        elif element.name == 'span':
            kana = element.get_text(strip=True)
            new_word += kana
            new_middle += kana

    return definitions, info, tags, alts, new_word, new_middle, notes


def query_jisho(word: str) -> Tuple[List, List, List, str]:
    '''
    Given a single Japanese word, query jisho.org and extract the relevant 
    metadata
    
    :param word: the query word
    :type word: str
    :returns: A list of the relevant defintions and a list of the supplemental 
        info for each definition (if present)
    '''
    url = ("https://jisho.org/word/" + word)
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) \
               AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 \
               Safari/537.36'}
    response = requests.get(url, headers=headers)

    if (response.status_code != 200):
        url = ("https://jisho.org/search/" + word)
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) \
                AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 \
                Safari/537.36'}
        response = requests.get(url, headers=headers)
        
        if (response.status_code != 200):
            return None, None, None, None, None, None, None

    soup = BeautifulSoup(response.content, 'html.parser')
    definitions, info, tags, alts, new_word, new_middle, notes = parse_jisho_html(soup)
    
    if (alts != None):
        alts = "<br>".join([alt for alt in alts if alt])

    return definitions, info, tags, alts, new_word, new_middle, notes


def query_jisho_with_kana(word: str, kana:str) -> Tuple[List, List, List, str]:
    '''
    Given a single Japanese word, query jisho.org and extract the relevant 
    metadata
    
    :param word: the query word
    :type word: str
    :returns: A list of the relevant defintions and a list of the supplemental 
        info for each definition (if present)
    '''
    url = ("https://jisho.org/search/" + word + "%20" + kana)
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) \
               AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 \
               Safari/537.36'}
    response = requests.get(url, headers=headers)

    if (response.status_code != 200):
        return None, None, None, None

    soup = BeautifulSoup(response.content, 'html.parser')
    definitions, info, tags, alts, new_word, new_middle, notes = parse_jisho_html(soup)

    if (alts != None):
        alts = "<br>".join([alt for alt in alts if alt])

    return definitions, info, tags, alts, new_word, new_middle, notes


def process_tags(meaning_tags: List[str], jisho_tags: List[str]) -> List[str]:
    '''
    Process the current anki tags compared to jisho, some tags only apply to
    specific meanings so this function ensures that each tag is strictly
    relevant
    '''
    for tag in jisho_tags:
        if tag not in meaning_tags:
            meaning_tags.append(tag)
    
    res = deepcopy(meaning_tags)
    for tag in meaning_tags:
        if any(tag in value_list for value_list in parts_of_speech_map.values()):
            if (tag not in jisho_tags) and (tag != "Expression/phrase"):
                try:
                    res.remove(tag)
                except ValueError:
                    continue
    return res


def process_supplemental_info(word: str, info:str) -> Tuple[str, List, bool]:
    '''
    This function extracts all the necessary/useful/relevant information when 
    given the content of single sub-definition's "supplemental info" html tag
    
    examples include:
     - if a specific sub-defintion uses a specific kanji
     - if a word is usually written in kana

    :returns: The new "front" side with relevant info from supplemental info,
        a list of tags to add, and a boolean dictating whether to redirect
    '''
    # only_applies_pattern = r'only applies to\s+([\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]+)'
    # esp_pattern = r'esp.\s+([\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]+)'

    card_info = []
    new_tags = []
    redirect_flag = False
    res_info = ""
    
    if (info == []):
        return res_info, [], False

    lower_info = [info_tag.lstrip().rstrip() for info_tag in info.lower().split(",")]
    
    if all(not info for info in lower_info):
        return res_info, [], False

    for info_tag in lower_info:
        if ((info_tag in redirect) or ("abbr" in info_tag) or ("abbreviation" in info_tag)):
            redirect_flag = True
        
        if info_tag in list(to_tag.keys()):
            if (to_tag[info_tag] not in info_tag):
                new_tags.append(to_tag[info_tag])
            continue

        if (info_tag == "usually written using kana alone"):
            info_tag = "usually as kana"

        if (info_tag not in card_info):
            card_info.append(info_tag)

    res_info = str(", ".join(card_info))

    return res_info, new_tags, redirect_flag


def extract_context_from_paranthesis(single_meaning: str, logger: Logger=None) -> str:
    '''
    this function will add more contextual info to the front of a card if
    such information is given from in the sub-defintion of the word via 
    example use-cases given within paranthesis (translated via google)

    :returns: an empty string if no context is found, or the context string
        to be added to the front side of the anki card
    '''
    paren_pattern = r'\((.*?)\)'
    matches = re.findall(paren_pattern, single_meaning)
    substrings = ["e.g.", "e.g. ", 
                  "eg ", 
                  "eg.", "eg. ", 
                  "e.x.", "e.x. ", 
                  "ex ",
                  "ex.", "ex. "]

    ex = ""
    words = []
    for match in matches:
        match_words = match.split(", ")

        for i, match_string in enumerate(match_words):
            for substring in substrings:
                if substring == match_string:
                    match_words.remove(match_words[i])
                    ex = "ex. "
                elif substring in match_string:
                    match_words[i] = match_string.replace(substring, "")
                    ex = "ex. "
                
        words.extend(match_words)

    skip_list = [[], ["a"], ["to"], ["in"], ["at"], ["on"], ["by"], ["the"]]

    if (words in skip_list):
        return ""
    
    etc = ""
    if ("etc." in words):
        etc = " etc."
        words.remove("etc.")
    elif ("etc" in words):
        etc = " etc."
        words.remove("etc")

    attempts = 1
    while True:
        try:
            translator = Translator()
            translated_words = [translator.translate(word, dest='ja').text for word in words]
            output_str = "(" + ex + ", ".join(translated_words) + etc + ") "
            break
        except:
            log_str = f"---> {attempts} failed translation attempt(s) {words}"
            print(log_str)
            if logger:
                logger.info(log_str)
            attempts += 1
            if attempts > 15:
                return ""
            sleep(5)

    return output_str


def get_synonyms(word, limit=4):
    synonyms = set()
    word_synsets = wordnet.synsets(word)
    for syn in word_synsets:
        for lemma in syn.lemmas():
            synonyms.add(lemma.name())

    synonyms.discard(word)
    ranked_synonyms = []
    for synonym in synonyms:
        syn_synsets = wordnet.synsets(synonym)
        if not syn_synsets:
            continue
        
        total_similarity = 0
        count = 0
        for syn in syn_synsets:
            for word_syn in word_synsets:
                similarity = word_syn.wup_similarity(syn)
                if similarity is not None:
                    total_similarity += similarity
                    count += 1
        if count > 0:
            average_similarity = total_similarity / count
            ranked_synonyms.append((synonym, average_similarity))

    ranked_synonyms.sort(key=lambda x: x[1], reverse=True)
    res = [syn[0] for syn in ranked_synonyms if (("-" not in syn[0]) and ("_" not in syn[0]))][:limit]
    return res


def group_similar_defintions(en_sides: List) -> List:
    '''
    Of the cards that have identical fronts+tags, determine if there is any
    overlap between their definitions. 

    :returns: a list of sets of indices where the definitions share at least one
        word or word stem exactly
    '''
    lemmatizer = WordNetLemmatizer()
    pattern = r'\([^)]*\)'
    defs = deepcopy(en_sides)
    defs = [side.replace(", ", " ") for side in defs]
    defs = [side.replace("<br>", " ") for side in defs]
    defs = [re.sub(pattern, '', side) for side in defs]
    word_sets = [set(defn.split()) for defn in defs]

    for words in word_sets:
        new_words = []
        words = discard_words(words)

        for word in words:
            new_words.extend(get_synonyms(word))
            new_words.append(lemmatizer.lemmatize(word))
        for word in new_words:
            words.add(word)

    # find the overlapping word sets
    overlapping_indices = []
    for i in range(len(word_sets)):
        print("word set", word_sets[i])
        for j in range(i+1, len(word_sets)):
            if word_sets[i] & word_sets[j]:
                added = False
                for ind_set in overlapping_indices:
                    if (i in ind_set) or (j in ind_set):
                        ind_set.add(i)
                        ind_set.add(j)
                        added = True
                if not added:
                    overlapping_indices.append({i,j})

    overlapping_indices = [tuple(sorted(ind_set)) for ind_set in overlapping_indices]

    print(overlapping_indices)
    return overlapping_indices


def get_duplicates(contexts: List, infos: List, tags: List) -> List[int]:
    '''
    Determines where duplicate card fronts are (to either be tagged or updated)
    '''

    tuple_indices = defaultdict(list)
    for i in range(len(contexts)):
        key = (contexts[i], infos[i], tuple(tags[i]))
        tuple_indices[key].append(i)

    matching_indices = [indices for indices in tuple_indices.values() if len(indices) > 1]
    matching_indices = [tuple(sorted(ind)) for ind in matching_indices]
    
    return matching_indices


def combine_indices(ja_sides, en_sides, flags, new_tags, contexts, res_infos, indices, identical_flag=True):
    print("combine", indices)
    updated_indices = []
    for id_tuple in indices:
        first_info = res_infos[id_tuple[0]]
        temp = list(deepcopy(id_tuple))
        for idx in id_tuple[1:]:
            not_shared = []
        
            if (first_info != res_infos[idx]):
                try:
                    print("Removing")
                    temp.remove(idx)
                    continue
                except ValueError:
                    continue

            not_shared = list(set(new_tags[id_tuple[0]]) ^ set(new_tags[idx]))
            cont_flag = False
            if ((not_shared != ["Adverb"]) or (identical_flag)):
                for tag in not_shared:
                    if (tag != "") and (tag in list(to_tag.values())):
                        try:
                            temp.remove(idx)
                        except ValueError:
                            pass
                        cont_flag = True
                        continue
                if cont_flag: continue
            
            en_sides[id_tuple[0]] += "; <br><br>" + en_sides[idx]
            if (contexts[id_tuple[0]] != contexts[idx]):
                contexts[id_tuple[0]] += " " + contexts[idx]

            if ("main" in not_shared) and ("variant" in not_shared):
                not_shared.remove("variant")
            new_tags[id_tuple[0]].extend(not_shared)
        
            if ("recombined" not in new_tags[id_tuple[0]]):
                new_tags[id_tuple[0]].append("recombined")
        updated_indices.append(tuple(temp))

    for id_tuple in updated_indices:
        en_sides  = [value for i, value in enumerate(en_sides)  if i not in id_tuple[1:]]
        ja_sides  = [value for i, value in enumerate(ja_sides)  if i not in id_tuple[1:]]
        new_tags  = [value for i, value in enumerate(new_tags)  if i not in id_tuple[1:]]
        flags     = [value for i, value in enumerate(flags)     if i not in id_tuple[1:]]
        contexts  = [value for i, value in enumerate(contexts)  if i not in id_tuple[1:]]
        res_infos = [value for i, value in enumerate(res_infos) if i not in id_tuple[1:]]
    return ja_sides, en_sides, flags, new_tags, contexts, res_infos
    

# def process_meaning(note: Note, col: Collection, count_new: int, count_redirect:int, num_not_skipped: int, logger: Logger): 
#     '''
#     The 'main' function of this procedure, queries the website, extracts the info
#     will eventually generate new cards for each def
#     '''
#     note.add_tag("processed")
#     kanji_pattern = re.compile(r'[\u4e00-\u9faf]')
#     hiragana_pattern = re.compile(r'^[\u3040-\u309f]+$')
#     extraneous_deck_id = col.decks.id("日本語::words::extraneous_meanings")
#     japanese_word = extract_main_japanese(note['Back'])

#     ja_sides, en_sides, flags, new_tags, contexts, res_infos = [], [], [], [], [], []
#     identical_indices = []
#     skipped = True
        
#     anki_meanings = break_up_anki_defintion(note["Front"])

#     if ("front-kana" in note.tags):
#         jisho_meanings, jisho_infos, jisho_tags, alts, new_word, new_middle, notes = query_jisho_with_kana(japanese_word, note["Middle"])
#     else:
#         jisho_meanings, jisho_infos, jisho_tags, alts, new_word, new_middle, notes = query_jisho(japanese_word)

#     note["Notes"] = notes

#     if (not jisho_meanings):
#         log_str = "\n\n\n\n\n====> JISHO QUERY FAILED ON JAPANESE WORD:" + repr(japanese_word) + " " + note["Back"] + "\n\n\n\n\n"
#         print(log_str)
#         logger.warning(log_str)
#         return col, count_new, count_redirect, num_not_skipped

#     if ((new_word != japanese_word) and ("keep" not in note.tags) and (count_kanji(japanese_word) <= count_kanji(new_word))):
#         log_str = f"--------> Updating word: {japanese_word} -> {new_word}"
#         print(log_str)
#         logger.info(log_str)
#         japanese_word = new_word
#         note.add_tag("updated_japanese_word")

#     if (len(japanese_word) == 1) and (bool(kanji_pattern.match(japanese_word))):
#         if ("Single-Kanji" not in note.tags):
#             log_str = "---> Added single-kanji tag"
#             print(log_str)
#             logger.info(log_str)
#             note.add_tag("Single-Kanji")
#     elif(bool(hiragana_pattern.match(japanese_word))):
#         if ("仮名" not in note.tags):
#             log_str = "---> Added kana-only tag"
#             print(log_str)
#             logger.info(log_str)
#             note.add_tag('仮名')

#     if ((new_middle != note["Middle"]) and 
#         (new_middle != "") and 
#         ("、" not in note["Middle"]) and 
#         ("front-kana" not in note.tags) and 
#         ("keep" not in note.tags) and 
#         ("仮名" not in note.tags)):
#         log_str = f"--------> Updating kana: {note['Middle']} -> {new_middle}"
#         print(log_str)
#         logger.info(log_str)
#         note["Middle"] = new_middle

#     _diff = len(jisho_meanings) - len(jisho_tags)
#     if (_diff > 0):
#         jisho_tags.extend([[] for i in range(_diff)])

#     log_str = "word " + " " + note['Back'] + " -> " + repr(japanese_word)
#     print(log_str)
#     logger.info(log_str)
#     note["Back"] = japanese_word
#     col.update_note(note)

#     log_str = "original meaning " + note['Front']
#     print(log_str)
#     logger.info(log_str)

#     if ((";" in note["Front"]) 
#         and ("main" not in note.tags) 
#         and ("variant" not in note.tags)
#         and (anki_meanings != None)):

#         skipped = False
#         num_not_skipped += 1

#         diff = len(anki_meanings) - len(jisho_meanings)
        
#         if (diff > 0):
#             jisho_tags.extend([[] for i in range(diff)])
#             note.add_tag("more_anki_meanings")

#         meanings, infos, _jisho_tags = match_anki_to_info(anki_meanings, jisho_meanings, jisho_infos, jisho_tags)

#         # parse meanings
#         for i, meaning in enumerate(meanings):
#             redirect_flag = False 
#             meaning_tags = deepcopy(note.tags)
#             info = ""

#             if (infos[i]):
#                 info, _tags, redirect_flag = process_supplemental_info(japanese_word, infos[i])
#                 meaning_tags.extend(_tags)

#             context = extract_context_from_paranthesis(meaning, logger)
                        
#             if(_jisho_tags[i]):
#                 meaning_tags = process_tags(meaning_tags, _jisho_tags[i])

#             new_tags.append(meaning_tags)
#             contexts.append(context)
#             res_infos.append(info)
#             ja_sides.append(japanese_word)
#             en_sides.append(meaning)
#             flags.append(redirect_flag)

#         if (len(new_tags) > 1):
#             for i, tag_list in enumerate(new_tags):
#                 if (i == 0):
#                     tag_list.append("main")
#                 else:
#                     tag_list.append("variant")

#         if ("Single-Kanji" not in note.tags):
#             overlapping_indices = group_similar_defintions(en_sides)
#             ja_sides, en_sides, flags, new_tags, contexts, res_infos = combine_indices(ja_sides, en_sides, flags, new_tags, contexts, res_infos, overlapping_indices, False)

#         temp_contexts = deepcopy(contexts)
#         temp_contexts[0] = ""

#         identical_indices = get_duplicates(temp_contexts, res_infos, new_tags)
#         if (identical_indices and (len(ja_sides) > 2)):
#             ja_sides, en_sides, flags, new_tags, contexts, res_infos = combine_indices(ja_sides, en_sides, flags, new_tags, contexts, res_infos, identical_indices)

#         count_new      += len(ja_sides) - 1
#         count_redirect += sum(flags)

#         # build new cards
#         note["Front"]      = en_sides[0]
#         note["Info"]       = res_infos[0]
#         note["Alternates"] = alts
#         note["Context"]    = contexts[0]
#         note.tags          = new_tags[0]
        
#         if (len(en_sides) > 1):
#             note.add_tag("split")
#         col.update_note(note)

#         for i in range(1, len(en_sides)):
#             new_note = Note(col=col, model=col.models.by_name('Japanese Card'))
#             new_note["Back"]       = japanese_word
#             new_note["Middle"]     = deepcopy(note["Middle"])
#             new_note["Front"]      = en_sides[i]
#             new_note["Alternates"] = alts
#             new_note["Context"]    = contexts[i]
#             new_note["Info"]       = res_infos[i]
#             new_note["Notes"]      = notes
#             new_note.add_tag("split")

#             for new_tag in new_tags[i]:
#                 new_note.add_tag(new_tag)

#             deck_id = extraneous_deck_id if flags[i] else note.cards()[0].did
#             col.add_note(note=new_note, deck_id=deck_id)

#             suspended_status = note.cards()[0].queue
#             for card in new_note.cards():
#                 card.queue = suspended_status
#                 col.update_card(card)
#             col.update_note(new_note)

#     else:
#         _, anki_info, _ = match_anki_to_info([note["Front"]], jisho_meanings, jisho_infos, jisho_tags)
#         note["Alternates"] = alts
#         if (anki_info[0]):
#             info, _tags, redirect_flag = process_supplemental_info(japanese_word, anki_info[0])
#             note.tags.extend(_tags)
#             note["Info"] = info

#             log_str2 = f"---> skip info    : {info}"
#             log_str3 = f"---> non-skip alts    : {alts}"
#             log_str4 = f"---> non-skip tags    : {note.tags}"
#             print(log_str2)
#             print(log_str3)
#             print(log_str4)
#             logger.info(log_str2)
#             logger.info(log_str3)
#             logger.info(log_str4)

#             if redirect_flag:
#                 if (len(jisho_meanings) == 1):
#                     log_str = "---> non-skip redirected"
#                     print(log_str)
#                     logger.info(log_str)
#                     col.set_deck(note.card_ids(), extraneous_deck_id)
#                     count_redirect += 1
#                 else:
#                     note.add_tag("need_split")
#         col.update_note(note)
            
#     log_str = f"---> skipped?         : {skipped}"
#     print(log_str)
#     logger.info(log_str)
#     if (not skipped):
#         log_str = f"---> # cards added    : {len(ja_sides)-1}"
#         print(log_str)
#         logger.info(log_str)
#     log_str2 = f"---> english          : {en_sides if en_sides else note['Front']}"
#     log_str3 = f"---> tags             : {new_tags if new_tags else note.tags}"
#     log_str4 = f"---> contexts         : {contexts}"
#     log_str5 = f"---> infos            : {res_infos}"
#     log_str6 = f"---> notes            : {notes}"
#     log_str7 = f"---> alts             : {alts}"
#     print(log_str2)
#     print(log_str3)
#     print(log_str4)
#     print(log_str5)
#     print(log_str6)
#     print(log_str7)
#     logger.info(log_str2)
#     logger.info(log_str3)
#     logger.info(log_str4)
#     logger.info(log_str5)
#     logger.info(log_str6)
#     logger.info(log_str7)
#     if any(flags):
#         log_str = f"---> flags            : {flags}"

#     return col, count_new, count_redirect, num_not_skipped