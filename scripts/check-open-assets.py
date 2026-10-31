# SPDX-License-Identifier: Apache-2.0
"""Check archived open-source and original model bytes without network access."""
from pathlib import Path
import hashlib,json
root=Path(__file__).resolve().parents[1]
manifest=json.loads((root/'data/asset-sources/manifest.json').read_text(encoding='utf-8'))
assert manifest['source_license']=='CC0-1.0'
for name,expected in manifest['files'].items():
 path=(root/name).resolve()
 if not path.is_relative_to(root):raise ValueError('Asset path escapes repository')
 raw=path.read_bytes()
 if len(raw)!=expected['bytes'] or hashlib.sha256(raw).hexdigest()!=expected['sha256']:
  raise ValueError('Asset checksum mismatch: '+name)
print('Verified',len(manifest['files']),'archived open source/model files')
