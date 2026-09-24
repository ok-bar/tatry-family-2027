"""Curated public trip access plan. Regenerate data, then refresh walking routes separately."""
import json,pathlib
root=pathlib.Path(__file__).resolve().parent.parent
nodes={}
def N(id,he,en,ll=None,osm=None,kind='place',query=None):
 nodes[id]={'name':[he,en],'kind':kind}
 if ll:nodes[id]['ll']=ll
 if osm:nodes[id]['source']='https://www.openstreetmap.org/'+osm
 if query:nodes[id]['query']=query
 return id
N('lakepark','חניון מרכזי · Štrbské Pleso','Central car park · Štrbské Pleso',[49.1192171,20.0646226],'way/27925667','parking')
N('boat','רציף השייט · הגדה הדרומית','Boat rental · south shore',[49.119779,20.0589459],'way/743527778')
N('smokpark','חניון VPS TATRA · ליד Tricklandia','VPS TATRA car park · near Tricklandia',[49.1407202,20.2247109],'way/28051170','parking')
N('smokbase','תחנת הפוניקולר התחתונה','Lower funicular station',[49.1415616,20.2204254],'node/10665806769','station')
N('museumpark','חניון VPS MÚZEUM','VPS MÚZEUM car park',[49.1661453,20.2838101],'way/740981998','parking')
N('lompark','החניון המדורג · Lomnica','Cascade car park · Lomnica',[49.165041,20.2715763],'way/737770730','parking')
N('lombase','תחנת הגונדולה · Lomnica','Gondola station · Lomnica',[49.164993,20.270326],'node/3358061873','station')
N('bachpark','חניה ראשית בעמק Bachledka','Main valley car park · Bachledka',[49.2717986,20.3090622],'way/1468988797','parking')
N('bachbase','גונדולת Bachledka · למטה','Bachledka gondola · lower station',[49.2722171,20.3099203],'node/642266312','station')
N('bachtop','גונדולת Bachledka · למעלה','Bachledka gondola · upper station',[49.2854325,20.314786],'node/642266318','station')
N('jaspark','חניון P2 Biela Púť','P2 Biela Púť car park',[48.970812,19.5846289],'way/252323339','parking')
N('jasbase','תחנת A6 · Biela Púť','A6 station · Biela Púť',[48.9708435,19.584744],'node/10024881510','station')
N('priehyba','Priehyba · תחנת A6','Priehyba · A6 station',[48.9630901,19.5896222],'node/10024881511','station')
N('chopstation','Chopok · התחנה העליונה','Chopok · upper station',[48.9438968,19.5900743],'node/1941847909','station')
N('koliesko','Koliesko · תחנת A4','Koliesko · A4 station',[48.9632638,19.5843958],'node/13208536008','station')
N('forumpark','חניון Forum Poprad','Forum Poprad car park',[49.0536224,20.2998686],'node/9079093338','parking')
N('bonpark','חניה ציבורית · Dominika Tatarku','Public parking · Dominika Tatarku',[49.0577311,20.2975633],'way/970684797','parking')
N('p8','P8 · K vodopádom · רק אם פתוח','P8 · K vodopádom · only if open',kind='parking',query='P8 K vodopadom Strbske Pleso parking')
nodes['p8']['source']='https://www.strbskepleso.sk/parking'
N('krk','נמל התעופה קרקוב','Kraków Airport',[50.0777,19.7848],query='Krakow Airport KRK')
N('tat','נמל התעופה פופראד','Poprad Airport',[49.0736,20.2411],query='Poprad Tatry Airport')
# Endpoints missing a verified entrance stay query-only: no invented parking pins or walking times.
for id,q,he,en in [('aquapark','AquaCity Poprad parking','חניון AquaCity','AquaCity car park'),('woodpark','Woodlandia parking Liptovska Anna','חניון Woodlandia','Woodlandia car park'),('fishpark','parking Rybaren Na Haku Liptovska Sielnica','חניה ב־NA HÁKU · לברר כניסה','NA HÁKU parking · confirm entrance'),('tatrapark','Tatralandia parking','חניון Tatralandia','Tatralandia car park'),('famosapark','parking Restaurant Famosa Stara Lesna','חניה ב־Famosa · לברר מול המסעדה','Famosa parking · confirm with restaurant'),('sobpark','parking Sobotske namestie Poprad','חניה ב־Spišská Sobota · לפי שילוט','Spišská Sobota parking · follow signs')]:N(id,he,en,kind='parking',query=q)
legs={}
def L(a,b,mode='walk',he='',en='',source=None):
 id=a+'-'+b+'-'+mode
 legs[id]={'a':a,'b':b,'mode':mode}
 if he:legs[id]['note']=[he,en]
 if source:legs[id]['source']=source
 return id
