import uuid
from pathlib import Path


def random_str() -> str:
    return uuid.uuid4().hex


def create_random_dir(base_dir: Path) -> Path:
    random_dir = base_dir / random_str()
    random_dir.mkdir()
    return random_dir
