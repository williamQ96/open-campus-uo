"""Curated semantic locators from public building facts; no UO GIS geometries."""
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[1]
SOURCE='https://cpfm.uoregon.edu/sites/default/files/uo_building_inventory_202102.pdf'
# Independent, approximate locators interpreted against public map and street facts.
# They identify buildings, not authoritative footprints. Coordinates are reviewed separately.
anchors=[
 ('B0018','Knight Library',-123.0780,44.04330),
 ('B0008','Prince Lucien Campbell Hall',-123.07836,44.04433),
 ('B0024','Jordan Schnitzer Museum of Art',-123.07722,44.04417),
 ('B0034','Lillis Hall',-123.07765,44.04605),
 ('B0004','Condon Hall',-123.07803,44.04504),
 ('B0006','Chapman Hall',-123.07724,44.04536),
 ('B0016','Johnson Hall',-123.07577,44.04512),
 ('B0009','Friendly Hall',-123.07535,44.04593),
 ('B0005','University Hall',-123.07585,44.04670),
 ('B0031','Villard Hall',-123.07639,44.04722),
 ('B0031A','Miller Theatre Complex',-123.07685,44.04717),
 ('B0001','Lawrence Hall',-123.07470,44.04735),
 ('B0017','Allen Hall',-123.07435,44.04664),
 ('B0019','Fenton Hall',-123.07665,44.04599),
 ('B0022','Peterson Hall',-123.07817,44.04594),
 ('B0003','Anstett Hall',-123.07720,44.04592),
 ('B0002','Chiles Business Center',-123.07810,44.04647),
 ('B0030','McKenzie Hall',-123.07810,44.04733),
 ('B0039','Computing Center',-123.07878,44.04661),
 ('B0035','Pacific Hall',-123.07460,44.04632),
 ('B0036','Columbia Hall',-123.07385,44.04603),
 ('B0047','Cascade Hall',-123.07352,44.04601),
 ('B0046','Willamette Hall',-123.07270,44.04600),
 ('B0038','Klamath Hall',-123.07245,44.04668),
 ('B0037','Onyx Bridge',-123.07320,44.04708),
 ('B0045','Streisinger Hall',-123.07185,44.04663),
 ('B0040','Huestis Hall',-123.07207,44.04596),
 ('B0044','Deschutes Hall',-123.07100,44.04595),
 ('B0042','Oregon Hall',-123.07015,44.04601),
 ('B0033','Erb Memorial Union',-123.07370,44.04465),
 ('B0076','Carson Hall',-123.07146,44.04490),
 ('B0072','Straub Hall',-123.07270,44.04387),
 ('B0073','Earl Hall',-123.07365,44.04376),
 ('B0071','Hendricks Hall',-123.07532,44.04420),
 ('B0075','Susan Campbell Hall',-123.07628,44.04428),
 ('B0011','Gerlinger Hall',-123.07577,44.04360),
 ('B0062','Gerlinger Annex',-123.07502,44.04342),
 ('B0023','Esslinger Hall',-123.07453,44.04304),
 ('B0051','Student Recreation Center',-123.07343,44.04265),
 ('B0020','McArthur Court',-123.07400,44.04160),
 ('B0025','Frohnmayer Music Building',-123.07800,44.04070),
 ('B0029','Clinical Services Building',-123.08003,44.04085),
 ('B0007','Lokey Education Building',-123.07930,44.04220),
 ('B0050','Knight Law Center',-123.06876,44.04272),
 ('B0049','Museum of Natural and Cultural History',-123.06800,44.04300),
 ('B0064','Living-Learning Center South',-123.07150,44.04340),
 ('B0065','Living-Learning Center North',-123.07152,44.04391),
 ('B0068','Bean Hall',-123.06830,44.04350),
 ('B0077','Walton Hall South (2008)',-123.06965,44.04360),
 ('B0078','Walton Hall North (2008)',-123.06957,44.04420),
 ('B0032','Central Power Station',-123.07390,44.04833),
 ('B0081','Collier House',-123.07500,44.04490),
 ('B0052','Outdoor Program Barn',-123.07336,44.04029),
 ('B0158','Global Scholars Hall',-123.06700,44.04280),
 ('B0010','HEDCO Education',-123.08024,44.04174),
 ('B0074','Matthew Knight Arena',-123.06595,44.04502),
 ('B0066','Ford Alumni Center',-123.06752,44.04504),
 ('B0067','Jaqua Academic Center',-123.06903,44.04578),
 ('B0103','Tykeson Hall',-123.07655,44.04526),
]
# Post-survey envelopes are explicit content approximations, not LiDAR detections.
envelopes={
 'B0158':[85,60,19], 'B0010':[60,52,16], 'B0074':[125,110,30],
 'B0066':[40,45,16], 'B0067':[38,40,15], 'B0103':[38,40,20],
}
records=[]
import pymupdf, hashlib
reference=ROOT/'data/raw/current-campus-reference.pdf'
page=pymupdf.open(reference)[0]
queries={
 'B0018':'Knight Library','B0008':'Prince Lucien Campbell','B0024':'Schnitzer Museum of Art',
 'B0034':'Lillis','B0004':'Condon','B0006':'Chapman','B0016':'Johnson','B0009':'Friendly',
 'B0005':'University','B0031':'Villard','B0031A':'THEATRE','B0001':'Lawrence','B0017':'Allen',
 'B0019':'Fenton','B0022':'Peterson','B0003':'Anstett','B0002':'Chiles','B0030':'McKenzie',
 'B0039':'Computing','B0035':'Pacific','B0036':'Columbia','B0047':'Cascade','B0046':'Willamette',
 'B0038':'Klamath','B0037':'Onyx Bridge','B0045':'Streisinger','B0040':'Huestis','B0044':'Deschutes',
 'B0042':'Oregon','B0033':'Erb Memorial Union','B0076':'Carson','B0072':'Straub','B0073':'Earl',
 'B0071':'Hendricks','B0075':'Susan Campbell','B0011':'Gerlinger','B0062':'Gerlinger Annex',
 'B0023':'Esslinger','B0051':'Student Recreation','B0020':'McArthur Court','B0025':'Frohnmayer Music',
 'B0029':'Clinical Services','B0007':'Lokey Education','B0050':'Knight Law Center',
 'B0049':'Museum of Natural and Cultural History','B0068':'Bean','B0032':'Central Power Station',
 'B0081':'Collier House','B0052':'Outdoor Program Barn','B0158':'Global Scholars',
 'B0010':'HEDCO Education','B0074':'Matthew Knight Arena','B0066':'Ford Alumni Center',
 'B0067':'Jaqua Academic Center','B0103':'Tykeson'}
