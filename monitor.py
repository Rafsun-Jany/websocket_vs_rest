import argparse
import json
import sys
import time

import psutil


def main() -> int:
    parser = argparse.ArgumentParser(description="Sample CPU/memory for a process.")
    parser.add_argument("pid", type=int, help="PID of the process to monitor (e.g., uvicorn).")
    parser.add_argument("--interval", type=float, default=2.0, help="Seconds between samples.")
    parser.add_argument("--samples", type=int, default=60, help="Number of samples to capture.")
    args = parser.parse_args()

    try:
        proc = psutil.Process(args.pid)
    except psutil.NoSuchProcess:
        print(f"Process {args.pid} not found.", file=sys.stderr)
        return 1

    # Prime cpu_percent to establish a baseline
    proc.cpu_percent(None)

    for _ in range(args.samples):
        time.sleep(args.interval)
        try:
            data = {
                "ts": time.time(),
                "cpu_percent": proc.cpu_percent(None),
                "rss_mb": proc.memory_info().rss / (1024 * 1024),
            }
            print(json.dumps(data), flush=True)
        except psutil.NoSuchProcess:
            print(f"Process {args.pid} exited.", file=sys.stderr)
            return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
