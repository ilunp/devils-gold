import os
import UnityPy
from UnityPy.classes import PPtr, MonoBehaviour
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
        if "itemDescriptionName" in asset and len(asset["itemDescriptionName"]):
            name = asset["itemDescriptionName"]
        elif "label" in asset and len(asset["label"]):
            name = asset["label"]
        elif "enchantmentName" in asset and len(asset["enchantmentName"]):
            name = asset["enchantmentName"]
        asset_name_map[path_id] = name
        return name


def process_buffs(buffs: list[PPtr]) -> list[dict[str, str]]:
    processed_buffs = []
    for buff in buffs:
        buff_dict = {}
        buff_type = getattr(buff, "buffType", None)
        if isinstance(buff_type, int):
            buff_dict["buffType"] = BuffType(buff_type).name
        attribute: PPtr | None = getattr(buff, "attributeNew", None)
        if attribute:
            buff_dict["attribute"] = get_asset_name(attribute)
        stat_mod_type = getattr(buff, "statModType", None)
        if stat_mod_type:
            buff_dict["statModType"] = StatModType(stat_mod_type).name
        value = getattr(buff, "value", None)
        value_override = getattr(buff, "totalValueOverride", None)
        if isinstance(value, float) and isinstance(value_override, float):
            # In the game code, totalValueOverride takes precedence
            final_value = value
            if not value_override == float(0):
                final_value = value_override
            buff_dict["value"] = final_value
        duration = getattr(buff, "duration", None)
        if duration:
            buff_dict["duration"] = duration
        processed_buffs.append(buff_dict)
    return processed_buffs


def process_modifiers(modifiers: list[PPtr]) -> list[dict[str, Any]]:
    processed_modifiers = []
    for modifier in modifiers:
        modifier_dict = {}
        attribute: PPtr | None = getattr(modifier, "attribute", None)
        if attribute:
            modifier_dict["attribute"] = get_asset_name(attribute)
        mod_type = getattr(modifier, "modType", None)
        if mod_type:
            modifier_dict["modType"] = StatModType(mod_type).name
        value = getattr(modifier, "value", None)
        if isinstance(value, float):
            modifier_dict["value"] = value
        processed_modifiers.append(modifier_dict)
    return processed_modifiers


def process_base_attributes(attributes: list[PPtr]) -> list[dict[str, Any]]:
    processed_attributes = []
    for base_attribute in attributes:
        attribute_dict = {}
        attribute: PPtr | None = getattr(base_attribute, "attribute", None)
        if attribute:
            attribute_dict["attribute"] = get_asset_name(attribute)
        value = getattr(base_attribute, "value", None)
        if isinstance(value, float):
            attribute_dict["value"] = value
        processed_attributes.append(attribute_dict)
    return processed_attributes


def process_caliber_attributes(attributes: list[PPtr]) -> list[dict[str, Any]]:
    processed_attributes = []
    for attribute in attributes:
        attribute_dict = {}
        caliber = getattr(attribute, "Caliber", None)
        if caliber:
            attribute_dict["Caliber"] = get_asset_name(caliber)
        kick_power = getattr(attribute, "KickPower", None)
        if kick_power:
            attribute_dict["KickPower"] = kick_power
        spread = getattr(attribute, "Spread", None)
        if spread:
            attribute_dict["Spread"] = spread
        processed_attributes.append(attribute_dict)
    return processed_attributes


def process_value(
    asset: PPtr,
    name: str,
    dict: dict[str, Any],
    type: type | None = None,
) -> None:
    value = getattr(asset, name, None)
    if type:
        if isinstance(value, type):
            dict[name] = value
    else:
        if value:
            dict[name] = value


