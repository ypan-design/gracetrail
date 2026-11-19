from lib import *
from mk_sheet import build
import sys, json, math, os
import numpy as np
from matplotlib.path import Path as MPath

os.chdir('/home/claude/parks')
# origin: McWay Falls / Waterfall Overlook trailhead (Hikespeak 36.1587, -121.67054)
p = Park('mcway', 36.1587, -121.67054)


def fix_sea(p):
    # Ocean cells in the terrain tiles sit at about +1.2 m, so the engine would draw them as land. Rebuild the sea
    # from the OSM coastline (land on the left of the way): sea -1 m, land at least 1.5 m. Closed rings stay land.
    W = [w for w in p.W if w['k'] == 'coastline']
    open_ = [[p.xy(c) for c in w['p']] for w in W if w['p'][0] != w['p'][-1]]
    rings = [[p.xy(c) for c in w['p']] for w in W if w['p'][0] == w['p'][-1]]
    first = [c for c in open_ if not any(math.dist(c[0], d[-1]) < 1 for d in open_)][0]
    chain = list(first); used = [first]
    while True:
        nxt = [c for c in open_ if c not in used and math.dist(c[0], chain[-1]) < 1]
        if not nxt: break
        chain += nxt[0][1:]; used.append(nxt[0])
    print('coast chain', len(used), 'of', len(open_), [round(v) for v in chain[0]], [round(v) for v in chain[-1]])
    a, b = chain[0], chain[-1]
    sea = MPath(chain + [(b[0], -60000), (-60000, -60000), (-60000, 60000), (a[0], 60000)])
    z = p.meta['z']; nn = 2 ** z; H, Wd = p.M.shape
    jj, ii = np.mgrid[0:H, 0:Wd]
    lon = (p.meta['tx0'] + (ii + 0.5) / 256) / nn * 360 - 180
    lat = np.degrees(np.arctan(np.sinh(np.pi * (1 - 2 * (p.meta['ty0'] + (jj + 0.5) / 256) / nn))))
    X = (lon - p.lon0) * p.K; N = (lat - p.lat0) * 364000
    XY = np.column_stack([X.ravel(), N.ravel()])
    s = sea.contains_points(XY).reshape(H, Wd)
    for r in rings:
        s &= ~MPath(r).contains_points(XY).reshape(H, Wd)
    M = p.M.copy(); M[s] = -1.0; M[~s] = np.maximum(M[~s], 1.5)
    p.M = M


fix_sea(p)

LOT = (443, 319)        # day-use parking at McWay Canyon (OSM path/steps end by the lot)
PELTON = (335, 212)     # Pelton Wheel (OSM historic node)
TUN = (-18, 19)         # pedestrian tunnel under Highway 1 (OSM path segment under the road)
FALLS = (-567, -314)    # McWay Falls lip: OSM McWay Creek ends here (Wikipedia 36.15781,-121.67214 = -470,-325)
FV = (-388, 233)        # cliff-edge path facing the falls
WH = (-738, 426)        # end of the Overlook Trail: Waterfall House site (OSM viewpoint -813,444)
SADDLE = (-806, -349)   # Saddle Rock (OSM peak, 15 m)
TH_B = (-6823, 6695)    # Partington Cove gate at the Highway 1 bend (OSM track start; Hikespeak 36.1770,-121.6937)
KIOSK = (-7472, 6327)   # bottom of the fire road: kiosk and junctions (OSM)
PTUN = (-7548, 6165)    # Partington tunnel (OSM path between bridge and cove)
PCOVE = (-7575, 5784)   # Partington Cove landing / point (OSM path end)
PBEACH = (-7813, 6135)  # boulder beach at the mouth of Partington Creek (OSM path end)
PICNIC = (776, 723)     # picnic site (OSM)
CF = (1584, 1560)       # Canyon Falls (end of OSM Canyon Trail)
CJ = (1247, 1134)       # Canyon Trail junction
J1 = (2099, 1635)
LJ = (1393, 3432)       # Ewoldsen loop junction (OSM way ends)
RV = (-40, 2504)        # OSM viewpoint on the west half of the loop
TOP = (-167, 4856)
BENCH = (-277, 4304)    # Overlook Trail end, OSM "Bench" viewpoint

