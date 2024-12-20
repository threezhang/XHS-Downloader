from pathlib import Path
from subprocess import run

__all__ = []
ROOT = Path(__file__).resolve().parent


def scan_directory():
    return [
        item.joinpath("LC_MESSAGES/xhs.po")
        for item in ROOT.iterdir()
        if item.is_dir()
    ]


def generate_map(files: list[Path]):
    return [(i, i.with_suffix(".mo")) for i in files]


def generate_mo(maps: list[tuple[Path, Path]]):
    for i, j in maps:
        command = f"msgfmt \"{i}\" -o \"{j}\""
        print(run(command, shell=True, text=True))


if __name__ == "__main__":
    generate_mo(generate_map(scan_directory()))
