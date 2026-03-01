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
        ("Quest", 11),
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

WeaponType = Enum(
    "WeaponType",
    [
        ("None", 0),
        ("AssaultRifle", 1),
        ("Bow", 2),
        ("LMG", 3),
        ("Melee", 4),
        ("Pistol", 5),
        ("Revolver", 6),
        ("Rifle", 7),
        ("Shotgun", 8),
        ("SMG", 9),
        ("Sniper", 10),
        ("Throwable", 11),
    ],
)

DamageType = Enum(
    "DamageType",
    [
        ("None", 0),
        ("Critical", 1),
        ("Electric", 2),
        ("Explosive", 3),
        ("Fire", 4),
        ("Frost", 5),
        ("Holy", 6),
        ("Normal", 7),
        ("Physics", 8),
        ("Poison", 9),
        ("Punish", 10),
        ("Shadow", 11),
        ("Suffocate", 12),
        ("Water", 13),
        ("Sacrifice", 14),
        ("Dark", 15),
        ("Bleed", 16),
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
    [
        ("Common", 0), 
        ("Uncommon", 1), 
        ("Rare", 2), 
        ("Epic", 3), 
        ("Legendary", 4)
    ],
)

StatModType = Enum(
    "StatModType", [("NONE", 0),("Flat", 100), ("PercentAdd", 200), ("PercentMult", 300)]
)

BuffType = Enum("BuffType", [("Attribute", 0), ("Status", 1)])

# Cards
CardBuffType = Enum("CardBuffType", [("None", 0), ("IncreaseXPRange", 1), ("IncreaseXPAmount", 2), ("IncreaseAmmoGain", 3), ("MeleeXPBonus_UNUSED", 4), ("ExistingBuff", 5), ("PermanentModifier", 6)])

CardType = Enum("CardType", [("ItemSpawn", 0), ("EntitySpawn", 1), ("Buff", 2), ("Event", 3)])

CardLayout = Enum("CardLayout", [("Normal", 0), ("Side", 1), ("Center", 2)])

CardRewardType = Enum("CardRewardType", [("None", 0), ("SpawnFromLootTable", 1), ("SpawnSpecificItem_UNUSED", 2), ("SpawnPrefab_UNUSED", 3), ("SpawnInteractable", 4), ("SpawnRandomAllies", 5), ("ApplyBuff", 6), ("TriggerEvent", 7), ("SpawnNPC", 8), ("GiveResource", 9)])

CardEventType = Enum("CardEventType", [("None", 0), ("ExplosiveBarrels", 1), ("EnemiesDropFood_UNUSED", 2), ("TravelBackToChurch", 3), ("PassForStamps", 4), ("Reroll", 5), ("RepairAll", 6), ("InfiniteAmmo", 7), ("Indestructible", 8), ("Bonanza", 9), ("MeleeXPBonus", 10)])

# Units
UnitType = Enum("UnitType", [("Melee", 1), ("Ranged", 2), ("Flying", 4), ("Boss", 8), ("Big", 16), ("Swimmer", 32)])

FactionIds = Enum(
    "FactionIds",
    [
        ("None", 0),
        ("Bar", 1),
        ("BlackGuild", 2),
        ("BlackGuildMaskless", 3),
        ("Condemned", 4),
        ("Congregation", 5),
        ("Corrupted", 6),
        ("Crones", 7),
        ("DHell", 8),
        ("Gaia", 9),
        ("Ghosts", 10),
        ("Goblins", 11),
        ("Haradrians", 12),
        ("Haukland", 13),
        ("Hellshrews", 14),
        ("LuciaFaction", 15),
        ("Player", 16),
        ("RexPopuli", 17),
        ("ShantyCiv", 18),
        ("ShavWa", 19),
        ("SkripsSkrap", 20),
        ("TheCraw", 21),
        ("WitchFaction", 22),
    ]
)

AgentRole = Enum("AgentRole", [("Offensive", 0), ("Defensive", 1)])

ProjectileTypes = Enum(
    "ProjectileTypes",
    [("None", 0),("Bullet", 1),("Arrow", 2),("Laser", 3),("Snowball", 4),("End", 5)]
)

MutationDefinitions = Enum(
    "MutationDefinitions", 
    [("None", 0), ("Mutation_Big", 1), ("Mutation_Bomb", 2), ("Mutation_Fire", 3), ("Mutation_Frost", 4), ("Mutation_FrostTrail", 5), ("Mutation_Lava", 6), ("Mutation_Monstrosity", 7), ("Mutation_Poison", 8), ("Mutation_PoisonTrail", 9), ("Mutation_NoxiosaCloud", 10), ("Mutation_Shapeshifter", 11), ("Mutation_Shock", 12), ("Mutation_Small", 13), ("Mutation_Surge", 14), ("Mutation_Blink", 15), ("Mutation_Charming", 16), ("Mutation_Crypt", 17), ("End", 18)]
)

InteractableType = Enum(
    "InteractableType", 
    [("Dialog", 0), ("Shop", 1), ("Repair", 2), ("Enchant", 3), ("Cook", 4), ("Interact", 5), ("LockedDoor", 6), ("Dice", 7), ("Cleanse", 8), ("Quest", 9)]
)

CraftingType = Enum(
    "CraftingType",
    [("Generic", 0), ("Cooking", 1), ("Enchantments", 2)]
)

