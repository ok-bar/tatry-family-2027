/* Translate presentation only. IDs, form values, links and saved records stay intact. */
(()=>{
const dictionary=window.TRIP_EN||{},records=new WeakMap(),attributes=new WeakMap();
let lang=document.documentElement.dataset.savedLanguage==='en'?'en':'he';try{const saved=localStorage.getItem('tatry-language');if(saved==='en'||saved==='he')lang=saved}catch{}
const keys=Object.keys(dictionary).sort((a,b)=>b.length-a.length);
const pattern=new RegExp('(?<![א-ת])(?:'+keys.map(s=>s.replace(/[.*+?^${}()|[\]\\]/g,'\\$&')).join('|')+')(?![א-ת])','gu');
const english=s=>String(s).replace(pattern,key=>dictionary[key]);
const text=s=>lang==='en'?english(s):String(s);
let observer;
const skip=el=>!el||el.closest('script,style,textarea,[translate="no"],[contenteditable="true"]');
function translateNode(node){const el=node.parentElement;if(skip(el))return;const previous=records.get(node);const raw=previous&&node.nodeValue===previous.rendered?previous.raw:node.nodeValue;if(!/[א-ת]/.test(raw)&&!previous)return;
// Translating a label must never change a select option's stored value.
if(el.tagName==='OPTION'&&!el.hasAttribute('value'))el.setAttribute('value',el.textContent.trim());
const rendered=text(raw);records.set(node,{raw,rendered});if(node.nodeValue!==rendered)node.nodeValue=rendered;}
function translateElement(el){if(skip(el))return;let saved=attributes.get(el);if(!saved){saved={};attributes.set(el,saved)}for(const name of ['placeholder','title','aria-label','alt']){const value=el.getAttribute(name);if(value===null)continue;const old=saved[name];const raw=old&&value===old.rendered?old.raw:value;const rendered=text(raw);saved[name]={raw,rendered};if(value!==rendered)el.setAttribute(name,rendered)}}
function walk(root){if(root.nodeType===3){translateNode(root);return}if(root.nodeType!==1&&root.nodeType!==9)return;if(root.nodeType===1&&skip(root))return;if(root.nodeType===1)translateElement(root);const walker=document.createTreeWalker(root,NodeFilter.SHOW_ELEMENT|NodeFilter.SHOW_TEXT);let node;while(node=walker.nextNode()){if(node.nodeType===3)translateNode(node);else translateElement(node)}}
function observe(){observer?.observe(document.documentElement,{subtree:true,childList:true,characterData:true,attributes:true,attributeFilter:['placeholder','title','aria-label','alt']})}
function flush(roots){observer?.disconnect();for(const root of roots)if(root.isConnected||root===document.documentElement)walk(root);observe()}
function paint(){document.documentElement.lang=lang;document.documentElement.dir=lang==='en'?'ltr':'rtl';const button=document.querySelector('#language-toggle');if(button){button.setAttribute('aria-pressed',String(lang==='en'));button.setAttribute('aria-label',lang==='en'?'Switch to Hebrew':'Switch to English');button.querySelector('[data-lang-label="he"]')?.classList.toggle('active',lang==='he');button.querySelector('[data-lang-label="en"]')?.classList.toggle('active',lang==='en')}}
function setLanguage(next){if(!['he','en'].includes(next))return;lang=next;try{localStorage.setItem('tatry-language',lang)}catch{}paint();flush([document.documentElement]);window.dispatchEvent(new CustomEvent('tatry-language-changed',{detail:{language:lang}}))}
window.TripI18n={text,english,setLanguage,get language(){return lang},get locale(){return lang==='en'?'en-GB':'he-IL'},refresh:()=>flush([document.documentElement])};
paint();
function start(){paint();observer=new MutationObserver(changes=>{const roots=new Set();for(const c of changes){if(c.type==='childList')for(const n of c.addedNodes)roots.add(n);else roots.add(c.target)}flush(roots)});flush([document.documentElement]);document.addEventListener('click',e=>{if(e.target.closest('#language-toggle'))setLanguage(lang==='he'?'en':'he')});}
for(const name of ['alert','confirm','prompt'])if(typeof window[name]==='function'){const original=window[name].bind(window);window[name]=(message,...args)=>original(text(message),...args)}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',start,{once:true});else start();
})();
