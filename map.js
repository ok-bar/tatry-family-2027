/* Coordinates are only plotted when verified. No automatic geocoding requests. */
const MAP_POINTS={trick:{lat:49.141335,lon:20.2243328,source:'https://www.openstreetmap.org/node/4281681948'}};
const TripMap=(()=>{
 let map,group,filter='all';
 const colors=['#0b6d83','#e68a25','#3b8a65','#9661ba','#ca5867','#318bb5','#827c25','#cb7342','#486ab5','#678886'];
 function ids(){return filter==='all'?new Set(PLACES.map(p=>p.id)):new Set([...DAYS[Number(filter)].stops.map(s=>s[3]),...(DAYS[Number(filter)].options||[]).map(s=>s[2])])}
 function list(){const visible=PLACES.filter(p=>ids().has(p.id));group.clearLayers();let bounds=[];
 document.querySelector('#map-list').innerHTML=visible.map(p=>{const day=DAYS.findIndex(d=>d.stops.some(s=>s[3]===p.id)||d.options?.some(o=>o[2]===p.id));const pt=MAP_POINTS[p.id];if(pt){const marker=L.circleMarker([pt.lat,pt.lon],{radius:9,color:colors[Math.max(0,day)],fillOpacity:.9}).addTo(group);const el=document.createElement('div');el.textContent=p.name;marker.bindPopup(el);bounds.push([pt.lat,pt.lon])}return '<article class="map-place"><span class="map-dot" style="background:'+colors[Math.max(0,day)]+'"></span><div><b>'+esc(p.name)+'</b><p>'+esc(p.area)+(pt?'':' · מיקום על המפה ממתין לאימות')+'</p><div class="actions">'+external(pin(p),'חיפוש במפה')+external(waze(p.map),'Waze')+'<button class="softbutton" data-place="'+p.id+'">פרטים</button></div></div></article>'}).join('');
 document.querySelector('#map-count').textContent=visible.length+' מקומות · '+bounds.length+' נקודות עם מיקום מאומת';if(bounds.length)map.fitBounds(bounds,{padding:[35,35],maxZoom:12});
 }
 function show(){if(map){map.remove();map=null}main.innerHTML='<section class="map-title"><p class="eyebrow">כל ההרפתקאות על מפה אחת</p><h2>מה קרוב למה?</h2><p>בחרו יום כדי לצמצם את רשימת המקומות. נקודות שטרם אומתו מופיעות ברשימה עם קישור לחיפוש.</p></section><div class="map-toolbar"><label>יום בטיול <select id="map-day"><option value="all">כל הימים</option>'+DAYS.map((d,i)=>'<option value="'+i+'" '+(filter===String(i)?'selected':'')+'>'+esc(d.date+'.08 · '+d.short)+'</option>').join('')+'</select></label><span id="map-count"></span><button class="softbutton" id="map-background">טעינת מפת רקע · דורש אינטרנט</button></div><div class="map-layout"><div id="trip-map" aria-label="מפת מקומות הטיול"></div><div id="map-list"></div></div><p class="source">נתוני מיקום: © OpenStreetMap contributors. רשימת המקומות זמינה אופליין; מפת הרקע דורשת אינטרנט. המפה אינה מסלול נהיגה ואינה מאמתת זמני נסיעה.</p>';
 if(!window.L){document.querySelector('#trip-map').textContent='המפה לא נטענה. קישורי הניווט זמינים במסלול.';return}
 map=L.map('trip-map',{scrollWheelZoom:false}).setView([49.13,20.05],9);group=L.layerGroup().addTo(map);
 document.querySelector('#map-day').addEventListener('change',e=>{filter=e.target.value;list()});
 document.querySelector('#map-background').addEventListener('click',e=>{L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png',{attribution:'© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',maxZoom:18}).addTo(map);e.target.disabled=true;e.target.textContent='רקע המפה נטען'});list();
 }
 return {show};
})();
