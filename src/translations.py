from pyI2L import read_assets, write_output, parsers
import csv

DEFAULT_PATH = (
    r"C:\Program Files (x86)\Steam\steamapps\common\SULFUR\Sulfur_Data\resources.assets"
)


def extract_translations(path: str = DEFAULT_PATH) -> None:
    writer = parsers.rawCSV.Writer
    assets = read_assets(path)
    write_output("unpacked/translations.csv", assets, writer)


def getTranlatedName(
    name: str, prefix: str = "Items/", lang: str = "English [en]"
) -> str:
    with open("unpacked/translations.csv", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        fullName = prefix + name
        for row in reader:
            if row["20"] == fullName:
                return row["English [en]"]
        return name
