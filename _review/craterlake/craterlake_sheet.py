from lib import *
from mk_sheet import build
import sys, json, os, math, glob, re
import numpy as np

os.chdir('/home/claude/parks')
sys.path.insert(0, '/home/claude/parks')
p = Park('craterlake', 42.94, -122.10)   # origin over Crater Lake; x east, n north, feet
# all points from OSM ways/nodes (Crater Lake NP)
WOV = (-18469, 2029)     # Watchman Overlook: start of the trail at the south end of the lot (OSM Rim Trail way end; viewpoint node -18310,2109)
RTJ = (-20117, 1347)     # Watchman Peak Trail leaves the Rim Trail (old Rim Drive)
WSUM = (-19269, 1088)    # Watchman Lookout on the summit (OSM peak "The Watchman" -19294,1075)
BTH = (4436, 14458)      # Cleetwood Cove Trail at Rim Drive
SHORE = (3081, 13272)    # trail reaches the shore (OSM way end, 6,174 ft)
DOCK = (2826, 13051)     # end of the spur to the boat landing
STH = (18594, -3966)     # Mount Scott Trail at East Rim Drive
SSUM = (22308, -6242)    # Mount Scott summit (OSM trail end, DEM max 8,900 ft at 22250,-6250)

def mkroute(pts):
    E = [p.elev(*q) for q in pts]
    cum = [0.0]
    for i in range(1, len(pts)): cum.append(cum[-1] + math.dist(pts[i - 1], pts[i]))
    gain = sum(max(0, E[i] - E[i - 1]) for i in range(1, len(E)))
    return dict(pts=pts, E=E, cum=cum, segs=[], gain=gain, mi=cum[-1] / 5280, lo=min(E), hi=max(E))
UP = {'A': route_xy(p, WOV, RTJ, WSUM), 'B': route_xy(p, BTH, SHORE, DOCK), 'C': route_xy(p, STH, SSUM)}
R = {}
for k in 'ABC':
    R[k] = mkroute(UP[k]['pts'] + UP[k]['pts'][-2::-1]); R[k]['segs'] = UP[k]['segs']
for k in R: Park.smooth_E(R[k], 9); p.describe(R[k], k)
for k in UP: p.describe(UP[k], k + ' up')

def at_frac(k, f):
    P = UP[k]['pts']; cum = [0.0]
    for i in range(1, len(P)): cum.append(cum[-1] + math.dist(P[i - 1], P[i]))
    t = f * cum[-1]; i = next(i for i in range(len(cum)) if cum[i] >= t)
    return (round(P[i][0]), round(P[i][1]))
B2 = at_frac('B', 0.45)
C2 = at_frac('C', 0.62)
ST = snap_stops(p, R, {
    'A1': (*WOV, 'A'), 'A2': (*RTJ, 'A'), 'A3': (*WSUM, 'A'),
    'B1': (*BTH, 'B'), 'B2': (*B2, 'B'), 'B3': (*SHORE, 'B'), 'B4': (*DOCK, 'B'),
    'C1': (*STH, 'C'), 'C2': (*C2, 'C'), 'C3': (*SSUM, 'C'),
})
TILE = (-36000, 39000, -32500, 32500)
GRID = (-36500, 39500, -33000, 33000)
STEP = 350
b64, NX, NN = p.dem_b64(*GRID, STEP=STEP)
inner = p.grid[3:-3, 3:-3]
RIDGE = int(round(float(np.percentile(inner, 75)), -1))
print('grid', NX, NN, NX * NN, p.grid.min(), p.grid.max(), 'p75', RIDGE)

