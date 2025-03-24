import json

from thefuzz import fuzz
from thefuzz import process


def list_flatten(to_flatten):
    return [x for xs in to_flatten for x in xs]


def read_json(file):
    with open(file, 'r') as f:
        return json.load(f)


def replace_accent_mark_lower(text):
    if not text:
        return ''
    a, b = ('áéíóúüÁÉÍÓÚ\n', 'aeiouuaeiou ')
    trans = str.maketrans(a, b)
    return text.translate(trans).lower().strip()


def words_distance(keywords, to_search):
    matches = []
    if keywords:
        keywords_preprocessed = {replace_accent_mark_lower(el): el for el in keywords}
        to_search_preprocessed = {replace_accent_mark_lower(el): el for el in to_search}
        for word in keywords_preprocessed:
            matches.append([el[0] for el in process.extract(word, [k for k in to_search_preprocessed], scorer=fuzz.partial_token_sort_ratio) if el[1] > 90])
    return [[to_search_preprocessed[el] for el in l] for l in matches]


def write_json(data, file):
    with open(file, 'w') as f:
        json.dump(data, f)
