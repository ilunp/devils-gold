import os
import UnityPy
from UnityPy.classes import PPtr
import argparse
import json
import re

UNPACK_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "unpacked"))
if not os.path.exists(UNPACK_DIR):
    os.makedirs(UNPACK_DIR)

DEFAULT_PATH = r"C:\Program Files (x86)\Steam\steamapps\common\SULFUR\Sulfur_Data\StreamingAssets\aa\StandaloneWindows64"

parser = argparse.ArgumentParser("unpack")
parser.add_argument(
    "--assetpath",
    help="Asset directory or file to unpack",
    type=str,
    default=DEFAULT_PATH,
    required=False,
)
args = parser.parse_args()


def clean_file_name(name: str) -> str:
    # Removes invalid chars from a filename str
    return re.sub(r"[/\\?%*:|\"<>\x7F\x00-\x1F]", "-", name)


def unpack_assets(source: str, destination_folder: str) -> None:
    if os.path.isfile(source):
        root = os.path.dirname(source)
        file_name = os.path.basename(source)
        unpack_file(root, file_name, destination_folder)
    for root, dirs, files in os.walk(source):
        for file_name in files:
            unpack_file(root, file_name, destination_folder)


def unpack_file(root: str, file_name: str, destination_folder: str) -> None:
    # generate file_path
    file_path = os.path.join(root, file_name)
    print("PARSING FILE: " + os.path.join(file_path))
    # load that file via UnityPy.load
    env = UnityPy.load(file_path)
    for pptr in env.objects:
        assetType = ""
        try:
            assetType = pptr.type.name
        except:
            print("error")
        if assetType == "MonoBehaviour":
            breakpoint()
            write_asset(pptr, destination_folder)


def unpack_loot_table(source: str) -> None:
    env = UnityPy.load(source)
    for pptr in env.objects:
        if pptr.path_id == -2273047535729816587:
            loot_table = pptr.parse_as_object()
            name = loot_table.m_Name
            unpack_dir = f"{UNPACK_DIR}/{name}"
            if not os.path.exists(unpack_dir):
                os.makedirs(unpack_dir)
            for loot in loot_table.entries:
                write_asset(loot.lootItem, unpack_dir)


def write_asset(pptr: PPtr, destination_folder: str) -> None:
    tree = pptr.deref_parse_as_dict()
    name = ""
    if "m_Name" in tree:
        name = tree["m_Name"]
    else:
        name = str(pptr.path_id)
    fp = os.path.join(destination_folder, f"{clean_file_name(name)}.json")
    with open(fp, "wt", encoding="utf8") as f:
        json.dump(tree, f, ensure_ascii=False, indent=4)


# unpack_all_assets(args.assetpath, UNPACK_DIR)
unpack_loot_table(args.assetpath)
