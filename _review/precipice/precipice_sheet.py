from lib import *
from mk_sheet import build
import sys, json, os, math
import numpy as np

os.chdir('/home/claude/parks')
p = Park('precipice', 44.3515, -68.1945)
# key points (local feet, x east / n north from 44.3515, -68.1945); all from OSM
SUM = (117, -256)      # Champlain Mountain, 323 m (OSM peak node)
HUG = (-1411, 635)     # Huguenot Head, 222 m (OSM peak node); the Beachcroft Path circles below it
PTH = (1712, -724)     # Precipice Trail start at the Precipice parking area on the Park Loop Road (OSM way end)
OBJ = (1229, -35)      # Orange & Black Path meets the Precipice Trail (OSM shared vertex)
NRJ = (709, 2297)      # Champlain North Ridge Trail meets the Orange & Black Path (OSM way end)
FORK = (915, 1846)     # Orange & Black Path fork at the base of the stone staircase (OSM way end)
BTH = (-2866, 2506)    # Beachcroft Path trailhead, east side of ME Route 3 (OSM way end)
TARN = (-3301, 2558)   # north end of The Tarn, Wild Gardens / Jesup / Kane / Beachcroft junction (OSM)
SDM = (-3480, 3800)    # Sieur de Monts: Nature Center, spring and Wild Gardens (OSM memorial/water nodes)
SPRING = (-3649, 3591)  # Sieur de Monts Spring (OSM natural=spring)
BOWL = (1083, -6446)   # The Bowl, south shore where the Bowl Trail passes (no OSM polygon)
BOWLJ = (525, -5767)   # Champlain South Ridge Trail meets the Bowl Trail (OSM)
BWT = (2422, -7265)    # Bowl Trail trailhead on the Park Loop Road, across from the Sand Beach entrance (OSM way end)
SAND = (2633, -7876)   # Sand Beach parking / beach entrance


def cat(*rs):
    # join routes end to end (the Beachcroft Path crosses Route 3 where OSM leaves a 37-ft gap)
    pts = []; E = []
    for r in rs:
        a = 0 if not pts else 1
        pts += r['pts'][a:]; E += r['E'][a:]
    cum = [0.0]
    for i in range(1, len(pts)): cum.append(cum[-1] + math.dist(pts[i - 1], pts[i]))
    segs = []; off = 0
    for r in rs:
        for nm, m in r['segs']:
            if not segs or segs[-1][0] != nm: segs.append([nm, round(m + off, 2)])
        off += r['mi']
    gain = sum(max(0, E[i] - E[i - 1]) for i in range(1, len(E)))
    return dict(pts=pts, E=E, cum=cum, segs=segs, gain=gain, mi=cum[-1] / 5280, lo=min(E), hi=max(E))


R = {}
R['A'] = route_xy(p, BTH, SUM)
R['B'] = route_xy(p, PTH, OBJ, (905, -656), SUM, NRJ, FORK, (1640, 1950), (1590, 600), PTH)
R['C'] = cat(route_xy(p, SDM, TARN, (-2884, 2538)), route_xy(p, BTH, SUM, (-720, -5285), BOWLJ, (904, -6476), BWT, SAND))
for k in R: Park.smooth_E(R[k], 9); p.describe(R[k], k)
ST = snap_stops(p, R, {
    'S1': BTH + ('AC',), 'S2': (-1250, 560, 'AC'), 'S3': SUM + ('ABC',),
    'B1': PTH + ('B',), 'B2': OBJ + ('B',), 'B3': (803, -613, 'B'), 'B4': NRJ + ('B',), 'B5': FORK + ('B',),
    'C1': SDM + ('C',), 'C2': TARN + ('C',), 'C3': BOWL + ('C',), 'C4': SAND + ('C',),
})
TILE = (-5800, 5400, -10600, 6200)
GRID = (-6100, 5700, -10900, 6500)
if 'plot' in sys.argv:
    from plot import plot
    plot(p, TILE, 'precipice/routes.png', routes=R, stops=ST, title='precipice', grid=1000)
    sys.exit()

