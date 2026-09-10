import os
import UnityPy
from UnityPy.classes import PPtr, MonoBehaviour, int2_storage
import argparse
import json
import re
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

asset_access: dict[int, MonoBehaviour] = {}

global_language: str
global_items: dict[int, MonoBehaviour] = {}
global_items_id: dict[int, str] = {}

global_item_attr: dict[int, MonoBehaviour] = {}
global_entity_attr: dict[int, MonoBehaviour] = {}
global_enchant_attr: dict[int, MonoBehaviour] = {}

global_calibers: dict[int, MonoBehaviour] = {}
global_usesResource: dict[int, MonoBehaviour] = {}

global_game_settings: MonoBehaviour | None = None
global_world_environment: dict[int, MonoBehaviour] = {}
global_loot_tables: dict[int, MonoBehaviour] = {}

global_factions: dict[int, MonoBehaviour] = {}
global_units: dict[int, MonoBehaviour] = {}
global_npcs: dict[int, MonoBehaviour] = {}
global_dialog: dict[int, MonoBehaviour] = {}

global_recipes: MonoBehaviour | None = None
global_recipes_id: dict[int, str] = {}
global_interacts: dict[int, MonoBehaviour] = {}
global_achievements: dict[int, MonoBehaviour] = {}
global_cards: dict[int, MonoBehaviour] = {}
global_quest_items: dict[int, MonoBehaviour] = {}