R = {}
R['A'] = route_xy(p, LOT, WH, LOT)
R['B'] = route_xy(p, TH_B, PCOVE, KIOSK, PBEACH, TH_B)
R['C'] = route_xy(p, LOT, CF, CJ, LJ, RV, TOP, BENCH, TOP, (1100, 4950), LJ, J1, LOT)
for k in R: Park.smooth_E(R[k], 9); p.describe(R[k], k)

ST = snap_stops(p, R, {
    'LOT': (*LOT, 'AC'),
    'PELTON': (*PELTON, 'A'), 'TUN': (*TUN, 'A'), 'FV': (*FV, 'A'), 'WH': (*WH, 'A'),
    'THB': (*TH_B, 'B'), 'KIOSK': (*KIOSK, 'B'), 'PTUN': (*PTUN, 'B'), 'PCOVE': (*PCOVE, 'B'), 'PBEACH': (*PBEACH, 'B'),
    'PICNIC': (*PICNIC, 'C'), 'CF': (*CF, 'C'), 'LJ': (*LJ, 'C'), 'RV': (*RV, 'C'), 'BENCH': (*BENCH, 'C'),
})
TILE = (-10500, 4800, -3300, 9700)
GRID = (-10800, 5100, -3600, 10000)
if 'plot' in sys.argv:
    from plot import plot
    plot(p, TILE, 'mcway/routes.png', routes=R, stops=ST, title='mcway', grid=1000)
    sys.exit()

STEP = 80
b64, NX, NN = p.dem_b64(*GRID, STEP=STEP)
T_ = p.grid[int((TILE[2] - GRID[2]) / STEP):int((TILE[3] - GRID[2]) / STEP), int((TILE[0] - GRID[0]) / STEP):int((TILE[1] - GRID[0]) / STEP)]
RIDGE = int(round(float(np.percentile(T_[T_ > 10], 75)), -1))
print('grid', NX, NN, NX * NN, p.grid.min(), p.grid.max(), 'p75', RIDGE)
for k, q in dict(FALLS=FALLS, WH=WH, BENCH=BENCH, PCOVE=PCOVE, SADDLE=SADDLE).items(): print(k, round(p.elev(*q)))

