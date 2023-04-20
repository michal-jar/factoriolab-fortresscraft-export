from argparse import ArgumentParser
from pathlib import Path
from typing import Dict, List, Tuple, Union, Iterator, Callable, Optional, cast
from PIL import Image
from UnityPy.classes import Texture2D, Sprite
from UnityPy.enums import ClassIDType
import UnityPy
import json


def crop_box_x(image_size: Tuple[int, int], start_position: int, end_position: Optional[int]) -> Tuple[int, int, int, int]:
    return (start_position, 0, end_position if end_position else image_size[0], image_size[1])


def crop_box_y(image_size: Tuple[int, int], start_position: int, end_position: Optional[int]) -> Tuple[int, int, int, int]:
    return (0, start_position, image_size[0], end_position if end_position else image_size[1])


def projection_x(image_projection: Tuple[List[int], List[int]]) -> List[int]:
    return image_projection[0]


def projection_y(image_projection: Tuple[List[int], List[int]]) -> List[int]:
    return image_projection[1]


def split_image(image: Image.Image, projection_extractor: Callable[[Tuple[List[int], List[int]]], List[int]], crop_box_builder: Callable[[Tuple[int, int], int, Optional[int]], Tuple[int, int, int, int]], debug: bool = False, debug_name: str = 'image part') -> Iterator[Image.Image]:
    previous_projection = 0
    start_position = 0
    debug_index = 0
    for current_position, current_projection in enumerate(projection_extractor(image.getprojection())):
        if previous_projection != current_projection:
            previous_projection = current_projection
            if current_projection == 1:
                start_position = current_position
            if current_projection == 0:
                if current_position - start_position < 5:
                    if debug:
                        print(f'Skipping element (would be {debug_index:02}. {debug_name}) of size {current_position - start_position}px ({start_position}-{current_position}) as too small.')
                    continue
                crop_box = crop_box_builder(image.size, start_position, current_position)
                if debug:
                    print(f'{debug_index:02}. {debug_name} - size {crop_box[2] - crop_box[0]}x{crop_box[3] - crop_box[1]}px - {start_position}-{current_position}')
                    debug_index += 1
                yield image.crop(crop_box)
    else:
        if previous_projection == 1:
            crop_box = crop_box_builder(image.size, start_position, None)
            if debug:
                print(f'{debug_index:02}. {debug_name} - size {crop_box[2] - crop_box[0]}x{crop_box[3] - crop_box[1]}px - {start_position}')
            yield image.crop(crop_box)


def asset_image_objects(game_data: Path) -> Iterator[Tuple[ClassIDType, Union[Texture2D, Sprite]]]:
    env = UnityPy.load(game_data.absolute().as_posix())
    print(f'assets = {len(env.assets)}')
    print(f'conteiners = {len(env.container)}')
    print(f'objects = {len(env.objects)}')
    for obj in env.objects:
        if obj.type == ClassIDType.Texture2D:
            yield (obj.type, cast(Texture2D, obj.read()))
        elif obj.type == ClassIDType.Sprite:
            yield (obj.type, cast(Sprite, obj.read()))

def main():
    # Parse command line arguments
    parser = ArgumentParser()
    parser.add_argument('game', nargs='?', default='~/.steam/root/steam/steamapps/common/FortressCraft/FC_Linux_Universal_Data/', help='The directory with the FortressCraft Evolved! game files')
    args = parser.parse_args()

    game_data = Path(args.game).expanduser()

    obj_dict = dict()
    for img_type, data in asset_image_objects(game_data):
        obj_dict.setdefault(img_type.name, dict()).setdefault(data.assets_file.name, list()).append({'file': data.assets_file.name, 'name': data.name, 'type': img_type.name, 'path_id': data.path_id})
        # try:
        #     data.image.save(Path(__file__).parent / 'assets' / f'{data.name}.png')
        # except:
        #     print(f'Failed to save image: {data.assets_file.name}/{data.name}.png of type {img_type.name}')
        if data.name == 'BlockPreview':
            img = data.image
            icons = [[icon for icon in split_image(icons_row, projection_x, crop_box_x)] for icons_row in split_image(img, projection_y, crop_box_y)]
            icons.reverse()
            # icons[26][7].show()
            # icons[4][4].show()

    output_file = Path(__file__).parent / 'assets.json'
    output_file.write_text(json.dumps({'game_assets': obj_dict}, indent=4))


if __name__ == '__main__':
    main()