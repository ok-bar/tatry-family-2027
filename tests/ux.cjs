const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const base=require('node:path').join(__dirname,'../');const root=fs.existsSync(base+'dist/app.js')?base+'dist/':base;
const element={innerHTML:'',textContent:'',classList:{toggle(){}},setAttribute(){}};
const ctx={console,Date,Intl,Set,Map,URL,crypto:require('node:crypto').webcrypto,navigator:{},document:{querySelector:()=>element,querySelectorAll:()=>[],addEventListener(){}},window:{addEventListener(){}},setTimeout(){},clearTimeout(){}};
vm.createContext(ctx);vm.runInContext(fs.readFileSync(root+'data.js','utf8'),ctx);vm.runInContext(fs.readFileSync(root+'app.js','utf8').replace('\nrender();','\n'),ctx);
vm.runInContext('day=0;dayView()',ctx);const html=element.innerHTML;
assert.equal((html.match(/id="day-place-hotel"/g)||[]).length,1);
assert.equal((html.match(/id="day-place-rabka"/g)||[]).length,1);
assert.equal((html.match(/href="#day-place-hotel"/g)||[]).length,2);
assert(html.includes('ארוחה ראשונה במלון'));assert(html.includes('Hubertíkovo בקצב שלכם'));
for(let day=0;day<10;day++){vm.runInContext(`day=${day};dayView()`,ctx);const ids=[...element.innerHTML.matchAll(/data-visit="([^"]+)"/g)].map(m=>m[1]);assert.equal(ids.length,new Set(ids).size,'duplicate activity on day '+day)}
let nodes=[],ops=[];const handlers={};const c={console,Intl,Date,Map,Set,PLACES:[],esc:String,lookup(){},document:{querySelectorAll:()=>nodes,addEventListener(){}},window:{addEventListener:(n,f)=>handlers[n]=f},setTimeout(){},clearTimeout(){}};
vm.createContext(c);const source=fs.readFileSync(root+'trip-tools.js','utf8').replace('return {init,filesView,','return {testSet:(conn)=>{db=conn;ready=true},paintSaveStatus,init,filesView,');vm.runInContext(source,c);
const connection={transaction(){const tx={objectStore:()=>({getAll:()=>({result:ops})})};queueMicrotask(()=>tx.oncomplete());return tx}};c.conn=connection;vm.runInContext('TripTools.testSet(conn)',c);
(async()=>{nodes=[{dataset:{itemKind:'expense',itemId:'e1',localFile:'yes'}},{dataset:{itemKind:'file',itemId:'f1',localFile:'no'}}];ops=[{kind:'expense',item_id:'e1'}];await vm.runInContext('TripTools.paintSaveStatus()',c);assert(nodes[0].innerHTML.includes('ממתין לסנכרון'));assert(!nodes[0].innerHTML.includes('סונכרן למשפחה'));assert(nodes[1].innerHTML.includes('טרם הורד'));assert(nodes[1].innerHTML.includes('סונכרן למשפחה'));ops=[];await vm.runInContext('TripTools.paintSaveStatus()',c);assert(nodes[0].innerHTML.includes('סונכרן למשפחה'));nodes[1].dataset.localFile='yes';await vm.runInContext('TripTools.paintSaveStatus()',c);assert(nodes[1].innerHTML.includes('כל עוד התיק פתוח'));console.log('PASS: no repeated activity controls across 10 days; timeline preserved; pending/acknowledged/local-file badges distinct');})().catch(e=>{console.error(e);process.exitCode=1});
