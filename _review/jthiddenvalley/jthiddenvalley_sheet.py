from lib import *
from mk_sheet import build
import sys, json, os, re, math, random
import numpy as np

os.chdir('/home/claude/parks')
# origin: Hidden Valley Nature Trail trailhead (Hiking Project 34.012391, -116.168039)
p = Park('jthiddenvalley', 34.0124, -116.1680)
TH = (-15, -3)            # Hidden Valley trailhead, picnic area
LOT = (7840, 4640)        # Barker Dam parking area (B west side, C east side)
MILL = (10415, 9054)      # end of the OSM Wall Street Mill Trail at the mill
R = {}
R['A'] = route_xy(p, TH, (-550, 240), (-1600, 900), (-1250, 1380), (-170, 720), TH)
R['B'] = route_xy(p, LOT, (7050, 6490), (6100, 6000), (6340, 5050), (7000, 5150), LOT)
R['C'] = route_xy(p, LOT, MILL, LOT)
for k in R: Park.smooth_E(R[k], 9); p.describe(R[k], k)
am = lambda k, mi: p.at_mile(R[k], mi)[0]
ST = snap_stops(p, R, {
    'S1': (*LOT, 'BC'),
    'A1': (*TH, 'A'), 'A2': (-250, 178, 'A'), 'A3': (-996, 489, 'A'), 'A4': (-1499, 1079, 'A'), 'A5': (-203, 602, 'A'),
    'B1': (7209, 6158, 'B'), 'B2': (6540, 6720, 'B'), 'B3': (6212, 5828, 'B'), 'B4': (6353, 5032, 'B'),
    'C1': (10117, 6621, 'C'), 'C2': (10524, 7611, 'C'), 'C3': (*am('C', 0.97), 'C'), 'C4': (*MILL, 'C'),
})
TILE = (-5200, 14200, -3750, 12750)
GRID = (-5600, 14600, -4100, 13100)
if 'plot' in sys.argv:
    from plot import plot
    sa = {k: v for k, v in ST.items() if k.startswith('A')}
    sb = {k: v for k, v in ST.items() if not k.startswith('A')}
    plot(p, (-2000, 500, -400, 1800), 'jthiddenvalley/routes_A.png', routes={'A': R['A']}, stops=sa, title='A', grid=250)
    plot(p, (5500, 11000, 4200, 9500), 'jthiddenvalley/routes_BC.png', routes={'B': R['B'], 'C': R['C']}, stops=sb, title='BC', grid=500)
    sys.exit()

STEP = 100
b64, NX, NN = p.dem_b64(*GRID, STEP=STEP)
RIDGE = int(np.percentile(p.grid, 75))
print('grid', NX, NN, NX * NN, p.grid.min(), p.grid.max(), 'p75', RIDGE)

