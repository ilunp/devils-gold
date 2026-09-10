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
    # "Enchantment_OverdoseOil": "超量油",
    "Enchantment_TooMuchOil": "过量油（Too Much Oil）",
    "Item_Marshmallow": "棉花糖（Marshmallows）",
    "Item_EyePatch": "眼罩（Eye Patch）",
    "Attachment_LaserSightLime": "激光瞄准镜（青柠色）",
    "Attachment_LaserSightBone": "激光瞄准镜（骨色）",
    "Attachment_LaserSightRed": "激光瞄准镜（红色）",
    "Attachment_LaserSightTangerine": "激光瞄准镜（橘色）",
    "Attachment_LaserSightTeal": "激光瞄准镜（蓝绿色）",
    "Attachment_LaserSightLightBlue": "激光瞄准镜（浅蓝色）",
    "Attachment_LaserSightGold": "激光瞄准镜（金色）",
    "Attachment_LaserSightGreen": "激光瞄准镜（绿色）",
    "Attachment_LaserSightMagenta": "激光瞄准镜（洋红色）",
    "Attachment_LaserSightOrange": "激光瞄准镜（橙色）",
    "Attachment_LaserSightRosePink": "激光瞄准镜（玫瑰粉色）",
    "Attachment_LaserSightDenimBlue": "激光瞄准镜（牛仔蓝）",
    "Attachment_LaserSightPurple": "激光瞄准镜（紫色）",
    "Attachment_LaserSightYellow": "激光瞄准镜（黄色）",
    "Attachment_LaserSightPoop": "激光瞄准镜（棕色）",

    "Enchantment_Vinesprout": "藤蔓嫩芽卷轴",
    "Enchantment_RigidSystemOil": "坚固魔油（Rigid System Oil）",
    # "Enchantment_SturdyOil": "坚固魔油",
}

EN_DISPLAYNAME_MAPPING = {
    "Attachment_LaserSightLime": "Laser Sight (Lime)",
    "Attachment_LaserSightBone": "Laser Sight (Bone)",
    "Attachment_LaserSightRed": "Laser Sight (Red)",
    "Attachment_LaserSightTangerine": "Laser Sight (Tangerine)",
    "Attachment_LaserSightTeal": "Laser Sight (Teal)",
    "Attachment_LaserSightLightBlue": "Laser Sight (Light Blue)",
    "Attachment_LaserSightGold": "Laser Sight (Gold)",
    "Attachment_LaserSightGreen": "Laser Sight (Green)",
    "Attachment_LaserSightMagenta": "Laser Sight (Magenta)",
    "Attachment_LaserSightOrange": "Laser Sight (Orange)",
    "Attachment_LaserSightRosePink": "Laser Sight (Rose Pink)",
    "Attachment_LaserSightDenimBlue": "Laser Sight (Denim Blue)",
    "Attachment_LaserSightPurple": "Laser Sight (Purple)",
    "Attachment_LaserSightYellow": "Laser Sight (Yellow)",
    "Attachment_LaserSightPoop": "Laser Sight (Poop)",

    "Enchantment_Vinesprout": "Scroll of Vine Sprout",
}