S = lambda i: ST[i]
def st(key, trs, name, desc): return dict(id=key, key=key, trails=list(trs), x=S(key)[0], n=S(key)[1], name=name, desc=desc)
stops = [
 st('LOT', 'AC', 'McWay Canyon parking', 'The park’s day-use lot in McWay Canyon, just east of Highway 1, with restrooms, drinking water and picnic tables. Both the Waterfall Overlook and the Ewoldsen trails start here.'),
 st('PELTON', 'A', 'Pelton Wheel', 'In 1932 Hans Ewoldsen, foreman of the Saddle Rock Ranch, set a Pelton wheel in McWay Creek. Its 32-volt generator made the first electric power on the Big Sur coast, for three houses, a blacksmith shop and later a funicular.'),
 st('TUN', 'A', 'Tunnel under Highway 1', 'The path follows McWay Creek down and passes through a short pedestrian tunnel under the highway to the ocean side.'),
 st('FV', 'A', 'McWay Falls view', 'McWay Falls drops about 80 feet from the granite cliff onto the beach of McWay Cove; at high tide it falls straight into the sea. Before a huge 1983 landslide north of the park sent sand into the cove, the falls always met the ocean. The beach, the falls area and Saddle Rock are closed: stay behind the fence.'),
 st('WH', 'A', 'Waterfall House site', 'Lathrop and Hélène Brown, who owned the Saddle Rock Ranch, built a two-story house on this point in 1940, reached by a funicular. Hélène gave the land to the state in 1961, asking that the park honor Julia Pfeiffer Burns, a Big Sur pioneer; the house was taken down in 1965 and the overlook replaced it.'),
 st('THB', 'B', 'Partington Cove trailhead', 'A gate on the ocean side of Highway 1 at a sharp bend in Partington Canyon, about 2 miles north of the park entrance. Park on the wide shoulder; no fee and no trail sign. The Tanbark Trail starts across the road.'),
 st('KIOSK', 'B', 'Kiosk and creek junction', 'The fire road drops about 200 feet in 0.3 mile to an information kiosk near Partington Creek. A short spur heads upstream along the creek; the cove trail turns left over a wooden footbridge, and a path goes straight to the beach.'),
 st('PTUN', 'B', 'Partington tunnel', 'A tunnel through the rock, lined with redwood planks, cut in the late 1800s for John Partington. Tanoak bark from the canyon, valued for tanning leather, was hauled through it to ships in the cove.'),
 st('PCOVE', 'B', 'Partington Cove', 'A fenced ledge with a bench above the small, kelp-filled cove, once a landing where tanbark and redwood were loaded for Santa Cruz and San Francisco. Swimming and climbing on the rocks are unsafe: the surf is strong.'),
 st('PBEACH', 'B', 'Partington Creek beach', 'A short path through brush and blackberry ends at a small boulder-and-sand beach where Partington Creek meets the sea.'),
 st('PICNIC', 'C', 'Redwood picnic area', 'Picnic tables and grills under coast redwoods on McWay Creek, where the Ewoldsen Trail begins. Old- and second-growth redwoods here grow within 100 yards of the shore.'),
 st('CF', 'C', 'Canyon Falls', 'A short side trail leads to Canyon Falls, a moss-lined cascade about 30 feet high, heard before it is seen.'),
 st('LJ', 'C', 'Loop junction', 'The trail splits into its loop above McWay Creek. In recent years the east half has often been closed for repairs, and hikers went out and back on the west half.'),
 st('RV', 'C', 'Coast view', 'Out of the canyon the redwoods give way to chaparral and live oak, and the first ocean views open up over McWay Rocks and the coast.'),
 st('BENCH', 'C', 'Ewoldsen overlook', 'A short spur to a small meadow with a wooden bench, about 1,600 feet above the sea, the high point of the hike, looking down the Big Sur coast.'),
]
stops, order = renumber(p, R, stops)
KEY2ID = {s['key']: s['id'] for s in stops}
print(order, KEY2ID)
trails = [
 dict(id='A', name='Waterfall Overlook Trail', short='McWay Falls', official=0.6, unit='round trip', route='Out and back', time='20–30 min', level='Easy', color='--tA',
      desc='A short, nearly level path from the parking lot down McWay Creek, through a tunnel under Highway 1, and out along the cliff above McWay Cove to the overlook on the old Waterfall House site. The view of the 80-foot falls is from behind the fence; there is no beach access.', anchors=p.anchors(R['A'])),
 dict(id='B', name='Partington Cove Trail', short='Partington Cove', official=1.25, unit='round trip', route='Out and back', time='45 min–1 hr', level='Moderate', color='--tB',
      desc='Two miles north of the main entrance, a steep fire road drops into Partington Canyon. At the bottom, cross the creek on a footbridge and walk through a plank-lined tunnel to a ledge over Partington Cove, a tanbark landing in the 1800s; a side path leads to the beach at the creek mouth. The climb back up is the hard part.', anchors=p.anchors(R['B'])),
 dict(id='C', name='Ewoldsen Trail', short='Ewoldsen', official=4.8, unit='loop', route='Lollipop loop', time='2.5–3.5 hr', level='Strenuous', color='--tC',
      desc='Named for Hans Ewoldsen, the ranch foreman. From the picnic area the trail follows McWay Creek through redwoods, with a side trip to Canyon Falls, then climbs out of the canyon into chaparral and loops over the ridge, with a spur to an ocean overlook at about 1,600 feet. Closed for now, with the other trails east of Highway 1.', anchors=p.anchors(R['C'])),
]

