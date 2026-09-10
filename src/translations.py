import csv
import glob
import os
from functools import lru_cache
import UnityPy
from UnityPy.classes import MonoBehaviour

"""
Translations are important for getting the correct data.
The asset properties are written in English, but a lot of the
flavor text and even some of the names are changed by the
translation library.
"""

translations_path = ""

languages = {
    "en": "English [en]",
    "sv": "Swedish [sv]",
    "fr": "French [fr]",
    "it": "Italian [it]",
    "de": "German [de]",
    "es": "Spanish [es]",
    "pt": "Portuguese [pt]",
    "ru": "Russian [ru]",
    "pl": "Polish [pl]",
    "ja": "Japanese [ja]",
    "ko": "Korean [ko]",
    "zh": "Chinese (Simplified) [zh-CN]",
    "tr": "Turkish [tr]",
    "ar": "Arabic [ar]",
}


def extract_translations(path: str, unpack_dir: str) -> None:
    global translations_path

    # file_path = glob.glob(os.path.join(path, "StreamingAssets/aa/StandaloneWindows64/defaultlocalgroup_assets_all_*.bundle"))[0]
    file_path = glob.glob(os.path.join(path, "StreamingAssets/aa/StandaloneWindows64/onstartup_assets_all_*.bundle"))[0]
    
    env = UnityPy.load(file_path)

    translation_data = None
    for obj in env.objects:
        if obj.type.name == "MonoBehaviour":
            data: MonoBehaviour = obj.parse_as_object()
            if data.m_Name == "I2Languages":
                translation_data = data
                print("Found translations")
                # print(data.mSource.mTerms)
                break

    if translation_data is None:
        print("No translations found")
        return

    unpack_path = os.path.join(unpack_dir, "translations.csv")

    with open(unpack_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile, quoting=csv.QUOTE_ALL, quotechar='"')
        writer.writerow(["20"] + list(languages.values()))
        for term in translation_data.mSource.mTerms:
            writer.writerow([term.Term] + term.Languages)

    translations_path = unpack_path
    _table.cache_clear()
    get_translation.cache_clear()


@lru_cache(maxsize=None)
def _table(lang: str) -> dict[str, str]:
    with open(translations_path, encoding="utf-8", newline="") as csvfile:
        reader = csv.reader(csvfile)
        column = next(reader).index(languages[lang])
        table: dict[str, str] = {}
        for row in reader:
            if len(row) > column:
                table.setdefault(row[0], row[column])
        return table


@lru_cache(maxsize=100_000)
def get_translation(name: str, lang: str = "en", prefix: str = "Items/") -> str:
    table = _table(lang)
    key = prefix + name
    return table[key] if key in table else name

