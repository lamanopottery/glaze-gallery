from typing import TypeVar, Any
import shutil
from pathlib import Path
import json
from tqdm import tqdm
from dotenv import load_dotenv
import pandas as pd
from glaze_gallery._constants import (
    DOWNLOADS_DIR,
    LA_MANO_DOWNLOADS_DIR,
    MUD_MATTERS_DOWNLOADS_DIR,
    LA_MANO_R2_DIR,
    MUD_MATTERS_R2_DIR,
)
from glaze_gallery._google_api import GoogleDrive
from glaze_gallery._r2 import save_to_local_r2
from glaze_gallery._image_processing import Images


_T = TypeVar("_T", bool, str)


def _format_glaze(glaze: str) -> str:
    return "".join(glaze.split()).lower()


def _get_value(
    image_data: "pd.Series[str]",
    name: str,
    expected_type: type[_T],
    optional: bool = False,
) -> _T:
    value_str = image_data[name]
    value: _T
    if issubclass(expected_type, bool):
        value = value_str == "TRUE"
    else:
        value = value_str
    if isinstance(value, expected_type) and (
        optional or (value is not None and value != "")
    ):
        return value
    image_name = image_data["front_image"]
    raise TypeError(f"property '{name}' of '{image_name}' is {value!r}")


def _save_json(
    downloads_dir: Path,
    r2_dir: str,
    file_name: str,
    data: dict[str, Any],
    sort_keys: bool = True,
) -> None:
    file_path = downloads_dir / file_name
    with open(file_path, "w") as f:
        f.write(json.dumps(data, separators=(",", ":"), sort_keys=sort_keys))
    save_to_local_r2(file_path, f"{r2_dir}/{file_name}")


def download() -> None:
    load_dotenv()
    google_drive = GoogleDrive()
    glaze_data = google_drive.get_glaze_data()
    if DOWNLOADS_DIR.is_dir():
        shutil.rmtree(DOWNLOADS_DIR)
    DOWNLOADS_DIR.mkdir()
    LA_MANO_DOWNLOADS_DIR.mkdir()
    MUD_MATTERS_DOWNLOADS_DIR.mkdir()
    filtered_glaze_data = glaze_data[glaze_data["front_image"].astype(bool)]
    la_mano_glazes = {}
    la_mano_glaze_combos = {}
    mud_matters_glazes = {}
    mud_matters_glaze_combos = {}
    for i in tqdm(range(len(filtered_glaze_data))):
        image_data = filtered_glaze_data.iloc[i]
        hide_la_mano = _get_value(image_data, "hide_la_mano", bool)
        hide_mud_matters = _get_value(image_data, "hide_mud_matters", bool)

        if hide_la_mano and hide_mud_matters:
            continue

        front_file_id = _get_value(image_data, "front_file_id", str)
        back_file_id = _get_value(image_data, "back_file_id", str, optional=True)
        glaze1 = _get_value(image_data, "glaze1", str)
        glaze2 = _get_value(image_data, "glaze2", str)

        glaze1_formatted = _format_glaze(glaze1)
        glaze2_formatted = _format_glaze(glaze2)
        glaze_combo = f"{glaze1_formatted}-{glaze2_formatted}"

        glaze_combo_data: dict[str, bool | str] = {}
        not_food_safe = _get_value(image_data, "not_food_safe", bool)
        runny = _get_value(image_data, "runny", bool)
        blister_jump_crawl = _get_value(image_data, "blister_jump_crawl", bool)
        notes = _get_value(image_data, "notes", str, optional=True)
        if not_food_safe:
            glaze_combo_data["notFoodSafe"] = not_food_safe
        if runny:
            glaze_combo_data["runny"] = runny
        if blister_jump_crawl:
            glaze_combo_data["blisterJumpCrawl"] = blister_jump_crawl
        if notes:
            glaze_combo_data["notes"] = notes

        front_images = Images(
            image_bytes=google_drive.download_glaze_image(front_file_id),
            file_name_base=f"{glaze_combo}-front",
        )
        back_images: Images | None = None
        if back_file_id:
            back_images = Images(
                image_bytes=google_drive.download_glaze_image(back_file_id),
                file_name_base=f"{glaze_combo}-back",
            )

        if not hide_la_mano:
            la_mano_glazes[glaze1_formatted] = glaze1
            la_mano_glazes[glaze2_formatted] = glaze2
            la_mano_glaze_combos[glaze_combo] = glaze_combo_data
            front_images.save(LA_MANO_DOWNLOADS_DIR, LA_MANO_R2_DIR)
            if back_images:
                back_images.save(LA_MANO_DOWNLOADS_DIR, LA_MANO_R2_DIR)
        if not hide_mud_matters:
            mud_matters_glazes[glaze1_formatted] = glaze1
            mud_matters_glazes[glaze2_formatted] = glaze2
            mud_matters_glaze_combos[glaze_combo] = glaze_combo_data
            front_images.save(MUD_MATTERS_DOWNLOADS_DIR, MUD_MATTERS_R2_DIR)
            if back_images:
                back_images.save(MUD_MATTERS_DOWNLOADS_DIR, MUD_MATTERS_R2_DIR)

    _save_json(
        LA_MANO_DOWNLOADS_DIR,
        LA_MANO_R2_DIR,
        file_name="glazes.json",
        data=la_mano_glazes,
    )
    _save_json(
        LA_MANO_DOWNLOADS_DIR,
        LA_MANO_R2_DIR,
        file_name="glaze-combos.json",
        data=la_mano_glaze_combos,
    )
    _save_json(
        MUD_MATTERS_DOWNLOADS_DIR,
        MUD_MATTERS_R2_DIR,
        file_name="glazes.json",
        data=mud_matters_glazes,
    )
    _save_json(
        MUD_MATTERS_DOWNLOADS_DIR,
        MUD_MATTERS_R2_DIR,
        file_name="glaze-combos.json",
        data=mud_matters_glaze_combos,
    )
