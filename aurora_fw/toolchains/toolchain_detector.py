#!/usr/bin/env python3
"""
Detect installed toolchains and suggest candidate toolchains for targets.
Offline-first: looks at PATH & common install locations.
"""

import shutil

COMMON = {
    "esp32": ["xtensa-esp32-elf-gcc", "esp-idf"],
    "cortex-m": ["arm-none-eabi-gcc", "openocd"],
    "riscv": ["riscv64-unknown-elf-gcc"],
    "x86": ["gcc", "clang"],
}


def detect():
    found = {}
    for key, cmds in COMMON.items():
        found[key] = []
        for c in cmds:
            p = shutil.which(c)
            if p:
                found[key].append({"cmd": c, "path": p})
    # also search PATH for toolchain prefixes
    return found


if __name__ == "__main__":
    print(detect())