STEP = 80
b64, NX, NN = p.dem_b64(*GRID, STEP=STEP)
T_ = p.grid[int((TILE[2] - GRID[2]) / STEP):int((TILE[3] - GRID[2]) / STEP), int((TILE[0] - GRID[0]) / STEP):int((TILE[1] - GRID[0]) / STEP)]
RIDGE = int(round(float(np.percentile(T_[T_ > 5], 75)), -1))
print('grid', NX, NN, NX * NN, p.grid.min(), p.grid.max(), 'p75', RIDGE)

S = lambda i: ST[i]
def st(i, trs, name, desc): return dict(id=i, trails=list(trs), x=S(i)[0], n=S(i)[1], name=name, desc=desc)
stops = [
 st('S1', 'AC', 'Beachcroft Path trailhead', 'On ME Route 3 just south of the Sieur de Monts entrance. A small lot sits on the west side of the road by the Tarn; the path starts directly across, so cross with care.'),
 st('S2', 'AC', 'Huguenot Head', 'The path climbs cut granite stairs and crosses a big boulder field, then circles below the summit of Huguenot Head, a little over 700 ft. The best views back over the Tarn and Dorr Mountain are from these ledges.'),
 st('S3', 'ABC', 'Champlain Mountain summit', '1,058 ft, the highest point on the east side of Mount Desert Island. Open granite with views over Frenchman Bay, the Porcupine Islands, Bar Harbor and the Schoodic Peninsula. The Beachcroft Path, the Precipice and both ridge trails meet here.'),
 st('B1', 'B', 'Precipice trailhead', 'The Precipice parking area on the one-way Park Loop Road, below Champlain’s east face. The lot is small and closes to cars with the trail during the peregrine falcon closure.'),
 st('B2', 'B', 'Orange & Black Path junction', 'After a traverse of a rugged slope, with a wooden bridge and iron handrails on narrow ledges, the Orange & Black Path comes in from the right. Stay left on the Precipice Trail.'),
 st('B3', 'B', 'Iron rungs and ladders', 'Iron rungs and ladders lead up the open cliff of the east face, with long drops and no railings. Many of the rungs date from 1920s trailwork; the route was laid out about 1913 by Rudolph Brunnow. Granite slopes above lead to the summit.'),
 st('B4', 'B', 'North Ridge / Orange & Black junction', 'About 0.6 mile down the open granite of the Champlain North Ridge Trail. Turn right onto the Orange & Black Path, named by Brunnow for the colors of Princeton, where he taught.'),
 st('B5', 'B', 'Stone staircase fork', 'At the base of a stone staircase the Orange & Black Path splits. This loop keeps right, traversing the rocky east face back to the Precipice Trail. Left is easier: it drops to the Park Loop Road, which leads south to the parking area; watch for traffic.'),
 st('C1', 'C', 'Sieur de Monts', 'The Nature Center, the Wild Gardens of Acadia and Sieur de Monts Spring, under a small domed spring house. Restrooms and water. The Island Explorer bus stops here mid-June to mid-October.'),
 st('C2', 'C', 'The Tarn', 'A shallow pond in the gap between Dorr Mountain and Huguenot Head, about 0.3 mile south of Sieur de Monts on the Wild Gardens Path. It is slowly filling in to meadow.'),
 st('C3', 'C', 'The Bowl', 'A small mountain pond behind the Beehive, about 1.6 miles down the South Ridge from the summit. Swimming is allowed. From here the Bowl Trail drops to Sand Beach.'),
 st('C4', 'C', 'Sand Beach', 'The Bowl Trail ends on the Park Loop Road across from the Sand Beach entrance. Restrooms, water and an Island Explorer stop for the ride back to Sieur de Monts.'),
]
stops, order = renumber(p, R, stops)
print(order, [(s['id'], s['name']) for s in stops])
trails = [
 dict(id='A', name='Beachcroft Path', short='Beachcroft', official=2.4, unit='round trip', route='Out and back', time='2–3 hr', level='Strenuous', color='--tA',
      desc='A memorial path built in 1915, climbing about 950 ft in 1.2 miles on cut granite steps and flat stone paving. It switchbacks up past Huguenot Head, dips into a small notch, then scrambles up open ledges to the summit of Champlain Mountain. The bare granite near the top is slick when wet. Return the same way.', anchors=p.anchors(R['A'])),
 dict(id='B', name='Precipice Loop', short='Precipice', official=2.5, unit='loop', route='Loop', time='2–3 hr', level='Strenuous', color='--tB',
      desc='Acadia’s best-known iron-rung climb: over 1,000 ft in 0.9 mile up Champlain’s east face on ledges, iron rungs and ladders. Not for children under 12, anyone afraid of heights, or wet weather, and no pets. Do not descend the Precipice: come down the North Ridge Trail and the Orange & Black Path. Closed each spring and summer for nesting peregrine falcons.', anchors=p.anchors(R['B'])),
 dict(id='C', name='Champlain traverse, Sieur de Monts to Sand Beach', short='Champlain traverse', official=3.7, unit='one way', route='One way', time='2–4 hr', level='Strenuous', color='--tC',
      desc='A one-way crossing of Champlain Mountain: past the Tarn, up the Beachcroft Path to the summit, then down the long, open South Ridge to the Bowl and the Bowl Trail to Sand Beach. The climb is the hard part; the descent is gentler but rocky. Use the Island Explorer bus (summer to mid-October) to get back.', anchors=p.anchors(R['C'])),
]