pa = place_along
A_ = lambda k, f, s=1, o=300: pa(p, R[k], [f], s, o)[0]
def path(k, f, s=1, o=350, d=0.03): return js(A_(k, f, s, o) + A_(k, f + d, s, o))


def sea_pt(x, n, dx, dn, extra=150):
    # walk from (x, n) in direction (dx, dn) to the first sea cell, then a bit further out
    for i in range(1, 200):
        q = (x + dx * 20 * i, n + dn * 20 * i)
        if p.elev(*q) < 0: return [round(q[0] + dx * extra), round(q[1] + dn * extra)]
    return [x, n]


OT1 = sea_pt(-500, 100, -0.7, -0.7, 250)
OT2 = sea_pt(-7500, 5900, -0.8, -0.6, 200)
print('otters', OT1, OT2)
an = []
an += [f'{{k:"deer",path:{path("C",.18,-1,420)},per:28}}', f'{{k:"deer",path:{path("C",.72,1,450)},per:30,ph:0.4}}']
an += [f'{{k:"squirrel",at:{js(A_("B",.18,1,200))},hop:true}}', f'{{k:"squirrel",at:{js(A_("C",.45,-1,260))},hop:true}}']
an += [f'{{k:"bobcat",path:{path("C",.86,-1,380)},per:32,ph:0.2}}']
an += [f'{{k:"turkey",at:{js(A_("C",.55,-1,380))},flock:3}}']
an += [f'{{k:"quail",at:{js(A_("B",.42,-1,220))},flock:3}}']
an += [f'{{k:"otter",at:{js(OT1)}}}', f'{{k:"otter",at:{js(OT2)},ph:0.5}}']
animals_js = '[\n ' + ',\n '.join(an) + '\n]'

species_extra = {
 'sorrel': 'sorrel:{name:"Redwood sorrel",latin:"Oxalis oregana",color:"#F2C9D6",shape:"cup",bloom:[3,4,5,6,7,8],sum:"Clover-like leaves that carpet the redwood floor along McWay Creek and fold down in direct sun, with small pink-white flowers.",rule:(d,e,g,s)=>d<500&&s<0.2&&e>30}',
 'wcolumbine': 'wcolumbine:{name:"Western columbine",latin:"Aquilegia formosa",color:"#D9452F",shape:"tube",bloom:[4,5,6,7],sum:"Nodding red-and-yellow flowers on moist, shady banks along the creeks; hummingbirds feed on them.",rule:(d,e,g,s)=>d<400&&e>40}',
 'douglasiris': 'douglasiris:{name:"Douglas iris",latin:"Iris douglasiana",color:"#7B6FD0",shape:"cup",bloom:[3,4,5],sum:"A coastal iris with lavender to purple flowers veined in white, in clumps on grassy bluffs and open slopes in spring.",rule:(d,e,g,s)=>e>20&&e<1200&&g<0.7&&d>150}',
 'ceanothus': 'ceanothus:{name:"Blueblossom",latin:"Ceanothus thyrsiflorus",color:"#8C86D9",shape:"dome",bloom:[3,4,5],sum:"A coastal wild lilac covered in fragrant clusters of pale blue flowers in spring, on the chaparral slopes the Ewoldsen Trail climbs through.",rule:(d,e,g,s)=>s>0.0&&d>250&&e>200}',
}
species = ['fuchsia', 'monkey', 'yucca'] + list(species_extra)

