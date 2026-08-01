#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

THIS = Path(__file__).resolve()
PY_ROOT = THIS.parent
PROJECT_ROOT = PY_ROOT.parent
sys.path.insert(0, str(PY_ROOT))

from holodori_optimizer.constants import APP_VERSION
from holodori_optimizer.htmlbuild import build_html
from holodori_optimizer.normalize import normalize_master
from holodori_optimizer.rawio import fetch_raw, load_raw
from holodori_optimizer.release import asset_manifest, build_info, write_manifest
from holodori_optimizer.validate import validate_master


def parse_args():
    ap = argparse.ArgumentParser(description="Build Holodori Optimizer v2.2 from raw HolodoriDB data")
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--db", help="Path to holodori-db-eng-diff checkout or ZIP")
    src.add_argument("--fetch", action="store_true", help="Fetch current public HolodoriDB raw tables")
    ap.add_argument("--out", default=str(PROJECT_ROOT / "dist"), help="Output directory")
    ap.add_argument("--template", default=str(PROJECT_ROOT / "source" / "optimizer_template.html"))
    ap.add_argument("--worker", default=str(PROJECT_ROOT / "source" / "worker.js"))
    ap.add_argument("--generated-at", default=None, help="Override generatedAtUTC for reproducible builds")
    return ap.parse_args()


def main() -> int:
    args = parse_args()
    raw, version = fetch_raw() if args.fetch else load_raw(args.db)
    master = validate_master(normalize_master(raw, version))
    build = build_info(master, generated_at=args.generated_at)

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    html_path = out / f"Holodori_Optimizer_v{APP_VERSION}.html"
    snapshot_path = out / "HolodoriDB_Bundled_Normalized_Snapshot.json"
    assets_path = out / "HolodoriDB_Card_Asset_Manifest.json"
    manifest_path = out / "BUILD_MANIFEST.json"

    snapshot_path.write_text(json.dumps(master, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    assets_path.write_text(json.dumps(asset_manifest(master), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    html_path.write_text(build_html(args.template, args.worker, master, build), encoding="utf-8")
    write_manifest(manifest_path, build=build, artifact_paths=[html_path, snapshot_path, assets_path, args.worker, args.template])

    print(f"Built Holodori Optimizer v{APP_VERSION}")
    print(f"  source version: {version}")
    print(f"  cards: {len(master['cards'])} ({master['counts']})")
    print(f"  asset IDs: {build['assetIdCoverage']}/{build['cardCount']}")
    print(f"  output: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
