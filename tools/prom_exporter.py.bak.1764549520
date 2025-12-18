#!/usr/bin/env python3
# very small prometheus exporter stub to expose metrics for packs (example)
try:
    from prometheus_client import start_http_server, Gauge
except ImportError:
    print('prometheus_client not installed, skipping exporter')
    import sys; sys.exit(0)
import time
g = Gauge('aurora_pack_heartbeat','heartbeat')
if __name__ == '__main__':
    start_http_server(8000)
    while True:
        g.set_to_current_time()
        time.sleep(5)