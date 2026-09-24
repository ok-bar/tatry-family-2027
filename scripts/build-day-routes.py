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
N('krk','נמל התעופה קרקוב','Kraków Airport',[50.072048,19.8017213],query='Krakow Airport KRK')
N('tat','נמל התעופה פופראד','Poprad Airport',[49.068698,20.247995],query='Poprad Tatry Airport')
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
# Family transfer policy: at most ten minutes per walking leg.
N('rabkapark','חניה ליד Park Zdrojowy · SIMPLY PARKING','Parking by Park Zdrojowy · SIMPLY PARKING',[49.607471,19.964192],'way/372327954','parking')
N('rabkaplay','מגרש המשחקים בפארק Rabka','Rabka park playground',[49.6058003,19.9625723],'way/75005099')
N('icepark','חניה במרכז Nowy Targ','Nowy Targ town-centre parking',[49.4791579,20.0252501],'way/292843787','parking')
N('fispublic','P1 ציבורי ליד FIS · בתשלום','Public P1 by FIS · paid parking',[49.1278248,20.061735],'way/819541302','parking')
nodes['fispublic']['accessSource']='https://www.tmrhotels.com/hotel-fis/sk/Parkovanie/'
nodes['fispublic']['note']=['לפי מלון FIS, חניון P1 ציבורי ובתשלום ואינו בניהול המלון. אין להיכנס לחניות P2–P4 של האורחים; השילוט וזמינות ביום הביקור קובעים.','Hotel FIS identifies P1 as public paid parking, operated separately from the hotel. Do not use guest parking P2–P4; follow current signs and availability.']
for id,ll,osm in [('aquapark',[49.0607417,20.3072689],'way/416190961'),('woodpark',[49.1393108,19.4642496],'way/1544904473'),('fishpark',[49.1455836,19.5179062],'way/1418853995'),('tatrapark',[49.1043583,19.5717757],'way/234171470'),('famosapark',[49.1445298,20.2921919],'way/1298670624')]:
 nodes[id]['ll']=ll;nodes[id]['source']='https://www.openstreetmap.org/'+osm;nodes[id].pop('query',None)