def unpack_assets(source: str, version: str, language: str) -> None:
    global global_language
    global global_game_settings
    global global_quest_items
    global global_recipes
    
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
            if data.m_Name in ["ItemDatabase", "EndlessCardRewardDatabase", "UnitDatabase", "RecipeDatabase", "EnchantmentDatabase"]:
                asset_access[pptr.path_id] = data

            if hasattr(data, "applyAttributeModifier"):
                item_attr_id = data.id
                if isinstance(item_attr_id, int):
                    global_item_attr[item_attr_id] = data
            if hasattr(data, "effectSettings"):
                entity_attr_id = data.id
                if isinstance(entity_attr_id, int):
                    global_entity_attr[entity_attr_id] = data
            if data.m_Name.startswith("EnchantmentDefinition_"):
                enchant_attr_id = data.id.value
                if isinstance(enchant_attr_id, int):
                    global_enchant_attr[enchant_attr_id] = data

            if hasattr(data, "entries") and "Demo" not in data.m_Name:
                global_loot_tables[pptr.path_id] = data
            if hasattr(data, "useType"):
                global_items[pptr.path_id] = data
                item_id = data.id.value
                if isinstance(item_id, int):
                    global_items_id[item_id] = data.m_Name
            if data.m_Name.startswith("Caliber_"):
                global_calibers[pptr.path_id] = data
                caliber_id = data.id
                if isinstance(caliber_id, int):
                    global_calibers[caliber_id] = data.label
            if data.m_Name.startswith("Resource_"):
                global_usesResource[pptr.path_id] = data
                resource_id = data.id
                if isinstance(resource_id, int):
                    global_usesResource[resource_id] = data.m_Name
            if data.m_Name == "GameSettings_EarlyAccess" or data.m_Name == "GameSettings_Full":
                global_game_settings = data
            if data.m_Name.startswith("WorldEnvironment_"):
                global_world_environment[pptr.path_id] = data
                env_id = getattr(data, "id", None).value if hasattr(getattr(data, "id", None), "value") else getattr(data, "id", None)
                if isinstance(env_id, int):
                    global_world_environment[env_id] = data
            if data.m_Name == "RecipeDatabase":
                global_recipes = data
                for recipe in data.recipes:
                    recipe_id = recipe.id.value
                    if isinstance(recipe_id, int):
                        global_recipes_id[recipe_id] = recipe.name
            if hasattr(data, "demonym"):
                global_factions[pptr.path_id] = data
                faction_id = getattr(data, "id", None).value if hasattr(getattr(data, "id", None), "value") else getattr(data, "id", None)
                if isinstance(faction_id, int):
                    global_factions[faction_id] = pptr.path_id
            if hasattr(data, "unitType"):
                global_units[pptr.path_id] = data
            # if hasattr(data, "meleeDamageType"):
            if hasattr(data, "damageTypeOverride"):
                global_npcs[pptr.path_id] = data
            if data.m_Name.startswith("Dialog_"):
                global_dialog[pptr.path_id] = data
            if data.m_Name.startswith("Achievement_"):
                global_achievements[pptr.path_id] = data
            if data.m_Name.startswith("Card_"):
                global_cards[pptr.path_id] = data
            if (data.m_Name.endswith("QuestItems") or 
                data.m_Name.endswith("QuestItemRewards")):
                global_quest_items[pptr.path_id] = data
            if hasattr(data, "interactableType"):
                global_interacts[pptr.path_id] = data

    print(
        f"Found: {len(global_items)} Items, \n"
        f"       {len(global_recipes.recipes)} Recipes, \n"
        f"       {len(global_item_attr)} Item Attributes, \n"
        f"       {len(global_loot_tables)} Loot tables, \n"
        f"       {len(global_world_environment)} World Environments, \n"
        f"       {len(global_factions) / 2} Factions, \n"
        f"       {len(global_units)} Units, \n"
        f"       {len(global_npcs)} NPCs, \n"
        f"       {len(global_dialog)} Dialogs, \n"
        f"       {len(global_achievements)} Achievements, \n"
        f"       {len(global_cards)} Cards, \n"
        f"       {len(global_quest_items)} Quest items, \n"
        f"       {len(global_interacts)} Interacts. \n"
    )

    print("Unpacking Asset Access...")
    aa_unpack_dir = os.path.join(unpack_dir, "Asset Access")
    for path_id, item in asset_access.items():
        process_basic(item, aa_unpack_dir)

    
    print("Unpacking Calibers...")
    caliber_unpack_dir = os.path.join(unpack_dir, "Calibers")
    for item in global_calibers.values():
        if isinstance(item, MonoBehaviour):
            process_basic(item, caliber_unpack_dir)

    print("Unpacking Resource...")
    resource_unpack_dir = os.path.join(unpack_dir, "Resources")
    for item in global_usesResource.values():
        if isinstance(item, MonoBehaviour):
            process_basic(item, resource_unpack_dir)

    print("Unpacking Items...")
    item_unpack_dir = os.path.join(unpack_dir, "Items")
    for path_id, item in global_items.items():
        process_item(item, path_id, item_unpack_dir)

    print("Unpacking Recipes...")
    recipe_unpack_dir = os.path.join(unpack_dir, "Recipes")
    process_recipe(global_recipes, recipe_unpack_dir)

    print("Generating Recipe List...")
    generate_recipe_list(unpack_dir, version)

    print("Unpacking Units...")
    unit_unpack_dir = os.path.join(unpack_dir, "Units")
    for item in global_units.values():
        process_unit(item, unit_unpack_dir)

    # print("Unpacking NPCs...")
    # npc_unpack_dir = os.path.join(unpack_dir, "NPCs")
    # for path_id, item in global_npcs.items():
    #     process_npc(item, npc_unpack_dir, path_id)

    # print("Unpacking Dialogs...")
    # dialog_sunpack_dir = os.path.join(unpack_dir, "Dialogs")
    # for item in global_dialog.values():
    #     process_dialog(item, dialog_sunpack_dir)

    print("Unpacking Loot Tables...")
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
    for item in global_cards.values():
        process_card(item, cards_unpack_dir)

    print("Unpacking Quest Items...")
    quest_unpack_dir = os.path.join(unpack_dir, "Quests")
    for item in global_quest_items.values():
        process_basic(item, quest_unpack_dir)

    # print("Unpacking Interacts...")
    # interact_unpack_dir = os.path.join(unpack_dir, "Interacts")
    # for path_id, interact in global_interacts.items():
    #     process_interact(interact, interact_unpack_dir, path_id)

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

