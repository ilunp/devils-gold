import json
import os
from collections import defaultdict

def load_environment_data(json_file):
    """从 JSON 文件加载环境数据并提取战利品表信息"""
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 提取所有战利品表相关的字段
    loot_tables = {}
    
    # 定义可能的战利品表字段
    loot_fields = [
        "armorLoot", "armorLootDemo", "scavengeLoot", 
        "valuablesLoot", "valuablesLootDemo", "weaponsLoot", "weaponsLootDemo"
    ]
    
    for field in loot_fields:
        if field in data and data[field] is not None:
            loot_tables[field] = data[field]
    
    return {
        "environment_name": data.get("environmentName", "Unknown"),
        "identifier": data.get("identifier", "Unknown"),
        "loot_tables": loot_tables
    }

def find_loot_table_files(loot_table_name, loot_folder="Loot Tables"):
    """在Loot Tables文件夹中查找对应的战利品表文件"""
    if not os.path.exists(loot_folder):
        return None
    
    # 可能的文件扩展名
    possible_files = [
        f"{loot_table_name}.json",
        f"Loot_{loot_table_name}.json",
        f"{loot_table_name}_NEW.json",
        f"{loot_table_name}_Demo.json"
    ]
    
    for filename in possible_files:
        file_path = os.path.join(loot_folder, filename)
        if os.path.exists(file_path):
            return file_path
    
    # 如果没有找到精确匹配，尝试部分匹配
    json_files = [f for f in os.listdir(loot_folder) if f.endswith('.json')]
    for json_file in json_files:
        if loot_table_name in json_file:
            return os.path.join(loot_folder, json_file)
    
    return None

def load_loot_data(json_file):
    """从 JSON 文件加载战利品数据"""
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 过滤掉lootItem为None或缺失的条目
    valid_entries = [item for item in data["entries"] if item.get("lootItem") is not None]
    data["entries"] = valid_entries
    return data

def calculate_probabilities(data):
    """计算概率并归类"""
    total_weight = sum(item["lootWeight"] for item in data["entries"])
    prob_dict = defaultdict(list)
    
    for item in data["entries"]:
        try:
            prob = (item["lootWeight"] / total_weight) * 100
            prob_rounded = round(prob, 2)  # 保留2位小数
            prob_dict[prob_rounded].append(str(item["lootItem"]))  # 确保转换为字符串
        except (KeyError, TypeError) as e:
            print(f"警告: 跳过无效物品条目 - {item}. 错误: {e}")
            continue
    
    return dict(sorted(prob_dict.items())), total_weight

def generate_wikitext(prob_dict, loot_table_name, environment_name, loot_type):
    """生成Wikitext表格"""
    wikitext = f"=== {environment_name} - {loot_type} ===\n"
    wikitext += "{| class=\"wikitable sortable mw-collapsible mw-collapsed\" data-expandtext=\"{{int:show}}\" data-collapsetext=\"{{int:hide}}\" style=\"min-width: -webkit-fill-available\"\n|+ \n|-\n! 概率 (%) !! 物品列表\n"
    for prob, items in prob_dict.items():
        # 再次确保所有物品名称都是字符串
        safe_items = [str(item) for item in items if item is not None]
        wikitext += f"|-\n| {prob} || {', '.join(safe_items)}\n"
    wikitext += "|}\n"
    return wikitext

def main():
    try:
        # 定义环境配置文件夹和战利品表文件夹路径
        environment_folder = "Game Settings/Act I/2_Caves/"  # 环境配置文件夹
        loot_folder = "Loot Tables"  # 战利品表文件夹
        
        # 检查文件夹是否存在
        if not os.path.exists(environment_folder):
            print(f"错误: 找不到环境配置文件夹 {environment_folder}")
            return
        
        if not os.path.exists(loot_folder):
            print(f"错误: 找不到战利品表文件夹 {loot_folder}")
            return
        
        # 获取环境配置文件夹中所有的JSON文件
        environment_files = [f for f in os.listdir(environment_folder) if f.endswith('.json')]
        
        if not environment_files:
            print(f"在文件夹 {environment_folder} 中没有找到环境配置JSON文件")
            return
        
        print(f"找到 {len(environment_files)} 个环境配置文件:")
        for file in environment_files:
            print(f"  - {file}")
        
        # 创建输出文件夹
        output_folder = "loot_output"
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        
        # 循环处理每个环境配置文件
        for env_file in environment_files:
            try:
                file_path = os.path.join(environment_folder, env_file)
                print(f"\n正在处理环境配置文件: {env_file}")
                
                # 加载环境数据
                env_data = load_environment_data(file_path)
                environment_name = env_data["environment_name"]
                identifier = env_data["identifier"]
                loot_tables = env_data["loot_tables"]
                
                print(f"  环境: {environment_name} ({identifier})")
                print(f"  找到 {len(loot_tables)} 个战利品表:")
                
                # 为每个环境创建一个汇总文件
                env_output_filename = f"{identifier}.wiki"
                env_output_path = os.path.join(output_folder, env_output_filename)
                env_wikitext = f"= {environment_name} 战利品概率 =\n\n"
                
                # 处理每个战利品表
                for loot_type, loot_table_name in loot_tables.items():
                    print(f"    - {loot_type}: {loot_table_name}")
                    
                    # 查找对应的战利品表文件
                    loot_file_path = find_loot_table_files(loot_table_name, loot_folder)
                    
                    if loot_file_path and os.path.exists(loot_file_path):
                        try:
                            # 加载战利品数据
                            loot_data = load_loot_data(loot_file_path)
                            
                            # 计算概率
                            prob_dict, total_weight = calculate_probabilities(loot_data)
                            
                            # 生成Wikitext
                            wikitext = generate_wikitext(prob_dict, loot_table_name, environment_name, loot_type)
                            env_wikitext += wikitext + "\n"
                            
                            print(f"      已处理: {len(loot_data['entries'])} 个物品, 总权重: {total_weight}")
                            
                        except Exception as e:
                            print(f"      处理战利品表 {loot_table_name} 时出错: {e}")
                            env_wikitext += f"=== {loot_type} ===\n错误: 处理战利品表时出错 - {e}\n\n"
                    else:
                        print(f"      警告: 找不到战利品表文件 {loot_table_name}")
                        env_wikitext += f"=== {loot_type} ===\n警告: 找不到战利品表文件 {loot_table_name}\n\n"
                
                # 保存环境汇总文件
                with open(env_output_path, "w", encoding="utf-8") as f:
                    f.write(env_wikitext)
                print(f"  环境汇总已保存到: {env_output_path}")
                
            except Exception as e:
                print(f"处理环境配置文件 {env_file} 时发生错误: {e}")
        
        print(f"\n所有文件处理完成！结果保存在 {output_folder} 文件夹中")
    
    except Exception as e:
        print(f"发生意外错误: {e}")

if __name__ == "__main__":
    main()