S = lambda i: ST[i]
stops = [
 dict(id='S1', trails=['B', 'C'], x=S('S1')[0], n=S('S1')[1], name='Barker Dam parking area', desc='A paved lot at the end of Barker Dam Road with vault toilets. The Barker Dam loop leaves from its west side and the Wall Street Mill trail from its east side. It fills by midday on busy days.'),
 dict(id='A1', trails=['A'], x=S('A1')[0], n=S('A1')[1], name='Hidden Valley trailhead', desc='At the Hidden Valley picnic area on Park Boulevard. No water here or on the trail.'),
 dict(id='A2', trails=['A'], x=S('A2')[0], n=S('A2')[1], name='Gap in the rock wall', desc='Steps lead up and over a low gap into the valley. In 1936 rancher Bill Keys blasted this notch through the boulders so his cattle could reach the grass inside.'),
 dict(id='A3', trails=['A'], x=S('A3')[0], n=S('A3')[1], name='Valley floor', desc='A flat, sandy floor ringed by boulder walls. The enclosure catches more rain than the land around it, so plants grow thicker here, with Joshua trees, yuccas, cacti, pinyon pines and scrub oaks side by side. Signs along the way name them.'),
 dict(id='A4', trails=['A'], x=S('A4')[0], n=S('A4')[1], name='Far end of the valley', desc='The loop’s halfway point, an open, level spot at the back of the valley looking back toward the entrance. The valley was rumored to have hidden cattle rustlers and their herds.'),
 dict(id='A5', trails=['A'], x=S('A5')[0], n=S('A5')[1], name='Sports Challenge Rock', desc='Near the end of the loop the trail climbs a few steps past this tall, smooth rock face, one of the park’s best-known climbing walls. Climbers are often on it in the cooler months.'),
 dict(id='B1', trails=['B'], x=S('B1')[0], n=S('B1')[1], name='Into the boulders', desc='The trail winds north between piles of rounded monzogranite at the southern edge of the Wonderland of Rocks.'),
 dict(id='B2', trails=['B'], x=S('B2')[0], n=S('B2')[1], name='Barker Dam', desc='Cattlemen including C. O. Barker built the dam around 1900 to hold rainwater for stock. Rancher Bill Keys raised it six feet in 1949–50; his inscription on top calls it Big Horn Dam. The water level depends on rain. When the reservoir is full it draws birds and desert bighorn sheep.'),
 dict(id='B3', trails=['B'], x=S('B3')[0], n=S('B3')[1], name='Joshua tree flats', desc='Past the dam the trail drops onto open, sandy flats of Joshua trees, yuccas and cacti, passing an old cattle trough.'),
 dict(id='B4', trails=['B'], x=S('B4')[0], n=S('B4')[1], name='Petroglyphs', desc='A short side path leads to an overhanging boulder with Native American petroglyphs. A Disney film crew painted over the carvings in 1961 to make them show on camera, so they look brighter than the originals. Look, don’t touch.'),
 dict(id='C1', trails=['C'], x=S('C1')[0], n=S('C1')[1], name='Windmill', desc='An old, rusting windmill stands just right of the trail. A side trail before it leads to the ruins of Wonderland Ranch.'),
 dict(id='C2', trails=['C'], x=S('C2')[0], n=S('C2')[1], name='Worth Bagley stone', desc='Here Bill Keys and his neighbor Worth Bagley met in a 1943 gunfight over the road to the mill; Bagley was killed. Keys served five years for manslaughter, was pardoned in 1956, and later set this stone himself. The original was vandalized in 2014; a steel replica stands in its place.'),
 dict(id='C3', trails=['C'], x=S('C3')[0], n=S('C3')[1], name='Sandy wash', desc='For the last stretch the trail drops into a sandy wash that leads to the mill, past rusted-out cars from the 1930s and 1940s.'),
 dict(id='C4', trails=['C'], x=S('C4')[0], n=S('C4')[1], name='Wall Street Mill', desc='Bill Keys built this two-stamp mill in 1933 to crush gold ore, and ran it for miners in the area for decades. The mill shed, well and pump, ore-cart rails and winch still stand against a pile of white granite boulders. Leave everything in place.'),
]
stops, order = renumber(p, R, stops)
print(order, [(s['id'], s['name']) for s in stops])
trails = [
 dict(id='A', name='Hidden Valley Nature Trail', short='Hidden Valley', official=1.0, unit='loop', route='Loop', time='1 hr', level='Easy', color='--tA',
      desc='From the Hidden Valley picnic area, steps lead through a gap in the boulders into a small valley walled in by rock. The sandy loop circles the valley floor past signs about its plants and animals; the enclosure holds more moisture than the desert around it. Rock climbers are often on the walls. No dogs.', anchors=p.anchors(R['A'], every=40)),
 dict(id='B', name='Barker Dam Trail', short='Barker Dam', official=1.1, unit='loop', route='Loop', time='1 hr', level='Easy', color='--tB',
      desc='A nearly flat loop from the west side of the Barker Dam lot, usually walked counterclockwise. It threads north between boulders to the small reservoir behind Barker Dam, then returns south across Joshua tree flats with a short side path to a petroglyph boulder. Busy at midday.', anchors=p.anchors(R['B'], every=50)),
 dict(id='C', name='Wall Street Mill Trail', short='Wall Street Mill', official=2.0, unit='round trip', route='Out and back', time='1–1.5 hr', level='Moderate', color='--tC',
      desc='From the east side of the Barker Dam lot, a flat, sandy trail heads northeast across open desert past an old windmill, the Worth Bagley stone and rusting cars to Bill Keys’ Wall Street Mill, where gold ore was crushed until the 1960s. Little shade. A smaller lot off Queen Valley Road shortens the walk.', anchors=p.anchors(R['C'])),
]

