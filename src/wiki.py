def generate_wiki_table(columns: list[str], row_data: list[list[str]]) -> str:
    table_str = '{| class="wikitable"\n'
    for column in columns:
        table_str += f"!{column}\n"
    for row in row_data:
        table_str += "|-\n"
        for data in row:
            table_str += f"|{data}\n"
    table_str += "|}"
    return table_str