TARNP = [p.xy(q) for q in p.WID['128577414']['p']]
pa = place_along
A_ = lambda k, f, s=1, o=400: pa(p, R[k], [f], s, o)[0]
def path(k, f, s=1, o=500, d=0.04): return js(A_(k, f, s, o) + A_(k, f + d, s, o))
an = []
an += [f'{{k:"deer",path:{path("C",.17,-1,600)},per:28}}', f'{{k:"deer",path:{path("B",.86,1,500)},per:30,ph:0.4}}']
an += [f'{{k:"fox",path:{path("C",.86,1,500)},per:24}}']
an += [f'{{k:"beaver",at:{js([SDM[0] + 40, SDM[1] + 520])}}}']
TC = [round(sum(q[0] for q in TARNP) / len(TARNP)), round(sum(q[1] for q in TARNP) / len(TARNP))]
an += [f'{{k:"otter",at:{js(TC)}}}', f'{{k:"raccoon",at:{js(A_("C",.07,1,380))}}}', f'{{k:"coyote",path:{path("C",.66,-1,650)},per:32}}']
an += [f'{{k:"squirrel",at:{js(A_("C",.6,-1,320))},hop:true}}', f'{{k:"squirrel",at:{js(A_("A",.55,-1,320))},hop:true}}']
an += [f'{{k:"chipmunk",at:{js(A_("B",.15,-1,260))},hop:true}}', f'{{k:"chipmunk",at:{js(A_("C",.74,1,280))},hop:true}}']
an += [f'{{k:"snake",path:{path("C",.5,1,300,.02)},per:30}}']
animals_js = '[\n ' + ',\n '.join(an) + '\n]'

species_extra = {
 'blueberry': 'blueberry:{name:"Lowbush blueberry",latin:"Vaccinium angustifolium",color:"#4A5FA8",shape:"berry",bloom:[5,6],fruit:[7,8,9],sum:"A knee-high shrub that carpets the open granite of Champlain’s ridges. White bell flowers in late spring, berries in August, and red leaves in fall.",rule:(d,e,g,s)=>e>300&&g<0.8}',
 'sheeplaurel': 'sheeplaurel:{name:"Sheep laurel",latin:"Kalmia angustifolia",color:"#D9558E",shape:"dome",bloom:[6,7],sum:"A low evergreen shrub with rings of small deep-pink flowers in early summer, common on ledges and heath openings. The leaves are poisonous to livestock.",rule:(d,e,g,s)=>e>200&&g<0.9}',
 'rhodora': 'rhodora:{name:"Rhodora",latin:"Rhododendron canadense",color:"#C46BB8",shape:"dome",bloom:[5,6],sum:"A small native azalea whose rose-purple flowers open before the leaves, in late May and early June. Look in the Wild Gardens at Sieur de Monts and in damp spots along the ridges.",rule:(d,e,g,s)=>(e<120&&s<0.3)||(e>500&&g<0.5)}',
 'harebell': 'harebell:{name:"Harebell",latin:"Campanula rotundifolia",color:"#8C86D8",shape:"cup",bloom:[6,7,8,9],sum:"Nodding blue-violet bells on thin stems, growing from cracks in the granite on the summit ledges.",rule:(d,e,g,s)=>e>400&&g>0.15}',
 'cinquefoil': 'cinquefoil:{name:"Three-toothed cinquefoil",latin:"Sibbaldia tridentata",color:"#F5F3EA",shape:"cup",bloom:[6,7,8],sum:"A low, mat-forming plant of the open summits, with small white five-petaled flowers and three-toothed leaves that turn red in fall.",rule:(d,e,g,s)=>e>600&&g<0.8}',
 'sandwort': 'sandwort:{name:"Mountain sandwort",latin:"Minuartia groenlandica",color:"#FBFAF4",shape:"cup",bloom:[6,7,8],sum:"Tiny white flowers in tufts in the thin soil of granite crevices near the summit. Step on bare rock to spare them.",rule:(d,e,g,s)=>e>800}',
 'bunchberry': 'bunchberry:{name:"Bunchberry",latin:"Cornus canadensis",color:"#F3F1E6",shape:"dome",bloom:[5,6,7],fruit:[8,9],sum:"A tiny dogwood of the spruce woods, with four white bracts in early summer and a cluster of red berries in late summer.",rule:(d,e,g,s)=>e>40&&e<600&&g<0.6&&s<0.25}',
}

