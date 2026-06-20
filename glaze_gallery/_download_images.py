from typing import TypeVar, Any
import shutil
import json
from pathlib import Path
from dataclasses import dataclass, field
from tqdm import tqdm
from dotenv import load_dotenv
import pandas as pd
from PIL import Image
from glaze_gallery._random_dirs import create_random_dir
from glaze_gallery._google_api import GoogleDrive
from glaze_gallery._image_processing import Images, load_logo_image
from glaze_gallery._studios import _STUDIOS

_T = TypeVar("_T", bool, str)

_DOWNLOADS_DIR = Path("downloads")


@dataclass
class GlazeCombo:
    glaze1: str
    glaze2: str
    not_food_safe: bool
    runny: bool
    blister_jump_crawl: bool
    notes: str

    def __post_init__(self) -> None:
        self.glaze1_formatted = self._format_glaze(self.glaze1)
        self.glaze2_formatted = self._format_glaze(self.glaze2)
        self.glaze_combo = f"{self.glaze1_formatted}-{self.glaze2_formatted}"
        self.front_name_base = f"{self.glaze_combo}-front"
        self.back_name_base = f"{self.glaze_combo}-back"
        self.info: dict[str, bool | str] = {}
        if self.not_food_safe:
            self.info["notFoodSafe"] = self.not_food_safe
        if self.runny:
            self.info["runny"] = self.runny
        if self.blister_jump_crawl:
            self.info["blisterJumpCrawl"] = self.blister_jump_crawl
        if self.notes:
            self.info["notes"] = self.notes

    def _format_glaze(self, glaze: str) -> str:
        return "".join(glaze.split()).lower()


@dataclass
class GlazeData:
    downloads_dir: Path
    names: dict[str, str] = field(default_factory=dict)
    combo_info: dict[str, dict[str, bool | str]] = field(default_factory=dict)
    images_high: dict[str, str] = field(default_factory=dict)
    images_low: dict[str, str] = field(default_factory=dict)

    def _save_json(
        self,
        file_name: str,
        data: dict[str, Any],
    ) -> None:
        file_path = create_random_dir(self.downloads_dir) / file_name
        with open(file_path, "w") as f:
            print(json.dumps(data, separators=(",", ":"), sort_keys=True), file=f)
        with open(_DOWNLOADS_DIR / "paths.txt", "a") as f:
            print(file_path, file=f)

    def save(self) -> None:
        self._save_json("glaze-names.json", self.names)
        self._save_json("glaze-combo-info.json", self.combo_info)
        self._save_json("images-high.json", self.images_high)
        self._save_json("images-low.json", self.images_low)
        with open(self.downloads_dir / "robots.txt", "w") as f:
            print("User-agent: *\nDisallow: /", file=f)

    def save_images_and_update(
        self,
        combo: GlazeCombo,
        front_images: Images,
        back_images: Images | None,
        logo_im: Image.Image,
        logo_color: str,
    ) -> None:
        self.names[combo.glaze1_formatted] = combo.glaze1
        self.names[combo.glaze2_formatted] = combo.glaze2
        self.combo_info[combo.glaze_combo] = combo.info

        front_image_paths = front_images.save(
            self.downloads_dir, logo_im, logo_color
        )
        self.images_high[combo.front_name_base] = front_image_paths.high.dir_name
        self.images_low[combo.front_name_base] = front_image_paths.low.dir_name
        if back_images:
            back_image_paths = back_images.save(
                self.downloads_dir, logo_im, logo_color
            )
            self.images_high[combo.back_name_base] = back_image_paths.high.dir_name
            self.images_low[combo.back_name_base] = back_image_paths.low.dir_name


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


def download_images() -> None:
    load_dotenv()

    logos = {
        studio_key: load_logo_image(studio["logo_path"])
        for studio_key, studio in _STUDIOS.items()
    }

    google_drive = GoogleDrive()
    glaze_data = google_drive.get_glaze_data()
    google_drive.update_last_synced_cell()
    if _DOWNLOADS_DIR.is_dir():
        shutil.rmtree(_DOWNLOADS_DIR)
    _DOWNLOADS_DIR.mkdir()
    for studio in _STUDIOS.values():
        studio["downloads_dir"].mkdir()
    filtered_glaze_data = glaze_data[glaze_data["front_image"].astype(bool)]
    studio_glaze_data = {
        studio_key: GlazeData(studio["downloads_dir"])
        for studio_key, studio in _STUDIOS.items()
    }
    for i in tqdm(range(len(filtered_glaze_data))):
        image_data = filtered_glaze_data.iloc[i]
        hidden = {
            studio_key: _get_value(image_data, studio["hide_column"], bool)
            for studio_key, studio in _STUDIOS.items()
        }

        if all(hidden.values()):
            continue

        front_file_id = _get_value(image_data, "front_file_id", str)
        back_file_id = _get_value(image_data, "back_file_id", str, optional=True)
        combo = GlazeCombo(
            glaze1=_get_value(image_data, "glaze1", str),
            glaze2=_get_value(image_data, "glaze2", str),
            not_food_safe=_get_value(image_data, "not_food_safe", bool),
            runny=_get_value(image_data, "runny", bool),
            blister_jump_crawl=_get_value(image_data, "blister_jump_crawl", bool),
            notes=_get_value(image_data, "notes", str, optional=True),
        )

        front_images = Images(
            image_bytes=google_drive.download_glaze_image(front_file_id),
            file_name_base=combo.front_name_base,
        )
        back_images: Images | None = None
        if back_file_id:
            back_images = Images(
                image_bytes=google_drive.download_glaze_image(back_file_id),
                file_name_base=combo.back_name_base,
            )

        for studio_key, studio in _STUDIOS.items():
            if not hidden[studio_key]:
                studio_glaze_data[studio_key].save_images_and_update(
                    combo,
                    front_images,
                    back_images,
                    logos[studio_key],
                    studio["logo_color"],
                )

    for glaze_data_for_studio in studio_glaze_data.values():
        glaze_data_for_studio.save()
