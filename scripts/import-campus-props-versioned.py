# SPDX-License-Identifier: Apache-2.0
"""Create a new editable Blender import from an exported campus prop GLB.

Run with Blender in background mode: blender -b --python import-campus-props-versioned.py
-- --input /path/to/campus-props.glb --output /path/to/new-file.blend
Existing output files are never overwritten. Procedural props.js remains the
source of truth; this import is an editable snapshot, not a round-trip source.
"""
import argparse
import hashlib
from pathlib import Path
import sys
import bpy

args = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
parser = argparse.ArgumentParser()
parser.add_argument('--input', required=True)
parser.add_argument('--output', required=True)
opts = parser.parse_args(args)
source = Path(opts.input).resolve(strict=True)
target = Path(opts.output).resolve()
if source.suffix.lower() != '.glb' or target.suffix.lower() != '.blend':
    raise ValueError('Expected a GLB input and a .blend output')
if target.exists():
    raise FileExistsError(f'Refusing to overwrite {target}')
source_hash = hashlib.sha256(source.read_bytes()).hexdigest()
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=str(source))
meshes = [o for o in bpy.data.objects if o.type == 'MESH']
if len(meshes) not in (5, 6) or any(len(o.data.vertices) == 0 for o in meshes):
    raise ValueError('Expected five legacy or six current nonempty campus prop meshes')
bpy.context.scene['campus_props_glb_sha256'] = source_hash
bpy.context.scene['campus_props_provenance'] = 'Editable snapshot imported from procedural GLB; props.js is source of truth.'
target.parent.mkdir(parents=True, exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=str(target))
print('CAMPUS_PROP_IMPORT', source_hash, [(o.name, len(o.data.vertices), len(o.data.polygons)) for o in meshes])
