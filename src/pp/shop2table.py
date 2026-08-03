import json
from collections import defaultdict

# Language mapping dictionaries
LANG_MAPPING = {
    'en': {
        'regular_table': "Regular Table",
        'demo_table': "Demo Table",
        'hidden_table': "Hidden Table",
        'name': "Name",
        'price': "Price",
        'type': "Type",
        'chance': "Chance(%)",
        'quantity': "Qty",
        'unlock': "Unlock",
        'always': "Always",
        'random': "Random",
        'categories': {
            'Ammo': "Ammo",
            'attachment': "Attachments",
            'consumable': "Consumables",
            'item': "Items",
            'weapon': "Weapons",
            'manual': "Manuals",
        },
        'checkpoints': {
            'church': "The Church",
            'cave': "Cave",
            'shanty': "Town",
            'sewers': "Sewers",
            'dungeon': "Dungeon",
            'castle': "Castle",
            'forest': "Forest",
            'fortress': "Shav'Wani Fortress",
            'desert': "Desert",
            'default': "-"  # Default case if no match found
        }
    },
    'zh': {
        'regular_table': "普通商店",
        'demo_table': "试玩版商店",
        'hidden_table': "隐藏商店",
        'name': "名称",
        'price': "价格",
        'type': "类型",
        'chance': "概率(%)",
        'quantity': "数量",
        'unlock': "解锁条件",
        'always': "常驻",
        'random': "随机",
        'categories': {
            'ammo': "弹药",
            'attachment': "配件",
            'consumable': "消耗品",
            'item': "物品",
            'weapon': "武器",
            'manual': "食谱",
        },
        'checkpoints': {
            'church': "教堂",
            'cave': "洞穴",
            'shanty': "小镇",
            'sewers': "下水道",
            'dungeon': "地牢",
            'castle': "城堡",
            'forest': "森林",
            'fortress': "沙瓦尼堡",
            'desert': "沙漠",
            'default': "-"  # Default case if no match found
        }
    }
}

def get_localized_category(category, lang='en'):
    """Get localized category name"""
    lang_dict = LANG_MAPPING.get(lang, LANG_MAPPING['en'])
    category_mapping = lang_dict.get('categories', {})
    return category_mapping.get(category.lower(), category)

def get_localized_checkpoint(checkpoint, lang='en'):
    """Get localized checkpoint name"""
    if not checkpoint:
        return ""
    
    checkpoint = checkpoint.lower()
    lang_dict = LANG_MAPPING.get(lang, LANG_MAPPING['en'])
    checkpoint_mapping = lang_dict.get('checkpoints', {})
    
    # Try exact match first
    if checkpoint in checkpoint_mapping:
        return checkpoint_mapping[checkpoint]
    
    # Try partial match (e.g., 'church_1' will match 'church')
    for key in checkpoint_mapping:
        if key in checkpoint:
            return checkpoint_mapping[key]
    
    return checkpoint_mapping.get('default', checkpoint)

