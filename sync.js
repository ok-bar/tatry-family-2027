/* Family synchronization: authenticated, allowlisted accounts; private Storage.
   Each local edit and its outbox entry commit in the same IndexedDB transaction.
   Edits to different items merge; edits to the same item use last server write. */
const FamilySync=(()=>{
 const URL='https://zszmhanowbfwbtjmdwmz.supabase.co',KEY='sb_publishable_kf2FQG8MQGlWN4U__6ci4A_Exzo2e-b';
 const REDIRECT='https://ok-bar.github.io/tatry-family-2027/';
 let client,session,trip,channel,running=false,again=false,epoch=0,active=false,message='התחברו כדי לפתוח את התיק המשפחתי',timer;
 const emit=()=>window.dispatchEvent(new CustomEvent('tatry-sync-status',{detail:{email:session?.user.email,trip,active,message}}));
 const status=text=>{message=text;emit()};
 const check=r=>{if(r.error)throw r.error;return r.data};
 const db=()=>TripTools.connection();
 function read(store){return new Promise((resolve,reject)=>{const tx=db().transaction(store);const r=tx.objectStore(store).getAll();tx.oncomplete=()=>resolve(r.result);tx.onerror=()=>reject(tx.error)})}
 function ack(id){return new Promise((res,rej)=>{const tx=db().transaction('outbox','readwrite');tx.objectStore('outbox').delete(id);tx.oncomplete=res;tx.onerror=()=>rej(tx.error)})}
 async function apply(rows){
  const connection=db(); if(!connection)return;
  await new Promise((resolve,reject)=>{
   const tx=connection.transaction(['expenses','files','settings','outbox'],'readwrite'),q=tx.objectStore('outbox').getAll();
   q.onsuccess=()=>{const pending=new Set(q.result.map(o=>o.kind+':'+o.item_id));
    for(const row of rows){if(pending.has(row.kind+':'+row.item_id))continue;
     const store=row.kind==='expense'?'expenses':row.kind==='file'?'files':'settings';
     const key=['visit','check'].includes(row.kind)?row.kind+':'+row.item_id:row.item_id;
     if(row.deleted){tx.objectStore(store).delete(key);continue}
     const payload={...row.payload,id:key};
     if(row.kind==='file'){
      const r=tx.objectStore('files').get(key);r.onsuccess=()=>{const cached=r.result;tx.objectStore('files').put({...payload,blob:cached?.version===payload.version?cached?.blob:undefined})};
     }else tx.objectStore(store).put(payload);
    }
   };tx.oncomplete=resolve;tx.onerror=()=>reject(tx.error);
  });
  const settings=await read('settings'),visited={},checked={};for(const s of settings){if(s.id.startsWith('visit:'))visited[s.id.slice(6)]=!!s.value;if(s.id.startsWith('check:'))checked[s.id.slice(6)]=!!s.value}
  window.dispatchEvent(new CustomEvent('tatry-private-state',{detail:{visited,checked}}));await TripTools.update();
 }
 async function cycle(){
  if(!active||!db())return;if(running){again=true;return}running=true;const generation=epoch;
  try{
   if(!navigator.onLine)throw Error('offline');
   const allowed=check(await client.rpc('tatry_access'));if(!allowed){await lock();status('האימייל הזה לא אושר לטיול.');return}
   status('מסנכרנים…');
   do {again=false;
    let ops=await read('outbox');
    // Date/UUID ordering is unnecessary for different entities; retain insertion order per item.
    ops.sort((a,b)=>(a.order||0)-(b.order||0));
    for(const op of ops){if(generation!==epoch)return;
     const payload={...op.payload};
     if(op.kind==='file'&&!op.deleted){
      if(!op.blob)throw Error('הקובץ המקומי חסר');
      // A new immutable object for each file version avoids retry/update races.
      payload.version=op.id;payload.path=trip.id+'/'+op.item_id+'/'+op.id;
      payload.size=op.blob.size;payload.type=op.blob.type;
      const uploaded=await client.storage.from('tatry-tickets').upload(payload.path,op.blob,{upsert:true,contentType:op.blob.type});check(uploaded);
     }
     check(await client.from('tatry_shared_items').upsert({trip_id:trip.id,kind:op.kind,item_id:op.item_id,payload,deleted:op.deleted,updated_by:session.user.id},{onConflict:'trip_id,kind,item_id'}));
     if(generation!==epoch)return;
     if(op.kind==='file'&&op.deleted){
      const prefix=trip.id+'/'+op.item_id;
      const objects=check(await client.storage.from('tatry-tickets').list(prefix));
      if(objects.length)check(await client.storage.from('tatry-tickets').remove(objects.map(o=>prefix+'/'+o.name)));
     }
     await ack(op.id);
    }
    let rows=[],start=0;
    while(true){const page=check(await client.from('tatry_shared_items').select('*').eq('trip_id',trip.id).order('kind').order('item_id').range(start,start+499));rows.push(...page);if(page.length<500)break;start+=500}
    if(generation!==epoch)return;await apply(rows);
    if((await read('outbox')).length)again=true;
   }while(again&&generation===epoch);
   status('מסונכרן ✓ · '+new Date().toLocaleTimeString('he-IL',{hour:'2-digit',minute:'2-digit'}));
  }catch(e){if(generation===epoch)status(e.message==='offline'?'אופליין · השינויים ממתינים לחיבור':'הסנכרון לא הושלם · השינויים נשמרו במכשיר. '+(e.message||''))}
  finally{running=false}
 }
 async function attach(t){
  trip=t;active=true;epoch++;if(channel)client.removeChannel(channel);
  TripTools.init('tatry-private-v2-'+session.user.id+'-'+trip.id);
  channel=client.channel('family-'+trip.id).on('postgres_changes',{event:'*',schema:'public',table:'tatry_shared_items',filter:'trip_id=eq.'+trip.id},()=>{clearTimeout(timer);timer=setTimeout(cycle,300)}).subscribe();emit();
 }
 async function loadAccount(){
  if(!session){active=false;trip=null;TripTools.lock();status('התחברו כדי לפתוח את התיק המשפחתי');return}
  try{
   if(!check(await client.rpc('tatry_access'))){active=false;TripTools.lock();status('האימייל הזה עדיין לא אושר לטיול.');return}
   const trips=check(await client.from('tatry_trips').select('id,name,join_code').order('created_at').limit(1));
   if(trips.length)await attach(trips[0]);else status('האימייל אושר · צרו טיול או הצטרפו עם קוד');
  }catch(e){status('לא ניתן לבדוק הרשאה כרגע · התחברו לאינטרנט ונסו שוב.');}
 }
 async function lock(){
  active=false;epoch++;if(channel){client.removeChannel(channel);channel=null}
  const connection=db();if(connection){await new Promise((resolve,reject)=>{const tx=connection.transaction(['files','expenses','settings','outbox'],'readwrite');for(const name of ['files','expenses','settings','outbox'])tx.objectStore(name).clear();tx.oncomplete=resolve;tx.onerror=()=>reject(tx.error)})}
  TripTools.lock();trip=null;window.dispatchEvent(new CustomEvent('tatry-private-state',{detail:{visited:{},checked:{}}}));emit();
 }
 async function signout(){
  if(db()&&(await read('outbox')).length&&!confirm('יש שינויים שטרם הסתנכרנו. יציאה תמחק את העותק הפרטי במכשיר. לצאת?'))return;
  await lock();check(await client.auth.signOut({scope:'local'}));session=null;status('יצאתם · העותק הפרטי במכשיר נוקה');
 }
 async function download(f){
  if(!active||!session)throw Error('נדרשת התחברות');
  // Use authenticated download; do not create bearer URLs that bypass membership checks.
  const blob=check(await client.storage.from('tatry-tickets').download(f.path));
  return blob;
 }
 async function create(){const row=check(await client.rpc('tatry_create_trip',{p_name:'הטיול של עומרי וליאת'}))[0];await attach({id:row.trip_id,name:'הטיול של עומרי וליאת',join_code:row.join_code})}
 async function join(code){check(await client.rpc('tatry_join_trip',{p_join_code:code.trim().toUpperCase()}));await loadAccount()}
 async function login(email){check(await client.auth.signInWithOtp({email:email.trim(),options:{emailRedirectTo:REDIRECT}}));status('קישור נשלח אם שירות המייל מאפשר זאת · בדקו גם ספאם')}
 async function start(){
  if(!window.supabase){status('מצב מקומי · כניסה דורשת חיבור לאינטרנט');return}
  client=window.supabase.createClient(URL,KEY,{auth:{storageKey:'tatry-auth-v2',detectSessionInUrl:true}});
  session=check(await client.auth.getSession()).session;
  client.auth.onAuthStateChange((event,next)=>{if(event==='SIGNED_OUT'){session=null;void lock();status('יצאתם מהחשבון')}else if(event==='SIGNED_IN'&&next?.user.id!==session?.user.id){session=next;setTimeout(loadAccount,0)}else session=next});
  await loadAccount();
 }
 window.addEventListener('tatry-db-ready',cycle);
 window.addEventListener('tatry-local-change',()=>{clearTimeout(timer);timer=setTimeout(cycle,100)});
 window.addEventListener('online',()=>active?cycle():loadAccount());
 window.addEventListener('focus',()=>active&&cycle());
 setInterval(()=>{if(active&&!document.hidden)void cycle()},20000);
 document.addEventListener('change',e=>{if(!active)return;if(e.target.matches('[data-visit]'))TripTools.mark('visit',e.target.dataset.visit,e.target.checked).catch(err=>status(err.message));if(e.target.matches('[data-check]'))TripTools.mark('check',e.target.dataset.check,e.target.checked).catch(err=>status(err.message))});
 return {start,login,create,join,signout,download,cycle,importLegacy:()=>TripTools.importLegacy(),get active(){return active}};
})();
