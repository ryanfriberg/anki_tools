from pykakasi import kakasi
import re
import requests

def has_katakana(input_str: str) -> bool:
    '''
    Uses regex to tell if a string has any katana characters 
    '''
    katakana_pattern = re.compile(r'[\u30A0-\u30FF]+') 
    return bool(katakana_pattern.search(input_str))


def get_kana_spelling(japanese_word: str) -> str:
    '''
    Programatically determines the kana spelling of strings with kanji
    '''
    kakasi_obj = kakasi()
    kakasi_obj.setMode("J", "H")
    conv = kakasi_obj.getConverter()
    kana_spelling = conv.do(japanese_word)
    return kana_spelling


def count_kanji(word: str) -> int:
    kanji_pattern = re.compile(
        r'[\u4E00-\u9FFF]'           # CJK Unified Ideographs
        r'|[\u3400-\u4DBF]'          # CJK Unified Ideographs Extension A
        r'|[\uF900-\uFAFF]'          # CJK Compatibility Ideographs
        r'|[\U00020000-\U0002A6DF]'  # CJK Unified Ideographs Extension B
        r'|[\U0002A700-\U0002B73F]'  # CJK Unified Ideographs Extension C
        r'|[\U0002B740-\U0002B81F]'  # CJK Unified Ideographs Extension D
        r'|[\U0002B820-\U0002CEAF]'  # CJK Unified Ideographs Extension E
        r'|[\U0002CEB0-\U0002EBEF]'  # CJK Unified Ideographs Extension F
    )
    
    kanji_characters = kanji_pattern.findall(word)
    return len(kanji_characters)


def extract_main_japanese(word: str) -> str:
    '''
    Removes excess information found within a card (such as particles, 
    English text, etc.)
    '''
    kanji_range = r'\u4E00-\u9FFF\u3007々'
    na_pattern =  re.compile(f'^[' + kanji_range + r']+な$')
    no_pattern =  re.compile(f'^[' + kanji_range + r']+の$')
    ni_pattern =  re.compile(f'^[' + kanji_range + r']+に$')
    o_pattern = re.compile(f'^お[' + kanji_range + r']+$')
    go_pattern =  re.compile(f'^ご[' + kanji_range + r']+$')

    extract_japanese = re.compile(
        "[々"
        "\u3040-\u309F"  # hiragana
        "\u30A0-\u30FF"  # katakana
        "\u3400-\u4DBF"  # CJK Unified Ideographs Extension A
        "\u4E00-\u9FFF"  # CJK Unified Ideographs
        "\uF900-\uFAFF"  # CJK Compatibility Ideographs
        "]+"
    )
    
    # get rid of parenthesis values
    res = re.sub("[\(（].*?[\)）]", "", word)

    # get rid of non-japanese text          
    res = ''.join(extract_japanese.findall(res))
    
    # get rid of extraneous kana letters (お、な、ご、etc.)
    na = bool(re.match(na_pattern, res))
    no = bool(re.match(no_pattern, res))
    ni = bool(re.match(ni_pattern, res))

    if (na or no or ni):
        res = res[:-1]
    if (bool(re.match(o_pattern, res)) or bool(re.match(go_pattern, res))):
        res = res[1:]

    return str(res)

