from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
LEGACY_ALIASES = {
    "DataBase1": REPO_ROOT / "data" / "database1",
    "DataBase2": REPO_ROOT / "data" / "database2",
    "Results-DataBase1": REPO_ROOT / "results" / "legacy" / "database1",
    "Results-DataBase2": REPO_ROOT / "results" / "legacy" / "database2",
}


def project_root():
    return REPO_ROOT


def resolve_path(path_like):
    candidate = Path(path_like)

    if candidate.is_absolute():
        if candidate.exists():
            return candidate
        raise FileNotFoundError(f"Path '{candidate.as_posix()}' does not exist.")

    direct_path = REPO_ROOT / candidate
    if direct_path.exists():
        return direct_path

    if candidate.parts and candidate.parts[0] in LEGACY_ALIASES:
        translated_path = LEGACY_ALIASES[candidate.parts[0]].joinpath(
            *candidate.parts[1:]
        )
        if translated_path.exists():
            return translated_path

    raise FileNotFoundError(f"Path '{candidate.as_posix()}' does not exist.")


def read_pair(path_like):
    path = resolve_path(path_like)

    with path.open("r", encoding="utf-8") as file:
        lines = ["".join(line.split()) for line in file if line.strip()]

    if len(lines) < 2:
        raise ValueError(
            f"Expected at least two non-empty lines in '{to_repo_relative(path)}'."
        )

    return lines[0], lines[1]


def to_repo_relative(path_like):
    path = Path(path_like)
    try:
        return path.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return path.as_posix()
