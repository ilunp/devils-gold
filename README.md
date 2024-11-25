# devils-gold

Datamining tool for SULFUR. Very much a work-in-progress. Requires a python development environment with `uv` installed. Eventually it will be packaged better and maybe I'll make some compiled builds. Currently extracts all relevant item data and recipes as JSON files, as well as a CSV file containing all the in-game translations, and a TXT file of all recipes.


```
uv sync
uv run src/unpack.py '0.9.12'
```

The first position argument is a string representing the game version. All it does currently is name the output directory, in order to differentiate and compare data from different builds. This will probably be automated at some point.

The default SULFUR data path is `C:\Program Files (x86)\Steam\steamapps\common\SULFUR\Sulfur_Data`. This can be changed with `--assetpath`.

The default language is English. This can be changed with `--lang` using an ISO-639 2 digit code.