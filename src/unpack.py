import os
import UnityPy
from UnityPy.classes import PPtr, MonoBehaviour, int2_storage
import argparse
import json
from translations import extract_translations, get_translation
from typing import Any
from sulfur import (
    UseType,
    ItemQuality,
    SlotType,
    HoldableWeightClass,
    BuffType,
    StatModType,
)
from utils import clean_file_name, create_uuid_from_string
from recipe import generate_recipe_list

DEFAULT_UNPACK_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "unpacked")
)

DEFAULT_PATH = r"C:\Program Files (x86)\Steam\steamapps\common\SULFUR\Sulfur_Data"

parser = argparse.ArgumentParser("unpack")
# This is kind of dumb but I can't figure out how to get the game version
parser.add_argument(
    "gameversion",
    help="Sulfur game version",
    type=str,
)
parser.add_argument(
    "--assetpath",
    help="Sulfur_Data path",
    type=str,
    default=DEFAULT_PATH,
    required=False,
)
parser.add_argument(
    "--lang",
    help="Language to use for translations in ISO-639 2-letter code",
    type=str,
    default="en",
    required=False,
)
args = parser.parse_args()

global_language: str
global_items: dict[int, MonoBehaviour] = {}
global_recipes: dict[int, MonoBehaviour] = {}

global_loot_tables: dict[int, MonoBehaviour] = {}


def unpack_assets(source: str, version: str, language: str) -> None:
    global global_recipes
    global global_items
    global global_language
    global global_loot_tables

    global_language = language
    unpack_dir = os.path.join(
        DEFAULT_UNPACK_DIR,
        "SULFUR_" + clean_file_name(version).replace(".", "-"),
    )
    if not os.path.exists(unpack_dir):
        os.makedirs(unpack_dir)

    print("Unpacking translations...")
    extract_translations(source, unpack_dir)
    print("Loading asset bundles...")
    assets_dir = os.path.join(source, "StreamingAssets")
    env = UnityPy.load(assets_dir)
    print("Finding assets...")
    for pptr in env.objects:
        if pptr.type.name == "MonoBehaviour":
            data: MonoBehaviour = pptr.parse_as_object()
            if hasattr(data, "entries") and "Demo" not in data.m_Name:
                global_loot_tables[pptr.path_id] = data
            if hasattr(data, "useType"):
                if hasattr(data, "usableByPlayer"):
                    if data.usableByPlayer:
                        # Don't select monster weapons
                        global_items[pptr.path_id] = data
                else:
                    global_items[pptr.path_id] = data
            if data.m_Name.startswith("Recipe_"):
                global_recipes[pptr.path_id] = data

    print("Unpacking Items...")
    item_unpack_dir = f"{unpack_dir}/Items"
    if not os.path.exists(item_unpack_dir):
        os.makedirs(item_unpack_dir)
    for path_id, item in global_items.items():
        process_asset(item)
        write_asset(item, path_id, item_unpack_dir)

    print("Unpacking Recipes...")
    recipe_unpack_dir = f"{unpack_dir}/Recipes"
    if not os.path.exists(recipe_unpack_dir):
        os.makedirs(recipe_unpack_dir)
    for recipe in global_recipes.values():
        write_asset(recipe, path_id, recipe_unpack_dir)

    print("Unpacking Loot Tables..")
    loot_table_unpack_dir = f"{unpack_dir}/Loot Tables"
    if not os.path.exists(loot_table_unpack_dir):
        os.makedirs(loot_table_unpack_dir)
    for path_id, table in global_loot_tables.items():
        write_asset(table, path_id, loot_table_unpack_dir)

    print("Generating Recipe List...")
    generate_recipe_list(unpack_dir, version)

    print(f"Finished unpacking data to {unpack_dir}")


def get_item_type_dir(asset: PPtr, destination_folder: str) -> str:
    identifier = getattr(asset, "identifier", "")
    use_type = getattr(asset, "useType", "")
    dir = ""
    if "Consumable_ChamberChisel" in identifier:
        dir = "Chisels"
    elif "Valuable" in identifier:
        dir = "Valuables"
    elif UseType(use_type) == UseType["Equippable"]:
        if identifier.startswith("Weapon_"):
            dir = "Weapons"
        else:
            dir = "Equipment"
    elif UseType(use_type) == UseType["ItemRepair"]:
        dir = "Repair Items"
    elif UseType(use_type) == UseType["Consumable"]:
        dir = "Consumables"
    elif UseType(use_type) == UseType["Attachment"]:
        dir = "Attachments"
    elif UseType(use_type) == UseType["Enchantment"]:
        # Feature Gun Oil for some reason does not have Oil in the identifier
        if "Oil" in identifier or "FeatureGun" in identifier:
            dir = "Oils"
        else:
            dir = "Scrolls"
    elif UseType(use_type) == UseType["Storage"]:
        dir = "Storage"
    elif UseType(use_type) == UseType["Key"]:
        dir = "Keys"
    elif UseType(use_type) == UseType["None"]:
        dir = "Misc Items"
    type_dir = os.path.join(destination_folder, dir)
    if not os.path.exists(type_dir):
        os.makedirs(type_dir)
    return type_dir


