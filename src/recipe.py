import os
import json
from typing import Any


def print_recipe(amount: int, creates: str, items: list[dict[str, Any]]) -> str:
    recipeText = ""
    recipeText += str(amount) + " " + creates + " = "
    if items:
        for index, element in enumerate(items):
            ingredientAmount = element["quantity"]
            ingredient = element["item"]
            recipeText += str(ingredientAmount) + " " + ingredient
            if index + 1 < len(items):
                recipeText += " + "
    return recipeText


def generate_recipe_list(data_path: str, version: str) -> None:
    masterlist = f"SULFUR v{version} complete recipe list\n\n"
    for root, dirs, files in os.walk(os.path.join(data_path, "Recipes")):
        if len(files):
            masterlist += os.path.basename(root) + "\n\n"
            for file in files:
                file_path = os.path.join(root, file)
                with open(file_path, encoding="utf8") as jsonFile:
                    recipeText = ""
                    rawJson = json.load(jsonFile)
                    items = rawJson["itemsNeeded"]
                    amount = rawJson["quantityCreated"]
                    creates = rawJson["createsItem"]
                    recipeText = print_recipe(amount, creates, items)
                    masterlist += recipeText + "\n"
            masterlist += "\n\n"
    output_path = os.path.join(data_path, "recipes.txt")
    with open(output_path, "w", encoding="utf8") as newFile:
        newFile.write(masterlist)