# --- ponds (OSM polygons): The Tarn, Beaver Dam Pond, Kief Pond
lakes = []
for i in ('128577414', '220269935', '186629248'):
    P = [p.xy(q) for q in p.WID[i]['p']]
    if P[0] == P[-1]: P = P[:-1]
    lakes.append([[round(x), round(n)] for x, n in P])
extra_js = '''
function lakeP(){return lakeP.c||(lakeP.c=%s);}
function inLake(x,n){for(const P of lakeP()){let c=false;for(let i=0,j=P.length-1;i<P.length;j=i++){const a=P[i],b=P[j];if((a[1]>n)!==(b[1]>n)&&x<(b[0]-a[0])*(n-a[1])/(b[1]-a[1])+a[0])c=!c;}if(c)return true;}return false;}
(function(){const mat=new THREE.MeshLambertMaterial({color:"#8FC6DA",side:THREE.DoubleSide});const edge=new THREE.LineBasicMaterial({color:"#5E9FB8"});
  lakeP().forEach(P=>{const sh=new THREE.Shape(P.map(([x,n])=>new THREE.Vector2(x,n)));const geo=new THREE.ShapeGeometry(sh);const pa=geo.attributes.position;
    for(let i=0;i<pa.count;i++){const x=pa.getX(i),n=pa.getY(i);const v=G(x,n,0.12);pa.setXYZ(i,v.x,v.y,v.z);}
    pa.needsUpdate=true;geo.computeVertexNormals();const m=new THREE.Mesh(geo,mat);m.renderOrder=1;world.add(m);
    const ring=P.concat([P[0]]).map(([x,n])=>G(x,n,0.14));world.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints(ring),edge));});
})();
''' % js(lakes)