def process_json_data(json_data):
    # Initialize data structures
    regular_items = defaultdict(list)
    demo_items = defaultdict(list)
    hidden_items = defaultdict(list)
    
    # Initialize unique counters with empty sets
    regular_unique = defaultdict(set)
    demo_unique = defaultdict(set)
    hidden_unique = defaultdict(set)

    # Helper function to get category prefix
    def get_prefix(item_id):
        return item_id.split('_')[0] if '_' in item_id else 'Other'
    
     # Process RegularTable
    if 'RegularTable' in json_data:
        regular_table = json_data['RegularTable']
        
        # AlwaysAvailable items
        for item in regular_table.get('AlwaysAvailable', []):
            item['Availability'] = 'always'
            item['Count'] = 1
            prefix = get_prefix(item.get('ID', ''))
            regular_items[prefix].append(item)
            regular_unique[prefix].add(item['ID'])
        
        # SometimesAvailable items
        sometimes_items = regular_table.get('SometimesAvailable', [])
        total_weight = sum(item.get('Weight', 0) for item in sometimes_items)
        for item in sometimes_items:
            item['Availability'] = 'random'
            item['Probability'] = (item.get('Weight', 0) / total_weight * 100) if total_weight > 0 else 0
            prefix = get_prefix(item.get('ID', ''))
            regular_items[prefix].append(item)
            regular_unique[prefix].add(item['ID'])
    
    # Process DemoTable
    if 'DemoTable' in json_data:
        demo_table = json_data['DemoTable']
        
        # AlwaysAvailable items
        for item in demo_table.get('AlwaysAvailable', []):
            item['Availability'] = 'always'
            item['Count'] = 1
            prefix = get_prefix(item.get('ID', ''))
            demo_items[prefix].append(item)
            demo_unique[prefix].add(item['ID'])
        
        # SometimesAvailable items
        demo_sometimes = demo_table.get('SometimesAvailable', [])
        demo_total_weight = sum(item.get('Weight', 0) for item in demo_sometimes)
        for item in demo_sometimes:
            item['Availability'] = 'random'
            item['Probability'] = (item.get('Weight', 0) / demo_total_weight * 100) if demo_total_weight > 0 else 0
            prefix = get_prefix(item.get('ID', ''))
            demo_items[prefix].append(item)
            demo_unique[prefix].add(item['ID'])

    # Process HiddenTable
    if 'HiddenTable' in json_data:
        hidden_table = json_data['HiddenTable']
        
        # AlwaysAvailable items
        for item in hidden_table.get('AlwaysAvailable', []):
            item['Availability'] = 'always'
            item['Count'] = 1
            prefix = get_prefix(item.get('ID', ''))
            hidden_items[prefix].append(item)
            hidden_unique[prefix].add(item['ID'])
        
        # SometimesAvailable items
        hidden_sometimes = hidden_table.get('SometimesAvailable', [])
        hidden_total_weight = sum(item.get('Weight', 0) for item in hidden_sometimes)
        for item in hidden_sometimes:
            item['Availability'] = 'random'
            item['Probability'] = (item.get('Weight', 0) / hidden_total_weight * 100) if hidden_total_weight > 0 else 0
            prefix = get_prefix(item.get('ID', ''))
            hidden_items[prefix].append(item)
            hidden_unique[prefix].add(item['ID'])
    
    # Process DemoTable
    if 'DemoTable' in json_data:
        demo_table = json_data['DemoTable']
        
        # AlwaysAvailable items
        for item in demo_table.get('AlwaysAvailable', []):
            item['Availability'] = 'always'
            item['Count'] = 1
            prefix = get_prefix(item.get('ID', ''))
            demo_items[prefix].append(item)
            demo_unique[prefix].add(item['ID'])
        
        # SometimesAvailable items
        demo_sometimes = demo_table.get('SometimesAvailable', [])
        demo_total_weight = sum(item.get('Weight', 0) for item in demo_sometimes)
        for item in demo_sometimes:
            item['Availability'] = 'random'
            item['Probability'] = (item.get('Weight', 0) / demo_total_weight * 100) if demo_total_weight > 0 else 0
            prefix = get_prefix(item.get('ID', ''))
            demo_items[prefix].append(item)
            demo_unique[prefix].add(item['ID'])
    
    # Process ExpandedTables and merge into regular/demo/hidden
    for table in json_data.get('ExpandedTables', []):
        checkpoint = table.get('TableName', '').replace('ExpandTable - Checkpoint: ', '')
        expanded_items = table.get('SometimesAvailable', [])
        expanded_total_weight = sum(item.get('Weight', 0) for item in expanded_items)
        
        for item in expanded_items:
            item['Availability'] = 'random'
            item['Probability'] = (item.get('Weight', 0) / expanded_total_weight * 100) if expanded_total_weight > 0 else 0
            item['Checkpoint'] = checkpoint  # Store original checkpoint name for localization
            
            prefix = get_prefix(item.get('ID', ''))
            
            # Add to appropriate tables based on inclusion flags
            if item.get('IncludedInDemo', False):
                demo_items[prefix].append(item)
                demo_unique[prefix].add(item['ID'])
            if item.get('IsHidden', False):
                hidden_items[prefix].append(item)
                hidden_unique[prefix].add(item['ID'])
            regular_items[prefix].append(item)
            regular_unique[prefix].add(item['ID'])
    
    # Calculate final unique counts
    regular_counts = {k: len(v) for k, v in regular_unique.items()}
    demo_counts = {k: len(v) for k, v in demo_unique.items()}
    hidden_counts = {k: len(v) for k, v in hidden_unique.items()}
    
    return regular_items, demo_items, hidden_items, regular_counts, demo_counts, hidden_counts