# ---- animals (spread out along the trails)
pa = place_along
A_ = lambda k, f, s=1, o=240: pa(p, R[k], f, s, o)
an = []
an += [f'{{k:"bighorn",path:{js(A_("B",[.3],1,450)[0]+A_("B",[.34],1,450)[0])},per:30}}', f'{{k:"bighorn",at:{js(A_("C",[.58],-1,900)[0])},flock:2}}']
an += [f'{{k:"coyote",path:{js(A_("C",[.2],1,380)[0]+A_("C",[.25],1,380)[0])},per:24}}']
an += [f'{{k:"squirrel",at:{js(A_("A",[.62],-1,140)[0])},hop:true}}', f'{{k:"squirrel",at:{js(A_("C",[.33],-1,200)[0])},hop:true}}']
an += [f'{{k:"quail",at:{js(A_("B",[.8],-1,220)[0])},flock:3}}']
an += [f'{{k:"snake",path:{js(A_("A",[.15],1,110)[0]+A_("A",[.17],1,110)[0])},per:30}}']
an += [f'{{k:"turtle",path:{js(A_("C",[.12],-1,300)[0]+A_("C",[.13],-1,300)[0])},per:60}}']
an += [f'{{k:"heron",at:[6745,6735]}}']
animals_js = '[\n ' + ',\n '.join(an) + '\n]'

# ---- terrain dressing: boulder piles at OSM rock features, Joshua trees on the flats
X0i, X1i, N0i, N1i = TILE[0] + 1200, TILE[1] - 1200, TILE[2] + 1200, TILE[3] - 1200
TP = np.array([q for k in R for q in R[k]['pts']])
def near_trail(x, n, d): return np.min(np.hypot(TP[:, 0] - x, TP[:, 1] - n)) < d
piles = []
for w in p.W:
    t = w.get('tags') or {}
    if t.get('natural') not in ('bare_rock', 'stone') and not t.get('climbing'): continue
    P = np.array([p.xy(q) for q in w['p']]); cx, cn = P.mean(0)
    if not (X0i < cx < X1i and N0i < cn < N1i): continue
    r = max(70, min(380, (np.ptp(P[:, 0]) + np.ptp(P[:, 1])) / 4))
    if near_trail(cx, cn, 60 + r * 0.6): continue
    if any(math.hypot(cx - a, cn - b) < 90 for a, b, _ in piles): continue
    piles.append((round(cx), round(cn), round(r)))
# monzogranite ridges: add piles on rough high ground the OSM points miss
rng = random.Random(7)
def slope(x, n): return math.hypot(p.elev(x + 60, n) - p.elev(x - 60, n), p.elev(x, n + 60) - p.elev(x, n - 60)) / 120
tries = 0
while len([1 for q in piles]) < 230 and tries < 6000:
    tries += 1
    x, n = rng.uniform(X0i, X1i), rng.uniform(N0i, N1i)
    if slope(x, n) < 0.22 or near_trail(x, n, 120): continue
    if any(math.hypot(x - a, n - b) < 260 for a, b, _ in piles): continue
    piles.append((round(x), round(n), rng.choice([90, 130, 180, 240])))
jts = []
tries = 0
while len(jts) < 260 and tries < 20000:
    tries += 1
    x, n = rng.uniform(X0i, X1i), rng.uniform(N0i, N1i)
    if slope(x, n) > 0.12 or near_trail(x, n, 70): continue
    if any(math.hypot(x - a, n - b) < 140 for a, b, _ in piles): continue
    if any(math.hypot(x - a, n - b) < 230 for a, b, _, _ in jts): continue
    jts.append((round(x), round(n), round(rng.uniform(1.3, 2.3), 2), rng.randrange(6)))
print('piles', len(piles), 'jtrees', len(jts))

