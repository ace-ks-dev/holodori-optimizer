from __future__ import annotations

import io
import json
import os
from pathlib import Path
import urllib.request
import zipfile

from .constants import RAW_BASE_URL, RAW_FILES


class RawDataError(RuntimeError):
    pass


def _unwrap_rows(value, name: str):
    if not isinstance(value, list):
        raise RawDataError(f"{name} is missing or is not an array")
    return value


def _zip_member_by_basename(zf: zipfile.ZipFile, basename: str) -> str:
    matches = [n for n in zf.namelist() if n.rstrip("/").split("/")[-1] == basename]
    if len(matches) != 1:
        raise RawDataError(f"Expected exactly one {basename} in ZIP, found {len(matches)}")
    return matches[0]


def load_raw(source: str | os.PathLike) -> tuple[dict[str, list], str]:
    """Load the subset of HolodoriDB required by the optimizer.

    `source` may be a checked-out repository directory or a ZIP archive. Returns
    (raw_tables, source_version).
    """
    path = Path(source)
    if not path.exists():
        raise RawDataError(f"Raw database source does not exist: {path}")

    raw: dict[str, list] = {}
    if path.is_dir():
        for name in RAW_FILES:
            matches = list(path.rglob(name))
            if len(matches) != 1:
                raise RawDataError(f"Expected exactly one {name} below {path}, found {len(matches)}")
            with matches[0].open("r", encoding="utf-8") as fh:
                raw[name] = _unwrap_rows(json.load(fh), name)
        versions = list(path.rglob("version.txt"))
        source_version = versions[0].read_text(encoding="utf-8").strip() if versions else "unknown"
        return raw, source_version

    if zipfile.is_zipfile(path):
        with zipfile.ZipFile(path) as zf:
            for name in RAW_FILES:
                member = _zip_member_by_basename(zf, name)
                raw[name] = _unwrap_rows(json.loads(zf.read(member).decode("utf-8")), name)
            try:
                version_member = _zip_member_by_basename(zf, "version.txt")
                source_version = zf.read(version_member).decode("utf-8").strip()
            except RawDataError:
                source_version = "unknown"
        return raw, source_version

    raise RawDataError(f"Unsupported raw database source: {path}")


def fetch_raw(base_url: str = RAW_BASE_URL, timeout: int = 30) -> tuple[dict[str, list], str]:
    """Fetch the current required raw tables using only the Python standard library."""
    def get_text(url: str) -> str:
        req = urllib.request.Request(url, headers={"User-Agent": "Holodori-Optimizer-Python/2.2"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read().decode("utf-8")

    source_version = get_text(base_url + "version.txt").strip()
    raw = {}
    for name in RAW_FILES:
        raw[name] = _unwrap_rows(json.loads(get_text(base_url + name)), name)
    return raw, source_version