def generate_category_table(category_items, unique_counts, title_key, lang='en'):
    lang_dict = LANG_MAPPING.get(lang, LANG_MAPPING['en'])

    wikitext = ''

    if unique_counts:
        wikitext = f"=== {lang_dict[title_key]} ===\n"
    
    for category, items in sorted(category_items.items()):
        count = unique_counts.get(category, 0)
        if count == 0:
            continue  # Skip empty categories

        # Localize category name
        localized_category = get_localized_category(category, lang)

        # Start the table
        wikitext += '{| class="wikitable sortable mw-collapsible mw-collapsed" data-expandtext="{{int:show}}" data-collapsetext="{{int:hide}}" style="min-width: -webkit-fill-available"\n'
        wikitext += f"|+ {localized_category} ({count}) \n"
        wikitext += f'! {lang_dict["name"]} !! {lang_dict["price"]} !! {lang_dict["type"]} !! {lang_dict["chance"]} !! {lang_dict["quantity"]} !! {lang_dict["unlock"]}\n'
        
        # Group identical items
        item_groups = defaultdict(list)
        for item in items:
            key = (item.get('ID'), item.get('Name'), item.get('BasePrice'), 
                   item.get('Availability'), item.get('Checkpoint', ''))
            item_groups[key].append(item)
        
        for key, group in sorted(item_groups.items(), key=lambda x: x[0][1]):  # Sort by name
            item_id, name, price, availability, checkpoint = key
            quantity = len(group)
            first_item = group[0]

            # Localize checkpoint name
            localized_checkpoint = get_localized_checkpoint(checkpoint, lang)
            
            wikitext += "|-\n"
            wikitext += f"| {{{{icon|{name}|[[{name}]]}}}} || {price} || {lang_dict[availability]} || "
            
            if availability == 'random':
                prob = first_item.get('Probability', 0)
                wikitext += f"{prob:.2f}% || "
            else:
                wikitext += "— || "
            
            wikitext += f"{quantity} || {localized_checkpoint if localized_checkpoint else '—'}\n"
        
        wikitext += '|}\n\n'
    
    return wikitext

def main(lang='en', show_regular=True, show_demo=True, show_hidden=True):
    """
    Main function with configurable table output
    
    Args:
        lang: Language selection ('en' or 'zh')
        show_regular: Whether to show regular table (default True)
        show_demo: Whether to show demo table (default False)
        show_hidden: Whether to show hidden table (default True)
    """
    # Load the JSON data
    with open('shop_export.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Process the data
    regular_items, demo_items, hidden_items, regular_counts, demo_counts, hidden_counts = process_json_data(data)
    
    # Generate wikitext
    output = "'''NPC: " + data.get('NPCName', 'Unknown') + "'''\n\n"

    if show_regular and regular_counts:
        output += generate_category_table(regular_items, regular_counts, 'regular_table', lang)
    
    if show_hidden and hidden_counts:
        output += generate_category_table(hidden_items, hidden_counts, 'hidden_table', lang)
    
    if show_demo and demo_counts:
        output += generate_category_table(demo_items, demo_counts, 'demo_table', lang)
    

    # Print the output
    # print(output)
    # To save to a file:
    with open('output.wikitext', 'w', encoding='utf-8') as f:
        f.write(output)

if __name__ == "__main__":
    # Set language ('en' for English, 'zh' for Chinese)
    # Control which tables to show (regular, demo, hidden)
    main(
        lang='zh',          # Language selection
        show_regular=True,  # Show regular table
        show_demo=False,    # Hide demo table
        show_hidden=True    # Show hidden table
    )
