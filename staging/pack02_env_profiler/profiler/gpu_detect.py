#!/usr/bin/env python3
"""
Detects common GPU runtimes lightly. Safe checks only (no heavy CUDA calls).
"""
import shutil, json
from pathlib import Path

def detect():
    res = {"cuda": False, "nvidia_smi": False, "opencl": False}
    if shutil.which("nvidia-smi"):
        res["nvidia_smi"] = True
        res["cuda"] = True
    # OpenCL detection - try clinfo
    if shutil.which("clinfo"):
        res["opencl"] = True
    return res

if __name__ == "__main__":
    print(json.dumps(detect(), indent=2))
