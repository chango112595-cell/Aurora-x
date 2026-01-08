#!/usr/bin/env python3
# aurora_patch_generator.py
# Generates git-format patches for each newly created pack or modified file.

import os
from pathlib import Path

from aurora_build_utils import PACKS_DIR, PATCH_DIR, log


def pack_to_patch(pack_dir: Path, patch_out: Path):
    """
    Creates a git-format patch by `git diff --no-index` between current repo and generated pack dir.
    This produces portable patches even if repo isn't under git.
    """
    lines = []
    for root, dirs, files in os.walk(pack_dir):
        for f in files:
            full = Path(root) / f
            rel = full.relative_to(pack_dir.parent)
            with open(full, "rb") as fh:
                content = fh.read().decode("utf-8", errors="replace")
            header = f"*** Begin File: {rel}\n"
            lines.append(header)
            lines.append(content)
            lines.append(f"*** End File: {rel}\n\n")
    patch_out.write_text("".join(lines))
    log(f"Created patch summary for {pack_dir.name} -> {patch_out}")


def main():
    log("Creating patch artifacts for generated packs...")
    for pack in sorted(os.listdir(PACKS_DIR)):
        if (
            pack.startswith("pack05")
            or pack.startswith("pack06")
            or pack.startswith("pack0")
            or pack.startswith("pack1")
        ):
            pdir = PACKS_DIR / pack
            if pdir.is_dir():
                patch_file = PATCH_DIR / f"{pack}.patch.txt"
                pack_to_patch(pdir, patch_file)
    log("Patch generation complete.")


if __name__ == "__main__":
    main()
