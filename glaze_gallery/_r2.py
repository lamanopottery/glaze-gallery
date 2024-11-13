import subprocess
from pathlib import Path


def save_to_local_r2(file_path: Path, r2_path: str) -> None:
    subprocess.run(
        [
            "yarn",
            "wrangler",
            "r2",
            "object",
            "put",
            r2_path,
            "--file",
            file_path,
            "--local",
        ],
        stdout=subprocess.DEVNULL,
    )
