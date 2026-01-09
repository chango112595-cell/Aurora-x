#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from aurora_hybrid_core import AuroraHybridCore


def main():
    parser = argparse.ArgumentParser(description="Aurora Hybrid System")
    parser.add_argument("command", choices=["generate", "test", "inspect", "run", "status"])
    parser.add_argument("--count", type=int, default=550, help="Number of modules to generate")
    parser.add_argument("--module", type=str, help="Module path for test/inspect")
    parser.add_argument("--code", type=str, help="Code to run in sandbox")
    parser.add_argument("--mode", choices=["pure", "hybrid"], default="hybrid")
    args = parser.parse_args()

    core = AuroraHybridCore()

    if args.command == "generate":
        result = core.generate_modules(args.count)
        print(f"Generated {result['generated']} modules")
        print(f"Registry: {result['registry']}")
    elif args.command == "test":
        if not args.module:
            print("Error: --module required")
            sys.exit(1)
        result = core.test_module(args.module)
        print(f"Test result: {result}")
    elif args.command == "inspect":
        if not args.module:
            print("Error: --module required")
            sys.exit(1)
        result = core.inspect_module(args.module)
        print(f"Inspection: {result}")
    elif args.command == "run":
        if not args.code:
            print("Error: --code required")
            sys.exit(1)
        result = core.run_in_sandbox(args.code, args.mode)
        print(f"Result: {result}")
    elif args.command == "status":
        status = core.get_status()
        print(f"Status: {status}")
    core.shutdown()


if __name__ == "__main__":
    main()
