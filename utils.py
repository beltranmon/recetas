import json

from thefuzz import fuzz
from thefuzz import process


def words_distance(keywords, to_search):
    matches = []
    if keywords:
        for word in keywords:
            matches.append([el[0] for el in process.extract(replace_accent_mark_lower(word), [replace_accent_mark_lower(el) for el in to_search], scorer=fuzz.token_set_ratio) if el[1] > 90])
    return matches


def list_flatten(to_flatten):
    return [x for xs in to_flatten for x in xs]


def read_json(file):
    with open(file, 'r') as f:
        return json.load(f)


def replace_accent_mark_lower(text):
    if not text:
        return ''
    a, b = ('áéíóúüÁÉÍÓÚÑñ\n', 'aeiouuaeiounn ')
    trans = str.maketrans(a, b)
    return text.translate(trans).lower().strip()


def write_json(data, file):
    with open(file, 'w') as f:
        json.dump(data, f)
