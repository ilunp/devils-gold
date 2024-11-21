from pyI2L import read_assets, write_output, parsers

DEFAULT_PATH = (
    r"C:\Program Files (x86)\Steam\steamapps\common\SULFUR\Sulfur_Data\resources.assets"
)


def extract_translations(path: str = DEFAULT_PATH) -> None:
    writer = parsers.rawCSV.Writer
    assets = read_assets(path)
    write_output("unpacked/translations.csv", assets, writer)