asset_name_map: dict[int, str] = {}


def get_asset_name(pptr: PPtr) -> str:
    global asset_name_map
    path_id = pptr.path_id
    if path_id in asset_name_map:
        return asset_name_map[path_id]
    else:
        asset = pptr.deref_parse_as_dict()
        name = ""
        if "displayName" in asset and "identifier" in asset:
            translated = get_translation(asset["identifier"], global_language)
            name = translated
        elif "itemDescriptionName" in asset and len(asset["itemDescriptionName"]):
            name = asset["itemDescriptionName"]
        elif "label" in asset and len(asset["label"]):
            name = asset["label"]
        elif "enchantmentName" in asset and len(asset["enchantmentName"]):
            name = asset["enchantmentName"]
        elif "m_Name" in asset and len(asset["m_Name"]):
            name = asset["m_Name"]
        else:
            name = str(path_id)
        asset_name_map[path_id] = name
        return name


def get_enchantment_modifiers(enchantment: PPtr) -> list[dict[str, Any]]:
    modifiers = []
    asset = enchantment.deref_parse_as_object()
    for modifier in asset.modifiersApplied:
        modifiers.append(process_asset(modifier))
    return modifiers


def process_asset(asset: MonoBehaviour) -> dict[str, Any]:
    attr_list = [
        attr
        for attr in dir(asset)
        if not attr.startswith("_")
        and type(getattr(asset, attr)) in [int, float, str, PPtr, list, int2_storage]
        and attr not in ["m_Enabled", "m_Script", "m_GameObject", "assets_file"]
    ]
    asset_dict = {}
    for attr in attr_list:
        value = getattr(asset, attr)
        if type(value) is PPtr:
            if value.path_id != 0:
                value = get_asset_name(value)
            else:
                value = None
        if type(value) is int2_storage:
            value = {"x": value.x, "y": value.y}
        elif type(value) is list:
            new_list = []
            for item in value:
                new_item = process_asset(item)
                new_list.append(new_item)
            value = new_list
        elif attr == "displayName" and "identifier" in attr_list:
            value = get_translation(asset.identifier, global_language)
        elif attr == "flavor" and "identifier" in attr_list:
            value = get_translation(f"{asset.identifier}_flavor", global_language)
        elif attr == "useType":
            value = UseType(value).name
        elif attr == "slotType":
            value = SlotType(value).name
        elif attr == "weightClass":
            value = HoldableWeightClass(value).name
        elif attr == "modType":
            value = StatModType(value).name
        elif attr == "buffType":
            value = BuffType(value).name
        elif attr == "itemQuality":
            value = ItemQuality(value).name
        elif attr == "appliesEnchantment":
            value = get_enchantment_modifiers(value)
        asset_dict[attr] = value
    return asset_dict


def get_recipe_type_dir(asset: MonoBehaviour, destination_folder: str) -> str:
    global global_items
    item: PPtr | None = getattr(asset, "createsItem", None)
    if item:
        return get_item_type_dir(global_items[item.path_id], destination_folder)
    return destination_folder


def get_unique_recipe_name(recipe: dict[str, Any]) -> str:
    """
    This hack fixes some issues:
    There are some duplicate recipes (e.g. Poutine)
    There are some recipes with wrong names (e.g. Throwing Knife)
    Allows for crude sorting by quantity
    """
    item_name = recipe["createsItem"]
    quantity = recipe["quantityCreated"]
    new_dict = dict(recipe)
    del new_dict["m_Name"]
    recipe_str = json.dumps(new_dict, ensure_ascii=False)
    unique_name = f"{item_name}_{quantity}_{create_uuid_from_string(recipe_str)}"
    return unique_name


def process_loot_table(table: MonoBehaviour) -> dict[str, Any]:
    result = {}
    result["m_Name"] = table.m_Name
    entries = []
    for entry in table.entries:
        if not entry.lootItem.path_id == 0:
            item = {
                "name": get_asset_name(entry.lootItem),
                "lootWeight": entry.lootWeight,
            }
            entries.append(item)
    result["entries"] = entries
    return result


def write_asset(asset: MonoBehaviour, path_id: int, destination_folder: str) -> None:
    global asset_name_map
    global global_language
    final_destination = destination_folder
    name = ""
    tree: dict[str, Any] = {}
    if hasattr(asset, "identifier"):
        final_destination = get_item_type_dir(asset, destination_folder)
        name = get_translation(asset.identifier, global_language)
        asset_name_map[path_id] = name
        tree = process_asset(asset)
    if hasattr(asset, "createsItem"):
        if getattr(asset, "canBeCrafted", None):
            final_destination = get_recipe_type_dir(asset, destination_folder)
            tree = process_asset(asset)
            name = get_unique_recipe_name(tree)
        else:
            # Don't write uncraftable recipes
            return
    if hasattr(asset, "entries"):
        name = asset.m_Name
        tree = process_asset(asset)
    file_name = clean_file_name(name).replace(" ", "")
    fp = os.path.join(final_destination, f"{file_name}.json")
    with open(fp, "wt", encoding="utf8") as f:
        json.dump(tree, f, ensure_ascii=False, indent=4)


unpack_assets(args.assetpath, args.gameversion, args.lang)