b3 = S('B3')
lm = f'''  gate({BTH[0] + 60},{BTH[1] - 50},1.2);gate({PTH[0] + 60},{PTH[1] + 30},1.6);gate({SDM[0] + 50},{SDM[1] + 40},0.3);gate({BWT[0] + 40},{BWT[1] - 60},1.4);
  // Sieur de Monts Spring house: small open domed canopy (OSM spring node)
  {{const g=new THREE.Group();g.position.copy(G({SPRING[0]},{SPRING[1]}));g.scale.set(1.6,1.6,1.6);world.add(g);
   part(g,cyl,"#E8E2D4",0,0.08,0,0.75,0.16,0.75,1.06);[[0.5,0.5],[0.5,-0.5],[-0.5,0.5],[-0.5,-0.5]].forEach(([a,b])=>part(g,cyl,"#EFEBE2",a,0.65,b,0.08,1.0,0.08,1.06));
   part(g,box,"#E3DDCF",0,1.2,0,1.25,0.14,1.25,1.06);part(g,new THREE.SphereGeometry(0.62,14,8,0,Math.PI*2,0,Math.PI/2),"#B9AE96",0,1.27,0,1,1,1,1.06);}}
  // iron rungs and ladders on Champlain's east face, facing east (drawn large)
  {{const g=new THREE.Group();g.position.copy(G({b3[0] + 60},{b3[1]}));g.rotation.y=Math.PI/2;g.scale.set(1.7,1.7,1.7);world.add(g);
   part(g,box,"#9A9184",0,1.0,-0.25,1.6,2.2,0.5,1.04);
   part(g,cyl,"#3E3E3E",-0.35,1.15,0.08,0.05,2.3,0.05,0);part(g,cyl,"#3E3E3E",0.35,1.15,0.08,0.05,2.3,0.05,0);
   for(let i=0;i<7;i++)part(g,box,"#2F2F2F",0,0.2+i*0.32,0.1,0.78,0.07,0.09,0);}}
  // Champlain Mountain summit: stone cairn and sign (OSM peak)
  {{const g=new THREE.Group();g.position.copy(G({SUM[0]},{SUM[1]}));g.scale.set(1.9,1.9,1.9);world.add(g);
   [[0.9,0.35],[0.7,0.3],[0.52,0.28],[0.36,0.26],[0.22,0.22]].reduce((y,[r,h])=>{{part(g,new THREE.CylinderGeometry(r,r*1.1,h,9),"#B9B2A6",0,y+h/2,0,1,1,1,1.06);return y+h;}},0);
   part(g,cyl,"#6B4F3A",0.95,0.6,0,0.05,1.2,0.05,0);part(g,box,"#F4F1E8",0.95,1.1,0,0.08,0.3,0.6,1.06);}}
  // Beachcroft Path granite steps below Huguenot Head
  {{const q=G({S('S2')[0] - 120},{S('S2')[1] + 40});for(let i=0;i<5;i++)part(world,box,"#CFC6B6",q.x+i*0.28,q.y+0.1+i*0.16,q.z,0.32,0.16,0.9,1.04);}}
  bench({SAND[0] + 80},{SAND[1] - 40},0.6);
'''

tree_rule = '''if(inLake(x,n)||e<14){type=null;}
    else if(mk<0.25){type=tr()<.7?"conifer":"oak";p=0.05;}
    else if(g>1.0)type=null;
    else if(e>700||g>0.7){type=tr()<.6?"shrub":"conifer";p=0.06;}
    else if(cd<230){type=tr()<.5?"syc":"conifer";p=0.4;}
    else{const r0=tr();type=r0<.55?"conifer":r0<.8?"oak":r0<.9?"gold":"shrub";p=0.3+cl*.25;}'''

canyons = []
for wid in [w['id'] for w in p.W if w['k'] == 'stream' and w.get('n') in ('Cromwell Creek', 'Bear Brook')]:
    c = p.creek([wid], GRID, minor=True)
    if c: canyons.append(dict(id='cr' + wid, **c))
print('creeks', len(canyons))

RU = json.load(open('/mnt/files/gtb/cfg/precipice_reuse.json'))
def ph(*fs): return [RU[f] for f in fs if f in RU]
PH = json.load(open('precipice/photos.json')) if os.path.exists('precipice/photos.json') else {}
flower_photos = {'blueberry': ph('sp_ac_blueberry_2.jpg', 'sp_ac_blueberry_3.jpg'), 'sheeplaurel': ph('sp_ac_sheeplaurel_1.jpg', 'sp_ac_sheeplaurel_3.jpg'),
                 'rhodora': ph('sp_rhodora_fr_0.jpg', 'sp_rhodora_fr_3.jpg'), 'harebell': ph('sp_ac_harebell_0.jpg', 'sp_ac_harebell_3.jpg'),
                 'sandwort': ph('sp_sandwort_fr_0.jpg'), 'bunchberry': ph('sp_ac_bunchberry_1.jpg', 'sp_ac_bunchberry_2.jpg')}