N('aquaentry','הכניסה הראשית ל־AquaCity','AquaCity main entrance',[49.0606067,20.3076342],'node/4170185486')
# Airport pickup / final hotel arrival are destination areas, not measured indoor walks.
arrival=[D('krk','rabkapark'),W('rabkapark','rabkaplay'),W('rabkaplay','rabkapark'),D('rabkapark','icepark'),W('icepark','krzywa'),W('krzywa','icepark'),D('icepark','hotel')]
days[0].insert(0,S('קרקוב → פארק Rabka → גלידה → מלון','Kraków → Rabka park → ice cream → hotel',arrival,'כל נסיעה מתחילה בחניה של העצירה הקודמת. בפארק בוחרים את מגרש המשחקים הקרוב; לא מקיפים את הפארק. אפשר לדלג על עצירה אם הנחיתה מאוחרת.','Each drive starts at the previous stop’s car park. Visit the nearby playground, not the whole park. Skip a stop after a late arrival.'))
days[0].insert(1,S('קרקוב → פארק Rabka → מלון','Kraków → Rabka park → hotel',arrival[:3]+[D('rabkapark','hotel')]))
access.update({'rabka':'rabkapark','krzywa':'icepark','tower':'fispublic','orl':'fispublic'})
# A public car park close to the northern activities avoids the long lakeside transfer.
lakeboth=[D('hotel','lakepark'),W('lakepark','boat'),W('boat','lakepark'),D('lakepark','fispublic'),W('fispublic','tower'),W('tower','orl'),W('orl','fispublic'),D('fispublic','hotel')]
laketower=[D('hotel','fispublic'),W('fispublic','tower'),W('tower','orl'),W('orl','fispublic'),D('fispublic','hotel')]
days[3]=[S('עד 10 דקות במעברים · מגדל ו־Orlíkovo','Transfers within 10 min · tower and Orlíkovo',laketower,'השייט לא נכנס למסלול הקצר: מהחניון המרכזי לרציף כ־741 מ׳, כלומר כ־12–15 דק׳ לכל כיוון. אין לנו עדיין חניה ציבורית מאומתת ליד הרציף שמקצרת זאת לעד 10 דקות. כדי להוסיף שייט צריך לאשר חניה/הסעה קרובה מראש. העלייה בתוך המגדל היא מאמץ נוסף.','Boating is excluded from this short route: central parking to the jetty is about 741 m, or 12–15 min each way. No confirmed public parking by the jetty yet reduces this to 10 min. Add boating only after confirming closer parking or transport. Climbing the tower is additional effort.'),S('עם שייט ושתי חניות · עדיין חורג מ־10 דקות לשייט','Boating with two car parks · boat access still exceeds 10 min',lakeboth,'אחרי השייט חוזרים לאותו רכב ונוסעים ל־P1 הציבורי ליד FIS. לא הולכים מהשייט למגדל. ההליכה לרציף ובחזרה עדיין חורגת מהמגבלה; המסלול מוצג להשוואה בלבד.','Return to the same car after boating, then drive to public P1 by FIS. Do not walk from the boats to the tower. Jetty access and return still exceed your limit; this variant is for comparison only.'),S('המסלול הישן ברגל · לא מתאים למגבלת 10 דקות','Original walking route · exceeds the 10-minute limit',lakefull)]
# Keep optional long activity days visible, but make the short transfer plan the first choice.
days[4]=[days[4][1],days[4][0]]
shortbach=[D('hotel','bachpark'),L('bachpark','bachbob','walk','הכניסה המדויקת למגלשה לא אומתה. בקשו מהצוות חניה/גישה עד 10 דקות לפני שקונים כרטיס.','The coaster entrance is unverified. Ask staff to confirm parking/access within 10 min before buying a ticket.'),W('bachbob','bachpark'),D('bachpark','hotel')]
days[2].insert(0,S('מגלשת הרים בלבד · יש לאשר גישה קצרה','Coaster only · confirm short access',shortbach,'שביל הצמרות עצמו כ־1.23 ק״מ ולכן אינו מתאים למגבלת 10 דקות הליכה כוללת ברצף. גם המעבר המחושב בין PANORAMA לממלכת היער מעל 10 דקות. המסלול המלא נשאר להשוואה, ולא כהמלצה למגבלה שלכם.','The treetop walk itself is about 1.23 km and does not fit a continuous 10-minute walking limit. The calculated PANORAMA–Forest Kingdom transfer also exceeds 10 min. The full variant remains for comparison, not as a recommendation under your limit.'))
# Use an entrance, not a pool-area centroid.
for key,l in list(legs.items()):
 if l['a']=='aquapark' and l['b']=='aqua':l['b']='aquaentry';l['note']=['מחניית המבקרים לכניסה הראשית. זמן ההליכה בפנים, למלתחות ולבריכות, נוסף בנפרד.','From visitor parking to the main entrance. Walking inside to changing rooms and pools is additional.']
 if l['a']=='aqua' and l['b']=='aquapark':l['a']='aquaentry'
# Preserve key identity for previously declared route lists; renderer resolves by endpoints too.
for a,b in [('rabkapark','rabkaplay'),('icepark','krzywa'),('fispublic','tower'),('fispublic','orl'),('smokpark','smokbase'),('smokpark','eliska'),('museumpark','kometa'),('bonpark','bon'),('bachpark','bachbase')]:W(a,b);W(b,a)
# Facts about walking inside attractions must not be hidden by short parking access.
activityWarnings={
 'bach':['שביל הצמרות: כ־1.23 ק״מ בתוך הפעילות, בנוסף לגישה. לא מתאים ל־10 דקות הליכה רצופה.','Treetop walk: about 1.23 km inside the attraction, beyond access. Not a 10-minute continuous walk.'],
 'wood':['Woodlandia: מסלול טבע של כ־1.6 ק״מ. חניה קרובה אינה מקצרת את המסלול; לא לבחור את המסלול המלא תחת מגבלת 10 דקות.','Woodlandia: a nature trail of about 1.6 km. Nearby parking does not shorten it; avoid the full trail with a 10-minute limit.'],
 'falls':['המפלים דורשים הליכת שטח מעבר ל־10 דקות; אין תחליף של חניה צמודה. בחרו Hrebienok ליד הפוניקולר בלבד.','The waterfalls require a trail walk beyond 10 minutes, with no adjacent parking alternative. Stay near the Hrebienok funicular instead.'],
 'tower':['העלייה בתוך המגדל אינה כלולה במרחק מהחניה. חניה קרובה אינה מבטיחה פעילות של עד 10 דקות הליכה.','Climbing inside the tower is excluded from parking access. Nearby parking does not make the activity a walk of under 10 minutes.'],
 'jasna':['Slide Park הוא מסלול ירידה עם הליכה בין מגלשות. אורכו טרם נמדד כאן; תחת מגבלת 10 דקות בוחרים רכבלים וחזרה ולא מניחים שהמגלשות חוסכות הליכה.','Slide Park is a downhill trail with walking between slides. Its length is unmeasured here; with a 10-minute limit use the lifts and return instead.']}
