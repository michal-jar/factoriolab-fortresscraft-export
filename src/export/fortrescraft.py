from genericpath import isfile
import json
from argparse import ArgumentParser
from pathlib import Path
from typing import Dict, List, Tuple, Union, Iterator, cast
from assets import game_icons
import xml.etree.ElementTree as ET
import re


class IdConverter:

    __WORD_PATTERN = re.compile(r'[A-Z]?[a-z]+|[A-Z]{2,}(?=[A-Z][a-z]|\d|\W|$)|\d+')

    def __init__(self) -> None:
        self.__counter = 0

    def create_object_id(self, object_key: Union[str, None]) -> str:
        if object_key:
            words = self.__WORD_PATTERN.findall(object_key)
        else:
            words = ['missing', 'id', str(self.__counter)]
            self.__counter += 1
        return '-'.join(map(str.lower, words))


def write(output_file: Path, factoriolab_json: Dict, debug: bool=False):
    if debug:
        print(f'Writing data to: {output_file.name}')
        print(json.dumps(factoriolab_json, indent=4))
    output_file.write_text(json.dumps(factoriolab_json))


def extract_terrain(game_data: Path, id_converter: IdConverter) -> Iterator[Tuple[Dict, Dict]]:
    for terrain in ET.parse(game_data / "TerrainData.xml").getroot():
        category_name = terrain.findtext('Category', 'Terrain')
        category_id = id_converter.create_object_id(category_name)
        category = {
            "id": category_id,
            "name": category_name
        }
        object_id = id_converter.create_object_id(terrain.findtext('Key'))
        terrain = {
            "category": category_id,
            "id": object_id,
            "name": terrain.findtext('Name'),
            "row": 0,
            "stack": int(terrain.findtext('MaxStack', default=200))
        }
        yield terrain, category


def extract_items(game_data: Path, id_converter: IdConverter) -> Iterator[Tuple[Dict, Dict]]:
    for item_entry in ET.parse(game_data / 'Items.xml').getroot():
        category_name = item_entry.findtext('Category')
        category_id = id_converter.create_object_id(category_name)
        category = {
            "id": category_id,
            "name": category_name
        }
        object_id = id_converter.create_object_id(item_entry.findtext('Key'))
        object = {
            "category": category_id,
            "id": object_id,
            "name": item_entry.findtext('Name'),
            "row": 1,
            "stack": 200 if item_entry.findtext('Type') == "ItemStack" else 1
        }
        yield object, category


def extract_smelter_recipes(game_data: Path, id_converter: IdConverter, all_items: Dict, ore_smelter: Dict) -> Iterator[Tuple[Dict, List]]:
    for craft in ET.parse(game_data / 'SmelterRecipes.xml').getroot():
        used_items = list()
        craft_cost = dict()
        for cost in craft.findall("Costs/CraftCost"):
            object_id = id_converter.create_object_id(cost.findtext("Key"))
            used_items.append(object_id)
            craft_cost[object_id] = int(cost.findtext("Amount", default=0))
        object_id = id_converter.create_object_id(craft.findtext("CraftedKey"))
        used_items.append(object_id)
        receip = {
            "id": f'{object_id}-smelter',
            "name": f'{all_items[object_id]["name"]} (smelter)',
            "cost": 1000,
            "time": 2,
            "in": craft_cost,
            "out": { object_id: int(craft.findtext("CraftedAmount", default=0)) },
            "producers": [ore_smelter["id"]],
            "row": 0,
            "category": all_items[object_id]["category"]
        }
        yield receip, used_items


def icons_configuration() -> Dict[str, Tuple[int, int]]:
    icons_config_path = Path(__file__).parent / 'icons_fill.json'
    with icons_config_path.open() as icons_config_file:
        icons_config_json = json.load(icons_config_file)
    return {icon_name: (position['row'], position['col']) for icon_name, position in icons_config_json['icons'].items()}


def main():
    # Parse command line arguments
    parser = ArgumentParser()
    parser.add_argument('game', nargs='?', default='~/.steam/root/steam/steamapps/common/FortressCraft/Default/Data/', help='The directory with the FortressCraft Evolved! game files')
    args = parser.parse_args()

    game_data = Path(args.game).expanduser()

    id_converter = IdConverter()

    categories = dict()

    all_items = dict()
    for terrain, category in extract_terrain(game_data, id_converter):
        all_items[terrain["id"]] = terrain
        categories[category["id"]] = category
    for item, category in extract_items(game_data, id_converter):
        all_items[item["id"]] = item
        categories[category["id"]] = category

    used_items = dict()
    ore_smelter = all_items["ore-smelter"]
    ore_smelter["factory"] = { "speed": 1, "type": "electric", "usage": 4000 }
    used_items[ore_smelter["id"]] = ore_smelter

    data_recipes = dict()
    for receip, items in extract_smelter_recipes(game_data, id_converter, all_items, ore_smelter):
        data_recipes[receip["id"]] = receip
        for item_id in items:
            used_items[item_id] = all_items[item_id]

    icons_config = icons_configuration()
    icons_image, icons_positions = game_icons(game_data.parent.parent / 'FC_Linux_Universal_Data', icons_config)
    icons_image.save(Path(__file__).parent / 'icons.png')
    factoriolab_icons = {item: {"row": 19, "col": 15} for item in categories}
    factoriolab_icons.update({item: {"row": 19, "col": 15} for item in used_items.keys()})
    factoriolab_icons = {
        "no-icon": {
            "row": 19,
            "col": 15
        },
        "icons": factoriolab_icons
    }
    write(Path(__file__).parent / 'icons.json', factoriolab_icons, True)

    factoriolab_data = {
        "version": { "FortressCraft Evolved": "0.1" },
        "categories": list(categories.values()),
        "icons": [{"id": item, "position": icons_positions[item]} for item in categories] + [{"id": item, "position": icons_positions[item]} for item in used_items.keys()],
        "items": list(used_items.values()),
        "recipes": list(data_recipes.values())
    }
    write(Path(__file__).parent / 'data.json', factoriolab_data, True)

    factoriolab_hash = {
        "items": list(used_items.keys()),
        "factories": [ore_smelter["id"]],
        "recipes": list(data_recipes.keys())
    }
    write(Path(__file__).parent / 'hash.json', factoriolab_hash, True)


if __name__ == '__main__':
    main()