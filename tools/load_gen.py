#!/usr/bin/env python3
import argparse, os, requests, threading, time

p=argparse.ArgumentParser()
aurora_host = os.getenv("AURORA_HOST", "127.0.0.1")
p.add_argument("--url", default=os.getenv("AURORA_BASE_URL", f"http://{aurora_host}:5000") + "/health")
p.add_argument("--clients", type=int, default=5)
p.add_argument("--rps", type=float, default=1.0)
a=p.parse_args()

def worker():
    for _ in range(int(a.rps*10)):
        try: print("code",requests.get(a.url).status_code)
        except Exception as e: print("err",e)
        time.sleep(1/a.rps)

threads=[]
for _ in range(a.clients):
    t=threading.Thread(target=worker)
    t.start()
    threads.append(t)
for t in threads: t.join()