W = json.load(open('jthiddenvalley/water.json')) if os.path.exists('jthiddenvalley/water.json') else {}
pool = [p.xy(q) for q in p.WID['678429824']['p']] if '678429824' in p.WID else []
dam = [p.xy(q) for q in p.WID['1575997759']['p']] if '1575997759' in p.WID else [(6525, 6797), (6555, 6694)]
pcx, pcn = (np.mean([a for a, b in pool]), np.mean([b for a, b in pool])) if pool else (6740, 6730)
POOL = [[round(pcx + (a - pcx) * 3.0), round(pcn + (b - pcn) * 3.0)] for a, b in pool]   # drawn larger than life
d0, d1 = dam[0], dam[-1]
dmx, dmn = (d0[0] + d1[0]) / 2, (d0[1] + d1[1]) / 2
dang = math.atan2(d1[1] - d0[1], d1[0] - d0[0])
g = {s['name']: s for s in stops}
a1, s1 = g['Hidden Valley trailhead'], g['Barker Dam parking area']
lm = """  gate(%(ax)d,%(an)d,0.6);gate(%(sx)d,%(sn)d,0.2);
  // monzogranite boulder piles (OSM rock features plus rough high ground)
  function pile(x,n,r,i){const q=G(x,n),s=r*0.0068,g=new THREE.Group();g.position.copy(q);g.rotation.y=i*0.9;world.add(g);
    const cs=["#D8C3A2","#CDB592","#E2CFB0"];const k=3+(i%%3);
    for(let j=0;j<k;j++){const a=j/k*Math.PI*2+i,d=j?0.45*s:0;const b=part(g,new THREE.IcosahedronGeometry(1,1),cs[(i+j)%%3],Math.cos(a)*d,(j?0.32:0.48)*s,Math.sin(a)*d,(j?0.42:0.6)*s,(j?0.34:0.5)*s,(j?0.4:0.55)*s,1.06);rot(b,0.2*j,a,0.1);}}
  %(piles)s.forEach(([x,n,r],i)=>pile(x,n,r,i));
  // Joshua trees: shaggy trunk, a few angled arms, spiky leaf clusters at the tips
  function jtree(x,n,h,i){const g=new THREE.Group();g.position.copy(G(x,n));g.rotation.y=i*1.1;world.add(g);const tc="#7E6C55",lc="#7C8F4A";
    const t0=h*(0.45+0.08*(i%%3));part(g,cyl,tc,0,t0/2,0,0.09,t0,0.09,1.05);
    const arms=[[0.7,0],[-0.6,2.2],[0.5,4.1],[-0.8,1.1]].slice(0,2+(i%%3));
    arms.forEach(([tl,az],j)=>{const a=new THREE.Group();a.position.set(0,t0,0);a.rotation.y=az+i;g.add(a);
      const len=h*(0.38+0.06*j);const b=part(a,cyl,tc,0,len/2,0,0.06,len,0.06,1.05);
      const sub=new THREE.Group();sub.rotation.z=tl;a.add(sub);sub.add(b);b.position.set(0,len/2,0);
      const tip=new THREE.Vector3(0,len,0);part(sub,new THREE.IcosahedronGeometry(1,0),lc,tip.x,tip.y+0.08,tip.z,0.2,0.18,0.2,1.1);
      for(let s=0;s<5;s++){const c=part(sub,new THREE.ConeGeometry(0.05,0.32,4),lc,tip.x,tip.y+0.08,tip.z,1,1,1,1.1);rot(c,Math.cos(s*1.26)*1.0,0,Math.sin(s*1.26)*1.0);}});}
  %(jts)s.forEach(([x,n,h,i])=>jtree(x,n,h,i));
  // Barker Dam: concrete wall on the OSM dam line, drawn larger than life
  {const q=G(%(dmx)d,%(dmn)d),g=new THREE.Group();g.position.copy(q);g.rotation.y=%(dry).3f;world.add(g);
    part(g,box,"#BFB6A6",0,0.55,0,2.6,1.1,0.32,1.06);part(g,box,"#A79E8E",0,1.12,0,2.7,0.1,0.4,1.06);part(g,box,"#8E8576",0,0.25,0.22,2.6,0.5,0.12,1.06);}
  // reservoir (Barker Pool, OSM outline, enlarged)
  {const P=%(pool)s;if(P.length>2){const sh=new THREE.Shape(P.map(([x,n])=>new THREE.Vector2(x,n)));const geo=new THREE.ShapeGeometry(sh);const pa=geo.attributes.position;
    const y0=G(%(pcx)d,%(pcn)d).y+0.3;
    for(let i=0;i<pa.count;i++){const v=G(pa.getX(i),pa.getY(i));pa.setXYZ(i,v.x,y0+0.18,v.z);}
    pa.needsUpdate=true;geo.computeVertexNormals();const m=new THREE.Mesh(geo,new THREE.MeshLambertMaterial({color:"#8FC6DA",side:THREE.DoubleSide}));m.renderOrder=1;world.add(m);}}
  // petroglyph boulder: a dark-varnished overhanging rock
  {const q=G(%(px)d,%(pn)d),g=new THREE.Group();g.position.copy(q);g.rotation.y=0.4;world.add(g);
    part(g,new THREE.IcosahedronGeometry(1,1),"#D2BC98",0,0.7,0,1.1,0.8,0.9,1.06);part(g,new THREE.IcosahedronGeometry(1,1),"#C8B08A",0.5,1.3,0.1,0.9,0.45,0.75,1.06);
    part(g,box,"#5A3E2E",0.05,0.75,0.88,0.9,0.5,0.04,0);[[-0.2,0.85],[0.15,0.7],[0.35,0.9]].forEach(([x,y])=>part(g,box,"#E9D6B0",x,y,0.91,0.12,0.12,0.02,0));}
  // windmill: lattice tower with a bladed wheel and tail vane
  {const q=G(%(wx)d,%(wn)d),g=new THREE.Group();g.position.copy(q);g.rotation.y=0.9;world.add(g);const c="#7A5A44";
    [[1,1],[1,-1],[-1,1],[-1,-1]].forEach(([a,b])=>{const l=part(g,cyl,c,a*0.45,2.2,b*0.45,0.08,4.5,0.08,1.06);rot(l,-b*0.1,0,a*0.1);});
    [1.0,2.1,3.2].forEach((y,i)=>part(g,box,c,0,y,0,0.85-i*0.2,0.08,0.85-i*0.2,1.06));
    const hub=new THREE.Group();hub.position.set(0.3,4.55,0);g.add(hub);part(hub,cyl,"#5A5A5A",0,0,0,0.12,0.25,0.12,0).rotation.z=Math.PI/2;
    for(let b=0;b<12;b++){const bl=part(hub,box,"#9AA0A3",0.05,0,0,0.06,1.0,0.22,1.06);const a=b/12*Math.PI*2;bl.position.set(0.05,Math.cos(a)*0.6,Math.sin(a)*0.6);bl.rotation.x=a;}
    part(g,box,"#9AA0A3",-0.6,4.55,0,1.1,0.08,0.06,1.06);part(g,box,"#B5523B",-1.2,4.55,0,0.08,0.55,0.75,1.06);}
  // Worth Bagley stone (steel replica), upright and oversized
  {const q=G(%(bx)d,%(bn)d);part(world,box,"#B9A98E",q.x,q.y+0.1,q.z,1.2,0.2,0.7,1.06);part(world,box,"#6E3F2A",q.x,q.y+1.05,q.z,0.9,1.8,0.25,1.06);}
  // Wall Street Mill: tin-sided mill shed, ore chute, a rusted truck
  {const q=G(%(mx)d,%(mn)d),g=new THREE.Group();g.position.copy(q);g.rotation.y=0.5;world.add(g);
    part(g,box,"#8C98A0",0,0.8,0,1.6,1.6,1.2,1.06);const r=part(g,box,"#6F7B83",0,1.75,0,1.8,0.12,1.4,1.06);rot(r,0.18,0,0);
    part(g,box,"#7A5A44",1.0,1.2,0,0.25,2.4,0.25,1.06);const ch=part(g,box,"#7A5A44",1.9,1.5,0,2.0,0.14,0.3,1.06);rot(ch,0,0,-0.35);
    part(g,box,"#8A4B2E",-1.6,0.3,0.9,0.9,0.35,0.45,1.06);part(g,box,"#7A4028",-1.85,0.6,0.9,0.4,0.3,0.42,1.06);
    [[-1.3,0.7],[-1.3,1.1],[-1.95,0.7],[-1.95,1.1]].forEach(([x,z])=>{const w=part(g,cyl,"#2E2A26",x,0.13,z,0.13,0.08,0.13,0);rot(w,Math.PI/2,0,0);});}
""" % dict(ax=a1['x'] + 60, an=a1['n'] - 40, sx=s1['x'] + 40, sn=s1['n'] - 60,
           piles=js(piles), jts=js(jts), dmx=dmx, dmn=dmn, dry=-dang, pool=js(POOL), pcx=pcx, pcn=pcn,
           px=g['Petroglyphs']['x'] - 70, pn=g['Petroglyphs']['n'] - 30, wx=10117, wn=6621, bx=10524, bn=7611,
           mx=10430, mn=9110)