W=lambda a,b:L(a,b)
D=lambda a,b:L(a,b,'drive')
C=lambda a,b,he='',en='',source=None:L(a,b,'lift',he,en,source)
def S(he,en,ls,notehe='',noteen=''):
 return {'name':[he,en],'legs':ls,'note':[notehe,noteen]}
vt='https://www.vt.sk/en/info/info/cableways-opening-hours'
jas='https://www.jasna.sk/en/activities/summer-activities/slide-park'
bach='https://bachledka.sk/en/cennik-parkoviska'
sm=[D('hotel','smokpark'),W('smokpark','trick'),W('trick','smokbase'),C('smokbase','hreb','עולים בפוניקולר; לא בהליכה מהחניה.','Take the funicular; do not walk uphill from the car park.',vt)]
smend=[C('hreb','smokbase'),W('smokbase','kamzik'),W('kamzik','smokpark'),D('smokpark','hotel')]
bl=[D('hotel','bachpark'),L('bachpark','bachbob','walk','נקודת המגלשה היא אזור בלבד; עקבו אחר שילוט הקופות. זמן ההגעה טרם אומת.','The coaster pin marks the area only; follow signs to its ticket office. Access time unverified.'),L('bachbob','bachbase','walk','עקבו אחר השילוט לגונדולה.','Follow signs to the gondola.'),C('bachbase','bachtop','חונים בעמק ועולים בגונדולה. מהחניה הראשית לקופות כ־100 מטר לפי המפעיל.','Park in the valley and take the gondola. The operator puts the main car park about 100 m from the ticket offices.',bach),W('bachtop','bach'),W('bach','panorama'),W('panorama','forest'),W('forest','bachtop'),C('bachtop','bachbase'),W('bachbase','bachpark'),D('bachpark','hotel')]
lakefull=[D('hotel','lakepark'),W('lakepark','boat'),W('boat','tower'),W('tower','orl'),W('orl','lakepark'),D('lakepark','hotel')]
lakeshort=[D('hotel','lakepark'),W('lakepark','boat'),W('boat','lakepark'),D('lakepark','hotel')]
jstart=[D('hotel','jaspark'),W('jaspark','jasbase'),C('jasbase','priehyba','A6 לפי לוח ההפעלה.','A6, subject to the operating timetable.',jas)]
jend=[C('priehyba','jasbase'),W('jasbase','jaspark'),D('jaspark','hotel')]
slide=L('priehyba','koliesko','activity','מסלול Slide Park בירידה: הליכה ומגלשות, לא מעבר קצר. אורך וזמן המסלול טרם אומתו; פנו לפחות את חלון הפעילות שבתכנית.','Slide Park is a downhill walking-and-slide activity, not a short transfer. Length and walking time are unverified; allow the activity slot in the itinerary.',jas)
lomstart=[D('hotel','museumpark'),W('museumpark','bob'),W('bob','museumpark'),D('museumpark','lompark'),W('lompark','lombase'),C('lombase','skal','עלייה דרך Štart. תורים והחלפות אינם כלולים בזמן הליכה.','Ascend via Štart. Queues and changes are not walking time.',vt)]
lomend=[C('skal','lombase'),W('lombase','lompark'),D('lompark','museumpark'),W('museumpark','pab'),W('pab','museumpark'),D('museumpark','hotel')]
water=[D('hotel','aquapark'),L('aquapark','aqua','walk','החניה מאומתת; נקודת הכניסה וזמן ההליכה ממקום החניה בפועל טרם אומתו.','The car park is confirmed; its precise entrance and walk from your space are unverified.','https://aquacity.sk/en/faq/'),W('aqua','aquapark')]
forum=[D('aquapark','forumpark'),L('forumpark','choc','walk','עוברים מתוך החניון אל הקניון ומחפשים Delikateso. הליכה בתוך המבנה אינה מחושבת במפת הרחובות.','Enter the mall from its car park and find Delikateso. Indoor walking is not calculated by street routing.','https://forumpoprad.sk/informacie/cennik-parkovania/'),W('choc','forumpark'),D('forumpark','hotel')]
wood=[D('hotel','woodpark'),W('woodpark','wood'),W('wood','woodpark'),D('woodpark','fishpark'),W('fishpark','fish'),W('fish','fishpark'),D('fishpark','hotel')]
days=[
 [S('נחיתה בפופראד → מלון','Poprad arrival → hotel',[D('tat','hotel')]),S('נחיתה בקרקוב → מלון','Kraków arrival → hotel',[D('krk','hotel')])],
 [S('פוניקולר ומסעדה · בלי המפלים','Funicular and lunch · skip waterfalls',sm+smend),S('כולל הליכה למפלים','Include waterfall walk',sm+[W('hreb','falls'),W('falls','hreb')]+smend,'המפלים מוסיפים הליכה הלוך וחזור בשטח סלעי. אין חניה ציבורית קרובה למפלים שחוסכת את השביל.','The waterfalls add an out-and-back rocky walk. There is no nearby public car park that avoids this trail.')],
 [S('Bachledka · חניה בעמק וגונדולה','Bachledka · valley parking and gondola',bl,'בקשו P1/P2 או החניה הראשית. P3 Belské מרוחקת; אל תניחו שיש שאטל קיץ. שביל הצמרות עצמו מוסיף כ־1.23 ק״מ ואינו כלול בסכום המעברים.','Aim for P1/P2 or main parking. P3 Belské is farther away; do not assume a summer shuttle. The treetop walk itself adds about 1.23 km, excluded from transfer totals.')],
 [S('שייט + מגדל + Orlíkovo','Boats + tower + Orlíkovo',lakefull,'זה אינו יום בלי הליכה. הסכום כולל חזרה לרכב, אך לא הקפת האגם או העלייה בתוך המגדל. אם זה הרבה, בחרו שייט בלבד או בדקו מראש חניה עונתית P8; חניית FIS אינה חלופה ציבורית מובטחת.','This is not a walking-free day. Totals include returning to the car, but exclude a lake circuit and climbing the tower. If too much, choose boats only or confirm seasonal P8 parking in advance; FIS parking is not a guaranteed public alternative.'),S('מסלול קצר · שייט וחזרה','Short route · boats and return',lakeshort),S('בדיקת העברת רכב ל־P8 · מותנה בפתיחה','Consider moving to P8 · subject to opening',[D('hotel','lakepark'),W('lakepark','boat'),W('boat','lakepark'),D('lakepark','p8'),L('p8','tower','walk','חניה עונתית ברחוב K vodopádom לפי אתר היעד. הכניסה המדויקת לא אומתה ולכן אין כאן הבטחת דקות או חיסכון. אשרו פתיחה וגישה ציבורית לפני המעבר.','Seasonal parking on K vodopádom, listed by the destination. Its exact entrance is unverified, so no time or saving is promised. Confirm opening and public access before moving.','https://www.strbskepleso.sk/parking'),W('tower','orl'),W('orl','p8'),D('p8','hotel')])],
 [S('Chopok ו־Slide Park · חזרה ברכבלים','Chopok and Slide Park · return by lifts',jstart+[C('priehyba','chopstation'),C('chopstation','priehyba'),slide,C('koliesko','priehyba','לאחר Slide Park עולים ב־A4, ואז יורדים ב־A6 אל Biela Púť. אשרו ששני המקטעים פועלים וכלולים בכרטיס.','After Slide Park take A4 up, then A6 down to Biela Púť. Confirm both sections operate and are included in your ticket.',jas)]+jend,'לא מסיימים ב־Koliesko ומניחים שהרכב לידכם: חנינו ב־Biela Púť. החזרה תלויה בהפעלת A4 ו־A6.','Do not finish at Koliesko expecting your car there: it is at Biela Púť. The return relies on A4 and A6 operating.'),S('יום קצר · Priehyba בלי פסגה ומגלשות','Short day · Priehyba without summit or slides',jstart+jend)],
 [S('TatraBob + אגם + PaB · שתי חניות','TatraBob + tarn + PaB · two car parks',lomstart+lomend,'חוזרים לרכב אחרי TatraBob ומעבירים אותו לרכבלים. למסעדה חוזרים לחניית המוזיאון; כך לא בונים על הליכה ארוכה מההר למרכז ובחזרה.','Return to the car after TatraBob and move to cableway parking. For dinner return to museum parking, avoiding the long walk between cableways and town.'),S('כולל הפסגה · לפי כרטיס לשעה','Include the summit · timed ticket required',lomstart+[C('skal','peak','רכבל לפסגה, לא שביל הליכה משפחתי.','Summit cable car, not a family walking trail.',vt),C('peak','skal')]+lomend),S('Famosa במקום PaB','Famosa instead of PaB',lomstart+[C('skal','lombase'),W('lombase','lompark'),D('lompark','famosapark'),W('famosapark','famosa'),W('famosa','famosapark'),D('famosapark','hotel')])],
 [S('AquaCity וחזרה','AquaCity and return',water+[D('aquapark','hotel')]),S('AquaCity + Forum · מעבירים רכב','AquaCity + Forum · move the car',water+forum),S('AquaCity + Spišská Sobota · חניה נוספת','AquaCity + Spišská Sobota · separate parking',water+[D('aquapark','sobpark'),W('sobpark','sobota'),W('sobota','sobpark'),D('sobpark','hotel')])],
 [S('ליפטוב · Woodlandia ודיג','Liptov · Woodlandia and fishing',wood,'שתי חניות נפרדות. אין מעבר ברגל בין Woodlandia ל־NA HÁKU. אורכי המסלולים בתוך האטרקציות אינם כלולים.','Two separate parking stops. Do not walk between Woodlandia and NA HÁKU. Walking inside the attractions is excluded.'),S('Tatralandia · יום מים','Tatralandia · water park day',[D('hotel','tatrapark'),W('tatrapark','tatralandia'),W('tatralandia','tatrapark'),D('tatrapark','hotel')]),S('השלמת Bachledka','Catch up on Bachledka',bl)],
 [S('Forum · מלון · ארוחה ב־PaB','Forum · hotel · dinner at PaB',[D('hotel','forumpark'),W('forumpark','choc'),W('choc','forumpark'),D('forumpark','hotel'),D('hotel','museumpark'),W('museumpark','pab'),W('pab','museumpark'),D('museumpark','hotel')]),S('השלמת TatraBob','Catch up on TatraBob',[D('hotel','museumpark'),W('museumpark','bob'),W('bob','museumpark'),D('museumpark','hotel')])],
 [S('טיסה מפופראד','Depart from Poprad',[D('hotel','tat')]),S('טיסה מקרקוב','Depart from Kraków',[D('hotel','krk')])]
]
# Useful comparisons, separate from the selected day's actual itinerary.
comparisons={'3':[W('lakepark','tower'),W('boat','orl')],'5':[W('museumpark','lombase'),W('lombase','kometa')],'6':[W('aqua','sobota'),W('aqua','choc')],'1':[W('smokpark','smokbase')]}
# Arrival / flexible days also expose a self-contained route for every optional local visit.
# Mountain activities use existing curated scenarios; do not route walking straight from valley parking to summits.
access={'trick':'smokpark','hreb':'smokpark','falls':'smokpark','kamzik':'smokpark','eliska':'smokpark','tubing':'smokpark','bach':'bachpark','bachbob':'bachpark','forest':'bachpark','panorama':'bachpark','bachslide':'bachpark','bachballs':'bachpark','lake':'lakepark','tower':'lakepark','orl':'lakepark','jasna':'jaspark','chopok':'jaspark','sheep':'jaspark','jasballs':'jaspark','minitrain':'jaspark','bob':'museumpark','pab':'museumpark','kometa':'museumpark','skal':'lompark','peak':'lompark','carts':'lompark','aqua':'aquapark','choc':'forumpark','bon':'bonpark','sobota':'sobpark','wood':'woodpark','fish':'fishpark','tatralandia':'tatrapark','famosa':'famosapark'}
for a,b in [('smokpark','eliska'),('museumpark','kometa'),('bonpark','bon')]:W(a,b)
obj={'checked':'2026-09-24','nodes':nodes,'legs':legs,'days':days,'comparisons':comparisons,'access':access}
p=root/'day-routes-data.js';p.write_text('/* Public access plan; coordinates © OpenStreetMap contributors, ODbL. */\nwindow.DAY_ROUTES='+json.dumps(obj,ensure_ascii=False,separators=(',',':'))+';\n')
print(len(nodes),'nodes;',len(legs),'legs;',sum(map(len,days)),'day variants')
