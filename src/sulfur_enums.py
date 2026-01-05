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

AgentRole = Enum("AgentRole", [("Offensive", 0), ("Defensive", 1)])

ProjectileTypes = Enum(
    "ProjectileTypes",
    [("None", 0),("Bullet", 1),("Arrow", 2),("Laser", 3),("Snowball", 4),("End", 5)]
)
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      
EntityAttributes = Enum(
    "EntityAttributes", 
    [("None",0),("ExtraDamage_AssaultRifle",1),("ExtraDamage_Automatic",2),("ExtraDamage_Earth",3),("ExtraDamage_Electric",4),("ExtraDamage_Fire",5),("ExtraDamage_Frost",6),("ExtraDamage_Holy",7),("ExtraDamage_LMG",8),("ExtraDamage_Melee",9),("ExtraDamage_Pistol",10),("ExtraDamage_Poison",11),("ExtraDamage_Revolver",12),("ExtraDamage_Rifle",13),("ExtraDamage_Shadow",14),("ExtraDamage_Shotgun",15),("ExtraDamage_SMG",16),("ExtraDamage_Sniper",17),("NegativeEffect_Blinded",18),("NegativeEffect_Burning",19),("NegativeEffect_Charmed",20),("NegativeEffect_Crusader",21),("NegativeEffect_Electrocuted",22),("NegativeEffect_Feared",23),("NegativeEffect_Flashed",24),("NegativeEffect_Frozen",25),("NegativeEffect_Oily",26),("NegativeEffect_Petrified",27),("NegativeEffect_Poisoned",28),("NegativeEffect_Rooted",29),("NegativeEffect_Stunned",30),("NegativeEffect_Suffocating",31),("NegativeEffect_Voodoo",32),("NegativeEffect_Wet",33),("Resistance_Armor",34),("Resistance_Charm",35),("Resistance_Earth",36),("Resistance_Electric",37),("Resistance_Explosive",38),("Resistance_Fire",39),("Resistance_Frost",40),("Resistance_Holy",41),("Resistance_Poison",42),("Resistance_Punish",43),("Resistance_Shadow",44),("Stat_AimMovingBonus",45),("Stat_Blindfolded",46),("Stat_Charisma",47),("Stat_CoyoteTime",48),("Stat_CritChance",49),("Stat_CritChanceADS",50),("Stat_CrouchSlide",51),("Stat_DetectionDistance",52),("Stat_ExtraJumps",53),("Stat_HealthRegen",54),("Stat_JumpDuration",55),("Stat_JumpPower",56),("Stat_Lifesteal",57),("Stat_LuckGain",58),("Stat_LungCapacity",59),("Stat_MaxHealth",60),("Stat_MeleeDamage",61),("Stat_MovementSpeed",62),("Stat_Mutation_Big",63),("Stat_Mutation_Blink",64),("Stat_Mutation_Bomb",65),("Stat_Mutation_Fire",66),("Stat_Mutation_Fire_Ranged",67),("Stat_Mutation_Frost",68),("Stat_Mutation_Frost_Ranged",69),("Stat_Mutation_FrostTrail",70),("Stat_Mutation_Lava",71),("Stat_Mutation_Lightning",72),("Stat_Mutation_Monstrosity",73),("Stat_Mutation_Noxiosa",74),("Stat_Mutation_Poison",75),("Stat_Mutation_Poison_Ranged",76),("Stat_Mutation_PoisonNova",77),("Stat_Mutation_Shapeshifter",78),("Stat_Mutation_Shock",79),("Stat_Mutation_Small",80),("Stat_Mutation_Surge",81),("Stat_Mutation_Surge_Ranged",82),("Stat_Oxygen",83),("Stat_SlowMotion",84),("Stat_SpringyShoes",85),("Stat_SprintBonus",86),("Stat_SwimSpeed",87),("Stat_WeaponWeightPenalty",88),("Stat_WearingEarPro",89),("Stat_WearingShades",90),("Status_AirInLungs",91),("Status_CurrentHealth",92),("Status_Invisible",93),("Status_Luck",94),("Status_WearingGoggles",95),("Status_WearingStraitJacket",96),("Status_Buoyant",97),("Stat_WearingRudolfNose",98),("NegativeEffect_ChainLightning",99),("NegativeEffect_Charmed_Player",100),("Resistance_Petrified",101),("NegativeEffect_Bleed",102),("Resistance_Bleed",103),("Stat_BonusXP",104),("Stat_CrouchSpeed",105),("Stat_JumpShotDamage",106),("Status_OneInTheChamber",107),("Status_SpawnFriendOnLevelLoad",108),("Status_1HPSurvivial",109),("Stat_MovementSpeedBoostAfterEating",110),("Stat_DefaultTimeScale",111),("Status_NoNormalItemDrops",112),("Status_UnhealableDamage",113),("NegativeEffect_Knockback",114),("Stat_GlobalDamageMultiplier",115),("Stat_Thorns",116),("End",117)]
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