import os
import UnityPy
import argparse
import json
import re

parser = argparse.ArgumentParser("unpack")
parser.add_argument(
    "assetdir", help="Directory where sulfur assets are located", type=str)
args = parser.parse_args()

unpack_dir = os.path.abspath(os.path.join(
    os.path.dirname(__file__), '..', 'unpacked'))
if not os.path.exists(unpack_dir):
    os.makedirs(unpack_dir)


def clean_file_name(name: str):
    # Removes invalid chars from a filename str
    return re.sub(r"[/\\?%*:|\"<>\x7F\x00-\x1F]", "-", name)


def unpack_all_assets(source: str, destination_folder: str):
    if os.path.isfile(source):
        root = os.path.dirname(source)
        file_name = os.path.basename(source)
        unpack_file(root, file_name, destination_folder)
    for root, dirs, files in os.walk(source):
        for file_name in files:
            unpack_file(root, file_name, destination_folder)


def unpack_file(root, file_name, destination_folder):
    # generate file_path
    file_path = os.path.join(root, file_name)
    print('PARSING FILE: ' + os.path.join(file_path))
    # load that file via UnityPy.load
    env = UnityPy.load(file_path)
    for pptr in env.objects:
        assetType = ''
        try:
            assetType = pptr.type.name
        except:
            print('error')
        if assetType == "MonoBehaviour":
            write_asset(pptr, destination_folder)


def write_asset(pptr, destination_folder):
    tree = pptr.read_typetree()
    name = ''
    if 'm_Name' in tree:
        name = tree['m_Name']
    else:
        name = pptr.path_id
    fp = os.path.join(destination_folder, f"{clean_file_name(name)}.json")
    with open(fp, "wt", encoding="utf8") as f:
        json.dump(tree, f, ensure_ascii=False, indent=4)


unpack_all_assets(args.assetdir, unpack_dir)
