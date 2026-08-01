from __future__ import annotations

import json
from pathlib import Path

from .pack import pack_master


def build_html(template_path: str | Path, worker_path: str | Path, master: dict, build_info: dict) -> str:
    template = Path(template_path).read_text(encoding="utf-8")
    worker = Path(worker_path).read_text(encoding="utf-8")
    packed = pack_master(master)

    replacements = {
        "__WORKER_TEMPLATE__": json.dumps(worker, ensure_ascii=False, separators=(",", ":")),
        "__BUNDLED_PACKED__": json.dumps(packed, ensure_ascii=False, separators=(",", ":")),
        "__BUILD_INFO__": json.dumps(build_info, ensure_ascii=False, separators=(",", ":")),
    }
    out = template
    for marker, value in replacements.items():
        count = out.count(marker)
        if count != 1:
            raise RuntimeError(f"Expected one {marker} placeholder in template, found {count}")
        out = out.replace(marker, value)
    return out
