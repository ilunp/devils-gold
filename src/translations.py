from pyI2L import read_assets, write_output, parsers
import csv
import os
import UnityPy

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
    file_path = os.path.join("src/resources_old.assets")
    # file_path = os.path.join(path, "resources.assets")
    # file_path = os.path.join(path, "StreamingAssets/aa/StandaloneWindows64/defaultlocalgroup_assets_all_67e39e85b4ff7f4a7688c36ed26e76c9.bundle")
    env = UnityPy.load(file_path)
    # We need to find the correct file in the bundle
    # for ojb in env.objects:
    #     if ojb.type.name == "MonoBehaviour":
    #         if ojb.name == "translations":
    #             file_path = ojb.read()
    #             break
    # env = UnityPy.load(os.path.join(path, "StreamingAssets"))
    # We need to find the correct file in the bundle
    for ojb in env.objects:
        if ojb.type.name == "MonoBehaviour":
            if ojb.name == "I2Languages":
                file_path = ojb.read()
                print(f"Found translations at {file_path}")
                break
    unpack_path = os.path.join(unpack_dir, "translations.csv")
    writer = parsers.rawCSV.Writer
    assets = read_assets(file_path)
    write_output(unpack_path, assets, writer)
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
