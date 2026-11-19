from lib import *
from mk_sheet import build
import sys, json, os, math
import numpy as np

os.chdir('/home/claude/parks')
sys.path.insert(0, '/home/claude/parks')
p = Park('bigbluff', 36.0640, -93.3603)   # origin: Centerpoint Trailhead (OSM trail board)
TH = (0, 0)              # Centerpoint Trailhead, Hwy 43 (OSM board node, 36.06403 -93.36030)
CRJ = (719, 459)         # Chimney Rock Trail leaves the Centerpoint Trail (OSM way ends)
GTJ = (10795, -3433)     # Goat Trail leaves the Centerpoint Trail (OSM way 1096071474 start)
BB = (11970, -5390)      # Big Bluff (OSM natural=cliff node, 36.04924 -93.31963)
HIH = (15534, 2833)      # Hemmed-In-Hollow Falls (OSM waterfall node, 36.07207 -93.30740)
SC = (5842, -8614)       # Steel Creek: Buffalo River Trail leaves the access road where the pavement ends (OSM)
SCO = (8810, -8227)      # Steel Creek Overlook: high point of the BRT on the bluff above the river, 1.7 mi out (nwaonline: 1.75 mi)

R = {}
R['A'] = route_xy(p, SC, (8469, -9187), SCO)
R['B'] = route_xy(p, TH, GTJ, BB)
R['C'] = route_xy(p, TH, (13780, -2791), (15700, -66), HIH)
for k in R: Park.smooth_E(R[k], 9); p.describe(R[k], k)


def rt_gain(r):   # out-and-back: climb on the way out + climb on the way back
    E = r['E']; up = sum(max(0, E[i] - E[i - 1]) for i in range(1, len(E))); dn = sum(max(0, E[i - 1] - E[i]) for i in range(1, len(E)))
    return int(round((up + dn) / 10) * 10)


GAIN = {k: rt_gain(R[k]) for k in R}
print('round-trip gain', GAIN)


def cross(r, line):   # first point where route r crosses polyline line
    P = r['pts']
    for i in range(1, len(P)):
        a, b = P[i - 1], P[i]
        for j in range(1, len(line)):
            c, d = line[j - 1], line[j]
            den = (b[0] - a[0]) * (d[1] - c[1]) - (b[1] - a[1]) * (d[0] - c[0])
            if abs(den) < 1e-9: continue
            t = ((c[0] - a[0]) * (d[1] - c[1]) - (c[1] - a[1]) * (d[0] - c[0])) / den
            u = ((c[0] - a[0]) * (b[1] - a[1]) - (c[1] - a[1]) * (b[0] - a[0])) / den
            if 0 <= t <= 1 and 0 <= u <= 1: return (round(a[0] + t * (b[0] - a[0])), round(a[1] + t * (b[1] - a[1])))
    return None


wl = lambda wid: [p.xy(q) for q in p.WID[wid]['p']]
RIV = [w for w in p.W if w['n'] == 'Buffalo River' and w['k'] == 'river']
riv_line = [p.xy(q) for q in RIV[0]['p']]
FORD = cross(R['C'], riv_line)
SCX = cross(R['A'], wl('1355491253')) or cross(R['A'], wl('1359338133'))
print('ford', FORD, 'steel creek crossing', SCX)
mSN = [s[1] for s in R['C']['segs'] if s[0] == "Sneed's Creek Trail"][0]
SNJ = tuple(p.at_mile(R['C'], mSN)[0])   # Centerpoint Trail meets the Sneeds Creek Trail
print('sneeds jct', SNJ, mSN)

ST = snap_stops(p, R, {
    'S1': (*TH, 'BC'), 'S2': (*CRJ, 'BC'), 'S3': (*GTJ, 'BC'),
    'B1': (*BB, 'B'),
    'C1': (*SNJ, 'C'), 'C2': (*FORD, 'C'), 'C3': (*HIH, 'C'),
    'A1': (*SC, 'A'), 'A2': (*SCX, 'A'), 'A3': (*SCO, 'A'),
})
TILE = (-5000, 20600, -16500, 8300)
GRID = (-5400, 21000, -16700, 8700)
if 'plot' in sys.argv:
    from plot import plot
    plot(p, TILE, 'bigbluff/routes.png', routes=R, stops=ST, title='bigbluff', grid=1000)
    sys.exit()

