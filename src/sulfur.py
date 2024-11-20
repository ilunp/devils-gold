from enum import Enum

UseType = Enum(
    "UseType",
    [
        ("Consumable", 0),
        ("Equippable", 1),
        ("Attachment", 2),
        ("Enchantment", 3),
        ("None", 4),
        ("ItemConsumable", 5),
        ("ItemRepair", 6),
        ("Key", 7),
        ("Storage", 8),
    ],
)

ItemType = Enum(
    "ItemType",
    [
        ("Misc", 0),
        ("Armor", 1),
        ("Weapon", 2),
        ("Consumable", 3),
        ("Gadget", 4),
        ("Attachment", 5),
        ("Enchantment", 6),
        ("Ammo", 7),
        ("Scavenge", 8),
        ("EnchantmentOil", 9),
        ("Valuable", 10),
    ],
)

SlotType = Enum(
    "SlotType",
    [
        ("None", 0),
        ("Head", 1),
        ("Torso", 2),
        ("Legs", 3),
        ("Feet", 4),
        ("Hands", 5),
        ("Weapon", 6),
        ("BasicMelee", 7),
        ("Amulet", 8),
        ("PassiveEnhancements", 9),
    ],
)

HoldableWeightClass = Enum(
    "HoldableWeightClass",
    [
        ("Knife", 0),
        ("Pistol", 1),
        ("SMG", 2),
        ("Rifle", 3),
        ("Sniper", 4),
        ("Bigga", 5),
    ],
)

ItemQuality = Enum(
    "ItemQuality",
    [("Common", 0), ("Uncommon", 1), ("Rare", 2), ("Epic", 3), ("Legendary", 4)],
)
