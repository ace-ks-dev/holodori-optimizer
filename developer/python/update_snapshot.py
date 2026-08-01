#!/usr/bin/env python3
"""Fetch the current public HolodoriDB data and write a validated normalized snapshot.

This is a lightweight data-only command; build_release.py --fetch additionally produces
an HTML release and manifests.
"""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from holodori_optimizer.normalize import normalize_master
from holodori_optimizer.rawio import fetch_raw
from holodori_optimizer.validate import validate_master

ap=argparse.ArgumentParser(); ap.add_argument('--out',default='HolodoriDB_Bundled_Normalized_Snapshot.json')
args=ap.parse_args()
raw,ver=fetch_raw(); master=validate_master(normalize_master(raw,ver))
Path(args.out).write_text(json.dumps(master,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(f'Wrote {args.out}: {len(master["cards"])} cards, source {ver}')
