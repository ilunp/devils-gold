import pathlib, json
from typing import Any

weapon_types = {}
calibers = {}
weapons = {}

TEMP_DATA_DIR = r"C:\Users\clemf\code\devils-gold\unpacked\SULFUR_test"


def init_data(data_dir: str = TEMP_DATA_DIR) -> None:
    calibers_path = pathlib.Path(data_dir).joinpath("Calibers")
    for path in calibers_path.rglob("*.json"):
        with path.open(encoding="utf-8") as source:
            caliber = json.load(source)
            calibers[caliber["label"]] = caliber
    weapon_types_path = pathlib.Path(data_dir).joinpath("Weapon Types")
    for path in weapon_types_path.rglob("*.json"):
        with path.open(encoding="utf-8") as source:
            weapon_type = json.load(source)
            weapon_types[weapon_type["label"]] = weapon_type
    weapons_path = pathlib.Path(data_dir).joinpath("Items").joinpath("Weapons")
    for path in weapons_path.rglob("*.json"):
        with path.open(encoding="utf-8") as source:
            weapon = json.load(source)
            weapons[weapon["displayName"]] = weapon


def get_weapon_damage(weapon: str, data_dir: str, caliber: str = None) -> float:
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

    print(damage)
    return damage


init_data()
get_weapon_damage("Mossman", "", "9mm")
