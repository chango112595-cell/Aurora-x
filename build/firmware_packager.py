#!/usr/bin/env python3
import tarfile, sys, os, subprocess
from pathlib import Path

def make_package(src_dir, out_file):
    with tarfile.open(out_file, "w:gz") as tf:
        tf.add(src_dir, arcname=".")
    return out_file

def sign(path):
    subprocess.check_call(["gpg","--armor","--detach-sign", str(path)])
    return str(path)+".asc"

if __name__=="__main__":
    src = sys.argv[1]
    out = sys.argv[2]
    p = make_package(src, out)
    print("Packaged:", p)
    sign(p)