def wid(i): return i if i in p.WID else int(i)
creeks = []
for cid, ids in (('hv', ['422107525']), ('barker', ['422107517', '422107518', '422107523']), ('wsm', ['752875052'])):
    try:
        c = p.creek([wid(i) for i in ids], GRID, minor=True)
        if c and c.get('pts'): creeks.append(dict(id=cid, **c))
    except Exception as ex: print('creek', cid, ex)
print('creeks', [c['id'] for c in creeks])

species_extra = {
 'jt_joshua': 'jt_joshua:{name:"Joshua tree",latin:"Yucca brevifolia",color:"#EDEBCF",shape:"yucca",bloom:[2,3,4],sum:"The park’s namesake, a tree-sized yucca with shaggy trunks and clusters of stiff, spiky leaves. Thick on the flats around Barker Dam and along the Wall Street Mill trail. In spring some branch tips carry heavy clusters of creamy flowers, pollinated only by the yucca moth.",rule:(d,e,g,s)=>g<0.4}',
 'jt_mojyucca': 'jt_mojyucca:{name:"Mojave yucca",latin:"Yucca schidigera",color:"#F3EFDF",shape:"yucca",bloom:[2,3,4],sum:"A shorter, shrubby yucca with long, sharp leaves and cream flower clusters in late winter and early spring, also pollinated by yucca moths.",rule:(d,e,g,s)=>g<0.6}',
 'beavertail': 'beavertail:{name:"Beavertail cactus",latin:"Opuntia basilaris",color:"#D9418C",shape:"pad",bloom:[3,4,5],sum:"Flat, blue-gray pads that look spineless (the tiny bristles still hurt), with bright magenta flowers in spring. Rangers log it around Barker Dam.",rule:(d,e,g,s)=>g<0.8}',
 'jt_mojmound': 'jt_mojmound:{name:"Mojave mound cactus",latin:"Echinocereus triglochidiatus",color:"#D0283A",shape:"pad",bloom:[4,5],sum:"Mounds of ribbed, spiny stems tucked among boulders, covered in waxy scarlet cups in April and May. Hummingbirds pollinate them.",rule:(d,e,g,s)=>g>0.15}',
 'jt_goldenbush': 'jt_goldenbush:{name:"Interior goldenbush",latin:"Ericameria linearifolia",color:"#F2C230",shape:"dome",bloom:[3,4,5],sum:"A rounded shrub with narrow, sticky leaves that covers itself in yellow daisy-like flowers in spring. Among the most common spring bloomers around Barker Dam.",rule:(d,e,g,s)=>g<0.7}',
 'jt_dudleya': 'jt_dudleya:{name:"Rock live-forever",latin:"Dudleya saxosa",color:"#E8C64A",shape:"tube",bloom:[4,5,6],sum:"A succulent with fleshy gray-green rosettes wedged into cracks in the granite, sending up reddish stalks of small tubular flowers in late spring.",rule:(d,e,g,s)=>g>0.25}',
}
tree_rule = """if(mk<0.25){type=null;}
    else if(cd<200){type=tr()<.45?"oak":"shrub";p=0.14;}
    else if(g>0.9)type=null;
    else{type=tr()<.15?"oak":"shrub";p=0.03+cl*.02;}"""

