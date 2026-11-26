# SPDX-License-Identifier: Apache-2.0
from pathlib import Path
import json,hashlib,math
from geospatial3d.navigation import build_navigation_graph
root=Path.cwd();scene=root/'apps/web-preview/public/scene';m=json.loads((scene/'manifest.json').read_text(encoding='utf-8'));c=json.loads((root/'configs/visual-pilot.json').read_text())
features=m['corridors']['features']+[{'kind':'path','centerline_enu_m':p} for p in c['paths']]
graph=build_navigation_graph(features,m['buildings']);graph['source_manifest_sha256']=hashlib.sha256((scene/'manifest.json').read_bytes()).hexdigest()
# Trim the authored spur that used to end inside the registered Susan Campbell wall.
quad=json.loads((root/'data/metadata/womens-quad-site-review.json').read_bytes())
trim=quad['susan_south_path_trim']
nodes=graph['nodes_enu_m']
endpoint=next((i for i,p in enumerate(nodes) if list(p)==trim['previous_end_enu_m']),None)
if endpoint is not None:
    incident=[(index,edge) for index,edge in enumerate(graph['edges']) if endpoint in edge[:2]]
    assert len(incident)==1
    index,(a,b,_,kind)=incident[0]
    assert kind=='path' and list(nodes[b if a==endpoint else a])==trim['neighbor_enu_m']
    nodes[endpoint]=trim['end_enu_m']
    graph['edges'][index]=[a,b,round(math.dist(nodes[a],nodes[b]),4),kind]
(scene/'navigation.json').write_text(json.dumps(graph,separators=(',',':'))+'\n',encoding='utf-8')
# Authored activity corridors are selected from the same source centerlines.
walk=[p for p in c['paths'] if len(p)>=2]
roads=[f['centerline_enu_m'] for f in m['corridors']['features'] if f['name'] in ['University St','E 13th Ave','Kincaid St','E 15th Ave']]
activity={'version':1,'students':{'count':12,'routes_enu_m':walk},'traffic':{'count':4,'routes_enu_m':roads},'props':[{'kind':'car','east':-618,'north':-264,'yaw':0},{'kind':'van','east':-617,'north':-281,'yaw':0},{'kind':'car','east':-320,'north':-273,'yaw':1.57},{'kind':'pickup','east':-320,'north':-285,'yaw':1.57},{'kind':'van','east':-165,'north':-113,'yaw':0}], 'status':'Illustrative scripted activity and curated parking; not an inventory or current traffic/access model'}
# Version-2 activity is compiled separately with strict habitat classification.
import runpy
runpy.run_path(str(root/'scripts/prepare-semantic-activity.py'),run_name='__main__')

print(len(graph['nodes_enu_m']),'nodes',len(graph['edges']),'edges')