# --- Crater Lake from the DEM: cells at lake level (6,175 ft) connected to the middle of the lake
LS = 200; LX0, LX1, LN0, LN1 = -21000, 15000, -16000, 18000
nx, nn = (LX1 - LX0) // LS + 1, (LN1 - LN0) // LS + 1
EL = np.array([[p.elev(LX0 + i * LS, LN0 + j * LS) for i in range(nx)] for j in range(nn)])
LVL = float(p.elev(0, 0)); print('lake level', LVL)
wet = EL <= LVL + 6
M = np.zeros_like(wet); st = [((0 - LN0) // LS, (0 - LX0) // LS)]
while st:
    j, i = st.pop()
    if j < 0 or i < 0 or j >= nn or i >= nx or M[j, i] or not wet[j, i]: continue
    M[j, i] = True; st += [(j + 1, i), (j - 1, i), (j, i + 1), (j, i - 1)]
print('lake cells', int(M.sum()), 'area sq mi', round(M.sum() * LS * LS / 5280 ** 2, 1))
def dil(A):
    B = A.copy(); B[1:] |= A[:-1]; B[:-1] |= A[1:]; B[:, 1:] |= A[:, :-1]; B[:, :-1] |= A[:, 1:]; return B
MW = dil(dil(M))   # water plane: a little wider than the shore; the rising terrain hides the edge
def rle(A):
    rows = []
    for j in range(nn):
        r = A[j]; iv = []; i = 0
        while i < nx:
            if r[i]:
                k = i
                while k + 1 < nx and r[k + 1]: k += 1
                iv.append([LX0 + i * LS - LS // 2, LX0 + k * LS + LS // 2]); i = k + 1
            else: i += 1
        if iv: rows.append([LN0 + j * LS, iv])
    return rows
LAKE = {'s': LS, 'w': rle(MW), 'm': rle(dil(M))}
xs = np.where(M.any(0))[0]; ns_ = np.where(M.any(1))[0]
print('lake bbox x', LX0 + xs.min() * LS, LX0 + xs.max() * LS, 'n', LN0 + ns_.min() * LS, LN0 + ns_.max() * LS)
LAKE_FN = ('function lakeData(){return lakeData.c||(lakeData.c=%s);}\n' % js(LAKE) +
           'function lakeAt(x,n){const L=lakeData();if(!L.M){L.M={};L.m.forEach(([n0,iv])=>L.M[n0]=iv);}const r=L.M[Math.round(n/L.s)*L.s];if(!r)return false;for(const [a,b] of r){if(x>=a&&x<=b)return true;}return false;}\n'
           'function inLake(x,n){return surf(x,n)<%d&&lakeAt(x,n);}\n' % (LVL + 25))

S = lambda i: ST[i]
stops = [
 dict(id='A1', trails=['A'], x=S('A1')[0], n=S('A1')[1], name='Watchman Overlook',
      desc='A pullout on West Rim Drive, about 3.8 miles northwest of Rim Village, looking straight down on Wizard Island. Vault toilets. The trail starts at the south end of the lot.'),
 dict(id='A2', trails=['A'], x=S('A2')[0], n=S('A2')[1], name='Rim Trail junction',
      desc='The first stretch follows an old section of Rim Drive across loose dacite blocks and pumice. Here the Watchman Peak Trail leaves the Rim Trail and turns up the ridge in short switchbacks.'),
 dict(id='A3', trails=['A'], x=S('A3')[0], n=S('A3')[1], name='Watchman Lookout',
      desc='A two-story fire lookout of stone and glass, built in 1932 in the Park Service rustic style and listed on the National Register; it is still staffed in fire season. Wizard Island and the crater on its summit lie directly below, about 1,800 feet down. The summit is often windy.'),
 dict(id='B1', trails=['B'], x=S('B1')[0], n=S('B1')[1], name='Cleetwood Cove trailhead',
      desc='A large parking lot on the north side of Rim Drive, 4.6 miles east of North Junction, with vault toilets. Closed for the 2026, 2027 and 2028 seasons while the trail is rebuilt. No pets or wheeled devices on the trail.'),
 dict(id='B2', trails=['B'], x=S('B2')[0], n=S('B2')[1], name='Red fir switchbacks',
      desc='The trail drops 700 feet in 1.1 miles on long switchbacks of loose crushed pumice, under old red firs with partial shade and a few benches. The climb back up is like 65 flights of stairs; most search and rescues in the park are hikers who cannot make it back up.'),
 dict(id='B3', trails=['B'], x=S('B3')[0], n=S('B3')[1], name='Cleetwood Cove',
      desc='The only legal access to the shore: boulders, no beach and no shade, with deep blue water close in. Swimming is allowed within 100 yards of the cove; the surface averages 57°F in summer. A sheer rock beside the landing is a popular jump. The Mazama newt, found only in Crater Lake, lives along these rocky shores.'),
 dict(id='B4', trails=['B'], x=S('B4')[0], n=S('B4')[1], name='Boat dock',
      desc='Where lake tours and Wizard Island boats leave. The failed dock is being replaced with a floating dock and a viewing pier, plus new restrooms and a ticket booth; there are no public boat tours in 2026, 2027 or 2028.'),
 dict(id='C1', trails=['C'], x=S('C1')[0], n=S('C1')[1], name='Mount Scott trailhead',
      desc='A small pullout on East Rim Drive, across from the road to Cloudcap Overlook and about 14 miles from park headquarters by the east side of Rim Drive.'),
 dict(id='C2', trails=['C'], x=S('C2')[0], n=S('C2')[1], name='Whitebark pine slopes',
      desc='Whitebark pines and mountain hemlocks cover the slopes, more twisted and stunted toward the top. Clark’s nutcrackers pry seeds from the pine cones and bury them, planting new trees. Long switchbacks lead up the last stretch.'),
 dict(id='C3', trails=['C'], x=S('C3')[0], n=S('C3')[1], name='Mount Scott summit',
      desc='The highest point in the park, 8,929 feet: an old volcano, about 420,000 years old, that survived the collapse of Mount Mazama. A fire lookout stands on top. It is the only place in the park where you can see the whole lake, plus Upper Klamath Lake, Mount Shasta and Mount Thielsen.'),
]
stops, order = renumber(p, R, stops)
print(order, [(s['id'], s['name'], s['x'], s['n']) for s in stops])
trails = [
 dict(id='A', name='Watchman Peak', short='Watchman', official=1.6, unit='round trip', route='Out and back', time='1 hr', level='Moderate', color='--tA',
      desc='From the Watchman Overlook on West Rim Drive, the trail follows an old piece of Rim Drive across a pumice slope, then switchbacks up through sparse mountain hemlock and whitebark pine to the 1932 Watchman Lookout, right above Wizard Island. About 420 feet of climbing. Very crowded at sunset; usually under snow from October to early July.', anchors=p.anchors(R['A'])),
 dict(id='B', name='Cleetwood Cove Trail', short='Cleetwood Cove', official=2.2, unit='round trip', route='Out and back', time='1–1.5 hr', level='Strenuous', color='--tB',
      desc='The only trail down to the water. Long switchbacks drop 700 feet through old red firs to a rocky cove and the boat dock; the steepest parts are at the start and near the bottom. Closed for the 2026, 2027 and 2028 seasons for a full rebuild of the trail, dock and restrooms; normally open mid-June to late October.', anchors=p.anchors(R['B'])),
 dict(id='C', name='Mount Scott', short='Mount Scott', official=4.4, unit='round trip', route='Out and back', time='3 hr', level='Strenuous', color='--tC',
      desc='From East Rim Drive the trail climbs steadily through whitebark pine and mountain hemlock, then in long switchbacks, to the fire lookout on the park’s highest peak. About 1,250 feet of climbing, with views over the whole lake and east to the Klamath Basin.', anchors=p.anchors(R['C'])),
]

extra_js = '''
TRAILS.forEach(T=>{const g={A:420,B:700,C:1250}[T.id];if(g)T.gain=g;});
// out-and-back: report the outbound mile for a stop
mileOf=function(T,x,n){let b=null;T.pts.forEach(p=>{const d=Math.hypot(p.x-x,p.n-n);if(!b||d<b.d)b={d,m:p.m,e:p.e};});if(!b||b.d>=260)return null;const f=T.pts.find(p=>Math.hypot(p.x-x,p.n-n)<b.d+60);return {d:b.d,m:f.m,e:f.e};};
// Crater Lake: one flat deep-blue surface at lake level; the caldera walls and Wizard Island rise through it
(function(){const y0=G(0,0).y+0.05;const pos=[];
  const L=lakeData();L.w.forEach(([n,iv])=>iv.forEach(([a,b])=>{const n0=n-L.s/2,n1=n+L.s/2;
    const P=[G(a,n0),G(b,n0),G(b,n1),G(a,n1)].map(v=>[v.x,y0,v.z]);
    [0,1,2,0,2,3].forEach(i=>pos.push(...P[i]));}));
  const geo=new THREE.BufferGeometry();geo.setAttribute("position",new THREE.Float32BufferAttribute(pos,3));geo.computeVertexNormals();
  const m=new THREE.Mesh(geo,new THREE.MeshLambertMaterial({color:"#1D4F9E",side:THREE.DoubleSide}));m.renderOrder=1;world.add(m);
})();
'''
lm = f'''  [[{WOV[0] - 40},{WOV[1] - 60},0.4],[{STH[0] + 40},{STH[1] + 50},1.0]].forEach(([x,n,r])=>{{const g=new THREE.Group();g.position.copy(G(x,n));g.rotation.y=r;g.scale.setScalar(0.4);world.add(g);
   part(g,cyl,"#6B4F3A",-0.9,0.45,0,0.08,0.9,0.08);part(g,cyl,"#6B4F3A",0.9,0.45,0,0.08,0.9,0.08);part(g,box,"#E9E1D2",0,0.75,0,1.9,0.12,0.1,1.08);part(g,box,"#2D4A40",1.35,0.55,0.2,0.45,0.35,0.05,1.06);}});
  // Watchman Lookout (1932): stone ground floor, glass lookout room, low hipped roof, east wing; drawn large
  {{const q=G({WSUM[0]},{WSUM[1]});const g=new THREE.Group();g.position.copy(q);g.rotation.y=0.0;g.scale.setScalar(0.75);world.add(g);
   part(g,box,"#8A847B",0,0.55,0,1.3,1.1,1.0,1.05);part(g,box,"#7A746B",0.95,0.4,0,0.7,0.8,0.8,1.05);
   part(g,box,"#5A4632",0,1.14,0,1.5,0.1,1.2,1.05);part(g,box,"#BFE3EE",0,1.5,0,1.36,0.62,1.06,1.05);
   [[-0.66,-0.51],[0.66,-0.51],[-0.66,0.51],[0.66,0.51]].forEach(([a,b])=>part(g,box,"#5A4632",a,1.5,b,0.08,0.62,0.08,1.05));
   const rf=part(g,new THREE.ConeGeometry(1.15,0.5,4),"#4A3A2C",0,2.06,0,1.15,1,0.95,1.05);rf.rotation.y=Math.PI/4;}}
  // Mount Scott fire lookout on the summit, drawn large
  {{const q=G({SSUM[0]},{SSUM[1]});const g=new THREE.Group();g.position.copy(q);g.scale.setScalar(0.75);world.add(g);
   part(g,box,"#6E5236",0,0.45,0,1.1,0.9,1.1,1.05);part(g,box,"#5A4632",0,0.95,0,1.3,0.1,1.3,1.05);
   part(g,box,"#BFE3EE",0,1.3,0,1.16,0.6,1.16,1.05);
   [[-0.56,-0.56],[0.56,-0.56],[-0.56,0.56],[0.56,0.56]].forEach(([a,b])=>part(g,box,"#5A4632",a,1.3,b,0.08,0.6,0.08,1.05));
   const rf=part(g,new THREE.ConeGeometry(1.05,0.5,4),"#3E3A36",0,1.85,0,1,1,1,1.05);rf.rotation.y=Math.PI/4;}}
  // Cleetwood boat dock: floating dock out from the landing (on the lake surface)
  {{const a=G({SHORE[0]},{SHORE[1]}),b=G({DOCK[0]},{DOCK[1]});const y=G(0,0).y+0.12;const d=new THREE.Vector3(b.x-a.x,0,b.z-a.z).normalize();
   const g=new THREE.Group();g.position.set(b.x+d.x*0.15,y,b.z+d.z*0.15);g.rotation.y=Math.atan2(d.x,d.z);g.scale.setScalar(0.32);world.add(g);
   part(g,box,"#A08A6A",0,0.06,0.9,0.5,0.14,2.4,1.05);part(g,box,"#A08A6A",0,0.06,2.1,1.8,0.14,0.45,1.05);
   [-0.8,0.8].forEach(s=>part(g,box,"#5E4330",s,0.18,2.1,0.06,0.2,0.06,0));}}
  // trail closed 2026-2028: orange barrier at the Cleetwood trailhead
  {{const q=G({BTH[0]},{BTH[1]});const g=new THREE.Group();g.position.copy(q);g.rotation.y=0.7;g.scale.setScalar(0.5);world.add(g);
   [-0.6,0.6].forEach(s=>part(g,box,"#F2F0EA",s,0.35,0,0.08,0.7,0.08,1.05));
   part(g,box,"#E8762B",0,0.55,0,1.4,0.16,0.06,1.05);part(g,box,"#F2F0EA",0,0.38,0,1.4,0.12,0.06,1.05);part(g,box,"#E8762B",0,0.22,0,1.4,0.1,0.06,1.05);}}
'''
# --- photos (Wikimedia via gt6_photos; species photos reused from other pages on the site)
PM = json.load(open('/home/claude/gtb_cl/photos/craterlake/photos_meta.json'))
def keep(key, files):
    return [dict(x) for f in files for x in PM.get(key, []) if x['f'].endswith('/' + f)]
_reuse = {}
def reuse(*names):
    out = []
    for nm in names:
        if nm not in _reuse:
            for fp in glob.glob('/home/claude/site/out/*/index.html'):
                m = re.search(r'\{"f":"\.\./photos/' + re.escape(nm) + r'"[^}]*\}', open(fp, encoding='utf-8', errors='ignore').read())
                if m: _reuse[nm] = json.loads(m.group(0)); break
        if nm in _reuse: out.append(dict(_reuse[nm]))
        else: print('no meta for', nm)
    return out
stop_photos = {
 'A3': keep('watchman', ['pl_craterlake_watchman_2.jpg', 'pl_craterlake_watchman_0.jpg']) + keep('wizard', ['pl_craterlake_wizard_2.jpg', 'pl_craterlake_wizard_0.jpg']),
 'B2': keep('cleetwood', ['pl_craterlake_cleetwood_2.jpg', 'pl_craterlake_cleetwood_1.jpg']),
 'B3': keep('cleetwood', ['pl_craterlake_cleetwood_3.jpg']),
 'C2': keep('scotttrail', ['pl_craterlake_scotttrail_0.jpg', 'pl_craterlake_scotttrail_3.jpg', 'pl_craterlake_scotttrail_2.jpg']),
 'C3': keep('scott', ['pl_craterlake_scott_2.jpg', 'pl_craterlake_scott_0.jpg']),
}
stop_photos = {k: v for k, v in stop_photos.items() if v}
species_extra = {
 'dpen_cl': 'dpen_cl:{name:"Davidson’s penstemon",latin:"Penstemon davidsonii",color:"#9A62C8",shape:"tube",bloom:[7,8],sum:"A low mat of small leathery leaves with big lavender-purple trumpets, tucked into rock crevices high on the rim. Blooms on the Watchman in mid to late summer.",rule:(d,e,g,s)=>e>7300}',
 'pasque_cl': 'pasque_cl:{name:"Western pasqueflower",latin:"Anemone occidentalis",color:"#F3F0E4",shape:"cup",bloom:[6,7],sum:"Creamy white cups that open right after the snow melts, then turn into shaggy, mop-like seed heads by midsummer.",rule:(d,e,g,s)=>e>7200}',
 'phlox_cl': 'phlox_cl:{name:"Spreading phlox",latin:"Phlox diffusa",color:"#E6D3F0",shape:"cup",bloom:[6,7],sum:"Cushions of needle-like leaves covered in white to pale pink and lavender flowers, among the first to bloom as the snow recedes.",rule:(d,e,g,s)=>e>6300}',
 'sulph_cl': 'sulph_cl:{name:"Sulphur flower",latin:"Eriogonum umbellatum",color:"#F0D23A",shape:"dome",bloom:[7,8],sum:"A wild buckwheat with round umbrellas of tiny yellow flowers over low mats of leaves, on dry pumice and rocky slopes.",rule:(d,e,g,s)=>e>6800}',
 'knot_cl': 'knot_cl:{name:"Newberry’s knotweed",latin:"Polygonum davisiae",color:"#D8D2A6",shape:"dome",bloom:[7,8],sum:"Also called fleeceflower: a sprawling plant of loose pumice with small greenish-white flowers; its leaves turn bright red and orange in fall.",rule:(d,e,g,s)=>e>7000}',
 'hulsea_cl': 'hulsea_cl:{name:"Dwarf hulsea",latin:"Hulsea nana",color:"#F2C230",shape:"cup",bloom:[7,8],sum:"A tiny, woolly alpine sunflower with yellow heads, growing on high cinder and pumice slopes such as Mount Scott.",rule:(d,e,g,s)=>e>8000}',
}
flower_photos = {
 'dpen_cl': keep('sp:cl_davidsonpenstemon', ['sp_cl_davidsonpenstemon_1.jpg', 'sp_cl_davidsonpenstemon_0.jpg', 'sp_cl_davidsonpenstemon_3.jpg']),
 'pasque_cl': keep('sp:cl_wpasque', ['sp_cl_wpasque_0.jpg', 'sp_cl_wpasque_3.jpg', 'sp_cl_wpasque_2.jpg']),
 'phlox_cl': keep('sp:cl_spreadingphlox', ['sp_cl_spreadingphlox_1.jpg', 'sp_cl_spreadingphlox_2.jpg', 'sp_cl_spreadingphlox_3.jpg']),
 'sulph_cl': keep('sp:cl_sulphurflower', ['sp_cl_sulphurflower_0.jpg', 'sp_cl_sulphurflower_3.jpg']),
 'knot_cl': keep('sp:cl_newberryknotweed', ['sp_cl_newberryknotweed_0.jpg', 'sp_cl_newberryknotweed_2.jpg']),
}
flower_photos = {k: v for k, v in flower_photos.items() if v}
animal_photos = {
 'squirrel': reuse('sp_gmgsq_gt_0.jpg', 'sp_gmgsq_gt_1.jpg'),
 'pika': reuse('sp_l22_pika_0.jpg', 'sp_l22_pika_1.jpg'),
 'marmot': reuse('sp_ybmarmot_0.jpg', 'sp_ybmarmot_2.jpg'),
 'deer': reuse('sp_muledeer_0.jpg', 'sp_dp_btdeer_0.jpg'),
 'bear': reuse('sp_l22_blackbear_0.jpg', 'sp_l22_blackbear_1.jpg'),
 'elk': reuse('sp_elk_0.jpg', 'sp_elk_1.jpg'),
 'fox': reuse('sp_redfox_0.jpg', 'sp_redfox_1.jpg'),
 'coyote': reuse('sp_coyote_0.jpg'),
 'bobcat': reuse('sp_bobcat_0.jpg'),
 'lion': reuse('sp_lion_0.jpg'),
 'nutcracker': reuse('sp_nutcracker_0.jpg', 'sp_nutcracker_2.jpg'),
 'eagle': reuse('sp_baldeagle_0.jpg', 'sp_baldeagle_1.jpg'),
 'peregrine': reuse('sp_peregrine_0.jpg', 'sp_peregrine_2.jpg'),
 'bluebird': reuse('sp_sm_mtbluebird_0.jpg', 'sp_sm_mtbluebird_1.jpg'),
}
animal_photos = {k: v for k, v in animal_photos.items() if v}

pa = place_along
U = lambda k, f, s=1, o=240: pa(p, UP[k], [f], s, o)[0]
an = []
an += [f'{{k:"pika",at:{js(U("A",.55,-1,160))}}}', f'{{k:"pika",at:{js(U("C",.85,1,170))}}}']
an += [f'{{k:"marmot",at:{js(U("A",.25,1,220))}}}', f'{{k:"marmot",at:{js(U("C",.7,-1,220))}}}']
an += [f'{{k:"squirrel",at:{js(U("A",.08,-1,170))},hop:true}}', f'{{k:"squirrel",at:{js(U("B",.12,1,170))},hop:true}}', f'{{k:"squirrel",at:{js(U("C",.95,1,180))},hop:true}}']
an += [f'{{k:"deer",path:{js(U("A",.15,1,700)+U("A",.3,1,700))},per:30}}', f'{{k:"deer",path:{js(U("B",.7,1,500)+U("B",.78,1,500))},per:30,ph:0.4}}']
an += [f'{{k:"bear",path:{js(U("B",.45,-1,550)+U("B",.55,-1,550))},per:34}}']
an += [f'{{k:"elk",path:{js(U("C",.1,-1,900)+U("C",.2,-1,900))},per:36}}', f'{{k:"elk",path:{js(U("C",.12,-1,1150)+U("C",.22,-1,1150))},per:36,ph:0.3}}']
an += [f'{{k:"fox",path:{js(U("C",.4,1,450)+U("C",.46,1,450))},per:26}}']
an += [f'{{k:"coyote",path:{js(U("C",.3,-1,600)+U("C",.36,-1,600))},per:24,ph:0.5}}']
an += [f'{{k:"bobcat",path:{js(U("C",.55,-1,420)+U("C",.6,-1,420))},per:28}}']
an += [f'{{k:"lion",path:{js(U("B",.85,-1,700)+U("B",.95,-1,700))},per:34,ph:0.2}}']
SC = {'pika': 2.2, 'marmot': 1.8, 'elk': 1.25, 'fox': 1.4, 'bear': 1.7, 'deer': 1.4, 'bobcat': 1.45, 'coyote': 1.35, 'lion': 1.4, 'squirrel': 1.8}
an = [a[:-1] + ',s:%.2f}' % (SC[re.search(r'k:"(\w+)"', a).group(1)] * 0.5) for a in an]
animals_js = '[\n ' + ',\n '.join(an) + '\n]'

TREE = ('if(inLake(x,n)){type=null;}else if(mk<0.25){type="conifer";p=0.05;}else if(g>1.15)type=null;'
        'else if(e>8500){type=tr()<.6?"conifer":null;p=0.1;}'
        'else{type=tr()<.9?"conifer":"shrub";p=0.3+cl*.25;}')
cfg = dict(
    title='Crater Lake: Cleetwood Cove, Watchman Peak and Mount Scott', aria='Crater Lake National Park with the Cleetwood Cove Trail, Watchman Peak and Mount Scott',
    h1='Crater Lake &amp; Cleetwood Cove',
    canyons=[], trails=trails, stops=stops, order=order,
    species=list(species_extra), species_extra=species_extra,
    flora={'A': ['dpen_cl', 'pasque_cl', 'phlox_cl', 'sulph_cl', 'knot_cl'], 'B': ['phlox_cl', 'sulph_cl'], 'C': ['knot_cl', 'sulph_cl', 'hulsea_cl', 'phlox_cl']},
    wild=['squirrel', 'pika', 'marmot', 'deer', 'bear', 'elk', 'fox', 'coyote', 'bobcat', 'lion', 'nutcracker', 'eagle', 'peregrine', 'bluebird'],
    wild_sum={
     'squirrel': ('Golden-mantled ground squirrel', 'One of the most common animals along Rim Drive: like a big chipmunk with no stripes on its face. It perches on rocks along the Mount Scott trail and begs at overlooks; please don’t feed it.'),
     'pika': ('American pika', 'A tiny round-eared relative of rabbits that lives in rocky slopes and forages in nearby meadows. Listen for its sharp squeak in the rock fields on the Watchman and Mount Scott.'),
     'marmot': ('Yellow-bellied marmot', 'A big, chubby ground squirrel that suns on boulders near the rim roads and whistles when alarmed. Drive slowly: the park asks drivers to watch for marmots.'),
     'deer': ('Mule deer', 'The park has both mule deer and black-tailed deer. They browse the forest edges and meadows near the rim at dawn and dusk.'),
     'bear': ('Black bear', 'About 41 black bears live in the park; sightings are most common in late spring and autumn. Keep food in your car and give bears plenty of room.'),
     'elk': ('Elk', 'The largest animals in the park. Herds graze the meadows and open forest below the rim, mostly early and late in the day.'),
     'fox': ('Red fox', 'Rare here: the red foxes of Crater Lake’s high country belong to a montane population related to the Sierra Nevada red fox, one of the rarest mammals in North America; park cameras first photographed one here in 2011. Look for one hunting along Rim Drive at dawn or dusk.'),
     'coyote': ('Coyote', 'A lean gray-tan wild dog, common around Rim Drive. Often heard at night; never feed it.'),
     'bobcat': ('Bobcat', 'A short-tailed spotted cat, common around Rim Drive but shy. You are more likely to see its tracks in snow than the cat itself.'),
     'lion': ('Mountain lion', 'Lives in the park’s forests but is very rarely seen. If you meet one, stand tall, keep children close and back away slowly.'),
     'nutcracker': ('Clark’s nutcracker', 'A gray, black and white crow with a long bill, familiar all along the rim. It pries seeds from whitebark pine cones and buries thousands for winter, planting new pines.'),
     'eagle': ('Bald eagle', 'Nests on the caldera cliffs above the lake. Watch for one soaring over the water or perched on a snag on the rim.'),
     'peregrine': ('Peregrine falcon', 'Nests on the caldera cliffs and dives on other birds over the lake at very high speed.'),
     'bluebird': ('Mountain bluebird', 'A sky-blue thrush of open meadows and pumice flats; it hovers before dropping onto insects.'),
    },
    grid=GRID, step=STEP, dem_b64=b64, tile=TILE, ve=1.6, ridge_ft=RIDGE,
    palette='forest', tree_rule=TREE,
    landmarks=lm, animals_js=animals_js, extra_js=extra_js,
    stop_photos=stop_photos, flower_photos=flower_photos, animal_photos=animal_photos,
    overview=dict(h2='The deepest lake in the United States',
                  p='Crater Lake fills the caldera left when Mount Mazama erupted and collapsed about 7,700 years ago; at 1,943 feet it is the deepest lake in the country. A climbs the Watchman to a 1932 lookout above Wizard Island, B is the steep Cleetwood Cove Trail, the only way down to the water (closed through 2028), and C climbs Mount Scott, the park’s highest peak. Pick a trail to focus the model; click anything on it for a quick note.',
                  numbers='The three trails start miles apart on the rim and share no stops, so every stop is lettered: C3 is the third stop on Trail C. Each is an out-and-back; stop miles count from the trailhead.',
                  wild_h='Wildlife around the rim',
                  note='Crater Lake National Park, Oregon. Status (November 2026): Rim Drive, the North Entrance Road and the road up to Rim Village are closed for winter (they close by November 1 and reopen in stages as the snow melts). Cleetwood Cove Trail is closed for the 2026, 2027 and 2028 seasons for rehabilitation, so there is no lake access and there are no boat tours. Watchman and Mount Scott trails are usually snow-covered from about October to July. Highway 62 stays open; chains or traction tires are required in winter. Terrain from USGS elevation data, stylized; not for navigation.'),
    links={'A': [('Hiking trails · National Park Service', 'https://www.nps.gov/crla/planyourvisit/hiking.htm'), ('Watchman Peak Trail · Crater Lake Institute', 'https://craterlakeinstitute.com/?p=16947'), ('Watchman Lookout Station · Wikipedia', 'https://en.wikipedia.org/wiki/Watchman_Lookout_Station')],
           'B': [('Cleetwood Cove · National Park Service', 'https://www.nps.gov/crla/planyourvisit/cleetwood-cove.htm'), ('Cleetwood Cove Trail and Marina Rehabilitation · NPS', 'https://www.nps.gov/crla/planyourvisit/cleetwood-cove-trail-and-marina-rehabilitation.htm'), ('Current conditions · NPS', 'https://www.nps.gov/crla/planyourvisit/conditions.htm')],
           'C': [('Mount Scott Hike · Oregon Hikers', 'https://www.oregonhikers.org/field_guide/Mount_Scott_Hike'), ('Hiking trails · National Park Service', 'https://www.nps.gov/crla/planyourvisit/hiking.htm')]},
    viewaz={'all': 0.35, 'A': 0.35, 'B': 0.35, 'C': 0.35},
    zoomcap={'A': 12.0, 'B': 12.0, 'C': 8.0},
)
OUT = '/home/claude/site/out/crater-lake-cleetwood/index.html'
json.dump({k: {'mi': R[k]['mi'], 'gain': R[k]['gain'], 'lo': R[k]['lo'], 'hi': R[k]['hi']} for k in R} | {'stops': {s['id']: (s['name'], s['x'], s['n']) for s in stops}},
          open('craterlake/stats.json', 'w'))
os.makedirs(os.path.dirname(OUT), exist_ok=True)
print(build(cfg, OUT))
h = open(OUT).read(); n0 = len(h)
h = h.replace('/* ================= landmarks + waterfall ================= */', LAKE_FN + '/* ================= landmarks + waterfall ================= */', 1)
h = h.replace('inst[type].push({v,s:0.8+tr()*0.45,', 'inst[type].push({v,s:(0.8+tr()*0.45)*0.6,', 1)
h = h.replace('if(!sp.rule(creekDist(x,n),e,g,s))continue;', 'if(inLake(x,n)||!sp.rule(creekDist(x,n),e,g,s))continue;')
print('post', len(h) - n0, h.count('function inLake'), h.count('inLake(x,n)||!sp.rule'))
open(OUT, 'w').write(h)