# Surface advice for every date, including the days without measured indoor / hotel paths.
familyNotes=[
 ['קרקוב → חניית פארק → משחק → אותה חניה → חניית גלידה → גלידה → אותה חניה → מלון. שעת נחיתה מאוחרת: דלגו על עצירה.','Kraków → park parking → playground → same car → ice-cream parking → café → same car → hotel. Skip a stop after a late landing.'],
 ['משאירים את הרכב ב־TATRA לעיירה ולפוניקולר; בוחרים ב־Hrebienok בלי המפלים.','Keep the car at TATRA for town and the funicular; choose Hrebienok without the waterfalls.'],
 ['חניה קרובה לגונדולה אינה מבטלת הליכה בתוך שביל הצמרות. המסלול המלא דורש שינוי כדי לעמוד במגבלה.','Parking near the gondola does not remove walking on the treetop walk. The full day needs changes to meet your limit.'],
 ['למגדל ול־Orlíkovo משתמשים ב־P1 ליד FIS. אין מעבר רגלי מומלץ מהשייט למגדל תחת המגבלה שלכם.','Use public P1 by FIS for the tower and Orlíkovo. Walking from the boats to the tower is not recommended under your limit.'],
 ['P2 → A6 → Priehyba → רכבל חזרה. Slide Park והפסגה הם אפשרויות נפרדות שדורשות בדיקת הליכה בתוך הפעילות.','P2 → A6 → Priehyba → lift back. Slide Park and the summit are separate choices requiring checks of walking within the activity.'],
 ['TatraBob: חניית המוזיאון. לרכבלים מעבירים את הרכב לחניון המדורג, ואחר כך חונים שוב ליד ארוחת הערב.','TatraBob: museum parking. Move the car to cascade parking for the lifts, then park again near dinner.'],
 ['אחרי הבריכות חוזרים לרכב לפני כל תוספת בעיר. אין מסלול ברגל מ־AquaCity ל־Forum או לרובע העתיק כברירת מחדל.','Return to the car after the pools before any town visit. Walking from AquaCity to Forum or the old quarter is not the default.'],
 ['בוחרים יום אחד. Woodlandia כוללת 1.6 ק״מ הליכה ולכן אינה ברירת המחדל למגבלה שלכם.','Choose one outing. Woodlandia involves a 1.6 km walk and is not the default under your limit.'],
 ['חניה נפרדת לקניות ולמסעדה; לא מחברים אותן בטיול רגלי.','Separate parking for shopping and dinner; do not connect them with a walking tour.'],
 ['הנסיעה היא מהמלון לשדה שנבחר. הליכה מהחזרת הרכב לטרמינל תלויה בחברת ההשכרה וטרם אומתה.','Drive from the hotel to the selected airport. Walking from rental return to the terminal depends on the rental company and remains unverified.']]
days[7]=[days[7][1],days[7][0],days[7][2]]
# Default flexible-day catch-up inherits the explicitly cautioned Bachledka options.

N('tatralandia','Tatralandia · כניסה ראשית','Tatralandia · main entrance',[49.1053546,19.5705677],'node/9951083984')
obj={'checked':'2026-09-24','nodes':nodes,'legs':legs,'days':days,'comparisons':comparisons,'access':access,'walkLimit':10,'activityWarnings':activityWarnings,'familyNotes':familyNotes}
p=root/'day-routes-data.js';p.write_text('/* Public access plan; coordinates © OpenStreetMap contributors, ODbL. */\nwindow.DAY_ROUTES='+json.dumps(obj,ensure_ascii=False,separators=(',',':'))+';\n')
print(len(nodes),'nodes;',len(legs),'legs;',sum(map(len,days)),'day variants')