def process_item(asset: MonoBehaviour, translated_name: str) -> dict[str, Any]:
    global global_language
    asset_dict = {}
    # identifier is used by the translation library, not always the same as m_Name
    identifier = getattr(asset, "identifier", "")
    asset_dict["displayName"] = translated_name
    flavor: str | Any = get_translation(f"{identifier}_flavor", global_language)
    if not len(flavor):
        flavor = getattr(asset, "flavor", "")
    if flavor:
        asset_dict["flavor"] = flavor
    use_type = getattr(asset, "useType", None)
    if isinstance(use_type, int):
        asset_dict["useType"] = UseType(use_type).name
    if identifier:
        asset_dict["identifier"] = identifier
    process_value(asset, "basePrice", asset_dict, int)
    item_quality = getattr(asset, "itemQuality", None)
    if isinstance(item_quality, int):
        asset_dict["itemQuality"] = ItemQuality(item_quality).name
    slot_type = getattr(asset, "slotType", None)
    if slot_type:
        asset_dict["slotType"] = SlotType(slot_type).name
    inventory_size = getattr(asset, "inventorySize", None)
    if inventory_size:
        asset_dict["inventorySize"] = {"x": inventory_size.x, "y": inventory_size.y}
    weight_class = getattr(asset, "weightClass", None)
    if "Weapon_" in identifier and isinstance(weight_class, int):
        asset_dict["weightClass"] = HoldableWeightClass(weight_class).name
    durability = getattr(asset, "maxDurability", None)
    if durability and UseType(use_type) == UseType["Equippable"]:
        asset_dict["maxDurability"] = durability
    equip_modifiers = getattr(asset, "modifiersOnEquipNew", None)
    if equip_modifiers and len(equip_modifiers):
        asset_dict["modifiersOnEquip"] = process_modifiers(equip_modifiers)
    buffs = getattr(asset, "buffsOnConsume", None)
    if buffs and len(buffs):
        new_buffs = process_buffs(buffs)
        asset_dict["buffsOnConsume"] = new_buffs
    remove_status = getattr(asset, "removeStatusOnConsume", None)
    if remove_status and len(remove_status):
        new_remove_status = []
        for status in remove_status:
            new_remove_status.append(get_asset_name(status))
        asset_dict["removeStatusOnConsume"] = new_remove_status
    enchantment = getattr(asset, "appliesEnchantment", None)
    if enchantment:
        enchantment_def = enchantment.deref_parse_as_object()
        enchantment_modifiers = process_modifiers(enchantment_def.modifiersApplied)
        asset_dict["appliesEnchantmentModifiers"] = enchantment_modifiers
    base_attributes = getattr(asset, "baseAttributes", None)
    if base_attributes and len(base_attributes):
        asset_dict["baseAttributes"] = process_base_attributes(base_attributes)
    damage_type = getattr(asset, "damageType", None)
    if damage_type:
        asset_dict["damageType"] = get_asset_name(damage_type)
    weapon_type = getattr(asset, "weaponType", None)
    if weapon_type:
        asset_dict["weaponType"] = get_asset_name(weapon_type)
    caliber = getattr(asset, "caliber", None)
    if caliber:
        asset_dict["caliber"] = get_asset_name(caliber)
    process_value(asset, "damageMultiplier", asset_dict, float)
    kick_power = getattr(asset, "kickPower", None)
    if kick_power and len(kick_power):
        asset_dict["kickPower"] = process_caliber_attributes(kick_power)
    spread_caliber = getattr(asset, "spreadPerCaliber", None)
    if spread_caliber and len(spread_caliber):
        asset_dict["spreadPerCaliber"] = process_caliber_attributes(spread_caliber)
    process_value(asset, "adsEnabled", asset_dict, int)
    process_value(asset, "overrideDamage", asset_dict, float)
    process_value(asset, "bulletSpeed", asset_dict, float)
    process_value(asset, "iAmmoMax", asset_dict, float)
    process_value(asset, "shotsToReachFullSpread", asset_dict, int)
    process_value(asset, "timeToCooldownSpread", asset_dict, float)
    process_value(asset, "iMaxAmmoPerShot", asset_dict, int)
    process_value(asset, "rpm", asset_dict, int)
    process_value(asset, "cooldownBeforeReload", asset_dict, float)
    return asset_dict


def process_recipe(asset: MonoBehaviour) -> dict[str, Any]:
    asset_dict: dict[str, Any] = {}
    process_value(asset, "m_Name", asset_dict)
    creates = getattr(asset, "createsItem", None)
    if creates:
        asset_dict["createsItem"] = get_asset_name(creates)
    process_value(asset, "quantityCreated", asset_dict, int)
    items_needed = getattr(asset, "itemsNeeded", None)
    if items_needed:
        new_items_needed = []
        for entry in items_needed:
            new_entry = {}
            new_entry["item"] = get_asset_name(entry.item)
            process_value(entry, "quantity", new_entry, int)
            new_items_needed.append(new_entry)
        asset_dict["itemsNeeded"] = new_items_needed
    process_value(asset, "canBeCrafted", asset_dict, int)
    return asset_dict


def get_recipe_type_dir(asset: MonoBehaviour, destination_folder: str) -> str:
    global global_items
    item: PPtr = getattr(asset, "createsItem", None)
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
        tree = process_item(asset, name)
    if hasattr(asset, "createsItem"):
        if getattr(asset, "canBeCrafted", None):
            final_destination = get_recipe_type_dir(asset, destination_folder)
            tree = process_recipe(asset)
            name = get_unique_recipe_name(tree)
        else:
            # Don't write uncraftable recipes
            return
    if hasattr(asset, "entries"):
        name = asset.m_Name
        tree = process_loot_table(asset)
    file_name = clean_file_name(name).replace(" ", "")
    fp = os.path.join(final_destination, f"{file_name}.json")
    with open(fp, "wt", encoding="utf8") as f:
        json.dump(tree, f, ensure_ascii=False, indent=4)


unpack_assets(args.assetpath, args.gameversion, args.lang)
