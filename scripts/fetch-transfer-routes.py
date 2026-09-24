"""Cache public driving and walking transfers. OSRM/FOSSGIS: one request/second.
Separate profiles; never interpret driving routes as walking paths. No personal data.
"""
import json,pathlib,subprocess,time,urllib.request,math,sys
root=pathlib.Path(__file__).resolve().parent.parent
raw=subprocess.check_output(['node','-e',"const fs=require('fs'),vm=require('vm'),c={window:{}};vm.createContext(c);vm.runInContext(fs.readFileSync('map.js','utf8').split('const TripMap=')[0]+';this.points=MAP_POINTS',c);vm.runInContext(fs.readFileSync('day-routes-data.js','utf8'),c);console.log(JSON.stringify({points:c.points,...c.window.DAY_ROUTES}));"],cwd=root)
d=json.loads(raw);nodes={k:{'ll':[v['lat'],v['lon']]} for k,v in d['points'].items()};nodes.update(d['nodes'])
def read(f,var):
 return json.loads(f.read_text().split('window.'+var+'=')[1].rstrip(';\n')) if f.exists() else {}
walkfile=root/'walking-routes.js';drivefile=root/'driving-routes.js';walk=read(walkfile,'WALKING_ROUTES');drive=read(drivefile,'DRIVING_ROUTES')
def save():
 for f,var,c in [(walkfile,'WALKING_ROUTES',walk),(drivefile,'DRIVING_ROUTES',drive)]:f.write_text('/* OSM contributors / FOSSGIS OSRM; ODbL. Public calculated routes, not live traffic. */\nwindow.'+var+'='+json.dumps(c,separators=(',',':'))+';\n')
# Main routes first. Remaining comparisons and optional access follow.
keys=list(dict.fromkeys(k for variants in d['days'] for s in variants for k in s['legs']))
keys+=list(k for k in d['legs'] if k not in keys)
for key in keys:
 l=d['legs'][key];mode=l['mode'];a,b=l['a'],l['b'];c=walk if mode=='walk' else drive
 if '--walk-only' in sys.argv and mode!='walk':continue
 if mode not in ['walk','drive'] or key in c:continue
 if not nodes.get(a,{}).get('ll') or not nodes.get(b,{}).get('ll'):continue
 if mode=='walk' and (a in ['bachbob','choc','falls'] or b in ['bachbob','choc','falls']):continue
 if mode=='walk' and b+'-'+a+'-walk' in c:
  prev=c[b+'-'+a+'-walk'];c[key]={**prev,'geometry':list(reversed(prev['geometry']))};continue
 ps=[nodes[x]['ll'] for x in [a,b]];coords=';'.join(str(p[1])+','+str(p[0]) for p in ps);profile='foot' if mode=='walk' else 'car'
 u=f'https://routing.openstreetmap.de/routed-{profile}/route/v1/{profile}/'+coords+'?overview=simplified&geometries=geojson&steps=false'
 try:
  r=json.load(urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'TatryFamilyTrip/1.1 (https://ok-bar.github.io/tatry-family-2027/)'}),timeout=12))
  if r.get('code')!='Ok':raise ValueError(r.get('code'))
  route=r['routes'][0];snap=max(x['distance'] for x in r['waypoints'])
  straight=6371000*2*math.asin(math.sqrt(math.sin(math.radians(ps[1][0]-ps[0][0])/2)**2+math.cos(math.radians(ps[0][0]))*math.cos(math.radians(ps[1][0]))*math.sin(math.radians(ps[1][1]-ps[0][1])/2)**2))
  if mode=='walk' and route['distance']>max(1500,straight*4):raise ValueError('Suspicious foot detour')
  if snap>(90 if mode=='walk' else 150):raise ValueError('Endpoint too far from road/path '+str(snap))
  c[key]={'meters':round(route['distance']),'seconds':round(route['duration']),'geometry':[[round(p[1],6),round(p[0],6)] for p in route['geometry']['coordinates']],'snapMeters':round(snap),'checked':d['checked'],'mode':mode}
  print(key,c[key]['meters'],'m',flush=True)
 except Exception as e:print(key,'UNVERIFIED',str(e),flush=True)
 save();time.sleep(1.1)
save();print('DONE',len(walk),'walking,',len(drive),'driving',flush=True)
