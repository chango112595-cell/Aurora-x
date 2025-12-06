#!/usr/bin/env python3
import argparse, requests, threading, time

p=argparse.ArgumentParser()
p.add_argument("--url", default="http://localhost:5000/health")
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