STEP = 125
b64, NX, NN = p.dem_b64(*GRID, STEP=STEP)
RIDGE = int(round(float(np.percentile(p.grid, 75)), -1))
print('grid', NX, NN, NX * NN, p.grid.min(), p.grid.max(), 'p75', RIDGE)

S = lambda i: ST[i]
stops = [
 dict(id='S1', trails=['B', 'C'], x=S('S1')[0], n=S('S1')[1], name='Centerpoint Trailhead',
      desc='A gravel lot for 20–25 cars on Highway 43, about 3 miles north of Ponca, across from the Fire Tower Road turn. No restroom. The Centerpoint Trail, an old wagon road marked with yellow “CPT” blazes, enters the Ponca Wilderness here. No pets on wilderness trails.'),
 dict(id='S2', trails=['B', 'C'], x=S('S2')[0], n=S('S2')[1], name='Chimney Rock Trail junction',
      desc='The first of several side trails. Stay on the Centerpoint Trail, which runs nearly level along the ridgetop for about the first mile before it starts to drop.'),
 dict(id='S3', trails=['B', 'C'], x=S('S3')[0], n=S('S3')[1], name='Goat Trail junction',
      desc='After about 2.6 miles and a long, rocky descent, the unsigned Goat Trail branches right toward the river, marked only by a small post that bars horses. The Centerpoint Trail goes on toward Sneeds Creek and Hemmed-In Hollow.'),
 dict(id='B1', trails=['B'], x=S('B1')[0], n=S('B1')[1], name='Big Bluff',
      desc='The Goat Trail follows a ledge about 5 feet wide across the face of Big Bluff, about 350 feet straight above a bend in the Buffalo River. The whole face is about 550 feet tall, one of the highest bluffs in the Ozarks. There is no railing: not for children or anyone afraid of heights. No camping on the bluff.'),
 dict(id='C1', trails=['C'], x=S('C1')[0], n=S('C1')[1], name='Sneeds Creek Trail junction',
      desc='Near the bottom the Centerpoint Trail meets the Sneeds Creek Trail. To the right, the Sneeds Creek Trail leads to Granny Henderson’s house, an early-1900s homestead where she lived alone after her husband died in 1959. The route to Hemmed-In Hollow follows old roads down toward the river.'),
 dict(id='C2', trails=['C'], x=S('C2')[0], n=S('C2')[1], name='Buffalo River ford',
      desc='The route crosses the Buffalo River near the mouth of Hemmed-In Hollow. There is no bridge: expect to wade, and do not cross when the river is high. Check the river level before you go.'),
 dict(id='C3', trails=['C'], x=S('C3')[0], n=S('C3')[1], name='Hemmed-In Hollow Falls',
      desc='A waterfall about 210 feet tall at the head of a box canyon of sandstone bluffs, called the highest waterfall between the Rocky Mountains and the Appalachians. It flows only after a good rain and can be a trickle in dry weather. Turnaround point.'),
 dict(id='A1', trails=['A'], x=S('A1')[0], n=S('A1')[1], name='Steel Creek',
      desc='Steel Creek access and campground, on the river across from Roark Bluff, one of the most photographed bluffs in Arkansas. Drinking water and toilets. The Buffalo River Trail (white “BRT” markers) leaves the road where the pavement turns to gravel. No pets on this trail.'),
 dict(id='A2', trails=['A'], x=S('A2')[0], n=S('A2')[1], name='Steel Creek crossing',
      desc='The trail crosses Steel Creek on a narrow foot log. Usually an easy rock-hop, but the creek can run high after rain.'),
 dict(id='A3', trails=['A'], x=S('A3')[0], n=S('A3')[1], name='Steel Creek Overlook',
      desc='About three-quarters of a mile past the creek, mostly uphill, the trail reaches the top of the bluff, roughly 450 feet above the river, with a wide view up the valley to Steel Creek and Roark Bluff. A popular sunset spot. Turn around here.'),
]
stops, order = renumber(p, R, stops)
print(order, [(s['id'], s['name']) for s in stops])
trails = [
 dict(id='A', name='Steel Creek Overlook', short='Steel Creek Overlook', official=3.5, unit='round trip', route='Out and back', time='2 hr', level='Moderate', color='--tA',
      desc='From the Steel Creek access the Buffalo River Trail runs downstream along Steel Creek, crosses it on a foot log, then climbs steadily to an overlook high above the river and Roark Bluff. Return the same way.', anchors=p.anchors(R['A'])),
 dict(id='B', name='Big Bluff via Centerpoint and the Goat Trail', short='Big Bluff', official=6.0, unit='round trip', route='Out and back', time='4–6 hr', level='Strenuous', color='--tB',
      desc='The Centerpoint Trail follows an old wagon road off the ridge into the Ponca Wilderness, then the Goat Trail edges out along a narrow ledge on the face of Big Bluff, about 350 feet above the Buffalo River. Almost all downhill on the way in: save water and energy for the climb back, about 1,000 feet.', anchors=p.anchors(R['B'])),
 dict(id='C', name='Hemmed-In Hollow via Centerpoint', short='Hemmed-In Hollow', official=10.0, unit='round trip', route='Out and back', time='Full day', level='Strenuous', color='--tC',
      desc='Past the Goat Trail the route keeps descending nearly 1,300 feet to the river, fords the Buffalo and climbs into the box canyon of Hemmed-In Hollow, where a 210-foot waterfall pours off the bluff after rain. Long, rocky and steep coming back; plan a full day.', anchors=p.anchors(R['C'])),
]

