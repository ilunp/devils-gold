import os
import UnityPy
import argparse
import json

parser = argparse.ArgumentParser("unpack")
parser.add_argument("assetdir",
                    help="Directory where sulfur assets are located", type=str)
args = parser.parse_args()

unpack_dir = os.path.abspath(os.path.join(
    os.path.dirname(__file__), '..', 'unpacked'))
if not os.path.exists(unpack_dir):
    os.makedirs(unpack_dir)


def unpack_all_assets(source_folder: str, destination_folder: str):
    # iterate over all files in source folder
    for root, dirs, files in os.walk(source_folder):
        for file_name in files:
            print('PARSING FILE: ' + file_name)
            # generate file_path
            file_path = os.path.join(root, file_name)
            # load that file via UnityPy.load
            env = UnityPy.load(file_path)
            for path, pptr in env.container.items():
                isType = False
                try:
                    isType = pptr.type.name == "MonoBehaviour"
                except:
                    print('error: ' + path)
                if isType:
                    data = pptr.deref()
                    tree = data.read_typetree()
                    fp = os.path.join(destination_folder, f"{
                                      tree['m_Name']}.json")
                    with open(fp, "wt", encoding="utf8") as f:
                        json.dump(tree, f, ensure_ascii=False, indent=4)


unpack_all_assets(args.assetdir, unpack_dir)
