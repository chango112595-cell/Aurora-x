#!/usr/bin/env python3
"""
Sandbox runner helper:
- For heavy tasks use Docker containers or subprocess with UID/GID drop
- This file provides a helper function to run a command in a minimal sandbox using 'subprocess' and optional 'timeout' and 'resource' limits (unix)
"""

import subprocess, shlex, os, sys, resource, pwd

def run_sandbox(cmd, timeout=30, uid_name="nobody"):
    args = shlex.split(cmd)
    def preexec():
        # drop privileges
        try:
            pw = pwd.getpwnam(uid_name)
            os.setgid(pw.pw_gid)
            os.setuid(pw.pw_uid)
        except Exception:
            pass
        # CPU / memory limits
        resource.setrlimit(resource.RLIMIT_AS, (200*1024*1024, 200*1024*1024))
        resource.setrlimit(resource.RLIMIT_CPU, (10, 10))
    p = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout, preexec_fn=preexec)
    return {"rc": p.returncode, "out": p.stdout.decode(), "err": p.stderr.decode()}
