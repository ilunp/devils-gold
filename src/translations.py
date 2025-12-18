import csv
import glob
import os
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

    file_path = glob.glob(os.path.join(path, "StreamingAssets/aa/StandaloneWindows64/defaultlocalgroup_assets_all_*.bundle"))[0]
    
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


def get_translation(name: str, lang: str = "en", prefix: str = "Items/") -> str:
    global translations_path
    global languages
    column = languages[lang]
    with open(translations_path, encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        fullName = prefix + name
        for row in reader:
            if row["20"] == fullName:
                return row[column]
        return name