# ---- photos
MD = json.load(open('/mnt/files/gtb/photos/jthiddenvalley/photos_meta.json'))
MM = {m['f']: m for v in MD.values() for m in v}
def ph(*fs): return [dict(MM['../photos/' + f + '.jpg']) for f in fs if '../photos/' + f + '.jpg' in MM]
SPM = {}
for page in os.listdir('/home/claude/site/out'):
    fp = '/home/claude/site/out/%s/index.html' % page
    if not os.path.exists(fp): continue
    for m in re.findall(r'\{"f":"\.\./photos/sp_[^}]*\}', open(fp).read()):
        try: d = json.loads(m); SPM[d['f'].split('/')[-1][:-4]] = d
        except Exception: pass
def sp(*fs):
    out = []
    for f in fs:
        if f in SPM: out.append(SPM[f])
        elif '../photos/' + f + '.jpg' in MM: out.append(dict(MM['../photos/' + f + '.jpg']))
        else: print('missing photo', f)
    return out
nm = {s['name']: s['id'] for s in stops}
stop_photos = {nm['Hidden Valley trailhead']: ph('pl_jthiddenvalley_hv_1'),
               nm['Valley floor']: ph('pl_jthiddenvalley_hvtrail_1', 'pl_jthiddenvalley_hvtrail_2', 'pl_jthiddenvalley_hv_2'),
               nm['Barker Dam']: ph('pl_jthiddenvalley_bd_1', 'pl_jthiddenvalley_bd_3'),
               nm['Into the boulders']: ph('pl_jthiddenvalley_bd_0'),
               nm['Windmill']: ph('pl_jthiddenvalley_windmill_0', 'pl_jthiddenvalley_wsm_3'),
               nm['Worth Bagley stone']: ph('pl_jthiddenvalley_bagley_0', 'pl_jthiddenvalley_bagley_1'),
               nm['Wall Street Mill']: ph('pl_jthiddenvalley_wsm_0', 'pl_jthiddenvalley_wsm_2', 'pl_jthiddenvalley_wsm_1', 'pl_jthiddenvalley_car_0')}