single={'B0034','B0005','B0031','B0031A','B0047','B0046','B0011','B0042'}
def locator(query,first=False):
 rects=page.search_for(query)
 if not rects:return None
 if query=='Cascade':rects=rects[-1:]
 if first:rects=rects[:1]
 r=rects[0]
 for extra in rects[1:]:r=r|extra
 x,y=(r.x0+r.x1)/2,(r.y0+r.y1)/2
 # Approximate cartographic label locators, calibrated with public Census road facts.
 lon=-123.078578005425+(x-149.39)*(-123.074546322021+123.078578005425)/(267.52-149.39)
 lat=44.045562293955+(y-251.14)*(44.043368722479-44.045562293955)/(341.54-251.14)
 return [round(lon,7),round(lat,7)]
fallbacks={'B0005':[42,22,20],'B0039':[28,20,10],'B0038':[55,45,20],'B0045':[35,25,18],
           'B0040':[42,32,18],'B0073':[48,38,12],'B0062':[45,42,11],
           'B0020':[62,65,24],'B0052':[18,16,6]}
for id,name,lon,lat in anchors:
 if id in ['B0077','B0078']:continue
 precise=locator(queries[id],id in single) if id in queries else None
 if precise:lon,lat=precise
 if id=='B0008':lon,lat=-123.078361111,44.044333333
 if id in ['B0064','B0065']:
  rect=page.search_for('Living Learning Center')[0]
  precise=locator('Living Learning Center')
  if precise:lon,lat=precise[0],precise[1]+(.00023 if id=='B0065' else -.00025)
 r={'id':id,'name':name,'lon_lat':[lon,lat],'max_match_distance_m':35,
    'source':SOURCE,'coordinate_note':'Project-curated approximate locator, checked against public campus maps and Wikidata where available; not an official UO GIS geometry.'}
 if id in envelopes:r['placeholder']={'size_m':envelopes[id],'note':'Approximate envelope of a post-2008 building. No surveyed geometry claim.'}
 if id in fallbacks:r['fallback_envelope_m']=fallbacks[id]
 if id=='B0008':
  r['coordinate_note']='Precise Wikidata Q105686211 locator overrides the offset cartographic text position; still needs independent site verification.'
  r['coordinate_source']='https://www.wikidata.org/wiki/Q105686211'
 records.append(r)
for id,name,query,size in [
 ('OC-UNTHANK','Unthank Hall','Unthank',[90,50,22]),
 ('OC-YASUI','Yasui Hall','Yasui',[45,65,22]),
 ('OC-CEDAR','Cedar Hall','Cedar',[45,70,22]),
 ('OC-KNIGHT-1','Knight Campus 1','Knight Campus 1',[95,50,25]),
 ('OC-KNIGHT-2','Knight Campus 2','Knight Campus 2',[75,85,25]),
 ('OC-HAYWARD','Hayward Field','Hayward Field',[28,150,20]),
]:
 point=locator(query)
 if not point:continue
 if id=='OC-HAYWARD':point[0]-=.00072
 records.append({'id':id,'name':name,'lon_lat':point,'source':'https://mapapps.uoregon.edu/campusMaps/ColorBasemap.pdf',
                 'coordinate_note':'Approximate public-map label locator. Hayward envelope represents the west stand only.',
                 'placeholder':{'size_m':size,'note':'Explicit approximate contextual envelope, not measured or copied GIS geometry.'}})
out={'schema_version':1,'sources':[SOURCE,'https://mapapps.uoregon.edu/campusMaps/ColorBasemap.pdf','https://geocoding.geo.census.gov/geocoder/'],
     'reference_pdf_sha256':hashlib.file_digest(reference.open('rb'),'sha256').hexdigest(),
     'metadata_scope':'Factual names and approximate independently curated locators only. Campus GIS polygons were not imported.',
     'verified_on':'2026-10-30','buildings':records}
(ROOT/'data/metadata/campus-buildings.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
print(len(records),'semantic building records; all locator matching remains approximate')