def get_attribute_modifier(attributes: list[PPtr], is_item: bool = False) -> list[dict[str, Any]]:
    attribute_list = []

    for attr in attributes:
        attr_dict = process_asset(attr)

        if "attribute" in attr_dict:
            if is_item:
                attr_obj = global_item_attr.get(attr_dict["attribute"])
            else:
                attr_obj = global_entity_attr.get(attr_dict["attribute"])
        else:
                attr_obj = global_entity_attr.get(attr_dict["attributeId"])

        if attr_obj:
            attr_dict["attributeName"] = attr_obj.m_Name
            attr_dict["label"] = attr_obj.label
            attr_dict["itemDescriptionName"] = attr_obj.itemDescriptionName
            if is_item:
                # attr_dict["attributeName"] = get_translation(f"{attr_obj.m_Name}_label", global_language, "ItemAttributes/")
                attr_dict["showInItemDescription"] = attr_obj.showInItemDescription
            # else:
                # attr_dict["attributeName"] = get_translation(f"{attr_obj.m_Name}_label", global_language, "EntityAttributes/")
            
            attr_dict["isBooleanAttribute"] = attr_obj.isBooleanAttribute
            attr_dict["isPercentageAttribute"] = attr_obj.isPercentageAttribute
            
            if is_item and attr_obj.simplifiedModAmount == 1:
                attr_dict["simplifiedModAmount"] = attr_obj.simplifiedModAmount
                attr_dict["simplifiedIncreaseString"] = attr_obj.simplifiedIncreaseString
                attr_dict["simplifiedDecreaseString"] = attr_obj.simplifiedDecreaseString
            
            attribute_list.append(attr_dict)

    return attribute_list


def get_recipe_createsItem_name(name: str) -> str:
    for recipe in global_recipes.recipes:
            if recipe.name == name:
                creates_item_id = recipe.createsItem
                if hasattr(creates_item_id, 'value'):
                    creates_item_id = creates_item_id.value
                if creates_item_id in global_items_id:
                    creates_item_name = global_items_id[creates_item_id]
                    return creates_item_name
                    # return get_translation(creates_item_name, global_language)
    return name


