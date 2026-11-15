"""Reads and writes the app's data; the tools go through it."""

import json
import unicodedata
from functools import cache
from pathlib import Path

from know_your_corner.schemas import Neighborhood

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def _key(name: str) -> str:
    plain = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
    return " ".join(plain.lower().split())


@cache
def neighborhoods() -> tuple[Neighborhood, ...]:
    rows = json.loads((DATA_DIR / "neighborhoods.json").read_text(encoding="utf-8"))
    return tuple(Neighborhood.model_validate(r) for r in rows)


def find_neighborhood(name: str) -> Neighborhood | None:
    wanted = _key(name)
    for n in neighborhoods():
        if wanted in {_key(n.name), *map(_key, n.aliases)}:
            return n
    return None