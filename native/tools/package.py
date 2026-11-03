"""Packages the shipped bundle as a registry file: native/target/spider_man-<version>.hnmod.

A `.hnmod` is a zip of `horizon-native.json` (what the launcher reads: the mod's id and version and the exact
Horizon and horizon-mixins commits it builds on) and the bundle's sources under `mixins/<id>/`, with the
repository's LICENSE beside them. Entries are sorted and dated alike, so the same sources give the same bytes.

Usage: package.py (after tools/release.sh). The mod pins one Horizon commit: it hooks game functions beyond the
stable hook points, so its manifest names no `hooks` version.
"""

import hashlib
import json
import sys
import tomllib
import zipfile
from pathlib import Path

NATIVE = Path(__file__).resolve().parent.parent
GAME = "26.3"


def main():
    compat = json.loads((NATIVE / "compatibility.json").read_text())
    bundles = sorted(p for p in (NATIVE / "mixins").iterdir() if (p / "horizon-mixin.toml").is_file())
    if len(bundles) != 1:
        sys.exit(f"expected one bundle in native/mixins/, found {[b.name for b in bundles]}")
    bundle = bundles[0]
    source = tomllib.loads((bundle / "horizon-mixin.toml").read_text())
    mod_id, version = source["mod"]["id"], source["mod"]["version"]
    if source["compatibility"]["horizon_revision"] != compat["horizon_revision"]:
        sys.exit("horizon-mixin.toml and compatibility.json pin different Horizon commits: run tools/release.sh")
    manifest = {
        "schema": 1,
        "id": mod_id,
        "version": version,
        "game": GAME,
        "horizon": compat["horizon_revision"],
        "mixins": compat["horizon_mixins_revision"],
    }
    files = {"horizon-native.json": (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode()}
    for path in sorted(bundle.rglob("*")):
        if path.is_file() and path.suffix in (".rs", ".toml"):
            files[f"mixins/{mod_id}/{path.relative_to(bundle).as_posix()}"] = path.read_bytes()
    files[f"mixins/{mod_id}/LICENSE"] = (NATIVE.parent / "LICENSE").read_bytes()
    out = NATIVE / "target" / f"{mod_id}-{version}.hnmod"
    out.parent.mkdir(exist_ok=True)
    with zipfile.ZipFile(out, "w") as archive:
        for name, content in sorted(files.items()):
            info = zipfile.ZipInfo(name, (2026, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, content)
    data = out.read_bytes()
    print(json.dumps({"file": str(out), "size": len(data), "sha256": hashlib.sha256(data).hexdigest()}, indent=2))


if __name__ == "__main__":
    main()
