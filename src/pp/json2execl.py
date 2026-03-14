import json
import pandas as pd
from openpyxl import Workbook

def json_to_excel_final(input_file, output_file):
    # 读取JSON文件
    with open(input_file, 'r', encoding='utf-8') as f:
        json_data = json.load(f)
    
    processed_data = []
    
    # 遍历 JSON，直接处理内部数据，不添加 key 字段
    for _, item in json_data.items():
        processed_item = item.copy()
        
        # 1. 处理数值/数组类字段 (大小写不敏感匹配，处理后会被统一转小写)
        for field in ['Size', 'Damage', 'Range', 'Area']:
            if field in processed_item and isinstance(processed_item[field], list):
                processed_item[field] = '×'.join(map(str, processed_item[field]))
        
        # 2. 处理 Effects 字段：合并为分号分隔的字符串
        if 'Effects' in processed_item:
            effects = processed_item['Effects']
            if isinstance(effects, dict):
                processed_item['Effects'] = "; ".join([f"{k}: {v}" for k, v in effects.items()])
            elif isinstance(effects, list):
                processed_item['Effects'] = "; ".join(map(str, effects))
        
        processed_data.append(processed_item)
    
    # 转换为 DataFrame
    df = pd.DataFrame(processed_data)
    
    # 3. 处理 Name 字段
    if 'Name' in df.columns:
        name_df = df['Name'].apply(pd.Series)
        # 前缀改为小写 "name_"
        name_df.columns = ['name_' + str(col).lower() for col in name_df.columns]
        df = pd.concat([df.drop(['Name'], axis=1), name_df], axis=1)
    
    # 4. 统一将所有表头转为小写
    df.columns = [str(col).lower() for col in df.columns]
    
    # 5. 自动排序：id 最前，name_ 相关列次之，其余在后
    cols = df.columns.tolist()
    priority_cols = ['id'] if 'id' in cols else []
    name_cols = sorted([c for c in cols if c.startswith('name_')])
    other_cols = [c for c in cols if c not in priority_cols and c not in name_cols]
    
    df = df[priority_cols + name_cols + other_cols]
    
    # 保存到 Excel
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='data')
        
        # 自动调整列宽
        worksheet = writer.sheets['data']
        for column in worksheet.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    val_len = len(str(cell.value))
                    if val_len > max_length:
                        max_length = val_len
                except: pass
            adjusted_width = min(max(max_length * 1.2, 10), 60)
            worksheet.column_dimensions[column_letter].width = adjusted_width

if __name__ == "__main__":
    input_json = "Storage_output.json"
    output_xlsx = "Storage_processed.xlsx"
    json_to_excel_final(input_json, output_xlsx)
    print(f"Excel文件已生成（表头已全部小写）: {output_xlsx}")