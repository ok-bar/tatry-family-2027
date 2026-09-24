"""One-time walking routes, <=1 request/s. FOSSGIS/OSRM foot profile, not car routing.
Only public coordinates are sent. Cached results make reruns incremental.
https://routing.openstreetmap.de/about.html
"""
import json,pathlib,subprocess,time,urllib.request,math
root=pathlib.Path(__file__).resolve().parent.parent
raw=subprocess.check_output(['node','-e',"const fs=require('fs'),vm=require('vm'),c={window:{}};vm.createContext(c);vm.runInContext(fs.readFileSync('map.js','utf8').split('const TripMap=')[0]+';this.points=MAP_POINTS',c);vm.runInContext(fs.readFileSync('day-routes-data.js','utf8'),c);console.log(JSON.stringify({points:c.points,...c.window.DAY_ROUTES}));"],cwd=root)
d=json.loads(raw);nodes={k:{'ll':[v['lat'],v['lon']]} for k,v in d['points'].items()};nodes.update(d['nodes'])
f=root/'walking-routes.js';cache=json.loads(f.read_text().split('window.WALKING_ROUTES=')[1].rstrip(';\n')) if f.exists() else {}
for key,l in d['legs'].items():
 if l['mode']!='walk' or key in cache:continue
 a,b=l['a'],l['b'];rev=b+'-'+a+'-walk'
 if rev in cache and 'geometry' in cache[rev]:cache[key]={**cache[rev],'geometry':list(reversed(cache[rev]['geometry']))};continue
 # Some pins mark only a broad area or an indoor attraction, not a verified routable entrance.
 if a in ['bachbob','choc'] or b in ['bachbob','choc'] or not nodes.get(a,{}).get('ll') or not nodes.get(b,{}).get('ll'):continue
 ps=[nodes[x]['ll'] for x in [a,b]];s=';'.join(str(p[1])+','+str(p[0]) for p in ps)
 u='https://routing.openstreetmap.de/routed-foot/route/v1/foot/'+s+'?overview=full&geometries=geojson&steps=false'
 try:
  r=json.load(urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'TatryFamilyTrip/1.0 (https://ok-bar.github.io/tatry-family-2027/)'}),timeout=20))
  if r.get('code')!='Ok':raise ValueError(r.get('code'))
  route=r['routes'][0];snap=max(x['distance'] for x in r['waypoints'])
  straight=6371000*2*math.asin(math.sqrt(math.sin(math.radians(ps[1][0]-ps[0][0])/2)**2+math.cos(math.radians(ps[0][0]))*math.cos(math.radians(ps[1][0]))*math.sin(math.radians(ps[1][1]-ps[0][1])/2)**2))
  if route['distance']>max(1500,straight*4):raise ValueError('Suspicious detour; needs manual trail verification')
  if snap>90:raise ValueError('Endpoint too far from network: '+str(snap))
  cache[key]={'meters':round(route['distance']),'seconds':round(route['duration']),'geometry':[[round(p[1],6),round(p[0],6)] for p in route['geometry']['coordinates']],'snapMeters':round(snap),'checked':d['checked']}
  print(key,cache[key]['meters'],'m',flush=True)
 except Exception as e:print(key,'UNVERIFIED',e,flush=True)
 f.write_text('/* Calculated foot paths © OpenStreetMap contributors / FOSSGIS OSRM. ODbL. */\nwindow.WALKING_ROUTES='+json.dumps(cache,separators=(',',':'))+';\n')
 time.sleep(1.1)
f.write_text('/* Calculated foot paths © OpenStreetMap contributors / FOSSGIS OSRM. ODbL. */\nwindow.WALKING_ROUTES='+json.dumps(cache,separators=(',',':'))+';\n')
