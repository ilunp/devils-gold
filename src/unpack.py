import os
import UnityPy
from UnityPy.classes import PPtr
import argparse
import json
import re
from translations import extract_translations, get_translation
from typing import Any
from sulfur import UseType, ItemQuality, SlotType, HoldableWeightClass

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
    extract_translations()
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


def getTypeDir(identifier: str, destination_folder: str) -> str:
    dir = ""
    if "Consumable_ChamberChisel" in identifier:
        dir = "Chisels"
    elif "Valuable" in identifier:
        dir = "Valuables"
    else:
        dir = identifier.split("_")[0] + "s"
    type_dir = os.path.join(destination_folder, dir)
    if not os.path.exists(type_dir):
        os.makedirs(type_dir)
    return type_dir


def process_asset(asset_tree: dict[str, Any], translated_name: str) -> dict[str, Any]:
    new_tree = {}
    # identifier is used by the translation library, not always the same as m_Name
    identifier = asset_tree.get("identifier")
    new_tree["displayName"] = translated_name
    flavor: str | Any = get_translation(f"{identifier}_flavor")
    if not len(flavor):
        flavor = asset_tree.get("flavor")
    if flavor and len(flavor):
        new_tree["flavor"] = flavor
    use_type = asset_tree.get("useType")
    if isinstance(use_type, int):
        new_tree["useType"] = UseType(use_type).name
    if identifier:
        new_tree["identifier"] = identifier
    base_price = asset_tree.get("basePrice")
    if isinstance(base_price, int):
        new_tree["basePrice"] = base_price
    item_quality = asset_tree.get("itemQuality")
    if isinstance(item_quality, int):
        new_tree["itemQuality"] = ItemQuality(item_quality).name
    slot_type = asset_tree.get("slotType")
    if slot_type:
        new_tree["slotType"] = SlotType(slot_type).name
    inventory_size = asset_tree.get("inventorySize")
    if inventory_size:
        new_tree["inventorySize"] = inventory_size
    weight_class = asset_tree.get("weightClass")
    if "Weapon_" in identifier and isinstance(weight_class, int):
        new_tree["weightClass"] = HoldableWeightClass(weight_class).name
    return new_tree


def write_asset(pptr: PPtr, destination_folder: str) -> None:
    tree = pptr.deref_parse_as_dict()
    type_dir = destination_folder
    name = ""
    if "identifier" in tree:
        type_dir = getTypeDir(tree["identifier"], destination_folder)
        name = get_translation(tree["identifier"])
        tree = process_asset(tree, name)
    elif "m_Name" in tree:
        name = tree["m_Name"]
    else:
        name = str(pptr.path_id)
    file_name = clean_file_name(name).replace(" ", "")
    fp = os.path.join(type_dir, f"{file_name}.json")
    with open(fp, "wt", encoding="utf8") as f:
        json.dump(tree, f, ensure_ascii=False, indent=4)


unpack_loot_table(args.assetpath)