def process_asset(asset: MonoBehaviour, is_card: bool = False) -> dict[str, Any]:
    global global_calibers
    global global_world_environment

    attr_list = [
        attr
        for attr in dir(asset)
        if not attr.startswith("_")
        and attr not in ["m_Enabled", "m_Script", "m_GameObject", "assets_file"]
    ]

    asset_dict = {}
    for attr in attr_list:
        try:
            value = getattr(asset, attr)
        except Exception:
            continue

        if hasattr(value, "value") and not isinstance(value, (PPtr, int2_storage)):
            if isinstance(value.value, (int, float, str, bool)):
                value = value.value

        if not isinstance(value, (int, float, str, PPtr, list, int2_storage, bool, dict)):
            continue

        if type(value) is PPtr:
            if value.path_id != 0:
                value = get_asset_name(value)
            else:
                value = None
        elif type(value) is int2_storage:
            value = {"x": value.x, "y": value.y}
        elif type(value) is list:
            # ItemAttribute 
            if attr == "baseAttributes" or attr == "modifiersOnAttachToItem" or attr == "valueChangeOnItemConsume" or attr == "modifiersApplied" or attr == "alternativeModAppliedOnWeapon":
                value = get_attribute_modifier(value, True)

            # EntityAttribute
            elif attr == "buffsOnConsume" or attr == "modifiersOnEquipNew" or attr == "buffsToApply" or attr == "permanentModifiers" or attr == "alternativeModAppliedOnOwner" or attr == "alternativeModOnHit":
                value = get_attribute_modifier(value)
            elif attr == "recipesTaughtOnConsume":
                recipe_list = []
                for recipe in value:
                    recipe_id = recipe.value
                    recipe_list.append(global_recipes_id.get(recipe_id))
                value = recipe_list
            elif attr == "removeStatusOnConsume":
                status_list = []
                for status in value:
                    # print(global_entity_attr.get(status))
                    if status:
                        status_list.append(global_entity_attr.get(status).m_Name)
                value = status_list
            
            elif attr == "addStatusOnConsume":
                status_list = []
                for status_item in value:
                    status_dict = process_asset(status_item)
                    status_id = status_dict.get("status")
                    if status_id:
                        status_obj = global_entity_attr.get(status_id)
                        if status_obj:
                            status_dict["statusName"] = status_obj.m_Name
                    status_list.append(status_dict)
                value = status_list
            elif attr == "friendlyIds" or attr == "neutralIds":
                faction_list = []
                for faction_id in value:
                    if faction_id:
                        faction_obj = global_factions.get(global_factions.get(faction_id))
                        faction_list.append(str(faction_obj.m_Name))
                value = faction_list
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
                        if attr == "environmentsToAnnounce":
                            env_obj = global_world_environment.get(item)
                            env_name = env_obj.m_Name if env_obj else str(item)
                            # print(f"Environment ID {item} maps to {env_name}")
                            new_item = env_name
                        else:
                            new_item = process_asset(item)
                    new_list.append(new_item)
                value = new_list
        # elif attr == "displayName" and "identifier" in attr_list:
        elif attr == "displayName" and "m_Name" in attr_list:
            # value = get_translation(asset.identifier, global_language)
            if is_card:
                value = get_translation(f"{asset.m_Name}_Title", global_language, "Endless/")
            elif asset.m_Name.startswith("Manual_Recipe"):
                value = get_translation("Manual_RecipeDynamic", global_language)
                if hasattr(asset, "recipesTaughtOnConsume") and asset.recipesTaughtOnConsume:
                    recipe_name = global_recipes_id.get(asset.recipesTaughtOnConsume[0].value)
                    if recipe_name:
                        createsItem = get_recipe_createsItem_name(recipe_name)
                        if createsItem:
                            value = value.replace("X_ITEM", get_translation(createsItem, global_language))

            else:
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
            elif is_card:
                value = get_translation(f"{asset.m_Name}_Description", global_language, "Endless/")
            elif asset.m_Name.startswith("Manual_"):
                value = get_translation("DynamicString_TeachesRecipes", global_language, "ItemDescriptions/")
                if value:
                    value = value.replace("AMOUNT_X", str(len(asset.recipesTaughtOnConsume)))
                else:
                    value = ""
        elif attr == "caliber" or attr == "Caliber" or attr == "modifiesCaliber":
            value = global_calibers.get(value)
        elif attr == "usesResource" or attr == "resource":
            value = global_usesResource.get(value) 
            # value = usesResource(value).name
        elif attr == "itemType":
            value = ItemType(value).name
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
        elif attr == "damageType":
            value = DamageType(value).name
        elif attr == "itemQuality":
            value = ItemQuality(value).name
        elif attr == "weaponType":
            value = WeaponType(value).name
        elif attr == "appliesEnchantment":
            enchant_obj = global_enchant_attr.get(value)
            value = process_asset(enchant_obj)

        asset_dict[attr] = value

    if hasattr(asset, 'm_Name') and asset.m_Name.startswith("Manual_Recipe") and hasattr(asset, "recipesTaughtOnConsume") and asset.recipesTaughtOnConsume:
        recipe_name = global_recipes_id.get(asset.recipesTaughtOnConsume[0].value)
        if recipe_name:
            createsItem = get_recipe_createsItem_name(recipe_name)
            if createsItem:
                asset_dict["taughtRecipeProduct"] = createsItem

    return asset_dict


def process_item(asset: MonoBehaviour, path_id: int, destination_folder: str) -> None:
    global asset_name_map
    global global_language
    final_destination = destination_folder
    name = ""
    tree: dict[str, Any] = {}
    final_destination = get_item_type_dir(asset, destination_folder)
    tree = process_asset(asset)
    # name = get_translation(asset.identifier, global_language)
    # name = get_translation(asset.m_Name, global_language)
    name = tree.get("displayName", "")
    if not name:
        name = get_translation(asset.m_Name, global_language)
    asset_name_map[path_id] = name
    
    write_asset(tree, name, final_destination)