# --- water: Buffalo River and the main creeks (OSM centerlines)
creeks = []
c = p.creek([RIV[0]['id']], GRID, minor=False, every=120)
if c: creeks.append(dict(id='buffalo', **c))
riv = [[x, n] for x, n, e in c['pts']]
named = {'Steel Creek': 'steel', 'Sneeds Creek': 'sneeds', 'Beech Creek': 'beech', 'Bradley Branch': 'bradley', 'Middle Prong Sneeds Creek': 'mprong'}
for i, w in enumerate([w for w in p.W if w['k'] == 'stream' and w['n'] in named]):
    cc = p.creek([w['id']], GRID, minor=True)
    if cc: creeks.append(dict(id=f"{named[w['n']]}{i}", **cc))
hih_w = min([w for w in p.W if w['k'] == 'stream'], key=lambda w: min(math.dist(p.xy(q), HIH) for q in w['p']))
cc = p.creek([hih_w['id']], GRID, minor=True)
if cc: creeks.append(dict(id='hih', **cc))
print('creeks', len(creeks), 'hih stream', hih_w['id'], hih_w['n'])

pa = place_along
A_ = lambda k, f, s=1, o=240: pa(p, R[k], [f], s, o)[0]
RV = lambda i: [round(v) for v in riv[i]]
ri = lambda x, n: min(range(len(riv)), key=lambda i: math.dist(riv[i], (x, n)))
iB, iS, iF = ri(11300, -6200), ri(7256, -9032), ri(*FORD)
an = []
an += [f'{{k:"elk",at:{js(A_("A",.06,1,450))},flock:3}}', f'{{k:"elk",path:{js(A_("A",.30,-1,420)+A_("A",.33,-1,420))},per:40,ph:0.3}}']
an += [f'{{k:"fox",path:{js(A_("A",.78,-1,320)+A_("A",.81,-1,320))},per:24}}']
an += [f'{{k:"bobcat",path:{js(A_("A",.55,1,420)+A_("A",.58,1,420))},per:30}}']
an += [f'{{k:"chipmunk",at:{js(A_("A",.20,-1,180))},hop:true}}']
an += [f'{{k:"beaver",path:{js(RV(iS)+RV(min(iS + 1, len(riv) - 1)))},per:30,ph:0.4}}']
an += [f'{{k:"turkey",at:{js(A_("C",.05,1,650))},flock:3}}']
an += [f'{{k:"coyote",path:{js(A_("C",.20,-1,520)+A_("C",.23,-1,520))},per:26}}']
an += [f'{{k:"deer",path:{js(A_("B",.45,1,380)+A_("B",.48,1,380))},per:30}}']
an += [f'{{k:"squirrel",at:{js(A_("C",.33,1,300))},hop:true}}']
an += [f'{{k:"bear",path:{js(A_("C",.60,-1,700)+A_("C",.62,-1,700))},per:44}}']
an += [f'{{k:"armadillo",path:{js(A_("C",.44,1,350)+A_("C",.46,1,350))},per:26}}']
an += [f'{{k:"raccoon",path:{js(A_("C",.90,1,260)+A_("C",.92,1,260))},per:22}}']
iO = min(iB + 8, len(riv) - 3)
an += [f'{{k:"otter",path:{js(RV(iO)+RV(iO + 2))},per:20}}']
an += [f'{{k:"heron",at:{js(RV(min(iF + 2, len(riv) - 1)))}}}']
animals_js = '[\n ' + ',\n '.join(an) + '\n]'

