#!/usr/bin/env python3
"""Sample CPU deltas for Chromium threads in an isolated hosted runner."""
import datetime
import os
from pathlib import Path
import time

clock_ticks = os.sysconf("SC_CLK_TCK")
previous = {}
last = time.monotonic()
while True:
    current = {}
    now = time.monotonic()
    elapsed = max(now - last, 0.001)
    samples = []
    for proc in Path('/proc').iterdir():
        if not proc.name.isdigit():
            continue
        try:
            cmd = (proc / 'cmdline').read_bytes().replace(b'\0', b' ').decode(errors='replace')
            if 'chrome-headless-shell' not in cmd:
                continue
            category = next((x.split('=', 1)[1] for x in cmd.split() if x.startswith('--type=')), 'browser')
            for thread in (proc / 'task').iterdir():
                try:
                    stat = (thread / 'stat').read_text()
                    close = stat.rfind(')')
                    name = stat[stat.find('(') + 1:close]
                    fields = stat[close + 2:].split()
                    ticks = int(fields[11]) + int(fields[12])
                    key = (proc.name, thread.name)
                    current[key] = ticks
                    if key in previous:
                        cpu = 100 * (ticks - previous[key]) / clock_ticks / elapsed
                        if cpu >= 1:
                            samples.append((cpu, proc.name, thread.name, category, name))
                except (FileNotFoundError, ProcessLookupError, PermissionError):
                    pass
        except (FileNotFoundError, ProcessLookupError, PermissionError):
            pass
    print(datetime.datetime.now(datetime.timezone.utc).isoformat(), flush=True)
    for cpu, pid, tid, category, name in sorted(samples, reverse=True)[:15]:
        print(f'cpu={cpu:.1f}% pid={pid} tid={tid} type={category} thread={name}', flush=True)
    previous = current
    last = now
    time.sleep(2)
