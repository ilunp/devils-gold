import os
import json
import csv

# 定义常量
BLOCKED_ATTRIBUTES = []
ATTRIBUTE_MAPPING = {

}

# 新增：手动指定 ID 对应的中文名称映射
# 键为 m_Name (identifier)，值为你想要的显示名称
DISPLAYNAME_MAPPING = {
    "Enchantment_OverdoseOil": "超量油",
    "Item_Marshmallow": "棉花糖（串）"
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
                    return row[column]
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

        mapped_attr = get_translation(attr_key, "zh-CN", "ItemAttributes/")
        print(mapped_attr)
        if mapped_attr == attr_key:
            mapped_attr = ATTRIBUTE_MAPPING.get(raw_attr, raw_attr)
        
        if raw_attr in BLOCKED_ATTRIBUTES: continue

        if is_bool:
            effects[mapped_attr] = True
            continue

        if "HealthRegen" in raw_attr or raw_attr == "Health regen":
            final_hp = total_override if total_override != 0 else int(value * duration)
            effects["生命恢复"] = f"{int(final_hp)} HP ({duration}秒)"
        elif duration:
            display_val = f"{int(total_override)}" if total_override != 0 else (f"+{int(value)}" if value > 1 else f"{int(round(value * 100))}%")
            effects[mapped_attr] = f"{display_val} ({duration}秒)"
        else:
            effects[mapped_attr] = f"+{int(value)}" if raw_attr == "Durability" else format_value(value, mod_type, is_bool, is_perc)

    if remove_status_on_consume:
        for status in remove_status_on_consume:
            # print(status)
            effects[f"移除{get_translation(f"{status}_label", 'zh-CN', 'EntityAttributes/')}"] = ""
    return effects

def damage(damageMultiplier, caliber, weapon_Type):
    caliber_damage = {"12ga": 20, "Laser": 50, "9mm": 60, "5.56mm": 80, "7.62mm": 100, "50 BMG": 200}
    weapon_Type_damage = {"Pistol": 1, "Revolver": 1.6, "Shotgun": 1, "SMG": 1, "Light Machine Gun": 1, "Rifle": 2, "Assault rifle": 1.2, "Sniper rifle": 2}
    return caliber_damage.get(caliber, 0) * weapon_Type_damage.get(weapon_Type, 1) * damageMultiplier

# --- 主逻辑 ---
def convert_to_target_format(input_folder, output_file, folder_type):
    result = {}
    if not os.path.exists(input_folder): return

    for filename in os.listdir(input_folder):
        if filename.endswith(".json"):
            try:
                with open(os.path.join(input_folder, filename), "r", encoding="utf-8") as f:
                    content = json.load(f)
                    identifier = content.get("m_Name", "")

                    # 名称获取
                    display_name = DISPLAYNAME_MAPPING.get(identifier) or get_translation(identifier, "zh-CN", "Items/")
                    if display_name == identifier: display_name = content.get("displayName", identifier)
                    
                    english_name = get_translation(identifier, "en", "Items/")
                    if english_name == identifier: english_name = content.get("displayName", identifier)

                    res_item = {
                        "ID": content.get("id"),
                        "Name": {"ZH": display_name, "EN": english_name},
                        "Desc": get_translation(identifier, "zh-CN", "ItemDescriptions/") if content.get("hasCustomDescription", 0) else content.get("description", ""),
                        "Flav": content.get("flavor", ""),
                        "Quality": content.get("itemQuality", ""),
                    }

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
                        slot = content.get("slotType", "")
                        res_item["Type"] = get_translation(slot, "zh-CN", "") if slot else "物品"

                    # 效果与修饰符
                    is_enchantment = folder_type in ["Oils", "Scrolls"]
                    mods_map = {
                        "Equipment": "modifiersOnEquipNew",
                        "Oils": "appliesEnchantment",
                        "Scrolls": "appliesEnchantment",
                        "Attachments": "modifiersOnAttachToItem",
                        "Consumables": ["buffsOnConsume", "valueChangeOnItemConsume"]
                    }
                    
                    target_key = mods_map.get(folder_type, "buffsOnConsume")
                    if isinstance(target_key, list):
                        mods = content.get(target_key[0], []) or content.get(target_key[1], [])
                    else:
                        mods = content.get(target_key, [])
                    
                    # --- 新增：处理食谱解锁逻辑 ---
                    recipesTaughtOnConsume = content.get("recipesTaughtOnConsume")
                    if recipesTaughtOnConsume and folder_type == "Consumables":
                        res_item["Recipes"] = recipesTaughtOnConsume

                    effects = map_effects(mods, ATTRIBUTE_MAPPING, BLOCKED_ATTRIBUTES, content.get("removeStatusOnConsume", []), is_enchantment)
                    if effects and folder_type != "Weapons": res_item["Effects"] = effects

                    # 其他通用字段
                    if folder_type == "Weapons":
                        caliber = content.get("caliber", "")
                        res_item["Damage"] = int(damage(content.get("damageMultiplier", 1), caliber, content.get("weaponType", ""))) if caliber else 0
                    
                    size = [content.get("inventorySize", {}).get("x", 0), content.get("inventorySize", {}).get("y", 0)]
                    if size[0] > 0: res_item["Size"] = size
                    if content.get("basePrice", 0) > 0: res_item["Price"] = content.get("basePrice")

                    

                    result[display_name] = res_item
            except Exception as e: print(f"错误 {filename}: {e}")
    
    sorted_res = {k: result[k] for k in sorted(result, key=lambda x: result[x]["ID"])}
    # sorted_res = {k: result[k] for k in sorted(result, key=lambda x: result[x]["Name"]["EN"])}
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(sorted_res, f, indent=4, ensure_ascii=False)

def main():
    folder = "Oils"   # 可以是 "Weapons", "Equipment", "Repair Items", "Misc Items", "Oils", "Scrolls", "Attachments", "Consumables"
    convert_to_target_format(f"./Items/{folder}", f"{folder}_output.json", folder)

if __name__ == "__main__":
    main()