bn = {s['name']: s for s in stops}
g = lambda nm: (bn[nm]['x'], bn[nm]['n'])
th, sc, sco = g('Centerpoint Trailhead'), g('Steel Creek'), g('Steel Creek Overlook')
cl = riv[iS]
lm = f'''  gate({th[0] + 90},{th[1] - 60},0.4);gate({sc[0] + 60},{sc[1] + 60},0.9);
  // Big Bluff: a tall, banded limestone wall on the OSM cliff node, facing the river bend to the west-southwest; the Goat Trail ledge drawn as a pale band
  {{const q=G({BB[0]},{BB[1]});const d=new THREE.Vector3(-0.9,0,0.45).normalize();const g=new THREE.Group();g.position.copy(q);g.position.y-=0.9;g.rotation.y=Math.atan2(d.x,d.z);g.scale.setScalar(2.2);world.add(g);
   const cols=["#B9AE9C","#A39784","#C8BEAD","#958A79","#B1A693"];
   for(let i=0;i<4;i++)part(g,box,cols[i],0,0.3+i*0.42,-0.06*i,5.2-0.25*i,0.42,0.8,1.05);
   part(g,box,"#EFE8DA",0,1.08,0.43,4.6,0.08,0.18,0);
   [-2.0,-1.2,-0.3,0.6,1.4,2.1].forEach((x,i)=>part(g,box,i%2?"#6F665A":"#7E7466",x,0.75+0.15*(i%3),0.42,0.1,0.9+0.3*(i%2),0.04,0));
   [-1.9,-0.7,0.5,1.8].forEach((x,i)=>part(g,ico,i%2?"#6E8A52":"#5E7A4A",x,1.95,-0.25,0.5,0.32,0.45));}}
  // Hemmed-In Hollow Falls: sandstone bluff with a 210 ft ribbon of water, on the OSM waterfall node, falling toward the hollow (south)
  const wf=new THREE.Group();wf.position.copy(G({HIH[0]},{HIH[1] - 60}));wf.rotation.y=0.15;wf.scale.setScalar(2.2);world.add(wf);
  [[0,1.4,-0.55,3.6,2.8,0.6,"#C7A27A"],[-1.5,1.1,-0.35,0.9,2.2,0.7,"#B48E68"],[1.5,1.1,-0.35,0.9,2.2,0.7,"#BF9A72"]].forEach(([x,y,z,sx,sy,sz,c])=>part(wf,box,c,x,y,z,sx,sy,sz,1.05));
  [0.6,1.3,2.0].forEach(y=>part(wf,box,"#9E7A58",0,y,-0.23,3.4,0.05,0.05,0));
  const fallTex=stripeTex("#E4F6F6","#FFFFFF",64,128,22,9,14);fallTex.repeat.set(1,2);
  const fallMat=new THREE.MeshBasicMaterial({{map:fallTex,side:THREE.DoubleSide}});
  {{const pl=new THREE.Mesh(new THREE.PlaneGeometry(0.35,2.8),fallMat);pl.position.set(0,1.4,-0.2);wf.add(pl);}}
  part(wf,new THREE.CylinderGeometry(0.55,0.6,0.08,16),"#8FC6DA",0,0.04,0.25,1,1,1,0);
  const rings=[],mist=[];for(let i=0;i<2;i++){{const rg=new THREE.Mesh(new THREE.RingGeometry(0.3,0.38,20),new THREE.MeshBasicMaterial({{color:"#FFFFFF",transparent:true,side:THREE.DoubleSide}}));rg.rotation.x=-Math.PI/2;rg.position.set(0,0.1,0.15);wf.add(rg);rings.push(rg);}}
  for(let i=0;i<3;i++){{const m=new THREE.Mesh(new THREE.SphereGeometry(0.12,8,6),new THREE.MeshBasicMaterial({{color:"#FFFFFF",transparent:true}}));wf.add(m);mist.push({{m,ph:i/3,x:(i%3-1)*0.2}});}}
  anim.water={{fallTex,rings,mist}};
  // Steel Creek Overlook: rock ledge and trail post on the bluff top, looking west up the valley
  {{const q=G({sco[0]},{sco[1]});const g=new THREE.Group();g.position.copy(q);g.rotation.y=Math.atan2(-1,0.1);g.scale.setScalar(2.0);world.add(g);
   part(g,box,"#B3AA9A",0,0.15,0.3,1.8,0.3,1.0,1.06);part(g,ico,"#9A9184",-0.6,0.42,0.1,0.5,0.35,0.45);part(g,ico,"#A69D90",0.6,0.38,0.0,0.42,0.3,0.4);
   part(g,cyl,"#6B4F3A",0.7,0.75,-0.3,0.06,1.2,0.06);part(g,box,"#FFFFFF",0.7,1.2,-0.26,0.32,0.22,0.04,1.06);}}
  // Goat Trail junction post
  {{const q=G({GTJ[0]},{GTJ[1]});part(world,cyl,"#6B4F3A",q.x,q.y+0.7,q.z,0.08,1.4,0.08,1.06);part(world,box,"#E9E1D2",q.x+0.15,q.y+1.25,q.z,0.5,0.28,0.05,1.06);}}
  // canoe on the river at Steel Creek, the usual put-in for floats to Kyles Landing
  {{const q=G({round(cl[0])},{round(cl[1])},0.15);const g=new THREE.Group();g.position.copy(q);g.rotation.y=0.6;g.scale.setScalar(1.6);world.add(g);
   part(g,new THREE.CylinderGeometry(0.16,0.16,1.4,10),"#C8402E",0,0.08,0,1,1,1,1.05).rotation.z=Math.PI/2;part(g,box,"#2E4A6B",0.25,0.3,0,0.12,0.3,0.12,0);part(g,box,"#E1C27A",-0.3,0.3,0,0.12,0.3,0.12,0);}}
  // Buffalo River ford: stepping stones
  [[-60,-20],[0,0],[60,15]].forEach(([dx,dn])=>{{const q=G({FORD[0]}+dx,{FORD[1]}+dn,0.1);part(world,ico,"#A8A196",q.x,q.y+0.12,q.z,0.32,0.18,0.28);}});
'''
import math as _m
_rd = []
for a, b in zip(riv, riv[1:]):
    k = max(1, int(_m.dist(a, b) // 90))
    for t in range(k): _rd.append([round(a[0] + (b[0] - a[0]) * t / k), round(a[1] + (b[1] - a[1]) * t / k)])
_rd.append([round(v) for v in riv[-1]])
RIV_FN = ('function rivP(){return rivP.c||(rivP.c=%s);}\n' % js(_rd) +
          'function rivD(x,n){let b=1e9;const P=rivP();for(let i=0;i<P.length;i+=2){const d=Math.abs(P[i][0]-x)+Math.abs(P[i][1]-n);if(d<b)b=d;}return b;}\n')
extra_js = RIV_FN + '''
// Buffalo River: a wide water ribbon on the OSM centerline (the engine's creek ribbon is too thin at this scale)
(function(){const pts=[];rivP().forEach(([x,n])=>{if(qOf(x,n)<0.96)pts.push(G(x,n));});
  if(pts.length>1){world.add(ribbon(pts,1.9,"#86C3C6",0.22));world.add(ribbon(pts,1.5,"#A9DCE2",0.27));}})();
TRAILS.forEach(T=>{const g=%s[T.id];if(g)T.gain=g;});
''' % js(GAIN)

species_extra = {
 'firepink_bb': 'firepink_bb:{name:"Fire pink",latin:"Silene virginica",color:"#D7263D",shape:"tube",bloom:[4,5,6],sum:"Brilliant red, star-shaped flowers with notched petals on rocky, open slopes and bluff ledges in spring.",rule:(d,e,g,s)=>g>0.3&&d>150}',
 'columbine_bb': 'columbine_bb:{name:"Wild columbine",latin:"Aquilegia canadensis",color:"#D9513A",shape:"tube",bloom:[4,5,6],sum:"Nodding red-and-yellow flowers with long spurs, hanging from moist ledges and bluffs; a favorite of hummingbirds.",rule:(d,e,g,s)=>g>0.45&&d<900}',
 'bloodroot_bb': 'bloodroot_bb:{name:"Bloodroot",latin:"Sanguinaria canadensis",color:"#F4F1E8",shape:"cup",bloom:[2,3,4],sum:"One of the first flowers of spring: a single white bloom wrapped in a lobed leaf, in rich woods along streams. The root bleeds red sap.",rule:(d,e,g,s)=>d<600&&e<1700}',
 'iris_bb': 'iris_bb:{name:"Dwarf crested iris",latin:"Iris cristata",color:"#8C7BD9",shape:"cup",bloom:[4,5],sum:"A small blue-violet iris with a white and gold crest, spreading in patches on shady wooded banks.",rule:(d,e,g,s)=>d<800&&g<0.6}',
 'coneflower_bb': 'coneflower_bb:{name:"Purple coneflower",latin:"Echinacea purpurea",color:"#C76BA8",shape:"dome",bloom:[6,7,8,9],sum:"Drooping pink-purple petals around a spiny orange cone, in open woods and sunny clearings in summer.",rule:(d,e,g,s)=>g<0.35&&d>300&&s>-0.2}',
 'butterfly_bb': 'butterfly_bb:{name:"Butterfly milkweed",latin:"Asclepias tuberosa",color:"#F28C28",shape:"dome",bloom:[5,6,7,8,9],sum:"Flat clusters of bright orange flowers on dry, sunny ground, busy with butterflies all summer.",rule:(d,e,g,s)=>g<0.3&&d>400&&s>0}',
}

# --- photos: new ones from gt6_photos, plus species photos already on the site
PM = json.load(open('/mnt/files/gtb/photos/bigbluff/photos_meta.json'))
RU = {}
for line in open('/mnt/files/gtb/photos/bigbluff/reuse.txt'):
    m = json.loads(line); RU[m['f'].split('/')[-1]] = m
def keep(key, files):
    return [dict(x) for f in files for x in PM.get(key, []) if x['f'].endswith('/' + f)]
ru = lambda *fs: [RU[f] for f in fs if f in RU]
by_name = {
 'Big Bluff': keep('bigbluff', ['pl_bigbluff_bigbluff_0.jpg', 'pl_bigbluff_bigbluff_1.jpg']),
 'Hemmed-In Hollow Falls': keep('hih', ['pl_bigbluff_hih_3.jpg', 'pl_bigbluff_hih_2.jpg', 'pl_bigbluff_hih_1.jpg', 'pl_bigbluff_hih_0.jpg']),
 'Steel Creek Overlook': keep('steelcreek', ['pl_bigbluff_steelcreek_2.jpg']),
 'Steel Creek': keep('steelcreek', ['pl_bigbluff_steelcreek_0.jpg', 'pl_bigbluff_steelcreek_1.jpg']),
}
stop_photos = {s['id']: by_name[s['name']] for s in stops if by_name.get(s['name'])}
flower_photos = {
 'firepink_bb': ru('sp_firepink_0.jpg', 'sp_firepink_4.jpg'),
 'columbine_bb': ru('sp_hk_redcolumbine_1.jpg', 'sp_hk_redcolumbine_2.jpg'),
 'bloodroot_bb': ru('sp_or_bloodroot_1.jpg', 'sp_wg_bloodroot_0.jpg'),
 'iris_bb': ru('sp_hk_crestediris_1.jpg', 'sp_hk_crestediris_2.jpg'),
 'coneflower_bb': keep('sp:purpleconeflower', ['sp_purpleconeflower_0.jpg', 'sp_purpleconeflower_2.jpg']),
 'butterfly_bb': keep('sp:butterflyweed', ['sp_butterflyweed_1.jpg', 'sp_butterflyweed_2.jpg']),
}
animal_photos = {
 'elk': ru('sp_elk_1.jpg', 'sp_elk_2.jpg'), 'deer': ru('sp_hk_wtdeer_0.jpg', 'sp_hk_wtdeer_1.jpg'), 'bear': ru('sp_sm_bear_0.jpg', 'sp_sm_bear_3.jpg'),
 'bobcat': ru('sp_bobcat_0.jpg'), 'coyote': ru('sp_coyote_0.jpg'), 'fox': ru('sp_grayfox_1.jpg', 'sp_grayfox_4.jpg'), 'raccoon': ru('sp_raccoon_0.jpg'),
 'otter': ru('sp_riverotter_0.jpg', 'sp_riverotter_1.jpg'), 'beaver': ru('sp_beaver_2.jpg', 'sp_beaver_3.jpg'), 'heron': ru('sp_gbheron_dl_1.jpg', 'sp_gbheron_dl_0.jpg'),
 'armadillo': ru('sp_er_armadillo_0.jpg'), 'chipmunk': ru('sp_hk_echipmunk_0.jpg', 'sp_hk_echipmunk_1.jpg'), 'squirrel': ru('sp_hk_graysquirrel_0.jpg', 'sp_hk_graysquirrel_1.jpg'),
 'turkey': ru('sp_sm_turkey_1.jpg', 'sp_sm_turkey_2.jpg'), 'eagle': ru('sp_baldeagle_0.jpg', 'sp_baldeagle_1.jpg'), 'kingfisher': ru('sp_hl_kingfisher_0.jpg', 'sp_hl_kingfisher_1.jpg'),
 'vulture': ru('sp_tvulture_0.jpg', 'sp_tvulture_1.jpg'), 'woodpecker': keep('sp:pileated', ['sp_pileated_0.jpg', 'sp_pileated_5.jpg']),
}
print('photos', {k: len(v) for k, v in {**stop_photos, **flower_photos, **animal_photos}.items()})

from fauna import TREE_RULES
cfg = dict(
    title='Big Bluff &amp; Hemmed-In Hollow', aria='Big Bluff, the Goat Trail, Hemmed-In Hollow and Steel Creek on the Buffalo National River', h1='Big Bluff &amp; the Goat Trail',
    canyons=creeks, trails=trails, stops=stops, order=order,
    species=list(species_extra), species_extra=species_extra,
    flora={'A': ['bloodroot_bb', 'iris_bb', 'columbine_bb', 'butterfly_bb'], 'B': ['firepink_bb', 'columbine_bb', 'coneflower_bb', 'butterfly_bb'], 'C': ['bloodroot_bb', 'iris_bb', 'firepink_bb', 'coneflower_bb']},
    wild=['elk', 'deer', 'bear', 'bobcat', 'coyote', 'fox', 'raccoon', 'otter', 'beaver', 'heron', 'armadillo', 'chipmunk', 'squirrel', 'turkey', 'eagle', 'kingfisher', 'vulture', 'woodpecker'],
    wild_sum={
     'elk': ('Elk', 'Rare here: elk were wiped out in Arkansas by the 1840s; this herd grew from 112 Rocky Mountain elk released along the Buffalo starting in 1981, and now numbers several hundred. They graze the river fields around Ponca and Boxley Valley at dawn and dusk and now and then wander through Steel Creek, most often in fall during the rut. Keep your distance.'),
     'deer': ('White-tailed deer', 'Common in the oak-hickory woods of the Ponca Wilderness, most often seen early and late in the day.'),
     'bear': ('Black bear', 'Black bears live along the Buffalo but are shy. Camp clean and store food well if you stay overnight in the wilderness.'),
     'bobcat': ('Bobcat', 'A short-tailed wild cat of the rocky bluffs and thickets; mostly out at dusk and rarely seen.'),
     'coyote': ('Coyote', 'Hunts the ridgetops and old fields; you are more likely to hear it at night than to see it.'),
     'fox': ('Gray fox', 'A small fox that can climb trees, living in the wooded hollows along the river.'),
     'raccoon': ('Raccoon', 'Forages along the creeks and gravel bars at night; look for its hand-like tracks in the mud.'),
     'otter': ('River otter', 'Otters fish the clear pools of the Buffalo; watch for a sleek head and a V-shaped wake below Big Bluff.'),
     'beaver': ('Beaver', 'Beavers den in the riverbanks rather than building big dams here; look for gnawed willows on the gravel bars.'),
     'heron': ('Great blue heron', 'A tall gray heron that stalks the shallows of the Buffalo year-round and flaps slowly downriver when disturbed.'),
     'armadillo': ('Nine-banded armadillo', 'An armored newcomer to the Ozarks that roots for insects in the leaf litter, often at dusk.'),
     'chipmunk': ('Eastern chipmunk', 'A small striped ground squirrel that chips loudly from rocks and logs along the trail.'),
     'squirrel': ('Gray squirrel', 'The common tree squirrel of the oak and hickory woods, busiest in fall when the nuts drop.'),
     'turkey': ('Wild turkey', 'Flocks walk the ridgetop woods and old fields near the Centerpoint Trail; toms gobble in spring.'),
     'eagle': ('Bald eagle', 'Listed as a year-round resident of the Buffalo; most often seen in winter, perched over the river or soaring past the bluffs.'),
     'kingfisher': ('Belted kingfisher', 'A blue-gray, crested bird that rattles as it flies low over the river and dives headfirst for fish.'),
     'vulture': ('Turkey vulture', 'Rides the updrafts along the bluffs on tilted wings; a common sight from Big Bluff.'),
     'woodpecker': ('Pileated woodpecker', 'A crow-sized woodpecker with a red crest; listen for its loud drumming and laughing call in the hollows.'),
    },
    grid=GRID, step=STEP, dem_b64=b64, tile=TILE, ve=1.7, ridge_ft=RIDGE,
    palette='east', tree_rule='if(rivD(x,n)<230){type=null;}else ' + TREE_RULES['east'], rock_all_aspects=True,
    landmarks=lm, animals_js=animals_js, extra_js=extra_js,
    stop_photos=stop_photos, flower_photos=flower_photos, animal_photos=animal_photos,
    overview=dict(h2='Ozark bluffs over the Buffalo',
                  p='The Buffalo National River, America’s first national river, runs free between sandstone and limestone bluffs in the Arkansas Ozarks. Near Ponca it cuts through the Ponca Wilderness. A climbs from Steel Creek to an overlook above the river, B drops off the ridge on the Centerpoint Trail to the Goat Trail ledge on Big Bluff, and C goes on down to the river and Hemmed-In Hollow’s 210-foot waterfall. Pick a trail to focus the model; click anything on it for a quick note.',
                  numbers='Plain numbers mark spots both Big Bluff and Hemmed-In Hollow share on the Centerpoint Trail. Lettered stops belong to one trail: C3 is the third stop on Trail C.',
                  wild_h='Wildlife along the Buffalo',
                  note='Buffalo National River, near Ponca, Arkansas. Centerpoint Trailhead: Highway 43 about 3 miles north of Ponca, gravel lot for 20–25 cars, no restroom. Steel Creek: Highway 74 about 1 mile east of Ponca, then 1.3 miles down the Steel Creek road; campground with water and toilets. No entrance fee; open all year. Status (November 2026): open, no alerts posted by the park. Pets are not allowed on Ponca Wilderness trails or the Steel Creek Overlook trail. Big Bluff and Hemmed-In Hollow are among the park’s most frequent search-and-rescue calls: carry at least 2 liters of water, a map and a light. The Hemmed-In Hollow route fords the river; do not cross in high water. Terrain from USGS elevation data, stylized; not for navigation.'),
    links={'A': [('Steel Creek Overlook · NWA Democrat-Gazette', 'https://www.nwaonline.com/news/2022/dec/27/high-above-the-buffalo/'), ('Steel Creek · Buffalo River Chamber', 'https://www.buffaloriverchamber.com/attraction_steel_creek.html')],
           'B': [('Hike to Big Bluff · NPS', 'https://www.nps.gov/thingstodo/hike-to-big-bluff.htm'), ('Big Bluff via Centerpoint · arkokhiker', 'https://arkokhiker.org/northwest-arkansas/big-bluff-center-point-trailhead/')],
           'C': [('Hike to Hemmed-In Hollow · NPS', 'https://www.nps.gov/thingstodo/hike-to-hemmed-in-hollow.htm'), ('Full Day Adventure: Upper District · NPS', 'https://www.nps.gov/buff/planyourvisit/full-day-adventure-upper-district.htm')]},
    viewaz={'all': 0.8, 'A': 0.9, 'B': 0.7, 'C': 0.6},
    zoomcap={'A': 5.0, 'B': 3.2},
)
json.dump({k: {'mi': R[k]['mi'], 'gain': R[k]['gain'], 'rt_gain': GAIN[k], 'lo': R[k]['lo'], 'hi': R[k]['hi']} for k in R}, open('bigbluff/stats.json', 'w'))
os.makedirs('/home/claude/site/out/buffalo-river-big-bluff', exist_ok=True)
print(build(cfg, '/home/claude/site/out/buffalo-river-big-bluff/index.html'))
