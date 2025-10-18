

GENERIC = """#!/usr/bin/env python3
import argparse

def main():
    parser = argparse.ArgumentParser(description={desc!r})
    parser.add_argument('--input', '-i', help='optional input')
    args = parser.parse_args()
    print("CLI tool ready.", "input=", args.input)

if __name__ == '__main__':
    main()
"""

def render_cli(name: str, brief: str) -> str:
    desc = brief or f"{name} command-line tool"
    return GENERIC.format(desc=desc)
