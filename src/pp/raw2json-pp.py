import os
import json
import csv

# 定义常量
BLOCKED_ATTRIBUTES = []
ATTRIBUTE_MAPPING = {
    # 卡牌数值奖励映射 (从 CardBuffType 映射到翻译 Key)
    "IncreaseXPRange": "PickUpRadius",
    "IncreaseXPAmount": "XPGain",
    "IncreaseAmmoGain": "AmmoGain",
    
    # 资源奖励映射
    "GiveResource": "ResourceAmount",
}

DISPLAYNAME_MAPPING = {
    "Enchantment_OverdoseOil": "超量油",
    "Item_Marshmallow": "棉花糖（串）",
    "Item_EyePatch": "独眼罩"
}

ITEMTYPE_MAPPING = {
    "PassiveEnhancements": "饰品"
}

# 全局变量
translations_path = "./translations.csv"
languages = {
    "en": "English [en]",
    "zh-CN": "Chinese (Simplified) [zh-CN]"
}
# --- 辅助函数 ---
def get_translation(name: str, lang: str = "zh-CN", prefix: str = "Items/") -> str:
    if not os.path.exists(translations_path): return name
    column = languages[lang]
    try:
        with open(translations_path, encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            fullName = prefix + name
            for row in reader:
                if row.get("20") == fullName:
                    new_name = row[column]
                    if not new_name:
                        return row[languages["en"]]
                    return new_name
            return name
    except: return name

def format_value(value, mod_type, isBoolean, isPercentage):
    if isBoolean: return ""
    if mod_type in ["Flat", 100]:
        if isPercentage:
            return f"+{int(round(value * 100))}%" if value >= 0 else f"{int(round(value * 100))}%"
        return f"+{round(value, 2)}" if value >= 0 else f"{round(value, 2)}"
    elif mod_type in ["PercentAdd", 200]:
        return f"(+) +{round(value * 100)}%" if value >= 0 else f"(+) {round(value * 100)}%"
    elif mod_type in ["PercentMult", 300]:
        return f"(×) +{round(value * 100)}%" if value >= 0 else f"(×) {round(value * 100)}%"
    return f"+{round(value, 2)}"

def map_effects(modifiers, ATTRIBUTE_MAPPING, BLOCKED_ATTRIBUTES, remove_status_on_consume, is_enchantment=False):
    effects = {}
    if isinstance(modifiers, dict):
        if modifiers.get("CostsDurability", 1) == 0:
            effects["不会额外损失耐久度"] = ""
        modifiers = modifiers.get("modifiersApplied", [])

    for modifier in modifiers:
        if is_enchantment and modifier.get("showInItemDescription", 1) == 0:
            continue
            
        raw_attr = modifier.get("localizationName") or modifier.get("attributeName") or str(modifier.get("attribute", ""))
        mod_type = modifier.get("modType") or modifier.get("statModType", "")
        value = modifier.get("value", 0)
        duration = modifier.get("duration", 0)
        total_override = modifier.get("totalValueOverride", 0)
        is_bool = modifier.get("isBooleanAttribute", 0)
        is_perc = modifier.get("isPercentageAttribute", 0)
        is_simplified = modifier.get("simplifiedModAmount", 0)

        attr_key = f"{raw_attr}_{'simplifiedIncrease' if value > 0 else 'simplifiedDecrease'}" if is_simplified else f"{raw_attr}_itemDescription"

        # 1. Define the search path for your translations
        namespaces = ["EntityAttributes/", "ItemAttributes/"]
        mapped_attr = attr_key

        # 2. Iterate through namespaces until a translation is found
        for ns in namespaces:
            translation = get_translation(attr_key, "zh-CN", ns)
            if translation != attr_key:
                mapped_attr = translation
                break
        else:
            # 3. Final fallback to the hardcoded mapping if no translation was found
            mapped_attr = ATTRIBUTE_MAPPING.get(raw_attr, get_translation(raw_attr, "zh-CN", "EntityAttributes/"))
        
        if raw_attr in BLOCKED_ATTRIBUTES:
            continue

        if is_bool:
            effects[mapped_attr] = True
            continue

        if "HealthRegen" in raw_attr or raw_attr == "Health regen":
            final_hp = total_override if total_override != 0 else int(value * duration)
            effects["生命恢复"] = f"{int(final_hp)} HP ({duration}秒)"
        elif duration:
            if total_override != 0:
                display_val = f"{int(total_override)}" 
            else:
                if value > 1 and not is_perc:
                    display_val = f"+{round(value)}"
                else:
                    display_val = f"{int(round(value * 100))}%"
            effects[mapped_attr] = f"{display_val} ({duration}秒)"
        else:
            effects[mapped_attr] = f"+{int(value)}" if raw_attr == "Durability" else format_value(value, mod_type, is_bool, is_perc)

    if remove_status_on_consume:
        for status in remove_status_on_consume:
            # print(status)
            effects[f"移除{get_translation(f"{status}_label", 'zh-CN', 'EntityAttributes/')}"] = ""
    return effects

def calc_damage(damageMultiplier, caliber, weapon_Type):
    caliber_damage = {"12ga": 20, "Laser": 50, "9mm": 60, "5.56mm": 80, "7.62mm": 100, "50 BMG": 200, "Arrow": 50}
    weapon_Type_damage = {"Pistol": 1, "Revolver": 1.6, "Shotgun": 1, "SMG": 1, "LMG": 1, "Rifle": 2, "AssaultRifle": 1.2, "Sniper": 2}
    demage = caliber_damage.get(caliber, 0) * weapon_Type_damage.get(weapon_Type, 1) * damageMultiplier
    return demage

# def card_effect():


# --- 主逻辑 ---
def convert_to_target_format(input_folder, output_file, folder_type, is_card=False):
    result = {}
    if not os.path.exists(input_folder): return

    for filename in os.listdir(input_folder):
        if filename.endswith(".json"):
            try:
                with open(os.path.join(input_folder, filename), "r", encoding="utf-8") as f:
                    content = json.load(f)
                    identifier = content.get("m_Name", "")

                    display_name = DISPLAYNAME_MAPPING.get(identifier,  get_translation(identifier, "zh-CN", "Items/"))
                    if display_name == identifier:
                        display_name = content.get("displayName", identifier)
                    
                    english_name = get_translation(identifier, "en", "Items/")
                    if english_name == identifier:
                        english_name = get_translation(f"{identifier}_Title", "en", "Endless/")

                    res_item = {}

                    res_item["ID"] = content.get("id", 0)

                    res_item["Name"] = {"ZH": display_name, "EN": english_name}

                    desc = get_translation(identifier, "zh-CN", "ItemDescriptions/") if content.get("hasCustomDescription", 0) else content.get("description", "")
                    
                    if is_card:
                        amount_value = ""
                        # Card Type 
                        rewardType = content.get("rewardType", "")
                        buffType = content.get("buffType", "")
                        cardType = content.get("cardType", "")
                        eventType = content.get("eventType", "")

                        buffAmount = content.get("buffAmount", 0)
                        spawnCount = content.get("spawnCount", 0)
                        resourceAmount = content.get("resourceAmount", 0)
                        if rewardType == "SpawnFromLootTable":
                            amount_value = int(spawnCount)

                        # elif rewardType == "GiveResource":
                            # amount_value = round(resourceAmount * 1)

                        elif rewardType == "SpawnRandomAllies" or rewardType == "SpawnNPC":
                            amount_value = int(spawnCount)
                        
                        # elif rewardType == "SpawnInteractable":
                        else:
                            if rewardType == "ApplyBuff":
                                
                                if buffType == "ExistingBuff" and len(content.get("buffsToApply", [])) > 0:
                                    if content.get("buffsToApply", [])[0].get("isPercentageAttribute", 0):
                                        amount_value = f"+{int(content.get("buffsToApply", [])[0].get("value") * 100)}%"
                                    else:
                                        amount_value = f"+{content.get("buffsToApply", [])[0].get("value")}"

                                elif buffType == "PermanentModifier" and len(content.get("permanentModifiers", [])) > 0:
                                    if content.get("permanentModifiers", [])[0].get("isPercentageAttribute", 0):
                                        amount_value = f"+{int(content.get("permanentModifiers", [])[0].get("value") * 100)}%"
                                    else:
                                        amount_value = f"+{content.get("permanentModifiers", [])[0].get("value")}"
                                
                                elif buffType == "IncreaseXPAmount" or buffType == "IncreaseAmmoGain":
                                    amount_value = f"+{int((buffAmount) * 100)}%"
                                else:
                                    amount_value = f"+{buffAmount}"
                            
                            elif rewardType == "GiveResource":
                                amount_value = round(resourceAmount * 1)

                            elif rewardType != "SpawnInteractable":
                                if rewardType == "TriggerEvent":
                                    if eventType == "InfiniteAmmo" or eventType == "Indestructible":
                                        amount_value = int(3)
                                else:
                                    amount_value = int(spawnCount)

                    res_item["Desc"] = desc.replace("+", "").replace("AMOUNT_X", str(amount_value)) if is_card else desc

                    if content.get("flavor"): res_item["Flav"] = content.get("flavor", "")

                    if content.get("customArtwork"): res_item["Artwork"] = content.get("customArtwork", "")

                    if content.get("itemQuality"): res_item["Quality"] = content.get("itemQuality", "")

                    # --- Type 核心处理逻辑 ---
                    if folder_type == "Weapons":
                        w_type = content.get("weaponType", "")
                        res_item["Type"] = get_translation(f"WeaponType_{w_type}", "zh-CN", "ItemDescriptions/")
                    elif folder_type == "Consumables":
                        if content.get("recipesTaughtOnConsume"): res_item["Type"] = "食谱"
                        elif content.get("currencyOnConsume"): res_item["Type"] = "货币"
                        elif content.get("resourceOnConsume"): res_item["Type"] = "资源"
                        else: res_item["Type"] = "消耗品"
                    else:
                        slot = content.get("slotType", "") or content.get("cardType", "")
                        if slot:
                            slot = get_translation(slot, "zh-CN", "")
                            res_item["Type"] = ITEMTYPE_MAPPING.get(slot, slot)

                    # 效果与修饰符
                    is_enchantment = folder_type in ["Oils", "Scrolls"]
                    # is_card = folder_type in ["Buff", "EntitySpawn", "Event", "ItemSpawn"]
                    mods_map = {
                        "Equipment": "modifiersOnEquipNew",
                        "Oils": "appliesEnchantment",
                        "Scrolls": "appliesEnchantment",
                        "Attachments": "modifiersOnAttachToItem",
                        "Consumables": ["buffsOnConsume", "valueChangeOnItemConsume"],
                    }
                    mods = []

                    if is_card:
                        reward_type = content.get("rewardType", "")
                        buff_type = content.get("buffType", "")
                        
                        if reward_type == "ApplyBuff":
                            if buff_type == "ExistingBuff":
                                mods = content.get("buffsToApply", [])
                            elif buff_type == "PermanentModifier":
                                mods = content.get("permanentModifiers", [])
                            else:
                                attr_name = ATTRIBUTE_MAPPING.get(buff_type, buff_type)
                                mods = [{
                                    "attributeName": attr_name,
                                    "value": content.get("buffAmount", 0),
                                    "isPercentageAttribute": 1 if any(x in buff_type for x in ["Amount", "Gain"]) else 0
                                }]
                        
                        elif reward_type == "TriggerEvent":
                            event_type = content.get("eventType", "")
                            if event_type:
                                mods = [{"attributeName": event_type, "isBooleanAttribute": 1}]
                        
                        elif reward_type == "GiveResource":
                            attr_name = ATTRIBUTE_MAPPING.get("GiveResource", "ResourceAmount")
                            mods = [{"attributeName": attr_name, "value": content.get("resourceAmount", 0)}]
                    
                    else:
                        target_key = mods_map.get(folder_type, "buffsOnConsume")
                        if isinstance(target_key, list):
                            mods = content.get(target_key[0], []) or content.get(target_key[1], [])
                        else:
                            mods = content.get(target_key, [])

                    recipesTaughtOnConsume = content.get("recipesTaughtOnConsume")
                    if recipesTaughtOnConsume and folder_type == "Consumables":
                        res_item["Recipes"] = recipesTaughtOnConsume

                    effects = map_effects(mods, ATTRIBUTE_MAPPING, BLOCKED_ATTRIBUTES, content.get("removeStatusOnConsume", []), is_enchantment)
                    if effects and folder_type != "Weapons": res_item["Effects"] = effects

                    if folder_type == "Weapons":
                        caliber = content.get("caliber", "")
                        weapon_type = content.get("weaponType", "")
                        iMaxAmmoPerShot = content.get("iMaxAmmoPerShot", 1)

                        if caliber: res_item["Caliber"] = caliber

                        # if caliber: res_item["Damage"] = int(calc_damage(content.get("damageMultiplier", 1), caliber, weapon_type))
                        weapon_damage = int(calc_damage(content.get("damageMultiplier", 1), caliber, weapon_type))
                        if weapon_damage > 0:
                            if caliber == "12ga":
                                if iMaxAmmoPerShot > 1:
                                    res_item["Damage"] = [weapon_damage, 8, int(iMaxAmmoPerShot)]
                                else:
                                    res_item["Damage"] = [weapon_damage, 8]
                            elif identifier == "Weapon_Augusta":
                                if iMaxAmmoPerShot > 1:
                                    res_item["Damage"] = [weapon_damage, 3, int(iMaxAmmoPerShot)]
                                else:
                                    res_item["Damage"] = [weapon_damage, 3]
                            else:
                                if iMaxAmmoPerShot > 1:
                                    res_item["Damage"] = [weapon_damage, int(iMaxAmmoPerShot)]
                                else:
                                    res_item["Damage"] = weapon_damage

                        if content.get("rpm", 0) > 0: res_item["RPM"] = content.get("rpm", 0)
                        if content.get("iAmmoMax", 0) > 0: res_item["AmmoMax"] = content.get("iAmmoMax", 0)
                        
                        spread_list = content.get("spreadPerCaliber", [])
                        for spread in spread_list:
                            if spread.get("Caliber") == caliber:
                                spread_value = spread.get("Spread", "")
                                break
                        if spread_value: res_item["Spread"] = spread_value

                        if content.get("bulletSpeed", 0) > 0: res_item["BulletSpeed"] = int(content.get("bulletSpeed", 0))

                        kick_power_list = content.get("kickPower", [])
                        for kick in kick_power_list:
                            if kick.get("Caliber") == caliber:
                                kick_power = kick.get("KickPower", None)
                                break
                        if kick_power: res_item["KickPower"] = round(kick_power, 3)

                        baseAttributes_list = content.get("baseAttributes", [])
                        for baseAttributes in baseAttributes_list:
                            if baseAttributes.get("attributeName") == "KickCompensation":
                                kickCompensation = baseAttributes.get("value", None)
                                break
                        if kickCompensation: res_item["KickCompensation"] = round(kickCompensation, 3)

                        weightType = {"Knife": 0,"Pistol": 5,"SMG": 8,"Rifle": 16,"Sniper": 25,"Bigga": 35}
                        res_item["Weight"] = weightType.get(content.get("weightClass", 0), 0)

                        if content.get("maxDurability", 0) > 0: res_item["Durability"] = int(content.get("maxDurability"))
                    size = [content.get("inventorySize", {}).get("x", 0), content.get("inventorySize", {}).get("y", 0)]
                    if size[0] > 0: res_item["Size"] = size
                    if content.get("basePrice", 0) > 0: res_item["Price"] = content.get("basePrice")
  
                    result[f"{'?_' if content.get("slotType", "") == 'Gadget' or display_name.startswith("Weapon_") or display_name.startswith("Manual_Recipe_") else ''}{display_name}"] = res_item
            except Exception as e: print(f"错误 {filename}: {e}")
    
    # sorted_res = {k: result[k] for k in sorted(result, key=lambda x: result[x]["ID"])}
    # sorted_res = {k: result[k] for k in sorted(result, key=lambda x: result[x]["ID"] if result[x]["ID"] is not None else 0)}
    sorted_res = {k: result[k] for k in sorted(result, key=lambda x: result[x]["Name"]["EN"])}
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(sorted_res, f, indent=4, ensure_ascii=False)

def main():
    folder = "ItemSpawn"   # 可以是 "Weapons", "Equipment", "Repair Items", "Misc Items", "Oils", "Scrolls", "Attachments", "Consumables"
    is_card = folder in ["Buff", "EntitySpawn", "Event", "ItemSpawn"] 
    # convert_to_target_format(f"./Items/{folder}", f"{folder}_output.json", folder)
    convert_to_target_format(f"./Cards/{folder}", f"{folder}_output.json", folder, is_card)

if __name__ == "__main__":
    main()