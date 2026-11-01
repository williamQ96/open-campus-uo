# SPDX-License-Identifier: Apache-2.0
from pathlib import Path
import json,hashlib
from geospatial3d.navigation import build_navigation_graph
root=Path.cwd();scene=root/'apps/web-preview/public/scene';m=json.loads((scene/'manifest.json').read_text(encoding='utf-8'));c=json.loads((root/'configs/visual-pilot.json').read_text())
features=m['corridors']['features']+[{'kind':'path','centerline_enu_m':p} for p in c['paths']]
graph=build_navigation_graph(features,m['buildings']);graph['source_manifest_sha256']=hashlib.sha256((scene/'manifest.json').read_bytes()).hexdigest()
(scene/'navigation.json').write_text(json.dumps(graph,separators=(',',':'))+'\n',encoding='utf-8')
# Authored activity corridors are selected from the same source centerlines.
walk=[p for p in c['paths'] if len(p)>=2]
roads=[f['centerline_enu_m'] for f in m['corridors']['features'] if f['name'] in ['University St','E 13th Ave','Kincaid St','E 15th Ave']]
activity={'version':1,'students':{'count':12,'routes_enu_m':walk},'traffic':{'count':4,'routes_enu_m':roads},'props':[{'kind':'car','east':-618,'north':-264,'yaw':0},{'kind':'van','east':-617,'north':-281,'yaw':0},{'kind':'car','east':-320,'north':-273,'yaw':1.57},{'kind':'pickup','east':-320,'north':-285,'yaw':1.57},{'kind':'van','east':-165,'north':-113,'yaw':0}], 'status':'Illustrative scripted activity and curated parking; not an inventory or current traffic/access model'}
activity.update(json.loads((root/'configs/campus-life.json').read_text(encoding='utf-8')))
(scene/'activity.json').write_text(json.dumps(activity,indent=2)+'\n',encoding='utf-8')
print(len(graph['nodes_enu_m']),'nodes',len(graph['edges']),'edges')
