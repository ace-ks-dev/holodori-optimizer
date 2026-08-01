from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Iterable

from .constants import APP_VERSION


def sha256_file(path: str | Path) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def build_info(master: dict, *, generated_at: str | None = None) -> dict:
    if generated_at is None:
        generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    coverage = sum(1 for c in master["cards"] if c.get("assetId"))
    return {
        "appVersion": APP_VERSION,
        "pipelineVersion": APP_VERSION,
        "generatedAtUTC": generated_at,
        "source": master["source"],
        "sourceVersion": master["sourceVersion"],
        "cardCount": len(master["cards"]),
        "counts": master["counts"],
        "assetIdCoverage": coverage,
        "schemaVersion": master["schemaVersion"],
    }


def asset_manifest(master: dict) -> dict:
    return {
        "schemaVersion": 1,
        "sourceVersion": master["sourceVersion"],
        "cards": [
            {
                "id": c["id"],
                "assetId": c.get("assetId"),
                "characterId": c["characterId"],
                "member": c["member"],
                "name": c["name"],
                "rarity": c["rarity"],
                "attribute": c["attribute"],
            }
            for c in master["cards"]
        ],
    }


def write_manifest(out_path: str | Path, *, build: dict, artifact_paths: Iterable[str | Path]) -> dict:
    files = {}
    for p in artifact_paths:
        p = Path(p)
        files[p.name] = {"sizeBytes": p.stat().st_size, "sha256": sha256_file(p)}
    manifest = {**build, "files": files}
    Path(out_path).write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return manifest
