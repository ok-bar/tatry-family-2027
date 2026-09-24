"""One public OSRM car-table request for the itinerary's parking-to-parking distances.
No geometry is inferred from the matrix; the map keeps these connections dashed.
"""
import json,pathlib,subprocess,urllib.request
root=pathlib.Path(__file__).resolve().parent.parent
raw=subprocess.check_output(['node','-e',"const fs=require('fs'),vm=require('vm'),c={window:{}};vm.createContext(c);vm.runInContext(fs.readFileSync('map.js','utf8').split('const TripMap=')[0]+';this.points=MAP_POINTS',c);vm.runInContext(fs.readFileSync('day-routes-data.js','utf8'),c);console.log(JSON.stringify({points:c.points,...c.window.DAY_ROUTES}));"],cwd=root)
d=json.loads(raw);nodes={k:{'ll':[v['lat'],v['lon']]} for k,v in d['points'].items()};nodes.update(d['nodes']);legs={k:l for k,l in d['legs'].items() if l['mode']=='drive' and nodes.get(l['a'],{}).get('ll') and nodes.get(l['b'],{}).get('ll')};ids=list(dict.fromkeys(n for l in legs.values() for n in [l['a'],l['b']]));coords=';'.join(str(nodes[x]['ll'][1])+','+str(nodes[x]['ll'][0]) for x in ids)
u='https://routing.openstreetmap.de/routed-car/table/v1/car/'+coords+'?annotations=distance,duration'
r=json.load(urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'TatryFamilyTrip/1.1 (https://ok-bar.github.io/tatry-family-2027/)'}),timeout=45));assert r['code']=='Ok'
f=root/'driving-routes.js';cache=json.loads(f.read_text().split('window.DRIVING_ROUTES=')[1].rstrip(';\n')) if f.exists() else {}
for k,l in legs.items():
 i,j=ids.index(l['a']),ids.index(l['b']);meters=r['distances'][i][j];seconds=r['durations'][i][j];snap=max(r['sources'][i]['distance'],r['destinations'][j]['distance'])
 if meters is not None and seconds is not None and snap<=150:
  cache[k]={**cache.get(k,{}),'meters':round(meters),'seconds':round(seconds),'snapMeters':round(snap),'checked':d['checked'],'mode':'drive'};print(k,round(meters),round(seconds/60),'min',flush=True)
 else:print(k,'UNVERIFIED',snap,flush=True)
f.write_text('/* Road distances: OpenStreetMap / FOSSGIS OSRM car; ODbL. No live traffic. */\nwindow.DRIVING_ROUTES='+json.dumps(cache,separators=(',',':'))+';\n')