PETRO = [k for k in MD if k.startswith('petro')]
KEEP_PETRO = json.load(open('jthiddenvalley/petro_keep.json')) if os.path.exists('jthiddenvalley/petro_keep.json') else []
if KEEP_PETRO: stop_photos[nm['Petroglyphs']] = ph(*KEEP_PETRO)
stop_photos = {k: v for k, v in stop_photos.items() if v}
flower_photos = {'jt_joshua': sp('sp_joshuatree_0', 'sp_joshuatree_1', 'sp_joshuatree_2'), 'jt_mojyucca': sp('sp_mojaveyucca_0', 'sp_mojaveyucca_1', 'sp_mojaveyucca_2'),
                 'beavertail': sp('sp_hs_beavertail_0', 'sp_hs_beavertail_1', 'sp_hs_beavertail_2'), 'jt_mojmound': sp('sp_mojmound_3', 'sp_mojmound_1', 'sp_mojmound_2'),
                 'jt_goldenbush': sp('sp_goldenbush_1', 'sp_goldenbush_2', 'sp_goldenbush_3'), 'jt_dudleya': sp('sp_dudleya_saxosa_1', 'sp_dudleya_saxosa_3')}
animal_photos = {'bighorn': sp('sp_bighorn_dl0', 'sp_bighorn_dl1'), 'coyote': sp('sp_coyote_0'), 'squirrel': sp('sp_wtantsquirrel_1', 'sp_wtantsquirrel_3'),
                 'quail': sp('sp_gambelquail_0', 'sp_gambelquail_1'), 'snake': sp('sp_speckledrattle_0', 'sp_speckledrattle_1'), 'turtle': sp('sp_tortoise_0', 'sp_tortoise_2'),
                 'heron': sp('sp_gbheron_dl_0', 'sp_gbheron_dl_1'), 'raven': sp('sp_sm_raven_0', 'sp_sm_raven_3'), 'hawk': sp('sp_redtail_1', 'sp_redtail_2')}
flower_photos = {k: v for k, v in flower_photos.items() if v}; animal_photos = {k: v for k, v in animal_photos.items() if v}
print('photos', {k: len(v) for k, v in {**stop_photos, **flower_photos, **animal_photos}.items()})