flower_photos.update(PH.get('flower', {}))
animal_photos = {'deer': ph('sp_ac_wtdeer_0.jpg', 'sp_ac_wtdeer_3.jpg'), 'fox': ph('sp_ac_redfox_2.jpg', 'sp_ac_redfox_3.jpg'),
                 'squirrel': ph('sp_ac_redsquirrel_1.jpg', 'sp_ac_redsquirrel_3.jpg'), 'chipmunk': ph('sp_ac_chipmunk_0.jpg', 'sp_ac_chipmunk_3.jpg'),
                 'snake': ph('sp_ac_garter_1.jpg', 'sp_ac_garter_3.jpg'), 'peregrine': ph('sp_ac_peregrine_0.jpg', 'sp_ac_peregrine_2.jpg'),
                 'gull': ph('sp_ac_gull_0.jpg', 'sp_ac_gull_3.jpg'), 'coyote': ph('sp_coyote_0.jpg'), 'otter': ph('sp_riverotter_0.jpg', 'sp_riverotter_1.jpg'), 'raccoon': ph('sp_raccoon_dl_0.jpg', 'sp_raccoon_dl_3.jpg'), 'eagle': ph('sp_ac_eagle_1.jpg', 'sp_ac_eagle_3.jpg'), 'osprey': ph('sp_osprey_gt_0.jpg', 'sp_osprey_0.jpg'), 'vulture': ph('sp_vulture_sed_0.jpg', 'sp_vulture_sed_3.jpg'), 'raven': ph('sp_raven_1.jpg'), 'beaver': ph('sp_beaver_2.jpg', 'sp_beaver_3.jpg')}

NOTE = ('Acadia National Park, Mount Desert Island, Maine. Precipice parking area on the one-way Park Loop Road; Beachcroft Path trailhead on ME Route 3 '
        'south of the Sieur de Monts entrance. A park entrance pass is required ($35 per private vehicle, 7 days). The Park Loop Road is open to cars '
        'April 15 to December 1. The fare-free Island Explorer bus stops at Sieur de Monts and Sand Beach in summer to mid-October. '
        'Status (November 2026): the Precipice Trail and its parking lot closed on March 1, 2026 to protect nesting peregrine falcons, “until further notice”; '
        'it usually reopens in late summer once the chicks fledge, and the park’s current-conditions page lists no trail closures. Check before you go. '
        'Terrain from USGS elevation data, stylized; not for navigation.')
