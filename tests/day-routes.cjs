const fs=require('fs'),vm=require('vm'),assert=require('node:assert/strict'),{parseHTML}=require('linkedom'),path=require('path');
const root=path.join(__dirname,'..'),{document,MutationObserver,CustomEvent}=parseHTML(fs.readFileSync(path.join(root,'index.html'),'utf8'));
const events={},c={document,MutationObserver,CustomEvent,NodeFilter:{SHOW_ELEMENT:1,SHOW_TEXT:4},console,Date,Intl,Set,Map,WeakMap,URL,URLSearchParams,crypto:require('crypto').webcrypto,navigator:{},location:{protocol:'https:'},setTimeout,clearTimeout,localStorage:{getItem:()=>null,setItem(){}},addEventListener:(n,f)=>(events[n]??=[]).push(f),dispatchEvent:e=>(events[e.type]||[]).forEach(f=>f(e)),TripTools:{isReady:()=>false,getReservations:()=>[],paintSaveStatus(){},init(){},fileCount:()=>0}};c.window=c;vm.createContext(c);
for(const f of ['i18n-dictionary.js','i18n.js','offline.js','data.js','place-photos.js','app.js','day-hub.js'])vm.runInContext(fs.readFileSync(path.join(root,f),'utf8').replace('\nrender();','\n'),c);
const layer=()=>({addTo(){return this},bindPopup(){return this},setStyle(){return this}});c.L={map:()=>({fitBounds(){},remove(){}}),tileLayer:layer,marker:layer,polyline:layer,divIcon:x=>x};
vm.runInContext(fs.readFileSync(path.join(root,'map.js'),'utf8').split('const TripMap=')[0],c);
for(const f of ['day-routes-data.js','walking-routes.js','driving-routes.js','day-routes.js'])vm.runInContext(fs.readFileSync(path.join(root,f),'utf8'),c);
let variants=0;for(let d=0;d<10;d++){vm.runInContext(`day=${d};view='days';dayView()`,c);assert(document.querySelector('#day-route-map'));const choices=[...document.querySelectorAll('#route-scenario option')].map(o=>o.value);for(const value of choices){const select=document.querySelector('#route-scenario');select.onchange({target:{value}});assert(document.querySelectorAll('.route-leg').length);for(const a of document.querySelectorAll('.route-leg a'))assert(!a.href.includes('undefined'));variants++}c.TripI18n.setLanguage('en');assert(!/[א-ת]/.test(document.querySelector('#day-routes').textContent));c.TripI18n.setLanguage('he');assert(document.querySelector('#day-routes').textContent.includes('חניה'))}
assert(c.WALKING_ROUTES['boat-tower-walk'].meters>1200);assert.equal(c.DAY_ROUTES.walkLimit,10);assert(c.DAY_ROUTES.days[0][0].legs.includes('rabkapark-icepark-drive'));assert(c.DAY_ROUTES.days[3][0].legs.includes('lakepark-fispublic-drive'));assert(!c.DAY_ROUTES.days[3][0].legs.includes('boat-tower-walk'));
vm.runInContext("day=3;dayView()",c);document.querySelector('#route-scenario').onchange({target:{value:'2'}});assert(document.querySelector('.route-long'));assert(document.querySelector('#day-routes').textContent.includes('10'));
assert(!c.WALKING_ROUTES['hreb-falls-walk']);
for(const [key,p] of Object.entries(c.WALKING_ROUTES)){assert(p.meters>0);assert(p.geometry.length>=2);assert(p.snapMeters<=90);}
assert(c.DAY_ROUTES.days[4][0].legs.some(k=>k==='koliesko-priehyba-lift'));
assert(c.DAY_ROUTES.days[5][0].legs.includes('museumpark-lompark-drive'));
console.log(`PASS: 10 daily maps, ${variants} main/optional itineraries, HE/EN, walking distances, car return and lift return.`);

// Full activities remain the default; shorter alternatives are opt-in.
assert(c.DAY_ROUTES.days[2][0].legs.includes('panorama-forest-walk'));
assert(c.DAY_ROUTES.days[3][0].legs.includes('lakepark-boat-walk'));
assert(c.DAY_ROUTES.days[7][0].legs.includes('woodpark-wood-walk'));
const oldContext={};vm.createContext(oldContext);vm.runInContext(require('child_process').execFileSync('git',['show','6565771:data.js'],{encoding:'utf8'}),oldContext);
const original=vm.runInContext('DAYS',oldContext),current=vm.runInContext('DAYS',c);
for(let d=0;d<10;d++){for(const stop of original[d].stops)assert(current[d].stops.some(s=>s[1]===stop[1]&&s[3]===stop[3]),'Missing stop '+d+': '+stop[1]);for(const option of original[d].options||[])assert((current[d].options||[]).some(o=>o[0]===option[0]),'Missing option '+option[0]);}
vm.runInContext('day=0;dayView()',c);assert(!document.querySelector('#day-routes').textContent.includes('→'));
c.TripI18n.setLanguage('en');assert(document.querySelector('#day-routes').textContent.includes('→'));
console.log('PASS: every original stop and option retained across all 10 days; full route defaults and Hebrew/English arrows.');