ITEMTYPE_MAPPING = {
    "PassiveEnhancements": "饰品",
    "ItemRepair": "维修",
    "ItemConsumable": "枪凿",
    "Key": "钥匙",
    "Attachment": "配件",
    "Misc Items": "杂物",
    "Valuables": "贵重",
}
ITEMTAG_MAPPING = {
    1: "器官",
    2: "贵重",
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
    #     if isBoolean: return ""
    #     if mod_type in ["Flat", 100]:
    #         if isPercentage:
    #             return f"+{int(round(value * 100))}%" if value >= 0 else f"{int(round(value * 100))}%"
    #         return f"+{round(value, 2)}" if value >= 0 else f"{round(value, 2)}"
    #     elif mod_type in ["PercentAdd", 200]:
    #         return f"(+) +{round(value * 100)}%" if value >= 0 else f"(+) {round(value * 100)}%"
    #     elif mod_type in ["PercentMult", 300]:
    #         return f"(×) +{round(value * 100)}%" if value >= 0 else f"(×) {round(value * 100)}%"
    #     return f"+{round(value, 2)}"
    if isBoolean:
        return ""

    if value == 0:
        if mod_type in ["PercentAdd", 200]:
            return "(+) 0%"
        if mod_type in ["PercentMult", 300]:
            return "(×) 0%"
        return "0"
    
    sign = "+" if value > 0 else "-"
    abs_val = abs(value)
    
    if isPercentage or mod_type in ["PercentAdd", 200, "PercentMult", 300]:
        num = f"{round(abs_val * 100)}%"
    else:
        num = str(int(abs_val)) if abs_val.is_integer() else f"{round(abs_val, 2)}"
    
    if mod_type in ["PercentAdd", 200]:
        return f"(+) {sign}{num}"
    if mod_type in ["PercentMult", 300]:
        return f"(×) {sign}{num}"
    return f"{sign}{num}"

def map_effects(modifiers, ATTRIBUTE_MAPPING, BLOCKED_ATTRIBUTES, remove_status_on_consume, is_enchantment=False, item_id=None, item_name=None):
    effects = {}
    enchantment_name = None  # 新增变量存储附魔名称
    
    if isinstance(modifiers, dict):
        if modifiers.get("CostsDurability", 1) == 0:
            effects["不会额外损失耐久度"] = ""
        if modifiers.get("enchantmentName", ""):
            enchantment_name = get_translation(f"{modifiers.get('m_Name', '')}", "zh-CN", "EnchantmentDefinitions/")
        modifiers = modifiers.get("modifiersApplied", [])

    for modifier in modifiers:
        if is_enchantment and modifier.get("showInItemDescription", 1) == 0:
            continue

        raw_attr = modifier.get("localizationName") or modifier.get("attributeName") or str(modifier.get("attribute", "")) or str(modifier.get("statusName", ""))
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
            if mapped_attr == raw_attr:
                mapped_attr = modifier.get("itemDescriptionName", "")
        
        if raw_attr in BLOCKED_ATTRIBUTES:
            continue

        if is_bool:
            effects[mapped_attr] = True
            continue

        if "statusName" in modifier:
            effects[get_translation(f"{raw_attr}_label", "zh-CN", "EntityAttributes/")] = f"{value} 秒"
            continue

        if "HealthRegen" in raw_attr or raw_attr == "Health regen":
            if mod_type not in ["Flat", 100]:
                print(f"Warning: HealthRegen '{raw_attr}' has mod_type {mod_type}, expected Flat - Item: {item_id} ({item_name})")
                mod_type = "Flat"
            
            if total_override != 0:
                total_hp = int(total_override)
                rate_per_sec = total_override / duration if duration > 0 else total_override
            else:
                total_hp = int(value * duration) if duration > 0 else int(value)
                rate_per_sec = value
            
            if duration > 0:
                if abs(rate_per_sec - int(rate_per_sec)) < 0.01:
                    rate_text = f"{int(rate_per_sec)}HP/s"
                else:
                    rate_text = f"{rate_per_sec:.1f}HP/s"
                effects["生命恢复"] = f"{total_hp} HP（{duration}秒, {rate_text}）"
            else:
                effects["生命恢复"] = f"{total_hp} HP"
            continue

        elif duration:
            if total_override != 0:
                display_val = f"{int(total_override)}" 
            else:
                sign = "+" if value > 0 else ""
                
                prefix = ""
                if mod_type in ["PercentAdd", 200]:
                    prefix = "(+) "
                elif mod_type in ["PercentMult", 300]:
                    prefix = "(×) "
                
                if not is_perc:
                    display_val = f"{sign}{round(value, 2)}"
                else:
                    display_val = f"{sign}{int(round(value * 100))}%"
                
                display_val = prefix + display_val
            effects[mapped_attr] = f"{display_val}（{duration}秒）"
        else:
            effects[mapped_attr] = f"+{int(value)}" if raw_attr == "Durability" else format_value(value, mod_type, is_bool, is_perc)

    if remove_status_on_consume:
        for status in remove_status_on_consume:
            effects[f"移除{get_translation(f'{status}_label', 'zh-CN', 'EntityAttributes/')}"] = ""
    
    return effects, enchantment_name

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

                    display_name = DISPLAYNAME_MAPPING.get(identifier, get_translation(identifier, "zh-CN", "Items/"))
                    if display_name == identifier:
                        display_name = content.get("displayName", identifier)

                    english_name = EN_DISPLAYNAME_MAPPING.get(identifier, get_translation(identifier, "en", "Items/"))
                    if english_name == identifier:
                        english_name = get_translation(f"{identifier}_Title", "en", "Endless/")

                    if display_name.startswith("食谱：") and content.get("taughtRecipeProduct"):
                        item_name = content.get("taughtRecipeProduct")
                        display_name = get_translation("Manual_RecipeDynamic", "zh-CN", "Items/").replace("X_ITEM", get_translation(item_name, "zh-CN", "Items/"))
                        english_name = get_translation("Manual_RecipeDynamic", "en", "Items/").replace("X_ITEM", get_translation(item_name, "en", "Items/"))

                    res_item = {}

                    res_item["ID"] = content.get("id", 0)

                    res_item["Name"] = {"ZH": display_name, "EN": english_name}

                    desc = content.get("description", "")

                    if content.get("hasCustomDescription", 0):
                        
                        if not desc:
                            desc = get_translation(f"{identifier}", "zh-CN", "ItemDescriptions/")

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

                    if is_card:
                        res_item["Desc"] = desc.replace("+", "").replace("AMOUNT_X", str(amount_value))
                    else:
                        res_item["Desc"] = desc

                    if content.get("flavor"): res_item["Flav"] = content.get("flavor", "").replace("BANISH_X", str(1)).replace("CHOICEDRAW_X", str(2)).replace("REROLLS_X", str(1))

                    if content.get("customArtwork"): res_item["Artwork"] = content.get("customArtwork", "")

                    if content.get("itemQuality"): res_item["Quality"] = content.get("itemQuality", "")

                    # --- Type 核心处理逻辑 ---
                    if folder_type == "Weapons":
                        w_type = content.get("weaponType", "")
                        res_item["Type"] = get_translation(f"WeaponType_{w_type}", "zh-CN", "ItemDescriptions/")
                    elif folder_type == "Consumables":
                        if content.get("recipesTaughtOnConsume"):
                            res_item["Type"] = "食谱"
                        elif content.get("currencyOnConsume"):
                            res_item["Type"] = "货币"
                        elif content.get("resourceOnConsume"):
                            res_item["Type"] = "资源"
                        else:
                            res_item["Type"] = "消耗品"
                    else:
                        item_type = (
                            content.get("slotType") if content.get("slotType") not in (None, "", "None") else None
                        ) or (
                            content.get("cardType") if content.get("cardType") not in (None, "", "None") else None
                        ) or (
                            f"UseType_{content.get('useType')}" if content.get("useType") not in (None, "", "None") else None
                        ) or (
                            ITEMTAG_MAPPING.get(content.get("itemTags")) if content.get("itemTags") not in (None, "", "None", 0) else None
                        ) or (
                            f"{folder_type}"
                        ) or ""
                        if item_type:
                            if item_type.startswith("UseType_"):
                                res_item["Type"] = get_translation(item_type, "zh-CN", "ItemDescriptions/")
                            else:
                                res_item["Type"] = ITEMTYPE_MAPPING.get(item_type, get_translation(item_type, "zh-CN"))

                    # 效果与修饰符
                    is_enchantment = folder_type in ["Oils", "Scrolls"]
                    # is_card = folder_type in ["Buff", "EntitySpawn", "Event", "ItemSpawn"]
                    mods_map = {
                        "Equipment": "modifiersOnEquipNew",
                        "Oils": "appliesEnchantment",
                        "Scrolls": "appliesEnchantment",
                        "Attachments": ["modifiersOnAttachToItem", "modifiersOnEquipNew"],
                        "Consumables": ["buffsOnConsume", "valueChangeOnItemConsume", "addStatusOnConsume"],
                        "Repair Items": "valueChangeOnItemConsume",
                        "Valuables": "modifiersOnEquipNew"
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
                            mods = []
                            for key in target_key:
                                mods_list = content.get(key, [])
                                if mods_list:
                                    mods.extend(mods_list)
                        else:
                            mods = content.get(target_key, [])

                    recipesTaughtOnConsume = content.get("recipesTaughtOnConsume")
                    if recipesTaughtOnConsume and folder_type == "Consumables":
                        res_item["Recipes"] = recipesTaughtOnConsume

                    effects, enchantment_name = map_effects(mods, ATTRIBUTE_MAPPING, BLOCKED_ATTRIBUTES, 
                                         content.get("removeStatusOnConsume", []), 
                                         is_enchantment, item_id=identifier, 
                                         item_name=display_name)
                    if enchantment_name:
                        res_item["EnchantmentName"] = enchantment_name
                        
                    if effects and folder_type != "Weapons": res_item["Effects"] = effects

                    if folder_type == "Weapons":
                        caliber = content.get("caliber", "")
                        weapon_type = content.get("weaponType", "")
                        iMaxAmmoPerShot = content.get("iMaxAmmoPerShot", 1)

                        if caliber: res_item["Caliber"] = caliber

                        overrideDamage = content.get("overrideDamage")
                        # if caliber: res_item["Damage"] = int(calc_damage(content.get("damageMultiplier", 1), caliber, weapon_type))
                        if overrideDamage:
                            weapon_damage = overrideDamage
                        else:
                            weapon_damage = int(calc_damage(content.get("damageMultiplier", 1), caliber, weapon_type))

                        if weapon_damage > 0:
                            pellet_count = None
                            if caliber == "12ga":
                                pellet_count = 8
                            elif identifier == "Weapon_Augusta":
                                pellet_count = 3
                            
                            if pellet_count:
                                damage_value = [weapon_damage, pellet_count]
                                if iMaxAmmoPerShot > 1:
                                    damage_value.append(iMaxAmmoPerShot)
                            else:
                                damage_value = weapon_damage
                                if iMaxAmmoPerShot > 1:
                                    damage_value = [weapon_damage, iMaxAmmoPerShot]
                            
                            res_item["Damage"] = damage_value
                            res_item["DamageMultiplier"] = content.get("damageMultiplier", 1)

                        if content.get("rpm", 0) > 0: res_item["RPM"] = content.get("rpm", 0)
                        if content.get("iAmmoMax", 0) > 0: res_item["AmmoMax"] = content.get("iAmmoMax", 0)
                        
                        spread_value = None
                        spread_list = content.get("spreadPerCaliber", [])
                        if spread_list:
                            for spread in spread_list:
                                if spread.get("Caliber") == caliber:
                                    spread_value = spread.get("Spread", "")
                                    break
                        else:
                            baseAttributes_list = content.get("baseAttributes", [])
                            for baseAttributes in baseAttributes_list:
                                if baseAttributes.get("attributeName") == "Spread":
                                    spread_value = baseAttributes.get("value", None)
                                    break
                        if spread_value: res_item["Spread"] = spread_value

                        if content.get("bulletSpeed", 0) > 0: res_item["BulletSpeed"] = int(content.get("bulletSpeed", 0))

                        kick_power = None
                        kick_power_list = content.get("kickPower", [])
                        for kick in kick_power_list:
                            if kick.get("Caliber") == caliber:
                                kick_power = kick.get("KickPower", None)
                                break
                        if kick_power: res_item["KickPower"] = round(kick_power, 3)

                        kickCompensation = None
                        baseAttributes_list = content.get("baseAttributes", [])
                        for baseAttributes in baseAttributes_list:
                            if baseAttributes.get("attributeName") == "KickCompensation":
                                kickCompensation = baseAttributes.get("value", None)
                                break
                        if kickCompensation: res_item["KickCompensation"] = round(kickCompensation, 3)

                        weightType = {"Knife": 0,"Pistol": 5,"SMG": 12,"Rifle": 20,"Sniper": 25,"Bigga": 35}
                        res_item["Weight"] = weightType.get(content.get("weightClass", 0), 0)

                    
                    if content.get("maxDurability", 0) > 0: res_item["Durability"] = int(content.get("maxDurability"))

                    size = [content.get("inventorySize", {}).get("x", 0), content.get("inventorySize", {}).get("y", 0)]
                    if size[0] > 0: res_item["Size"] = size

                    if content.get("basePrice", 0) > 0: res_item["Price"] = content.get("basePrice")
  
                    result[f"{'?_' if content.get("slotType", "") == 'Gadget' or display_name.startswith("Weapon_") or display_name.startswith("Manual_Recipe_") else ''}{display_name}"] = res_item
            except Exception as e: print(f"错误 {filename}: {e}")
    
    sorted_res = {k: result[k] for k in sorted(result, key=lambda x: result[x]["ID"])}
    # sorted_res = {k: result[k] for k in sorted(result, key=lambda x: result[x]["ID"] if result[x]["ID"] is not None else 0)}
    # sorted_res = {k: result[k] for k in sorted(result, key=lambda x: result[x]["Name"]["EN"])}
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(sorted_res, f, indent=4, ensure_ascii=False)

def main():
    folder = "Weapons"   # 可以是 "Weapons", "Equipment", "Repair Items", "Misc Items", "Oils", "Scrolls", "Attachments", "Consumables", "Chisels", "Keys"
    is_card = folder in ["Buff", "EntitySpawn", "Event", "ItemSpawn"] 
    convert_to_target_format(f"./Items/{folder}", f"{folder}_output.json", folder)
    # convert_to_target_format(f"./Cards/{folder}", f"{folder}_output.json", folder, is_card)

if __name__ == "__main__":
    main()