def get_unique_recipe_name(recipe: dict[str, Any]) -> str:
    """
    This hack fixes some issues:
    There are some duplicate recipes (e.g. Poutine)
    There are some recipes with wrong names (e.g. Throwing Knife)
    Allows for crude sorting by quantity
    """

    item_id = recipe["createsItem"]
    item_name = get_translation(global_items_id[item_id], global_language)
    quantity = recipe["quantityCreated"]
    new_dict = dict(recipe)
    # del new_dict["m_Name"]
    recipe_str = json.dumps(new_dict, ensure_ascii=False)
    unique_name = f"{item_name}_{quantity}_{create_uuid_from_string(recipe_str)}"
    return unique_name


def process_recipe(asset: MonoBehaviour, destination_folder: str) -> None:
    final_destination = destination_folder
    name = ""
    tree: dict[str, Any] = {}
   
    if getattr(asset, "recipes", None):
        tree = process_asset(asset)
        for recipe in tree["recipes"]:
            # print(recipe["itemsNeeded"])

            final_destination = os.path.join(destination_folder, str(CraftingType(recipe["type"]).name))
            name = get_unique_recipe_name(recipe)
            if "type" in recipe:
                recipe["type"] = CraftingType(recipe["type"]).name
            if "createsItem" in recipe:
                createsItem_id = recipe["createsItem"]
                recipe["createsItem"] = get_translation(global_items_id[createsItem_id], global_language)
            if "itemsNeeded" in recipe:
                for item in recipe["itemsNeeded"]:
                    if "item" in item:
                        needitem_id = item["item"]
                        if isinstance(needitem_id, int) and needitem_id in global_items_id:
                            item["item"] = get_translation(global_items_id[needitem_id], global_language)

            write_asset(recipe, name, final_destination)
    else:
        # Don't write uncraftable recipes
        return
    


def process_game_settings(asset: MonoBehaviour, destination_folder: str) -> None:
    global global_world_environment

    processed_settings = process_asset(asset)
    # print(f"{processed_settings}")
    write_asset(processed_settings, asset.m_Name, destination_folder)

    loot_settings_obj = asset.LootSettings.deref_parse_as_object()
    processed_loot_settings = process_asset(loot_settings_obj)
    write_asset(processed_loot_settings, loot_settings_obj.m_Name, destination_folder)
    
    for act in asset.Acts:
        act_obj = act.deref_parse_as_object()

        processed_act = process_asset(act_obj)
        act_dir = os.path.join(destination_folder, act_obj.actName)
        write_asset(processed_act, act_obj.actName, act_dir)
        
        for index, env_id in enumerate(act_obj.environments):
            # WorldEnvironment_
            environment_obj = global_world_environment.get(env_id)
            if environment_obj:
                processed_env = process_asset(environment_obj)
                level_dir = os.path.join(
                    act_dir, f"{index + 1}_{environment_obj.m_Name}"
                )
                write_asset(processed_env, environment_obj.m_Name, level_dir)
                for level in environment_obj.levels:
                    level_obj = level.deref_parse_as_object()
                    processed_level = process_asset(level_obj)
                    write_asset(processed_level, level_obj.m_Name, level_dir)
            else:
                print(f"Warning: Environment ID {env_id} not found in global_world_environment")

def process_achievement(asset: MonoBehaviour, destination_folder: str) -> None:
    final_destination = destination_folder
    
    processed_asset = process_asset(asset)
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
    try:
        # print(f"Processed NPC Asset: {processed_asset['unitSO']}")
        name = f"{processed_asset['unitSO']}_{path_id}"
        write_asset(processed_asset, name, destination_folder)
    except Exception as e:
        print(f"Error processing NPC Asset with path ID {path_id}: {e}")

