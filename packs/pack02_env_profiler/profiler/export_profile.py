#!/usr/bin/env python3
"""
Orchestrates probe, perf tests (safe by default), GPU detection, scoring, and writes
the final profile to live/environment/profile.json
"""
import argparse, json, os, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LIVE_ENV_DIR = ROOT.parents[0] / "live" / "environment"
LIVE_ENV_DIR.mkdir(parents=True, exist_ok=True)
PROFILE_PATH = LIVE_ENV_DIR / "profile.json"
TMP_PATH = Path("profile_tmp.json")

def run_cmd(cmd):
    try:
        out = subprocess.check_output(cmd, shell=True, stderr=subprocess.DEVNULL, timeout=30)
        return out.decode()
    except Exception:
        return None

def load_probe():
    out = run_cmd(f"python3 {Path(__file__).parent/'device_probe.py'} --safe")
    if out:
        return json.loads(out)
    return {"basic":{}, "details":{}}

def load_gpu():
    out = run_cmd(f"python3 {Path(__file__).parent/'gpu_detect.py'}")
    if out:
        return json.loads(out)
    return {}

def run_perf(deep=False):
    cmd = f"python3 {Path(__file__).parent/'perf_test.py'}"
    if deep:
        cmd += " --deep"
    out = run_cmd(cmd)
    if out:
        try:
            return eval(out.strip()) if out.strip().startswith("{") else {"raw": out.strip()}
        except Exception:
            return {"raw": out.strip()}
    return {}

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--auto-deep", action="store_true", help="Auto-run deep tests based on heuristics and operator prompt.")
    p.add_argument("--assume-no-interactive", action="store_true", help="If set assume operator consent is NO for deep tests.")
    p.add_argument("--dry", action="store_true", help="Write profile to tmp only.")
    args = p.parse_args()

    profile = {}
    profile["probe"] = load_probe()
    profile["gpu"] = load_gpu()

    # decide deep test
    allow_deep = False
    # heuristic: if cores >= 8 and has_node, allow deep
    cores = profile["probe"].get("basic",{}).get("cores",1)
    has_node = profile["probe"].get("basic",{}).get("has_node", False)
    if args.auto_deep and cores >= 8:
        if args.assume_no_interactive:
            allow_deep = False
        else:
            # ask operator
            try:
                ans = input(f"Detected {cores} cores. Run deeper perf tests? Type YES to allow: ")
                allow_deep = (ans.strip().upper() == "YES")
            except Exception:
                allow_deep = False

    profile["perf"] = run_perf(deep=allow_deep)
    # scoring
    try:
        sc = run_cmd(f"python3 {Path(__file__).parent/'env_score.py'}")
        # env_score expects profile_tmp.json to be present
        Path("profile_tmp.json").write_text(json.dumps(profile))
        sc = run_cmd(f"python3 {Path(__file__).parent/'env_score.py'}")
        if sc:
            profile["score"] = json.loads(sc)
    except Exception:
        profile["score"] = {"error": "scoring failed"}

    profile["summary"] = {"status": "ok", "recommended_mode": profile.get("score",{}).get("recommended_mode","unknown")}
    # write
    if args.dry:
        Path("profile_tmp.json").write_text(json.dumps(profile, indent=2))
        print("Wrote profile_tmp.json")
    else:
        LIVE_ENV_DIR.mkdir(parents=True, exist_ok=True)
        PROFILE_PATH.write_text(json.dumps(profile, indent=2))
        print("Wrote profile to", PROFILE_PATH)
    return 0

if __name__ == "__main__":
    main()
