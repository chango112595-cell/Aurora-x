#!/usr/bin/env python3
"""
node_bridge.py - simple helper to create node script runners in pack vfs.
It writes a small runner.js into the pack vfs and invokes node via runtime_loader.
"""

from .vfs import VirtualFS


def write_runner(pack_id: str, js_source: str, name="runner.js"):
    v = VirtualFS(pack_id)
    path = v.path(name)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(js_source)
    return str(path)


def sample_runner_js():
    return """console.log('node runner OK');"""


if __name__ == "__main__":
    import argparse

    p = argparse.ArgumentParser()
    p.add_argument("pack")
    p.add_argument("--name", default="runner.js")
    args = p.parse_args()
    pth = write_runner(args.pack, sample_runner_js(), name=args.name)
    print(pth)
