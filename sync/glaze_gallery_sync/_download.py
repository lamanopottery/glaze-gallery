from typing import TypeVar, Any
import os
import shutil
import json
from tqdm import tqdm
from dotenv import load_dotenv
import pandas as pd
from glaze_gallery_sync._google_api import GoogleDrive

_DOWNLOADS_DIR = "downloads"

_T = TypeVar("_T")


def _format_glaze(glaze: str) -> str:
    return "".join(glaze.split()).lower()


def _get_value(
    image_data: pd.Series, name: str, expected_type: type[_T], optional: bool = False
) -> _T:
    value = image_data[name]
    if expected_type is bool:
        value = value == "TRUE"
    if isinstance(value, expected_type) and (
        optional or (value is not None and value != "")
    ):
        return value
    image_name = image_data["front_image"]
    raise TypeError(f"property '{name}' of '{image_name}' is {value!r}")


def _save_json(
    directory: str, file_name: str, data: dict[str, Any], sort_keys: bool = True
) -> None:
    with open(os.path.join(directory, file_name), "w") as f:
        print(json.dumps(data, sort_keys=sort_keys, indent=2), file=f)


def download() -> None:
    load_dotenv()
    google_drive = GoogleDrive()
    glaze_data = google_drive.get_glaze_data()
    shutil.rmtree(_DOWNLOADS_DIR)
    os.mkdir(_DOWNLOADS_DIR)
    filtered_glaze_data = glaze_data[glaze_data["front_image"].astype(bool)]
    la_mano_glazes = {}
    la_mano_glaze_combos = set()
    mud_matters_glazes = {}
    mud_matters_glaze_combos = set()
    for i in tqdm(range(len(filtered_glaze_data))):
        image_data = filtered_glaze_data.iloc[i]
        front_file_id = _get_value(image_data, "front_file_id", str)
        back_file_id = _get_value(image_data, "back_file_id", str, optional=True)
        glaze1 = _get_value(image_data, "glaze1", str)
        glaze2 = _get_value(image_data, "glaze2", str)
        hide_la_mano = _get_value(image_data, "hide_la_mano", bool)
        hide_mud_matters = _get_value(image_data, "hide_mud_matters", bool)

        if hide_la_mano and hide_mud_matters:
            continue

        glaze1_formatted = _format_glaze(glaze1)
        glaze2_formatted = _format_glaze(glaze2)
        glaze_combo = f"{glaze1_formatted}-{glaze2_formatted}"
        glaze_dir = os.path.join(_DOWNLOADS_DIR, glaze_combo)

        google_drive.download_glaze_image(
            front_file_id,
            glaze_dir,
            glaze_combo,
            side="front",
        )
        if back_file_id:
            google_drive.download_glaze_image(
                back_file_id,
                glaze_dir,
                glaze_combo,
                side="back",
            )

        glaze_combo_data = {
            "not_food_safe": _get_value(image_data, "not_food_safe", bool),
            "runny": _get_value(image_data, "runny", bool),
            "blister_jump_crawl": _get_value(image_data, "blister_jump_crawl", bool),
            "notes": _get_value(image_data, "notes", str, optional=True),
        }
        _save_json(
            directory=glaze_dir,
            file_name=f"{glaze_combo}-data.json",
            data=glaze_combo_data,
            sort_keys=False,
        )

        if not hide_la_mano:
            la_mano_glazes[glaze1_formatted] = glaze1
            la_mano_glazes[glaze2_formatted] = glaze2
            la_mano_glaze_combos.add(glaze_combo)
        if not hide_mud_matters:
            mud_matters_glazes[glaze1_formatted] = glaze1
            mud_matters_glazes[glaze2_formatted] = glaze2
            mud_matters_glaze_combos.add(glaze_combo)

    _save_json(
        directory=_DOWNLOADS_DIR,
        file_name="la-mano-glazes.json",
        data=la_mano_glazes,
    )
    _save_json(
        directory=_DOWNLOADS_DIR,
        file_name="la-mano-glaze-combos.json",
        data=list(la_mano_glaze_combos),
    )
    _save_json(
        directory=_DOWNLOADS_DIR,
        file_name="mud-matters-glazes.json",
        data=mud_matters_glazes,
    )
    _save_json(
        directory=_DOWNLOADS_DIR,
        file_name="mud-matters-glaze-combos.json",
        data=list(mud_matters_glaze_combos),
    )
