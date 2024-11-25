import os
import UnityPy
from UnityPy.classes import PPtr, MonoBehaviour
import argparse
import json
import re
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


global_loot_table: MonoBehaviour | None = None
global_items: dict[str, MonoBehaviour] = {}
global_recipes: dict[str, MonoBehaviour] = {}


def unpack_loot_table(source: str) -> None:
    global global_loot_table
    global global_recipes
    global global_items
    print("Unpacking translations...")
    extract_translations()
    print("Loading asset bundles...")
    env = UnityPy.load(source)
    print("Unpacking assets...")
    for pptr in env.objects:
        if pptr.type.name == "MonoBehaviour":
            data: MonoBehaviour = pptr.parse_as_object()
            if not global_loot_table and data.m_Name == "Loot_Global_Everything":
                global_loot_table = data
                for loot in global_loot_table.entries:
                    if loot.lootItem.m_PathID not in global_items:
                        global_items[loot.lootItem.m_PathID] = (
                            loot.lootItem.deref_parse_as_object()
                        )
            if data.m_Name.startswith("Item_"):
                global_items[pptr.path_id] = data
            if data.m_Name.startswith("Recipe_"):
                global_recipes[pptr.path_id] = data
    unpack_dir = f"{UNPACK_DIR}/Items"
    if not os.path.exists(unpack_dir):
        os.makedirs(unpack_dir)
    for item in global_items.values():
        write_asset(item, unpack_dir)


def getTypeDir(asset: PPtr, destination_folder: str) -> str:
    identifier = getattr(asset, "identifier", "")
    slot_type = getattr(asset, "slotType", "")
    use_type = getattr(asset, "useType", "")
    dir = ""
    if "Consumable_ChamberChisel" in identifier:
        dir = "Chisels"
    elif "Valuable" in identifier:
        dir = "Valuables"
    elif UseType(use_type) == UseType["Equippable"]:
        if SlotType(slot_type) == SlotType["Weapon"]:
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


attribute_map: dict[int, str] = {}


def get_attribute_name(pptr: PPtr) -> str:
    global attribute_map
    path_id = pptr.path_id
    if path_id in attribute_map:
        return attribute_map[path_id]
    else:
        attribute = pptr.deref_parse_as_dict()
        name = ""
        if "itemDescriptionName" in attribute and len(attribute["itemDescriptionName"]):
            name = attribute["itemDescriptionName"]
        elif "label" in attribute and len(attribute["label"]):
            name = attribute["label"]
        elif "enchantmentName" in attribute and len(attribute["enchantmentName"]):
            name = attribute["enchantmentName"]
        attribute_map[path_id] = name
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
            buff_dict["attribute"] = get_attribute_name(attribute)
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
            modifier_dict["attribute"] = get_attribute_name(attribute)
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
            attribute_dict["attribute"] = get_attribute_name(attribute)
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
            attribute_dict["Caliber"] = get_attribute_name(caliber)
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


def process_asset(asset: MonoBehaviour, translated_name: str) -> dict[str, Any]:
    asset_dict = {}
    # identifier is used by the translation library, not always the same as m_Name
    identifier = getattr(asset, "identifier", "")
    asset_dict["displayName"] = translated_name
    flavor: str | Any = get_translation(f"{identifier}_flavor")
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
    buffs = getattr(asset, "buffsOnConsume", None)
    if buffs and len(buffs):
        new_buffs = process_buffs(buffs)
        asset_dict["buffsOnConsume"] = new_buffs
    remove_status = getattr(asset, "removeStatusOnConsume", None)
    if remove_status and len(remove_status):
        new_remove_status = []
        for status in remove_status:
            new_remove_status.append(get_attribute_name(status))
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
        asset_dict["damageType"] = get_attribute_name(damage_type)
    weapon_type = getattr(asset, "weaponType", None)
    if weapon_type:
        asset_dict["weaponType"] = get_attribute_name(weapon_type)
    caliber = getattr(asset, "caliber", None)
    if caliber:
        asset_dict["caliber"] = get_attribute_name(caliber)
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


def write_asset(asset: MonoBehaviour, destination_folder: str) -> None:
    type_dir = destination_folder
    name = ""
    tree: dict[str, Any] = {}
    if hasattr(asset, "identifier"):
        type_dir = getTypeDir(asset, destination_folder)
        name = get_translation(asset.identifier)
        tree = process_asset(asset, name)
    file_name = clean_file_name(name).replace(" ", "")
    fp = os.path.join(type_dir, f"{file_name}.json")
    with open(fp, "wt", encoding="utf8") as f:
        json.dump(tree, f, ensure_ascii=False, indent=4)


unpack_loot_table(args.assetpath)
