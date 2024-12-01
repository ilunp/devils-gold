from typing import TypedDict
from sulfur_enums import UnitType


class AttributeContainerNew(TypedDict):
    type: str  # EntityAttributeType.itemDescriptionName
    value: float


class Faction(TypedDict):
    # Data
    identifier: str
    # Lore
    prettyLabel: str
    adjective: str
    demonym: str
    showLabelOnUnits: bool
    # Alliances
    friendly: list[str]  # Faction.prettyLabel
    neutral: list[str]  # Faction.prettyLabel
    hostiles: list[str]  # Faction.prettyLabel
    # Generic Faction Loot
    lootTableUnits: str  # LootTable.m_Name
    lootTableScavenge: str  # LootTable.m_Name


class Unit(TypedDict):
    # File
    identifier: str
    excludeFromLocalization: bool
    # Lore
    displayName: str
    description: str
    # Unit Settings
    canBeDeactivated: bool
    unitType: str  # enum UnitType.name
    isCivilian: bool
    isProtectedNpc: bool
    disableMutations: bool
    canPanic: bool
    canRecieveKnockback: bool
    retreatWhileAttackCooldown: bool
    randomizeHealth: float  # Range 0f-1f
    shouldDropLoot: bool
    experienceOnKill: int
    spawnCost: int
    scanFrequency: int
    diceRollBonus: int  # Range 0f-20f
    alwaysKnowsPlayerPosition: bool
    invisibleBeforeAggro: bool
    firstShotMissingByPurpose: bool
    faction: str  # Faction.prettyLabel
    rolesAvailable: list[str]  # enum AgentRole.name
    characterBaseAttributesNew: list[AttributeContainerNew]