lm = f'''  gate({LOT[0] + 30},{LOT[1] + 40},0.5);gate({TH_B[0] - 40},{TH_B[1] - 30},-0.3);
  // McWay Falls: drops west from the cliff lip onto the beach of McWay Cove (OSM creek mouth), drawn tall so it reads
  {{const top=G({FALLS[0]},{FALLS[1]}),F=G({FALLS[0] - 60},{FALLS[1]});const h=Math.max(top.y-F.y,0.6)+2.6;
  const wf=new THREE.Group();wf.position.copy(F);wf.rotation.y=-Math.PI/2;wf.scale.setScalar(0.5);world.add(wf);
  const fallTex=stripeTex("#E4F6F6","#FFFFFF",64,128,22,9,14);fallTex.repeat.set(1,1.6);
  const fallMat=new THREE.MeshBasicMaterial({{map:fallTex,side:THREE.DoubleSide}});
  const pl=new THREE.Mesh(new THREE.PlaneGeometry(0.9,h),fallMat);pl.position.set(0,h/2,-0.55);wf.add(pl);
  part(wf,ico,PAL.rockDeep,-1.35,h*0.45,-1.0,0.9,h*0.55,1.0);part(wf,ico,PAL.rock,1.35,h*0.4,-1.0,0.9,h*0.5,1.0);part(wf,ico,PAL.rockDeep,0,h+0.1,-1.2,1.3,0.6,1.0);
  part(wf,new THREE.CylinderGeometry(1,1,0.06,18),"#BFE6EA",0,0.05,0.3,1.3,1,1.0,1.04,false);
  const rings=[];for(let i=0;i<3;i++){{const rg=new THREE.Mesh(new THREE.RingGeometry(0.5,0.62,24),new THREE.MeshBasicMaterial({{color:"#FFFFFF",transparent:true,side:THREE.DoubleSide}}));rg.rotation.x=-Math.PI/2;rg.position.set(0,0.1,0.1);wf.add(rg);rings.push(rg);}}
  const mist=[];for(let i=0;i<7;i++){{const m=new THREE.Mesh(new THREE.SphereGeometry(0.2,8,6),new THREE.MeshBasicMaterial({{color:"#FFFFFF",transparent:true}}));wf.add(m);mist.push({{m,ph:i/7,x:(i%3-1)*0.4}});}}
  // Canyon Falls: smaller cascade in the side canyon (end of the OSM Canyon Trail), facing down-canyon (southwest)
  const cf=new THREE.Group();cf.position.copy(G({CF[0] + 20},{CF[1] + 20}));cf.rotation.y=Math.atan2(-0.7,0.7);cf.scale.setScalar(0.6);world.add(cf);
  const pl2=new THREE.Mesh(new THREE.PlaneGeometry(0.55,2.4),fallMat);pl2.position.set(0,1.2,-0.4);cf.add(pl2);
  part(cf,ico,PAL.rockDeep,-0.8,1.1,-0.6,0.6,1.3,0.6);part(cf,ico,PAL.rock,0.8,1.0,-0.6,0.6,1.2,0.6);part(cf,ico,"#5E7A4A",0,2.5,-0.7,0.9,0.4,0.6);
  anim.water={{fallTex,rings,mist}};}}
  // Saddle Rock: the rock knob at the mouth of McWay Cove (OSM peak), exaggerated
  {{const q=G({SADDLE[0]},{SADDLE[1]});const g=new THREE.Group();g.position.copy(q);g.rotation.y=0.4;g.scale.setScalar(0.45);world.add(g);
   part(g,ico,"#8A8274",0,0.9,0,2.0,1.6,1.4);part(g,ico,"#7A7266",1.3,0.7,0.2,1.1,1.2,1.0);part(g,ico,"#958C7E",-1.2,0.6,-0.2,1.0,1.0,0.9);part(g,ico,"#6E675C",0.3,2.0,0.1,0.9,0.7,0.8);}}
  // pedestrian tunnel under Highway 1: concrete portals on both sides of the road
  {{const g=new THREE.Group();g.position.copy(G({TUN[0]},{TUN[1]}));g.rotation.y=0.15;world.add(g);g.scale.setScalar(0.4);
   [-1.1,1.1].forEach(dx=>{{part(g,box,"#CFC8BA",dx,0.7,-0.75,0.35,1.4,0.4,1.06);part(g,box,"#CFC8BA",dx,0.7,0.75,0.35,1.4,0.4,1.06);part(g,box,"#BDB5A6",dx,1.55,0,0.4,0.35,1.95,1.06);part(g,box,"#2A2622",dx,0.65,0,0.08,1.2,1.1,0);}});
   part(g,box,"#7A746A",0,1.78,0,2.6,0.12,2.4,1.04);}}
  // Pelton wheel house on McWay Creek (OSM node)
  {{const g=new THREE.Group();g.position.copy(G({PELTON[0]},{PELTON[1]}));g.rotation.y=0.6;world.add(g);g.scale.setScalar(0.42);
   part(g,box,"#8C6845",0,0.55,0,1.4,1.1,1.0,1.05);const r=part(g,roof,"#6E5A48",0,1.35,0,1.0,0.6,1.05,1.06);rot(r,0,Math.PI/2,0);
   const w=part(g,new THREE.TorusGeometry(0.55,0.09,6,16),"#5C5650",0.95,0.6,0,1,1,1,1.05);rot(w,0,Math.PI/2,0);part(g,cyl,"#5C5650",0.95,0.6,0,0.05,0.5,0.05,0);}}
  // Waterfall House site: stone terrace of the 1940 house, now the overlook, with a bench
  {{const q=G({WH[0] - 25},{WH[1] + 10});const g=new THREE.Group();g.position.copy(q);g.rotation.y=0.55;world.add(g);g.scale.setScalar(0.45);
   part(g,box,"#B9AE9A",0,0.25,0,2.6,0.5,1.8,1.05);part(g,box,"#A39782",0,0.75,-0.85,2.6,0.5,0.15,1.05);part(g,box,"#A39782",-1.25,0.75,0,0.15,0.5,1.8,1.05);
   part(g,box,"#9C7653",0.4,0.72,0.3,1.0,0.08,0.32,1.06);part(g,box,"#9C7653",0.4,0.95,0.15,1.0,0.35,0.06,1.06);}}
  // Partington tunnel: a rock knob with a plank-lined opening, trail runs north-south through it
  {{const q=G({PTUN[0]},{PTUN[1]});const g=new THREE.Group();g.position.copy(q);g.rotation.y=0.25;world.add(g);g.scale.setScalar(0.6);
   part(g,ico,"#8A8274",-1.1,0.9,0,1.2,1.3,1.6);part(g,ico,"#7E776B",1.1,0.9,0,1.2,1.3,1.6);part(g,ico,"#958C7E",0,1.9,0,1.6,0.8,1.6);
   part(g,box,"#9C7653",0,0.65,0,1.0,1.3,2.2,1.05);part(g,box,"#2A2622",0,0.6,0,0.75,1.1,2.25,0);}}
  // Partington Cove: fenced ledge with a bench
  bench({PCOVE[0] + 10},{PCOVE[1] + 20},0.4);
  [[-60,40],[-20,70],[20,95]].forEach(([dx,dn])=>{{const q=G({PCOVE[0]}+dx,{PCOVE[1]}+dn);part(world,box,"#8A6A4A",q.x,q.y+0.35,q.z,0.07,0.7,0.07,0);part(world,box,"#9C7653",q.x,q.y+0.6,q.z,0.9,0.05,0.05,0).rotation.y=0.6;}});
  // Ewoldsen overlook bench
  bench({BENCH[0]},{BENCH[1]},2.6);
'''