def process_dialog(asset: MonoBehaviour, destination_folder: str) -> None:
    dialog_data = process_asset(asset)

    serialized_graph = getattr(asset, "_serializedGraph", None)
    if serialized_graph:
        try:
            serialized_graph = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", serialized_graph)

            dialog_data["_serializedGraph"] = json.loads(serialized_graph, strict=False)

        except Exception as e:
            print(f"Failed parsing dialog {asset.m_Name}: {e}")

            dialog_data["_serializedGraph"] = serialized_graph

    actor_parameters = getattr(asset, "actorParameters", None)
    if actor_parameters:
        dialog_data["actorParameters"] = []
        for actor in actor_parameters:
            actor_dict = {}

            for key in ["_keyName", "_id", "_actorObject"]:
                if hasattr(actor, key):
                    value = getattr(actor, key)

                    if isinstance(value, PPtr):
                        if value.path_id != 0:
                            value = get_asset_name(value)
                        else:
                            value = None

                    elif hasattr(value, "value"):
                        value = value.value

                    actor_dict[key] = value

            dialog_data["actorParameters"].append(actor_dict)

    write_asset(dialog_data, asset.m_Name, destination_folder)

def process_character_base_attr(attrib: MonoBehaviour) -> AttributeContainerNew:
    # attrib_type = attrib.type.deref_parse_as_dict()["itemDescriptionName"]
    attrib_type = attrib.type
    # attrib_type_label = f"{attrib.type.deref_parse_as_dict()["m_Name"]}_label"
    attrib_type_label = f"{EntityAttributes(attrib.type).name}_label"
    # get_attrib_type_label = get_translation(attrib_type_label, global_language, "EntityAttributes/")
    get_attrib_type_label = get_translation(attrib_type_label, global_language, "EntityAttributes/")
    result: AttributeContainerNew = {}
    if get_attrib_type_label == attrib_type_label:
        result["type"] = EntityAttributes(attrib.type).name
    else:
    #     result["type"] = get_translation(f"{attrib.type.deref_parse_as_dict()["m_Name"]}_label", global_language, "EntityAttributes/")
        result["type"] = get_attrib_type_label
    result["value"] = attrib.value
    return result


def process_unit(asset: MonoBehaviour, destination_folder: str) -> None:
    asset_dict: Unit = {}

    m_name_value = getattr(asset, "m_Name", None)
    for key, type in Unit.__annotations__.items():
        value = getattr(asset, key)
        if key == "id":
            value = value.value
        elif key == "displayName":
            if m_name_value:
                value = get_translation(m_name_value, global_language, "UnitNames/")
            else:
                value = get_translation(value, global_language, "UnitNames/")
        elif key == "artworkRef":
            value = value.m_SubObjectName
            # if value.path_id == 0:
            #     value = None
            # else:
                # value = value.deref_parse_as_dict()["m_SubObjectName"]
        elif key == "unitType":
            try:
                value = UnitType(value).name
            except ValueError:
                value = str(value)

        # elif key == "faction":
        #     if value.path_id == 0:
        #         value = None
        #     else:
        #         process_faction(value, destination_folder)
        #         value = value.deref_parse_as_dict()["prettyLabel"]
        elif key == "factionId":
            value_path = global_factions.get(value)
            process_faction(global_factions.get(value_path), destination_folder)
            value = global_factions.get(value_path).m_Name

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

    final_destination = os.path.join(destination_folder, str(asset_dict["factionId"]))
    write_asset(asset_dict, asset_dict["displayName"], final_destination)

def process_faction(asset: MonoBehaviour, destination_folder: str) -> None:
    processed_asset = process_asset(asset)
    name = f"_{processed_asset['m_Name']}"
    final_destination = os.path.join(destination_folder, str(processed_asset['m_Name']))
    write_asset(processed_asset, name, final_destination)


def write_asset(tree: dict[str, Any], name: str, path: str) -> None:
    if not os.path.exists(path):
        os.makedirs(path)
    file_name = clean_file_name(name).replace(" ", "")
    base_name = file_name
    counter = 1

    while True:
        fp = os.path.join(path, f"{file_name}.json")
        if not os.path.exists(fp):
            break

        with open(fp, "rt", encoding="utf8") as f:
            existing_data = json.load(f)

        if tree == existing_data:
            return

        file_name = f"{base_name}_{counter}"
        counter += 1
    
    with open(fp, "wt", encoding="utf8") as f:
        json.dump(tree, f, ensure_ascii=False, indent=4)


unpack_assets(args.assetpath, args.gameversion, args.lang)
