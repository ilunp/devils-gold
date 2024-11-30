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
    ItemType,
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
global_game_settings: MonoBehaviour | None = None
global_loot_tables: dict[int, MonoBehaviour] = {}
global_calibers: dict[int, MonoBehaviour] = {}
global_weapon_types: dict[int, MonoBehaviour] = {}


def unpack_assets(source: str, version: str, language: str) -> None:
    global global_recipes
    global global_items
    global global_language
    global global_loot_tables
    global global_game_settings

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
            if data.m_Name == "GameSettings_Normal":
                global_game_settings = data
            if data.m_Name.startswith("Recipe_"):
                global_recipes[pptr.path_id] = data

    print("Unpacking Items...")
    item_unpack_dir = os.path.join(unpack_dir, "Items")
    for path_id, item in global_items.items():
        process_item(item, path_id, item_unpack_dir)

    print("Unpacking Calibers...")
    caliber_unpack_dir = os.path.join(unpack_dir, "Calibers")
    for item in global_calibers.values():
        process_basic(item, caliber_unpack_dir)

    print("Unpacking Weapon Types...")
    weapon_type_unpack_dir = os.path.join(unpack_dir, "Weapon Types")
    for item in global_weapon_types.values():
        process_basic(item, weapon_type_unpack_dir)

    print("Unpacking Recipes...")
    recipe_unpack_dir = os.path.join(unpack_dir, "Recipes")
    for recipe in global_recipes.values():
        process_recipe(recipe, recipe_unpack_dir)

    print("Unpacking Loot Tables..")
    loot_table_unpack_dir = os.path.join(unpack_dir, "Loot Tables")
    for table in global_loot_tables.values():
        process_basic(table, loot_table_unpack_dir)

    print("Unpacking Game Settings...")
    settings_unpack_dir = os.path.join(unpack_dir, "Game Settings")
    process_game_settings(global_game_settings, settings_unpack_dir)

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
    global global_calibers
    global global_weapon_types
    attr_list = [
        attr
        for attr in dir(asset)
        if not attr.startswith("_")
        and attr not in ["m_Enabled", "m_Script", "m_GameObject", "assets_file"]
        and type(getattr(asset, attr)) in [int, float, str, PPtr, list, int2_storage]
    ]
    asset_dict = {}
    for attr in attr_list:
        value = getattr(asset, attr)
        if type(value) is PPtr:
            if value.path_id != 0:
                if attr == "caliber":
                    if value.path_id not in global_calibers:
                        global_calibers[value.path_id] = value.deref_parse_as_object()
                if attr == "weaponType":
                    if value.path_id not in global_calibers:
                        global_weapon_types[value.path_id] = (
                            value.deref_parse_as_object()
                        )
                value = get_asset_name(value)
            else:
                value = None
        elif type(value) is int2_storage:
            value = {"x": value.x, "y": value.y}
        elif type(value) is list:
            new_list = []
            for item in value:
                new_item: Any | None = None
                if type(item) is PPtr:
                    if item.path_id == 0:
                        new_item = None
                    else:
                        new_item = get_asset_name(item)
                else:
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
        elif attr == "itemType":
            value = ItemType(value).name
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


def process_item(asset: MonoBehaviour, path_id: int, destination_folder: str) -> None:
    global asset_name_map
    global global_language
    final_destination = destination_folder
    name = ""
    tree: dict[str, Any] = {}
    final_destination = get_item_type_dir(asset, destination_folder)
    name = get_translation(asset.identifier, global_language)
    asset_name_map[path_id] = name
    tree = process_asset(asset)
    write_asset(tree, name, final_destination)


def process_recipe(asset: MonoBehaviour, destination_folder: str) -> None:
    final_destination = destination_folder
    name = ""
    tree: dict[str, Any] = {}
    if getattr(asset, "canBeCrafted", None):
        final_destination = get_recipe_type_dir(asset, destination_folder)
        tree = process_asset(asset)
        name = get_unique_recipe_name(tree)
    else:
        # Don't write uncraftable recipes
        return
    write_asset(tree, name, final_destination)


def process_game_settings(asset: MonoBehaviour, destination_folder: str) -> None:
    processed_settings = process_asset(asset)
    write_asset(processed_settings, asset.m_Name, destination_folder)
    loot_settings_obj = asset.LootSettings.deref_parse_as_object()
    processed_loot_settings = process_asset(loot_settings_obj)
    write_asset(processed_loot_settings, loot_settings_obj.m_Name, destination_folder)
    for act in asset.Acts:
        act_obj = act.deref_parse_as_object()
        processed_act = process_asset(act_obj)
        act_dir = os.path.join(destination_folder, act_obj.actName)
        write_asset(processed_act, act_obj.actName, act_dir)
        for index, environment in enumerate(act_obj.environments):
            environment_obj = environment.deref_parse_as_object()
            processed_env = process_asset(environment_obj)
            level_dir = os.path.join(
                act_dir, f"{index + 1}_{environment_obj.environmentName}"
            )
            write_asset(processed_env, environment_obj.m_Name, level_dir)
            for level in environment_obj.levelList:
                level_obj = level.deref_parse_as_object()
                processed_level = process_asset(level_obj)
                write_asset(processed_level, level_obj.m_Name, level_dir)


def process_basic(asset: MonoBehaviour, destination_folder: str) -> None:
    processed_asset = process_asset(asset)
    write_asset(processed_asset, asset.m_Name, destination_folder)


def write_asset(tree: dict[str, Any], name: str, path: str) -> None:
    if not os.path.exists(path):
        os.makedirs(path)
    file_name = clean_file_name(name).replace(" ", "")
    fp = os.path.join(path, f"{file_name}.json")
    with open(fp, "wt", encoding="utf8") as f:
        json.dump(tree, f, ensure_ascii=False, indent=4)


unpack_assets(args.assetpath, args.gameversion, args.lang)