cfg = dict(
    title='Joshua Tree: Hidden Valley & Barker Dam', aria='Hidden Valley, Barker Dam and Wall Street Mill in Joshua Tree National Park', h1='Joshua Tree: Hidden Valley &amp; Barker Dam',
    canyons=[], trees_anywhere=True, trails=trails, stops=stops, order=order,
    species=['jt_joshua', 'jt_mojyucca', 'beavertail', 'jt_mojmound', 'jt_goldenbush', 'jt_dudleya'], species_extra=species_extra,
    flora={'A': ['jt_joshua', 'jt_mojyucca', 'jt_mojmound', 'jt_dudleya', 'jt_goldenbush'], 'B': ['jt_joshua', 'jt_goldenbush', 'beavertail', 'jt_mojmound', 'jt_dudleya'], 'C': ['jt_joshua', 'jt_mojyucca', 'beavertail', 'jt_goldenbush']},
    wild=['bighorn', 'coyote', 'squirrel', 'quail', 'snake', 'turtle', 'heron', 'raven', 'hawk'],
    wild_sum={'bighorn': ('Desert bighorn sheep', 'Barker Dam is one of the likeliest places in the park to see them. They come down the boulders to drink when the reservoir holds water, most often early or late in the day. Keep your distance.'),
              'coyote': ('Coyote', 'Common across the park and often seen trotting over the open flats along the Wall Street Mill trail at dawn and dusk. Never feed them.'),
              'squirrel': ('White-tailed antelope squirrel', 'A small ground squirrel that runs with its white tail curled over its back, darting between boulders and shrubs even in midday heat.'),
              'quail': ('Gambel’s quail', 'Coveys run between the shrubs around Barker Dam and Hidden Valley; males have a black teardrop plume and a chestnut cap.'),
              'snake': ('Speckled rattlesnake', 'Its pale, mottled colors match the granite. Most active on warm days in spring and fall; watch where you put hands and feet among the boulders.'),
              'turtle': ('Desert tortoise', 'A threatened species that spends most of the year in burrows and comes out mainly after spring rains. If you see one, keep your distance and never pick it up.'),
              'heron': ('Great blue heron', 'When the reservoir behind Barker Dam holds water, wading birds such as herons sometimes stop to feed, a rare sight in the desert.'),
              'raven': ('Common raven', 'Big black birds that patrol the parking lots and boulder piles in pairs. Keep food packed away.'),
              'hawk': ('Red-tailed hawk', 'Soars over the open flats and perches on Joshua trees, hunting ground squirrels and rabbits.')},
    grid=GRID, step=STEP, dem_b64=b64, tile=TILE, ve=2.6, ridge_ft=RIDGE,
    palette='desert', tree_rule=tree_rule, rock_all_aspects=True,
    landmarks=lm, animals_js=animals_js,
    zoomcap={'A': 5.2, 'B': 5.0, 'C': 3.4},
    overview=dict(h2='Hidden Valley, Barker Dam and Wall Street Mill',
                  p='North of Park Boulevard, in the middle of Joshua Tree National Park, flats of Joshua trees run between piles of rounded monzogranite boulders at the edge of the Wonderland of Rocks, at about 4,200–4,300 ft. A is the Hidden Valley Nature Trail, a loop inside a ring of rock walls. B, the Barker Dam loop, visits a small reservoir built by cattlemen and a boulder of petroglyphs. C leaves the same lot for Bill Keys’ Wall Street Mill. All three are short and nearly flat. Pick a trail to focus the model; click anything on it for a quick note.',
                  numbers='Plain number 1 is the Barker Dam parking area, where B and C both start. Lettered stops belong to one trail: A3 is the third stop on Trail A.',
                  wild_h='Wildlife around Hidden Valley',
                  note='<b>Open.</b> Joshua Tree National Park, California, open 24 hours year-round; no reservation or timed entry. Entrance fee $30 per private vehicle, $25 per motorcycle or $15 per person on foot or bike, good for 7 days. Hidden Valley picnic area is on Park Boulevard; Barker Dam parking is at the end of Barker Dam Road, a short paved road off Park Boulevard nearby. Both lots fill by midday on busy days. No water in the park interior, little shade, and no pets on the trails. Terrain from USGS elevation data, stylized; not for navigation.'),
    links={'A': [('Hiking trails · NPS', 'https://www.nps.gov/jotr/planyourvisit/hiking.htm'), ('Hidden Valley Nature Trail · Hiking Project', 'https://www.hikingproject.com/trail/7016879/hidden-valley-nature-trail')],
           'B': [('Barker Dam Nature Trail · Hiking Project', 'https://www.hikingproject.com/trail/7017697/barker-dam-nature-trail'), ('Barker Dam · Wikipedia', 'https://en.wikipedia.org/wiki/Barker_Dam_(California)')],
           'C': [('Wall Street Mill Trailhead · NPS', 'https://www.nps.gov/places/wall-street-mill-trailhead.htm'), ('Wall Street Mill · Hikespeak', 'https://www.hikespeak.com/?p=10208'), ('Worth Bagley marker · NPS', 'https://www.nps.gov/jotr/learn/news/joshua-tree-national-park-replaces-historic-marker.htm')]},
    extra_js='TRAILS.forEach(T=>{const g={A:100,B:50,C:115}[T.id];if(g)T.gain=g;});\n// out-and-back: report the outbound mile for a stop\nmileOf=function(T,x,n){let b=null;T.pts.forEach(p=>{const d=Math.hypot(p.x-x,p.n-n);if(!b||d<b.d)b={d,m:p.m,e:p.e};});if(!b||b.d>=260)return null;const f=T.pts.find(p=>Math.hypot(p.x-x,p.n-n)<b.d+60);return {d:b.d,m:f.m,e:f.e};};\n// open a trail view from #trail-X\nwindow.addEventListener("load",()=>{const m=(location.hash||"").match(/trail-([ABC])/);if(m)setTimeout(()=>{const b=document.querySelector(\'#switch [data-v="\'+m[1]+\'"]\');if(b)b.click();},800);});\nwindow.addEventListener("hashchange",()=>{const m=(location.hash||"").match(/trail-([ABC])/);const b=m&&document.querySelector(\'#switch [data-v="\'+m[1]+\'"]\');if(b)b.click();});',
    viewaz={'all': 0.55, 'A': 0.6, 'B': 0.5, 'C': 0.7},
    stop_photos=stop_photos, flower_photos=flower_photos, animal_photos=animal_photos,
)
json.dump({k: {'mi': R[k]['mi'], 'gain': R[k]['gain'], 'lo': R[k]['lo'], 'hi': R[k]['hi']} for k in R}, open('jthiddenvalley/stats.json', 'w'))
os.makedirs('/home/claude/site/out/joshua-tree-hidden-valley', exist_ok=True)
print(build(cfg, '/home/claude/site/out/joshua-tree-hidden-valley/index.html'))
