import json
from pathlib import Path
from functools import reduce
from typing import Any
from wiki import generate_wiki_table
from utils import format_number

weapon_types = {}
calibers = {}
weapons = {}

TEMP_DATA_DIR = r"C:\Users\clemf\code\devils-gold\unpacked\SULFUR_test"


def init_data(data_dir: str = TEMP_DATA_DIR) -> None:
    calibers_path = Path(data_dir).joinpath("Calibers")
    for path in calibers_path.rglob("*.json"):
        with path.open(encoding="utf-8") as source:
            caliber = json.load(source)
            calibers[caliber["label"]] = caliber
    weapon_types_path = Path(data_dir).joinpath("Weapon Types")
    for path in weapon_types_path.rglob("*.json"):
        with path.open(encoding="utf-8") as source:
            weapon_type = json.load(source)
            weapon_types[weapon_type["itemDescriptionName"]] = weapon_type
    weapons_path = Path(data_dir).joinpath("Items").joinpath("Weapons")
    for path in weapons_path.rglob("*.json"):
        with path.open(encoding="utf-8") as source:
            weapon = json.load(source)
            weapons[weapon["displayName"]] = weapon


def get_weapon_damage(weapon: str, caliber: str = None) -> float:
    weapon_def = weapons[weapon]
    weapon_type = weapon_types[weapon_def["weaponType"]]
    caliber_def = None
    if caliber:
        caliber_def = calibers[caliber]
    else:
        caliber_def = calibers[weapon_def["caliber"]]

    override_damage = weapon_def["overrideDamage"]
    if override_damage > float(0):
        return override_damage
    type_damage_mult = weapon_type["damageMultiplier"]
    weapon_damage_mult = weapon_def["damageMultiplier"]
    caliber_damage = caliber_def["baseDamage"]

    damage = caliber_damage * type_damage_mult * weapon_damage_mult

    return round(damage, 2)


def row_sort(row: list[Any]) -> int:
    return int(row[1])


def generate_caliber_table(weapon: str, data_dir: str = TEMP_DATA_DIR) -> None:
    columns = ["Caliber", "Damage", "Spread", "Projectiles"]
    row_data = []
    weapon_def = weapons[weapon]
    for name, caliber in calibers.items():
        if caliber["CanBeCaliberModded"]:
            damage = get_weapon_damage(weapon, name)
            spread_list = weapon_def["spreadPerCaliber"]
            spread = next((x for x in spread_list if x["Caliber"] == name))["Spread"]
            projectiles = caliber["numberOfProjectiles"]
            row = [name, format_number(damage), format_number(spread), projectiles]
            row_data.append(row)
    row_data.sort(key=row_sort)
    table = generate_wiki_table(columns, row_data)
    with_title = "== Caliber Modding ==\n" + table
    with open(Path(data_dir).joinpath("wiki.txt"), "w", encoding="utf-8") as source:
        source.write(with_title)


init_data()
generate_caliber_table("Vrede")
