# SPDX-License-Identifier: Apache-2.0
import bpy
from pathlib import Path
root=Path(__file__).resolve().parents[1]
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=str(root/'apps/web-preview/public/props/campus-props.glb'))
(root/'assets/props').mkdir(parents=True,exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=str(root/'assets/props/campus-props.blend'))
