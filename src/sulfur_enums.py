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
        ("Gadget", 1),
        ("Head", 2),
        ("Torso", 3),
        ("Legs", 4),
        ("Feet", 5),
        ("Hands", 6),
        ("Weapon", 7),
        ("BasicMelee", 8),
        ("Amulet", 9),
        ("PassiveEnhancements", 10),
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

StatModType = Enum(
    "StatModType", [("Flat", 100), ("PercentAdd", 200), ("PercentMult", 300)]
)

BuffType = Enum("BuffType", [("Attribute", 0), ("Status", 1)])

# Units

UnitType = Enum(
    "UnitType", ("Melee", 1), ("Ranged", 2), ("Flying", 3), ("Boss", 4), ("Big", 0x10)
)

AgentRole = Enum("AgentRole", ("Offensive", 0), ("Defensive", 1))