canyons = []
def ids_of(nm): return [w['id'] for w in p.W if w.get('n') == nm and w['k'] == 'stream']
for nm, minor in (('McWay Creek', False), ('Partington Creek', False)):
    for i, wid in enumerate(ids_of(nm)):
        c = p.creek([wid], GRID, minor=minor)
        if c: canyons.append(dict(id=f"{nm.split()[0].lower()}{i}", **c))
for i, wid in enumerate(['72968451', '73165134', '73180823']):
    c = p.creek([wid], GRID, minor=True)
    if c: canyons.append(dict(id=f"trib{i}", **c))
print('creeks', len(canyons))

TREE_RULE = '''if(mk<0.25||e<14){type=null;}
    else if(cd<260){type=tr()<.75?"conifer":"syc";p=0.3;}
    else if(g>1.1)type=null;
    else if(south<-0.1){type=tr()<.55?"oak":"shrub";p=0.07+cl*.1;}
    else{type="shrub";p=0.035;}'''

PH = json.load(open('mcway/photos_cfg.json')) if os.path.exists('mcway/photos_cfg.json') else {}
stop_photos = {KEY2ID[k]: v for k, v in PH.get('stop', {}).items() if k in KEY2ID}
cfg = dict(
    title='McWay Falls', aria='McWay Falls, Partington Cove and the Ewoldsen Trail in Julia Pfeiffer Burns State Park, Big Sur', h1='McWay Falls',
    canyons=canyons, trails=trails, stops=stops, order=order,
    species=species, species_extra=species_extra,
    flora={'A': ['fuchsia', 'douglasiris', 'monkey'], 'B': ['douglasiris', 'monkey', 'fuchsia'], 'C': ['sorrel', 'wcolumbine', 'ceanothus', 'yucca', 'monkey']},
    wild=['deer', 'squirrel', 'bobcat', 'turkey', 'quail', 'otter', 'condor', 'eagle', 'peregrine', 'hawk', 'vulture', 'steller', 'gull'],
    wild_sum={
     'deer': ('Black-tailed deer', 'The coastal form of the mule deer. Browses along the Ewoldsen Trail and the canyon edges early and late in the day.'),
     'squirrel': ('California ground squirrel', 'Common around the parking lot, picnic tables and overlook paths. Please don’t feed it.'),
     'turkey': ('Wild turkey', 'Small flocks forage in the oak and grassland openings above McWay Canyon.'),
     'quail': ('California quail', 'California’s state bird. Coveys run through the coastal scrub along the bluffs.'),
     'otter': ('Southern sea otter', 'Rare here: a threatened subspecies that lives only on the central California coast, and the park lies inside the California Sea Otter State Game Refuge. Look for otters floating on their backs in the kelp off McWay and Partington coves.'),
     'condor': ('California condor', 'Rare here: one of the rarest birds in North America, listed as endangered for the park; Big Sur condors are released and tracked by the Ventana Wildlife Society, a park partner. With 9-foot wings and numbered tags, they ride the updrafts along the cliffs and ridges.'),
     'bobcat': ('Bobcat', 'Seen now and then along the Ewoldsen Trail, in the scrub and the edges of the redwood canyon, mostly early and late in the day.'),
     'eagle': ('Bald eagle', 'Listed among the park’s birds; watch for the white head and tail over the coast and ridges, especially in winter.'),
     'hawk': ('Red-tailed hawk', 'The common big hawk of the Big Sur coast, circling over the bluffs and chaparral on rising air.'),
     'gull': ('Western gull', 'The big, dark-backed gull of the Pacific coast; nests and rests on the rocks around McWay and Partington coves.'),
     'steller': ('Steller’s jay', 'The dark-crested blue jay of the redwoods. Loud and bold around the picnic area and along McWay Creek.'),
     'vulture': ('Turkey vulture', 'Teeters on tilted wings low over the bluffs and canyon slopes, often below the overlooks.'),
     'peregrine': ('Peregrine falcon', 'Nests on the sea cliffs of the park. Watch for a fast, sharp-winged falcon diving at seabirds along the coast.'),
    },
    grid=GRID, step=STEP, dem_b64=b64, tile=TILE, ve=1.5, ridge_ft=RIDGE,
    tree_rule=TREE_RULE, ocean=True, rock_all_aspects=True,
    landmarks=lm, animals_js=animals_js,
    overview=dict(h2='An 80-foot waterfall on the Big Sur coast',
                  p='Julia Pfeiffer Burns State Park is on Highway 1, 37 miles south of Carmel, where redwood canyons run down to granite cliffs. Its best-known sight, McWay Falls, drops 80 feet onto a cove beach. A is the short Waterfall Overlook Trail to the falls view, B is Partington Cove, two miles north, down a canyon and through a tunnel to an old tanbark landing, and C is the Ewoldsen Trail, a redwood-to-chaparral loop climbing to an ocean overlook. <b>Closed as of November 18, 2026:</b> State Parks lists the park closed because Highway 1 is closed from Nepenthe to Ragged Point (to be reassessed November 19), and the trails east of the highway, including Ewoldsen, remain closed after the 2026 Timber Fire. Pick a trail to focus the model; click anything on it for a quick note.',
                  numbers='The McWay Canyon parking lot is shared by A and C, so it carries a plain number. Every other stop belongs to one trail and carries its letter: B3 is the third stop on Trail B.',
                  wild_h='Wildlife at Julia Pfeiffer Burns',
                  note='Julia Pfeiffer Burns State Park, Highway 1, Big Sur, 37 miles south of Carmel and 12 miles south of Pfeiffer Big Sur State Park. Open 8 am to sunset when the highway is open; day use $10 per vehicle. No dogs on trails. The beach, Saddle Rock and the McWay Falls area beyond the fences are closed, and violators can be cited and arrested. Partington Cove has no lot or fee: park on the highway shoulder at the bend 2 miles north. Status (November 18, 2026): closed while Highway 1 is closed from Nepenthe to Ragged Point; backcountry trails east of Highway 1 closed until further notice. Check State Parks and Caltrans QuickMap before driving. Terrain from USGS elevation data, stylized; not for navigation.'),
    links={'A': [('Julia Pfeiffer Burns State Park · CA State Parks', 'https://www.parks.ca.gov/?page_id=578'), ('McWay Falls · Wikipedia', 'https://en.wikipedia.org/wiki/McWay_Falls'), ('Overlook Trail to McWay Falls · Hikespeak', 'https://www.hikespeak.com/trails/mcway-falls-big-sur/')],
           'B': [('Partington Cove · Modern Hiker', 'https://modernhiker.com/hike/partington-cove/'), ('Partington Cove Trail · Hikespeak', 'https://www.hikespeak.com/trails/partington-cove-big-sur/')],
           'C': [('Ewoldsen Loop · Hiking Project', 'https://hikingproject.com/trail/7003425/ewoldsen-loop'), ('Monterey District park status · CA State Parks', 'https://www.parks.ca.gov/?page_id=21284')]},
    extra_js='TRAILS.forEach(T=>{const g={A:50,B:275,C:1430}[T.id];if(g)T.gain=g;});\n// out-and-back: report the outbound mile for a stop\nmileOf=function(T,x,n){let b=null;T.pts.forEach(p=>{const d=Math.hypot(p.x-x,p.n-n);if(!b||d<b.d)b={d,m:p.m,e:p.e};});if(!b||b.d>=260)return null;const f=T.pts.find(p=>Math.hypot(p.x-x,p.n-n)<b.d+60);return {d:b.d,m:f.m,e:f.e};};',
    viewaz={'all': -0.75, 'A': -0.75, 'B': -0.3, 'C': -0.6},
    zoomcap={'A': 5.0, 'B': 4.5, 'C': 3.0},
    stop_photos=stop_photos, flower_photos=PH.get('flower', {}), animal_photos=PH.get('animal', {}),
)
json.dump({k: {'mi': R[k]['mi'], 'gain': R[k]['gain'], 'lo': R[k]['lo'], 'hi': R[k]['hi']} for k in R}, open('mcway/stats.json', 'w'))
OUT = '/home/claude/site/out/big-sur-mcway-falls/index.html'
os.makedirs(os.path.dirname(OUT), exist_ok=True)
print(build(cfg, OUT))
from marine import inject
inject(OUT, ['whale', 'sealion', 'seal', 'pelican'], {
    'whale': 'Gray whales pass close to this coast on their migration between Alaska and Baja, mostly winter and spring, sometimes near the mouth of McWay Cove. Look for the spout from the overlook.',
    'sealion': 'California sea lions rest on the offshore rocks and swim past the coves, barking.',
    'seal': 'Harbor seals haul out on rocks along this shore and bob up just beyond the surf.',
    'pelican': 'Brown pelicans glide in lines just above the waves and dive headfirst for fish.'},
    names={'whale': 'Gray whale', 'sealion': 'California sea lion', 'seal': 'Harbor seal'})
