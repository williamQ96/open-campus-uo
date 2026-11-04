# SPDX-License-Identifier: Apache-2.0
"""Check explicitly recorded downstream changes against the untouched viewer baseline."""
import hashlib, json
from pathlib import Path
root = Path(__file__).resolve().parents[1]
lock = json.loads((root / 'viewer-template.lock.json').read_text(encoding='utf-8'))
record = json.loads((root / 'viewer-overrides.json').read_text(encoding='utf-8'))
for name, details in record['overrides'].items():
    if lock['files'][name] != details['upstream_sha256']:
        raise SystemExit(f'Upstream baseline changed: {name}')
    if hashlib.sha256((root / name).read_bytes()).hexdigest() != details['local_sha256']:
        raise SystemExit(f'Downstream override changed: {name}')
for name, expected in record['outputs'].items():
    if hashlib.sha256((root / name).read_bytes()).hexdigest() != expected:
        raise SystemExit(f'Generated output changed: {name}')
print('Recorded downstream viewer override and output hashes match.')
