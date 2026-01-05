import os
import UnityPy
from UnityPy.classes import PPtr, MonoBehaviour, int2_storage
import argparse
import json
from translations import extract_translations, get_translation
from typing import Any
from sulfur_enums import *

from sulfur_types import Unit, Faction, AttributeContainerNew
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
global_units: dict[int, MonoBehaviour] = {}
global_npcs: dict[int, MonoBehaviour] = {}

global_interacts: dict[int, MonoBehaviour] = {}
global_achievements: dict[int, MonoBehaviour] = {}
global_cards: dict[int, MonoBehaviour] = {}
global_quest_items: dict[int, MonoBehaviour] = {}


def unpack_assets(source: str, version: str, language: str) -> None:
    global global_language
    global global_game_settings
    global global_quest_items
    
    global_language = language
    unpack_dir = os.path.join(
        DEFAULT_UNPACK_DIR,
        "SULFUR_" + clean_file_name(version).replace(".", "-") + "_" + clean_file_name(language).replace(".", "-"),
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
                global_items[pptr.path_id] = data
            if data.m_Name == "GameSettings_Normal":
                global_game_settings = data
            if data.m_Name.startswith("Recipe_"):
                global_recipes[pptr.path_id] = data
            if hasattr(data, "unitType"):
                global_units[pptr.path_id] = data
            if hasattr(data, "meleeDamageType"):
                global_npcs[pptr.path_id] = data     
            if data.m_Name.startswith("Achievement_"):
                global_achievements[pptr.path_id] = data
            if data.m_Name.startswith("Card_"):
                global_cards[pptr.path_id] = data
            if (data.m_Name.endswith("QuestItems") or 
                data.m_Name.endswith("QuestItemRewards")):
                global_quest_items[pptr.path_id] = data
            if hasattr(data, "interactableType"):
                global_interacts[pptr.path_id] = data

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

    print("Unpacking Units...")
    unit_unpack_dir = os.path.join(unpack_dir, "Units")
    for item in global_units.values():
        process_unit(item, unit_unpack_dir)

    print("Unpacking NPCs")
    npc_unpack_dir = os.path.join(unpack_dir, "NPCs")
    for path_id, item in global_npcs.items():
        process_npc(item, npc_unpack_dir, path_id)

    print("Unpacking Recipes...")
    recipe_unpack_dir = os.path.join(unpack_dir, "Recipes")
    for recipe in global_recipes.values():
        process_recipe(recipe, recipe_unpack_dir)

    print("Unpacking Loot Tables..")
    loot_table_unpack_dir = os.path.join(unpack_dir, "Loot Tables")
    for path_id, table in global_loot_tables.items():
        process_basic(table, loot_table_unpack_dir)

    print("Unpacking Game Settings...")
    settings_unpack_dir = os.path.join(unpack_dir, "Game Settings")
    process_game_settings(global_game_settings, settings_unpack_dir)

    print("Unpacking Achievements...")
    achievement_unpack_dir = os.path.join(unpack_dir, "Achievements")
    for achievement in global_achievements.values():
        process_achievement(achievement, achievement_unpack_dir)

    print("Unpacking Cards...")
    cards_unpack_dir = os.path.join(unpack_dir, "Cards")
    for card in global_cards.values():
        process_card(card, cards_unpack_dir)

    print("Unpacking Quest Items...")
    quest_unpack_dir = os.path.join(unpack_dir, "Quests")
    for quest_item in global_quest_items.values():
        process_basic(quest_item, quest_unpack_dir)

    print("Unpacking Interacts...")
    interact_unpack_dir = os.path.join(unpack_dir, "Interacts")
    for path_id, interact in global_interacts.items():
        process_interact(interact, interact_unpack_dir, path_id)

    print("Generating Recipe List...")
    generate_recipe_list(unpack_dir, version)

    print(f"Finished unpacking data to {unpack_dir}")


def get_card_type_dir(asset: MonoBehaviour, destination_folder: str) -> str:
    card_type = getattr(asset, "cardType", "")
    dir = ""
    if CardType(card_type) == CardType["ItemSpawn"]:
        dir = "ItemSpawn"
    elif CardType(card_type) == CardType["EntitySpawn"]:
        dir = "EntitySpawn"
    elif CardType(card_type) == CardType["Buff"]:
        dir = "Buff"
    elif CardType(card_type) == CardType["Event"]:
        dir = "Event"
    type_dir = os.path.join(destination_folder, dir)
    if not os.path.exists(type_dir):
        os.makedirs(type_dir)
    return type_dir 

def get_interact_type_dir(asset: MonoBehaviour, destination_folder: str) -> str:
    interactable_type = getattr(asset, "interactableType", "")
    dir = ""
    if InteractableType(interactable_type) == InteractableType["Dialog"]:
        dir = "Dialog"
    elif InteractableType(interactable_type) == InteractableType["Shop"]:
        dir = "Shop"
    elif InteractableType(interactable_type) == InteractableType["Repair"]:
        dir = "Repair"
    elif InteractableType(interactable_type) == InteractableType["Enchant"]:
        dir = "Enchant"
    elif InteractableType(interactable_type) == InteractableType["Cook"]:
        dir = "Cook"
    elif InteractableType(interactable_type) == InteractableType["Interact"]:
        dir = "Interact"
    elif InteractableType(interactable_type) == InteractableType["LockedDoor"]:
        dir = "LockedDoor"
    elif InteractableType(interactable_type) == InteractableType["Dice"]:
        dir = "Dice"
    elif InteractableType(interactable_type) == InteractableType["Cleanse"]:
        dir = "Cleanse"
    elif InteractableType(interactable_type) == InteractableType["Quest"]:
        dir = "Quest"
    type_dir = os.path.join(destination_folder, dir)
    if not os.path.exists(type_dir):
        os.makedirs(type_dir)
    return type_dir

def get_item_type_dir(asset: PPtr, destination_folder: str) -> str:
    # identifier = getattr(asset, "identifier", "")
    m_Name = getattr(asset, "m_Name", "")
    use_type = getattr(asset, "useType", "")
    slot_type = getattr(asset, "slotType", "")
    dir = ""
    # if "Consumable_ChamberChisel" in identifier:
    if "Consumable_ChamberChisel" in m_Name:
        dir = "Chisels"
    # elif "Valuable" in identifier:
    elif "Valuable" in m_Name:
        dir = "Valuables"
    elif UseType(use_type) == UseType["Equippable"]:
        # if SlotType(slot_type) == SlotType["Weapon"] or "Weapon" in identifier:
        if SlotType(slot_type) == SlotType["Weapon"] or "Weapon" in m_Name:
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
        # if "Oil" in identifier or "FeatureGun" in identifier:
        if "Oil" in m_Name or "FeatureGun" in m_Name:
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
        # if "displayName" in asset and "identifier" in asset:
        if "displayName" in asset and "m_Name" in asset:
            # translated = get_translation(asset["identifier"], global_language)
            translated = get_translation(asset["m_Name"], global_language)
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
    enchantment_modifiers = []
    asset = enchantment.deref_parse_as_object()
    if hasattr(asset, 'CostsDurability'):
        enchantment_modifiers.append({"costsDurability": asset.CostsDurability})

    for en_modifier in asset.modifiersApplied:
        en_modifier_dict = process_asset(en_modifier)
        arrt = en_modifier.attribute.deref_parse_as_dict()
        en_modifier_dict["id"] = arrt.get("id", 0)
        en_modifier_dict["localizationKey"] = arrt.get("m_Name", 0)
        en_modifier_dict["showInItemDescription"] = arrt.get("showInItemDescription", 0)
        en_modifier_dict["isBooleanAttribute"] = arrt.get("isBooleanAttribute", 0)
        en_modifier_dict["isPercentageAttribute"] = arrt.get("isPercentageAttribute", 0)
        en_modifier_dict["simplifiedModAmount"] = arrt.get("simplifiedModAmount", 0)
        # en_modifier_dict["simplifiedIncreaseString"] = arrt.get("simplifiedIncreaseString", "")
        # en_modifier_dict["simplifiedDecreaseString"] = arrt.get("simplifiedDecreaseString", "")
        enchantment_modifiers.append(en_modifier_dict)
    return enchantment_modifiers

def get_attribute_modifier(attribute: list[PPtr]) -> list[dict[str, Any]]:
    attr_modifiers = []

    for attr_modifier in attribute:
        attr_modifier_dict = process_asset(attr_modifier)
        if hasattr(attr_modifier, 'attribute'):
            arrt = attr_modifier.attribute.deref_parse_as_dict()
        elif hasattr(attr_modifier, 'attributeNew'):
            arrt = attr_modifier.attributeNew.deref_parse_as_dict()
        attr_modifier_dict["id"] = arrt.get("id", 0)
        attr_modifier_dict["localizationKey"] = arrt.get("m_Name", 0)
        attr_modifier_dict["showInItemDescription"] = arrt.get("showInItemDescription", 0)
        attr_modifier_dict["isBooleanAttribute"] = arrt.get("isBooleanAttribute", 0)
        attr_modifier_dict["isPercentageAttribute"] = arrt.get("isPercentageAttribute", 0)
        attr_modifiers.append(attr_modifier_dict)

    return attr_modifiers



def process_asset(asset: MonoBehaviour, is_card: bool = False) -> dict[str, Any]:
    global global_calibers
    global global_weapon_types
    attr_list = [
        attr
        for attr in dir(asset)
        if not attr.startswith("_")
        and attr not in ["m_Enabled", "m_Script", "m_GameObject", "assets_file"]
        and type(getattr(asset, attr)) in [int, float, str, PPtr, list, int2_storage, bool, dict]
    ]
    if hasattr(asset, 'id') and 'id' not in attr_list:
        attr_list.append('id')
    asset_dict = {}
    for attr in attr_list:
        value = getattr(asset, attr)

        if type(value) is PPtr:
            if value.path_id != 0:
                if attr == "appliesEnchantment":
                    value = get_enchantment_modifiers(value)
                elif attr == "vendorTable":
                    value = get_asset_name(value)

                else:
                    if attr == "caliber":
                        if value.path_id not in global_calibers:
                            global_calibers[value.path_id] = value.deref_parse_as_object()
                    if attr == "weaponType":
                        if value.path_id not in global_weapon_types:
                            global_weapon_types[value.path_id] = value.deref_parse_as_object()

                        weapon_type_obj = value.deref_parse_as_dict()
                        value = weapon_type_obj.get("m_Name", "")
                    else:
                        value = get_asset_name(value)
            else:
                value = None
        elif type(value) is int2_storage:
            value = {"x": value.x, "y": value.y}
        elif type(value) is list:
            if attr == "modifiersOnEquipNew":
                value = get_attribute_modifier(value)
            elif attr == "modifiersOnAttachToItem":
                value = get_attribute_modifier(value)
            elif attr == "buffsOnConsume":
                value = get_attribute_modifier(value) 
            else:
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
        
        elif attr == "id" and hasattr(value, '__class__') and value.__class__.__name__ == 'UnknownObject':
            if hasattr(value, 'value'):
                value = value.value
        # elif attr == "displayName" and "identifier" in attr_list:
        elif attr == "displayName" and "m_Name" in attr_list:
            # value = get_translation(asset.identifier, global_language)
            value = get_translation(asset.m_Name, global_language)
        # elif attr == "flavor" and "identifier" in attr_list:
        elif attr == "flavor" and "m_Name" in attr_list:
            # value = get_translation(f"{asset.identifier}_flavor", global_language)
            value = get_translation(f"{asset.m_Name}_flavor", global_language)
        # elif attr == "description" and "m_Name" in attr_list:
        elif attr == "description" and "m_Name" in attr_list:
            if getattr(asset, "hasCustomDescription", False):
                # value = get_translation(f"{asset.identifier}_description", global_language)
                value = get_translation(f"{asset.m_Name}_description", global_language)
        elif attr == "useType":
            value = UseType(value).name
        elif attr == "slotType":
            value = SlotType(value).name
        elif attr == "weightClass":
            value = HoldableWeightClass(value).name
        elif attr == "modType" or attr == "StatModType":
            value = StatModType(value).name
        elif attr == "buffType" and not is_card:
            value = BuffType(value).name
        elif attr == "itemQuality":
            value = ItemQuality(value).name
        # elif attr == "appliesEnchantment":
            # value = get_enchantment_modifiers(value)
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
    # name = get_translation(asset.identifier, global_language)
    name = get_translation(asset.m_Name, global_language)
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
            for level in environment_obj.levels:
                level_obj = level.deref_parse_as_object()
                processed_level = process_asset(level_obj)
                write_asset(processed_level, level_obj.m_Name, level_dir)


def process_achievement(asset: MonoBehaviour, destination_folder: str) -> None:
    final_destination = destination_folder
    
    processed_asset = process_asset(asset)
    # Get proper display name from translations
    # if hasattr(asset, 'identifier'):
    # if hasattr(asset, 'm_Name'):
    #     # display_name = get_translation(asset.identifier, global_language)
    #     display_name = get_translation(asset.m_Name, global_language)
    #     processed_asset['displayName'] = display_name
    # # if hasattr(asset, 'descriptionIdentifier'):
    # if hasattr(asset, 'description'):
    #     # description = get_translation(asset.descriptionIdentifier, global_language)
    #     description = get_translation(asset.description, global_language)
    #     processed_asset['description'] = description
    write_asset(processed_asset, asset.identifier, final_destination)


def process_card(asset: MonoBehaviour, destination_folder: str) -> None:
    enums = {
        'buffType': CardBuffType,
        'cardType': CardType,
        'cardLayout': CardLayout,
        'rewardType': CardRewardType,
        'eventType': CardEventType
    }
    final_destination = destination_folder
    name = ""
    tree: dict[str, Any] = {}
    final_destination = get_card_type_dir(asset, destination_folder)
    name = get_translation(f"{asset.m_Name}_Title", global_language, "Endless/")
    tree = process_asset(asset, is_card=True)
    for field, enum in enums.items():
        if field in tree:
            try:
                value = tree[field]
                if isinstance(value, int):
                    tree[field] = enum(value).name
            except (ValueError, KeyError):
                pass

    write_asset(tree, name, final_destination)

def process_interact(asset: MonoBehaviour, destination_folder: str, path_id: int) -> None:
    enums = {
        'craftingType': CraftingType,
        'interactableType': InteractableType
    }
    final_destination = destination_folder
    name = ""
    tree: dict[str, Any] = {}
    final_destination = get_interact_type_dir(asset, destination_folder)
    name = f"{path_id}"
    tree = process_asset(asset)
    for field, enum in enums.items():
        if field in tree:
            try:
                value = tree[field]
                if isinstance(value, int):
                    tree[field] = enum(value).name

            except (ValueError, KeyError):
                pass

    write_asset(tree, name, final_destination)

def process_basic(asset: MonoBehaviour, destination_folder: str) -> None:
    processed_asset = process_asset(asset)
    write_asset(processed_asset, asset.m_Name, destination_folder)


def process_npc(asset: MonoBehaviour, destination_folder: str, path_id: int) -> None:
    processed_asset = process_asset(asset)
    # print(f"Processed NPC Asset: {processed_asset['unitSO']}")
    name = f"{processed_asset['unitSO']}_{path_id}"
    write_asset(processed_asset, name, destination_folder)


def process_character_base_attr(attrib: MonoBehaviour) -> AttributeContainerNew:
    attrib_type = attrib.type.deref_parse_as_dict()["itemDescriptionName"]
    attrib_type_label = f"{attrib.type.deref_parse_as_dict()["m_Name"]}_label"
    get_attrib_type_label = get_translation(attrib_type_label, global_language, "EntityAttributes/")
    result: AttributeContainerNew = {}
    if get_attrib_type_label == attrib_type_label:
        result["type"] = attrib_type
    else:
        result["type"] = get_translation(f"{attrib.type.deref_parse_as_dict()["m_Name"]}_label", global_language, "EntityAttributes/")
    result["value"] = attrib.value
    return result


def process_unit(asset: MonoBehaviour, destination_folder: str) -> None:
    asset_dict: Unit = {}

    m_name_value = getattr(asset, "m_Name", None)
    for key, type in Unit.__annotations__.items():
        value = getattr(asset, key)
        if hasattr(asset, 'id') :
            id_value = getattr(asset, 'id')
            if hasattr(id_value, 'value'):
                asset_dict['id'] = id_value.value
            elif isinstance(id_value, dict) and 'value' in id_value:
                asset_dict['id'] = id_value['value']
            else:
                try:
                    asset_dict['id'] = int(id_value)
                except:
                    asset_dict['id'] = str(id_value)
        else:
            asset_dict['id'] = None

        if key == "displayName":
            if m_name_value:
                value = get_translation(m_name_value, global_language, "UnitNames/")
            else:
                value = get_translation(value, global_language, "UnitNames/")
        elif key == "artwork":
            if value.path_id == 0:
                value = None
            else:
                value = value.deref_parse_as_dict()["m_Name"]
        elif key == "unitType":
            try:
                value = UnitType(value).name
            except ValueError:
                value = str(value)
        elif key == "faction":
            if value.path_id == 0:
                value = None
            else:
                process_faction(value, destination_folder)
                value = value.deref_parse_as_dict()["prettyLabel"]
        elif key == "rolesAvailable":
            new_roles = []
            for role in value:
                new_roles.append(AgentRole(role).name)
            value = new_roles
        elif key == "characterBaseAttributesNew":
            new_attribs = []
            for attrib in value:
                new_attrib = process_character_base_attr(attrib)
                new_attribs.append(new_attrib)
            value = new_attribs
        elif key == "applicableAttributeEffects":
            new_effects = []
            for effect in value:
                effect_name = EntityAttributes(effect).name
                new_effects.append(effect_name)
                
            value = new_effects
        elif key == "availableMutations":
            new_mutations = []
            for mutation in value:
                mutation_name = MutationDefinitions(mutation).name
                new_mutations.append(mutation_name)

            value = new_mutations
        else:
            value = type(value)
        asset_dict[key] = value
    final_destination = os.path.join(destination_folder, str(asset_dict["faction"]))
    write_asset(asset_dict, asset_dict["displayName"], final_destination)

def process_faction(asset: MonoBehaviour, destination_folder: str) -> None:
    processed_asset = process_asset(asset.deref_parse_as_object())
    name = f"_Faction_{processed_asset['prettyLabel'] or processed_asset['m_Name']}"
    final_destination = os.path.join(destination_folder, str(processed_asset['prettyLabel']))
    write_asset(processed_asset, name, final_destination)


def write_asset(tree: dict[str, Any], name: str, path: str) -> None:
    if not os.path.exists(path):
        os.makedirs(path)
    file_name = clean_file_name(name).replace(" ", "")
    base_name = file_name
    counter = 1

    if "Item" in path:
        while True:
            fp = os.path.join(path, f"{file_name}.json")
            if not os.path.exists(fp):
                break

            with open(fp, "rt", encoding="utf8") as f:
                existing_data = json.load(f)

            if (tree.get("displayName") == existing_data.get("displayName") and
                # tree.get("identifier") == existing_data.get("identifier") and
                tree.get("m_Name") == existing_data.get("m_Name") and
                tree.get("itemDescriptionName") == existing_data.get("itemDescriptionName")):
                return

            file_name = f"{base_name}_{counter}"
            counter += 1
    else:
        fp = os.path.join(path, f"{file_name}.json")
    with open(fp, "wt", encoding="utf8") as f:
        json.dump(tree, f, ensure_ascii=False, indent=4)


unpack_assets(args.assetpath, args.gameversion, args.lang)