cfg = dict(
    title='The Precipice & Champlain Mountain', aria='the Precipice Trail, the Beachcroft Path and Champlain Mountain in Acadia National Park', h1='The Precipice & Champlain · Acadia',
    canyons=canyons, trails=trails, stops=stops, order=order,
    species=list(species_extra), species_extra=species_extra,
    flora={'A': ['blueberry', 'sheeplaurel', 'harebell', 'cinquefoil'], 'B': ['blueberry', 'harebell', 'sandwort', 'cinquefoil'], 'C': ['rhodora', 'bunchberry', 'blueberry', 'sheeplaurel']},
    wild=['deer', 'fox', 'coyote', 'beaver', 'otter', 'raccoon', 'squirrel', 'chipmunk', 'snake', 'peregrine', 'eagle', 'osprey', 'vulture', 'raven', 'gull'],
    wild_sum={'deer': ('White-tailed deer', 'The common deer of Mount Desert Island. Look in the woods around Sieur de Monts and along the Park Loop Road at dawn and dusk.'),
              'fox': ('Red fox', 'Hunts mice and voles along forest edges; sometimes trots along the Park Loop Road near Sand Beach early in the morning.'),
              'beaver': ('American beaver', 'Beavers live in the Great Meadow just north of Sieur de Monts; a lodge can be seen from the Emery Path. Best at dusk.'),
              'squirrel': ('Red squirrel', 'A small, noisy squirrel of the spruce woods that chatters at hikers and leaves piles of cone scales on rocks.'),
              'chipmunk': ('Eastern chipmunk', 'Darts between the granite blocks and roots on the lower slopes from spring to fall.'),
              'snake': ('Common garter snake', 'A harmless striped snake that suns on warm granite along the South Ridge. Acadia has no venomous snakes.'),
              'peregrine': ('Peregrine falcon', 'Rare here: peregrines vanished from Acadia after DDT and came back through chicks released at Jordan Cliffs in 1984–86; a pair now nests on Champlain’s east face, which is why the Precipice Trail closes each spring and summer.'),
              'coyote': ('Eastern coyote', 'Lives throughout the park but keeps out of sight; you are more likely to find tracks and scat on the trails than to see one.'),
              'otter': ('River otter', 'Otters travel between the ponds and streams of the island; look for one fishing in the Tarn or the Bowl early in the morning.'),
              'raccoon': ('Raccoon', 'A night forager in the woods and wet ground around Sieur de Monts and the Tarn.'),
              'eagle': ('Bald eagle', 'Nests on islands around Mount Desert Island; look for one cruising along the shore of Frenchman Bay below the ridges.'),
              'osprey': ('Osprey', 'A brown-and-white fish hawk that hovers over Frenchman Bay and the ponds, then dives feet first for fish. Spring to early fall.'),
              'vulture': ('Turkey vulture', 'Rides the warm updrafts along Champlain’s ridges on tilted wings, spring to fall.'),
              'raven': ('Common raven', 'Rides the updrafts along Champlain’s cliffs, croaking and tumbling in the wind.'),
              'gull': ('Herring gull', 'The big gray-and-white gull of the Maine coast, gliding over Frenchman Bay and Sand Beach below the ridges.')},
    grid=GRID, step=STEP, dem_b64=b64, tile=TILE, ve=2.0, ridge_ft=RIDGE,
    palette='east', tree_rule=tree_rule, ocean=True, rock_all_aspects=True,
    landmarks=lm, animals_js=animals_js, extra_js=extra_js,
    overview=dict(h2='Champlain Mountain, above Frenchman Bay',
                  p='Champlain Mountain, 1,058 ft, rises straight from the shore on the east side of Mount Desert Island. A climbs the stone steps of the Beachcroft Path from the Tarn, B is the Precipice, Acadia’s famous iron-rung climb up the east face, and C crosses the whole mountain from Sieur de Monts to Sand Beach. Pick a trail to focus the model; click anything on it for a quick note.',
                  numbers='Plain numbers mark spots more than one trail passes: the Beachcroft trailhead and Huguenot Head are on A and C, and the summit is on all three. Lettered stops belong to one trail: B3 is the third stop on Trail B.',
                  wild_h='Wildlife around Champlain Mountain',
                  note=NOTE),
    links={'A': [('Beachcroft Path · NPS', 'https://www.nps.gov/thingstodo/hike-beachcroft-path.htm'), ('Beachcroft Path · Bangor Daily News', 'https://www.bangordailynews.com/2020/10/08/outdoors/act-out/this-whimsical-stone-path-weaves-up-a-mountain-in-acadia-national-park/')],
           'B': [('Precipice Loop · NPS', 'https://www.nps.gov/thingstodo/hike-precipice-loop.htm'), ('Precipice and Beehive history · NPS', 'https://www.nps.gov/articles/000/precipice-and-beehive-history.htm'), ('Falcon closures, March 2026 · NPS', 'https://home.nps.gov/acad/learn/news/20260302.htm')],
           'C': [('Sieur de Monts to Sand Beach · NPS', 'https://www.nps.gov/thingstodo/hike-sieur-de-monts-to-sand-beach-trek-with-island-explorer.htm'), ('Beachcroft and Champlain South Ridge · Maine Trail Finder', 'https://mainetrailfinder.com/trails/trail/acadia-national-park-beachcroft-and-champlain-south-ridge-route')]},
    viewaz={'all': 0.45, 'A': 0.45, 'B': 0.6, 'C': 0.45},
    zoomcap={'A': 3.6, 'B': 3.6, 'C': 2.2},
    stop_photos=PH.get('stop', {}), flower_photos=flower_photos, animal_photos=animal_photos,
)
json.dump({k: {'mi': R[k]['mi'], 'gain': R[k]['gain'], 'lo': R[k]['lo'], 'hi': R[k]['hi']} for k in R}, open('precipice/stats.json', 'w'))
OUT = '/home/claude/site/out/acadia-precipice/index.html'
os.makedirs(os.path.dirname(OUT), exist_ok=True)
print(build(cfg, OUT))
# coastal colours from the raw DEM, not the edge-flattened mesh (otherwise the flattened rim of a coastal tile all paints as sea)
_s = open(OUT).read()
_a = 'if(me<3)c=col(me<1?"#9CCFE0":"#E9DDBF");else if(me<14&&g<0.25)'
assert _s.count(_a) == 1
open(OUT, 'w').write(_s.replace(_a, 'const hr=H(mx,mn);if(hr<3)c=col(hr<1?"#9CCFE0":"#E9DDBF");else if(hr<14&&g<0.25)'))
