import json
import csv

# 语言列表
languages = [
    {"Name": "English", "Code": "en"},
    {"Name": "Swedish", "Code": "sv"},
    {"Name": "French", "Code": "fr"},
    {"Name": "Italian", "Code": "it"},
    {"Name": "German", "Code": "de"},
    {"Name": "Spanish", "Code": "es"},
    {"Name": "Portuguese", "Code": "pt"},
    {"Name": "Russian", "Code": "ru"},
    {"Name": "Polish", "Code": "pl"},
    {"Name": "Japanese", "Code": "ja"},
    {"Name": "Korean", "Code": "ko"},
    {"Name": "Chinese (Simplified)", "Code": "zh-CN"},
    {"Name": "Turkish", "Code": "tr"},
    {"Name": "Arabic", "Code": "ar"}
]

# 创建语言列头
header = [20] + [f"{lang['Name']} [{lang['Code']}]" for lang in languages]

# 加载 JSON 文件
with open('I2Languages.json', 'r', encoding='utf-8') as json_file:
    data = json.load(json_file)

# 定义输出文件路径
csv_file_path = 'translations.csv'

# 创建 CSV 文件并写入内容
with open(csv_file_path, 'w', newline='', encoding='utf-8') as csv_file:
    writer = csv.writer(csv_file, quotechar='"', quoting=csv.QUOTE_ALL)

    # 写入表头
    writer.writerow(header)

    # 写入数据行
    for term in data['mTerms']:
        row = [term["Term"]] + term["Languages"]
        writer.writerow(row)

print("CSV 文件已成功创建并保存为", csv_file_path)
