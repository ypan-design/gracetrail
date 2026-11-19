from lib import *
from mk_sheet import build
import sys, json, math, os, re
import numpy as np
os.chdir('/home/claude/parks')
# origin: Fern Canyon trailhead at the end of Davison Road (Hiking Project 41.400446, -124.065623)
p = Park('ferncanyon', 41.4004, -124.0656)
# DEM note: the AWS terrarium tiles have a 150-200 ft step along a source seam at x~2190 ft (same at z13 and z14).
# ferncanyon_usgs.py rebuilt the npy on land from USGS 3DEP (exportImage, same tile grid), keeping terrarium
# bathymetry offshore.
LOT = (0, 120)          # day-use lot at the end of Davison Road (OSM road end 13,86; picnic sites)
MOUTH = (440, 1179)     # canyon mouth: OSM Fern Canyon Loop Trail starts here; west stairs (OSM steps 505,1286)
MID = (1000, 780)       # canyon floor, Home Creek
JIJ = (1600, 719)       # head of the canyon walk, junction with the James Irvine Trail (OSM)
RIM = (1000, 1050)      # James Irvine Trail on the north rim
FRJ = (2725, 786)       # Friendship Ridge / James Irvine junction (OSM way ends)
PRAIRIE = (330, 5000)   # Coastal Trail across the Gold Bluffs prairie
WRC = (1990, 12680)     # West Ridge Trail meets the Coastal Trail at Butler Creek (OSM)
WRF = (4407, 8473)      # West Ridge / Friendship Ridge junction (OSM)
VC = (11584, -13244)    # Prairie Creek Visitor Center (OSM)
JITH = (11397, -12731)  # James Irvine Trail start behind the visitor center (OSM)
MRJ = (10232, -11114)   # Miner's Ridge Trail junction (OSM)
GOD = (7815, -8337)     # James Irvine Trail along Godwood Creek (OSM way node)
CLJ = (4777, -4545)     # Clintonia Trail junction (OSM)
R = {}
R['A'] = route_xy(p, LOT, MOUTH, MID, JIJ, RIM, (505, 1240), LOT)
R['B'] = route_xy(p, LOT, MOUTH, PRAIRIE, WRC, (4245, 11991), WRF, FRJ, JIJ, MID, MOUTH, LOT)
OUTC = [VC, JITH, MRJ, GOD, CLJ, (3160, -1251), FRJ, JIJ, MID, MOUTH, LOT]
R['C'] = route_xy(p, *(OUTC + OUTC[::-1][1:]))
for k in R: Park.smooth_E(R[k], 9); p.describe(R[k], k)
ST = snap_stops(p, R, {
 'LOT': (*LOT, 'ABC'), 'MOUTH': (*MOUTH, 'ABC'), 'MID': (*MID, 'ABC'), 'JIJ': (*JIJ, 'ABC'), 'FRJ': (*FRJ, 'BC'),
 'RIM': (*RIM, 'A'), 'PRAIRIE': (*PRAIRIE, 'B'), 'WRC': (*WRC, 'B'), 'WRF': (*WRF, 'B'), 'FRM': (3600, 3900, 'B'),
 'VC': (*VC, 'C'), 'MRJ': (*MRJ, 'C'), 'GOD': (*GOD, 'C'), 'CLJ': (*CLJ, 'C'),
})
TILE = (-6200, 16400, -17900, 17400)
GRID = (-6500, 16700, -18200, 17700)
if 'plot' in sys.argv:
    from plot import plot
    plot(p, (-1500, 6500, -1500, 13500), 'ferncanyon/routesN.png', routes=R, stops=ST, title='fern north', grid=1000)
    plot(p, (0, 12500, -14000, 2000), 'ferncanyon/routesS.png', routes=R, stops=ST, title='fern south', grid=1000)
    plot(p, (-800, 2800, -400, 1800), 'ferncanyon/routesA.png', routes=R, stops=ST, title='fern A', grid=200)
    sys.exit()
STEP = 150
b64, NX, NN = p.dem_b64(*GRID, STEP=STEP)
T_ = p.grid[int((TILE[2] - GRID[2]) / STEP):int((TILE[3] - GRID[2]) / STEP), int((TILE[0] - GRID[0]) / STEP):int((TILE[1] - GRID[0]) / STEP)]
RIDGE = int(round(float(np.percentile(T_[T_ > 10], 75)), -1))
print('grid', NX, NN, NX * NN, p.grid.min(), p.grid.max(), 'p75', RIDGE)
S = lambda i: ST[i]
def st(key, trs, name, desc): return dict(id=key, key=key, trails=list(trs), x=S(key)[0], n=S(key)[1], name=name, desc=desc)
stops = [
 st('LOT', 'ABC', 'Fern Canyon trailhead', 'The day-use parking area at the end of Davison Road, behind Gold Bluffs Beach, with vault toilets and picnic tables. From May 15 to September 15 a free parking reservation is needed to drive here; the $12 day-use fee is cash or check.'),
 st('MOUTH', 'ABC', 'Mouth of Fern Canyon', 'Home Creek leaves the canyon here and crosses the meadow to the beach. Many visitors just walk a quarter mile in and back from here; a set of stairs on the north side climbs to the James Irvine Trail.'),
 st('MID', 'ABC', 'Fern Canyon', 'Home Creek has cut a narrow canyon here, its walls about 50 feet high and hung with five-finger, sword, deer, lady and chain ferns. There is no dry path: you wade the creek and climb over logs. Small footbridges go in only in summer. Scenes for The Lost World: Jurassic Park were filmed here.'),
 st('JIJ', 'ABC', 'Upper canyon stairs', 'At the head of the canyon walk, steps climb out of Home Creek to the James Irvine Trail. As of November 2026 the easternmost stairs are closed for construction; the western stairs near the canyon mouth stay open.'),
 st('FRJ', 'BC', 'Friendship Ridge junction', 'The Friendship Ridge Trail leaves the James Irvine Trail here and climbs north along the ridge.'),
 st('RIM', 'A', 'Canyon rim', 'The loop comes back along the James Irvine Trail above the canyon, then drops down the western stairs to the canyon mouth.'),
 st('PRAIRIE', 'B', 'Gold Bluffs prairie', 'North of Fern Canyon the Coastal Trail runs flat across grassland between the bluffs and the beach. Roosevelt elk graze here, often close to the trail; stay at least 25 yards away.'),
 st('WRC', 'B', 'West Ridge Trail at Butler Creek', 'Near Butler Creek the West Ridge Trail turns inland from the Coastal Trail and climbs steeply through fern and brush onto the ridge.'),
 st('WRF', 'B', 'West Ridge and Friendship Ridge', 'On the ridge top the loop turns south onto the Friendship Ridge Trail, about 3 miles of mostly gradual descent through redwood forest. This is the high part of the hike, a little over 800 feet.'),
 st('FRM', 'B', 'Friendship Ridge', 'The trail drops from high-slope redwood forest toward sea level. The park notes that elk are regularly seen along it.'),
 st('VC', 'C', 'Prairie Creek Visitor Center', 'The James Irvine Trail starts behind the visitor center and crosses Prairie Creek on a footbridge. No reservation is needed to hike to Fern Canyon from here; full-day parking is limited, with more along the parkway.'),
 st('MRJ', 'C', 'Miner’s Ridge junction', 'The Miner’s Ridge Trail splits off here, following the route gold miners used in the mid-1800s to reach Gold Bluffs Beach. As of November 2026 it is blocked by a large downed tree just past the Clintonia Trail.'),
 st('GOD', 'C', 'Godwood Creek', 'The trail follows Godwood Creek through old-growth redwoods, crossing it and its side streams on wooden footbridges.'),
 st('CLJ', 'C', 'Clintonia Trail junction', 'The Clintonia Trail, named for the red clintonia that blooms along it in spring, climbs a mile to the Miner’s Ridge Trail. Farther on, near the coast, the redwoods give way to Sitka spruce.'),
]
stops, order = renumber(p, R, stops)
KEY2ID = {s['key']: s['id'] for s in stops}
print(order, KEY2ID)
trails = [
 dict(id='A', name='Fern Canyon Loop', short='Fern Canyon', official=1.0, unit='loop', route='Lollipop loop', time='45–90 min', level='Easy', color='--tA',
      desc='From the lot, walk to the canyon mouth and up the bed of Home Creek between walls draped in ferns, wading and stepping over logs, then climb the stairs to the James Irvine Trail and loop back along the rim. Expect wet feet any time of year; the footbridges are up only in summer.', anchors=p.anchors(R['A'])),
 dict(id='B', name='Friendship Ridge Loop', short='Friendship Ridge', official=8.0, unit='loop', route='Loop', time='4–5 hr', level='Moderate', color='--tB',
      desc='North from Fern Canyon on the flat Coastal Trail across the Gold Bluffs prairie, inland near Butler Creek on the steep West Ridge Trail, then down the long Friendship Ridge through redwoods to the James Irvine Trail and back through Fern Canyon. Elk are often seen on the prairie and the ridge.', anchors=p.anchors(R['B'])),
 dict(id='C', name='James Irvine Trail to Fern Canyon', short='James Irvine', official=10.0, unit='round trip', route='Out and back', time='5–6 hr', level='Moderate', color='--tC',
      desc='The park’s classic redwood walk: from the Prairie Creek Visitor Center along Godwood Creek through old-growth redwoods, then spruce forest near the coast, down into Fern Canyon and out to Gold Bluffs Beach, and back the same way. No parking reservation needed.', anchors=p.anchors(R['C'])),
]
pa = place_along
A_ = lambda k, f, s=1, o=300: pa(p, R[k], [f], s, o)[0]
def path(k, f, s=1, o=350, d=0.02): return js(A_(k, f, s, o) + A_(k, f + d, s, o))
def beach_pt(x, n):
    # walk west from (x, n) to the first spot under 12 ft (the beach)
    for i in range(1, 300):
        q = (x - 20 * i, n)
        if p.elev(*q) < 12: return [round(q[0] + 40), round(q[1])]
    return [x, n]
PL1 = beach_pt(-100, -2600); PL2 = beach_pt(300, 6500); HER = beach_pt(300, 2200)
print('beach', PL1, PL2, HER, [round(p.elev(*q)) for q in (PL1, PL2, HER)])
an = []
an += [f'{{k:"elk",at:{js(A_("B",.17,-1,380))},flock:2,h:1.2}}', f'{{k:"elk",at:{js(A_("B",.30,-1,420))},flock:2,h:-0.6,ph:0.4}}',
       f'{{k:"elk",at:{js(A_("B",.60,1,420))},h:2.2}}', f'{{k:"elk",at:{js([-250, -2300])},flock:2,h:0.4}}',
       f'{{k:"elk",at:{js(A_("C",.02,1,500))},flock:2,h:2.6}}']
an += [f'{{k:"deer",path:{path("C",.10,1,420)},per:30}}', f'{{k:"deer",path:{path("B",.48,-1,420)},per:28,ph:0.4}}']
an += [f'{{k:"bear",path:{path("C",.27,-1,600)},per:40}}']
an += [f'{{k:"squirrel",at:{js(A_("C",.20,1,250))},hop:true}}', f'{{k:"chipmunk",at:{js(A_("C",.14,-1,250))},hop:true}}']
an += [f'{{k:"fox",path:{path("B",.70,1,380)},per:26}}', f'{{k:"coyote",path:{path("B",.08,1,500)},per:30,ph:0.2}}']
an += [f'{{k:"bobcat",path:{path("C",.36,1,420)},per:32,ph:0.6}}']
an += [f'{{k:"snake",path:{path("A",.75,1,160,.04)},per:30}}', f'{{k:"quail",at:{js(A_("B",.22,1,300))},flock:2}}']
an += [f'{{k:"heron",at:{js(HER)},h:1.5}}', f'{{k:"plover",at:{js(PL1)},flock:2}}', f'{{k:"plover",at:{js(PL2)},h:0.8}}']
an += [f'{{k:"salamander",at:{js(A_("A",.38,1,120))},h:0.6}}', f'{{k:"salamander",at:{js(A_("C",.18,-1,200))},h:2.0}}']
an += [f'{{k:"slug",at:{js(A_("C",.08,1,200))},h:0.3}}', f'{{k:"slug",at:{js(A_("B",.80,-1,220))},h:1.9}}']
animals_js = '[\n ' + ',\n '.join(an) + '\n]'
species_extra = {
 'fivefinger': 'fivefinger:{name:"Five-finger fern",latin:"Adiantum aleuticum",color:"#4E8F3E",shape:"fern",bloom:[],sum:"A maidenhair fern with fan-shaped fronds on black wiry stems, the most common fern on the dripping walls of Fern Canyon.",rule:(d,e,g,s)=>d<160&&e<400}',
 'swordfern': 'swordfern:{name:"Western sword fern",latin:"Polystichum munitum",color:"#3F7A3A",shape:"fern",bloom:[],sum:"Big evergreen clumps of stiff, dark fronds that fill the redwood floor along every trail here.",rule:(d,e,g,s)=>e>20&&s<0.3}',
 'sorrel': 'sorrel:{name:"Redwood sorrel",latin:"Oxalis oregana",color:"#F2C9D6",shape:"cup",bloom:[3,4,5,6,7,8],sum:"Clover-like leaves that carpet the redwood floor and fold down in direct sun, with small pink-white flowers.",rule:(d,e,g,s)=>d<500&&s<0.2&&e>30}',
 'clintonia': 'clintonia:{name:"Red clintonia",latin:"Clintonia andrewsiana",color:"#C8366E",shape:"dome",bloom:[4,5,6],sum:"Clusters of small rose-red bells on a tall stalk over broad glossy leaves, in deep redwood shade. The Clintonia Trail is named for its spring show.",rule:(d,e,g,s)=>e>120&&s<0.2&&d>150}',
 'rhododendron': 'rhododendron:{name:"Pacific rhododendron",latin:"Rhododendron macrophyllum",color:"#D86FAE",shape:"dome",bloom:[5,6],sum:"A tall shrub of the redwood understory with big pink flower clusters in late spring.",rule:(d,e,g,s)=>e>150&&d>200}',
 'skunkcabbage': 'skunkcabbage:{name:"Yellow skunk cabbage",latin:"Lysichiton americanus",color:"#E8C93A",shape:"spike",bloom:[2,3,4],sum:"A bright yellow hooded spike and huge leaves in boggy ground; the James Irvine Trail crosses one wet stretch on a boardwalk.",rule:(d,e,g,s)=>d<120&&e>40}',
 'seepmonkey': 'seepmonkey:{name:"Seep monkeyflower",latin:"Erythranthe guttata",color:"#F2C230",shape:"tube",bloom:[3,4,5,6,7,8],sum:"Yellow snapdragon-like flowers with red spots, growing where water seeps from the canyon walls and along the creek.",rule:(d,e,g,s)=>d<100}',
}
species = ['fern'] + list(species_extra)
# canyon floor polyline (mouth -> head of the canyon walk) from the A route, for the wall models
P = np.array(R['A']['pts']); iM = int(np.argmin(np.hypot(P[:, 0] - ST['MOUTH'][0], P[:, 1] - ST['MOUTH'][1]))); iJ = int(np.argmin(np.hypot(P[:, 0] - ST['JIJ'][0], P[:, 1] - ST['JIJ'][1])))
lm_pts = []; last = None
for q in P[iM:iJ + 1]:
    if last is None or math.dist(q, last) > 110: lm_pts.append(q); last = q
WALL = []
for a, b in zip(lm_pts, lm_pts[1:]):
    dx, dn = b[0] - a[0], b[1] - a[1]; l = math.hypot(dx, dn) or 1
    WALL.append([round((a[0] + b[0]) / 2), round((a[1] + b[1]) / 2), round(-dn / l, 3), round(dx / l, 3), round(l)])
print('walls', len(WALL))
SIGNS = [list(S(k)) for k in ('FRJ', 'WRC', 'WRF', 'MRJ', 'CLJ')]
lm = '''  gate(%d,%d,0.3);gate(%d,%d,0.8);
  // Fern Canyon: fern-covered walls on both sides of Home Creek, from the mouth to the head of the canyon walk; drawn tall
  {const W=%s;const S0=100/Math.max(C.x1-C.x0,C.n1-C.n0);
   W.forEach(([x,n,nx,nn,l],i)=>{[1,-1].forEach(sd=>{const q=G(x+nx*sd*80,n+nn*sd*80);const g=new THREE.Group();g.position.copy(q);g.rotation.y=Math.atan2(-nn,nx)+Math.PI/2;world.add(g);
     const L=l*S0*1.15,h=1.3+0.15*((i*7+(sd>0?3:0))%%4);part(g,box,"#6E6450",0,h/2,0,L,h,0.3,1.05);part(g,box,i%%2?"#4E8F3E":"#5E9E4A",0,h*0.55,-sd*0.12,L*0.98,h*0.8,0.06,0);
     for(let k=0;k<3;k++)part(g,new THREE.SphereGeometry(1,7,5),k%%2?"#3F7A3A":"#6BAA55",(k-1)*L*0.32,h*(0.3+0.25*k),-sd*0.16,0.16,0.12,0.06,0);});});
   // seasonal footbridges over Home Creek (summer only)
   [Math.floor(W.length*0.3),Math.floor(W.length*0.65)].forEach(i=>{const [x,n,nx,nn]=W[i];const g=new THREE.Group();g.position.copy(G(x,n,0.04));g.rotation.y=Math.atan2(-nn,nx);world.add(g);part(g,box,"#B08A5E",0,0.06,0,0.5,0.05,0.12,1.06);});}
  // Prairie Creek Visitor Center
  house(%d,%d,1.2,0.5);
  // trail signs at the junctions
  %s.forEach(([x,n],i)=>{const q=G(x+40,n+40);part(world,box,"#6B4F3A",q.x,q.y+0.35,q.z,0.08,0.7,0.08,1.06);const b=part(world,box,"#8A6A4A",q.x,q.y+0.66,q.z,0.5,0.16,0.06,1.06);b.rotation.y=i*0.7;});
''' % (S('LOT')[0] + 40, S('LOT')[1] - 20, VC[0] - 60, VC[1] + 60, js(WALL), VC[0] + 80, VC[1] - 40, js(SIGNS))
canyons = []
for nm in ('Home Creek', 'Godwood Creek', 'Boat Creek', 'Butler Creek', 'Squashan Creek', 'Prairie Creek'):
    ids = [w['id'] for w in p.W if w.get('n') == nm and w['k'] == 'stream']
    for i, wid in enumerate(ids):
        c = p.creek([wid], GRID, minor=nm not in ('Home Creek', 'Prairie Creek'))
        if c: canyons.append(dict(id=f"{nm.split()[0].lower()}{i}", **c))
print('creeks', len(canyons))
TREE_RULE = ('if(mk<0.25||e<18){type=null;}\n'
             '    else if(e<70&&g<0.35){type=tr()<.2?"shrub":null;p=0.03;}\n'
             '    else if(cd<220){type=tr()<.6?"conifer":"syc";p=0.3;}\n'
             '    else{type="conifer";p=0.17+cl*.1;}')
PH = json.load(open('ferncanyon/photos_cfg.json')) if os.path.exists('ferncanyon/photos_cfg.json') else {}
stop_photos = {KEY2ID[k]: v for k, v in PH.get('stop', {}).items() if k in KEY2ID}
SUM = {
 'elk': ('Roosevelt elk', 'Rare here: California’s Roosevelt elk fell to as few as 15 animals by 1925; protected herds like those at Gold Bluffs Beach and Prairie Creek helped bring them back to more than 1,000. Look on the Gold Bluffs prairie, around the Fern Canyon lot and along Friendship Ridge, and stay 25 yards away, farther in calving season (May–June) and the rut (late August–October).'),
 'deer': ('Black-tailed deer', 'The coastal form of the mule deer. Browses at forest edges along the James Irvine Trail and the ridges, early and late in the day.'),
 'bear': ('Black bear', 'Black bears live in the redwood forest here but are seldom seen. Store food properly and never approach one.'),
 'squirrel': ('Douglas’s squirrel', 'A small red squirrel of the conifer forest that chatters loudly from the trunks along the James Irvine Trail.'),
 'chipmunk': ('Shadow chipmunk', 'A small, dark chipmunk of the redwood floor, darting across logs near the visitor center end of the trail.'),
 'fox': ('Gray fox', 'A grizzled gray fox with rusty sides that can climb trees; mostly out at dusk and night, sometimes seen on the trails at dawn.'),
 'coyote': ('Coyote', 'Hunts voles in the grassland behind Gold Bluffs Beach, mostly early and late in the day.'),
 'bobcat': ('Bobcat', 'A short-tailed wild cat of the forest edges, seen now and then on quiet trails early in the morning.'),
 'snake': ('Common garter snake', 'A striped, harmless snake of wet meadows and creek edges, often sunning near Home Creek.'),
 'quail': ('California quail', 'California’s state bird. Coveys run through the brush at the edge of the Gold Bluffs prairie.'),
 'heron': ('Great blue heron', 'Stalks fish and voles where Home Creek crosses the meadow and in the wet grass behind the beach.'),
 'steller': ('Steller’s jay', 'The dark-crested blue jay of the redwoods, loud and bold around the Fern Canyon picnic tables and the visitor center.'),
 'raven': ('Common raven', 'Big black birds patrolling the beach and the parking areas; they will open unattended bags.'),
 'osprey': ('Osprey', 'A fish hawk that hunts the surf line and the creek mouths along Gold Bluffs Beach, mostly spring to fall.'),
 'vulture': ('Turkey vulture', 'Teeters on raised wings low over the bluffs and the prairie, spring through fall.'),
 'gull': ('Western gull', 'The big dark-backed gull of the Pacific coast, resting on Gold Bluffs Beach and at the creek mouths.'),
 'peregrine': ('Peregrine falcon', 'Listed among the park’s birds; hunts along the coast in fast dives.'),
 'swift': ('Marbled murrelet', 'Rare here: an endangered seabird that feeds at sea but nests high on mossy limbs of old-growth redwoods like those along the James Irvine Trail. It flies inland at dawn; you are more likely to hear its sharp keer call than see it.'),
}
cfg = dict(
    title='Fern Canyon · Prairie Creek Redwoods', aria='Fern Canyon, the Friendship Ridge Loop and the James Irvine Trail in Prairie Creek Redwoods State Park', h1='Fern Canyon',
    canyons=canyons, trails=trails, stops=stops, order=order,
    species=species, species_extra=species_extra,
    flora={'A': ['fivefinger', 'seepmonkey', 'fern', 'swordfern'], 'B': ['swordfern', 'sorrel', 'fern', 'fivefinger', 'seepmonkey'], 'C': ['sorrel', 'clintonia', 'rhododendron', 'skunkcabbage', 'swordfern', 'fivefinger']},
    wild=['elk', 'deer', 'bear', 'squirrel', 'chipmunk', 'fox', 'coyote', 'bobcat', 'snake', 'quail', 'heron', 'steller', 'raven', 'osprey', 'vulture', 'gull', 'peregrine', 'swift'],
    wild_sum=SUM,
    grid=GRID, step=STEP, dem_b64=b64, tile=TILE, ve=2.2, ridge_ft=RIDGE,
    palette='forest', tree_rule=TREE_RULE, ocean=True,
    landmarks=lm, animals_js=animals_js,
    overview=dict(h2='A canyon of ferns behind Gold Bluffs Beach',
                  p='In Prairie Creek Redwoods State Park, part of Redwood National and State Parks, Home Creek has cut a narrow canyon with fern-covered walls about 50 feet high just before it reaches the beach. A is the short Fern Canyon Loop from the end of Davison Road, B the Friendship Ridge Loop up the coast and back over the ridge, and C the James Irvine Trail, which comes about 4.5 miles through old-growth redwoods from the Prairie Creek Visitor Center. Pick a trail to focus the model; click anything on it for a quick note.',
                  numbers='The Fern Canyon trailhead and the canyon stops are on all three hikes, and Friendship Ridge junction is on B and C, so those carry plain numbers. Other stops belong to one trail and carry its letter: B3 is the third stop on Trail B. C is a round trip, with stop mileage counted on the way out.',
                  wild_h='Wildlife at Fern Canyon',
                  note='Prairie Creek Redwoods State Park, Orick, California. Fern Canyon trailhead: end of Davison Road, an 8-mile single-lane gravel road off Highway 101 about 3 miles north of Orick, with two stream crossings (high clearance recommended; no trailers or vehicles over 24 feet). Day use $12 per vehicle, cash or check; free parking reservation required May 15 to September 15. No dogs on trails. Status (November 19, 2026): Fern Canyon and Davison Road open; the footbridges are out for the season, so expect ankle- to knee-deep water; the easternmost stairs between Fern Canyon and the James Irvine Trail are closed for construction; the Miner’s Ridge Trail is blocked by a downed tree; the Newton B. Drury Scenic Parkway has been closed since November 17 for high winds, and the visitor center is reached from Highway 101 exit 753. Terrain from USGS elevation data, stylized; not for navigation.'),
    links={'A': [('Fern Canyon · NPS', 'https://www.nps.gov/thingstodo/ferncanyon.htm'), ('Fern Canyon reservations · NPS', 'https://www.nps.gov/redw/planyourvisit/ferncanyonpermits.htm'), ('Fern Canyon · Wikipedia', 'https://en.wikipedia.org/wiki/Fern_Canyon')],
           'B': [('Friendship Ridge Loop · Hiking Project', 'https://www.hikingproject.com/trail/7029542/friendship-ridge-loop-hike'), ('Trails south of the Klamath · NPS', 'https://www.nps.gov/redw/planyourvisit/hiking-trails-south.htm')],
           'C': [('James Irvine Trail to Fern Canyon · NPS', 'https://home.nps.gov/thingstodo/jamesirvine-ferncanyonloop.htm'), ('Current conditions · NPS', 'https://www.nps.gov/redw/planyourvisit/conditions.htm')]},
    extra_js='TRAILS.forEach(T=>{const g={A:150,B:1170}[T.id];if(g)T.gain=g;});\n// out-and-back: report the outbound mile for a stop\nmileOf=function(T,x,n){let b=null;T.pts.forEach(p=>{const d=Math.hypot(p.x-x,p.n-n);if(!b||d<b.d)b={d,m:p.m,e:p.e};});if(!b||b.d>=260)return null;const f=T.pts.find(p=>Math.hypot(p.x-x,p.n-n)<b.d+60);return {d:b.d,m:f.m,e:f.e};};',
    viewaz={'all': -0.6, 'A': -0.6, 'B': -0.5, 'C': -0.7},
    zoomcap={'A': 4.2, 'B': 3.0, 'C': 2.6},
    stop_photos=stop_photos, flower_photos=PH.get('flower', {}), animal_photos={k: v for k, v in PH.get('animal', {}).items() if k not in ('salamander', 'slug', 'plover')},
)
json.dump({k: {'mi': R[k]['mi'], 'gain': R[k]['gain'], 'lo': R[k]['lo'], 'hi': R[k]['hi']} for k in R}, open('ferncanyon/stats.json', 'w'))
OUT = '/home/claude/site/out/redwoods-fern-canyon/index.html'
os.makedirs(os.path.dirname(OUT), exist_ok=True)
print(build(cfg, OUT))
from marine import inject
inject(OUT, ['whale', 'sealion', 'seal', 'pelican'], {
    'whale': 'Gray whales pass this coast on their migration between Alaska and Baja, mostly winter and spring. Look for spouts beyond the surf from Gold Bluffs Beach.',
    'sealion': 'California and Steller sea lions swim along this coast, sometimes just beyond the breakers.',
    'seal': 'Harbor seals pop their heads up beyond the breakers and sometimes rest on the beach; give them plenty of room.',
    'pelican': 'Brown pelicans glide in lines just above the waves and dive headfirst for fish, mostly summer and fall.'},
    names={'whale': 'Gray whale', 'sealion': 'Sea lion', 'seal': 'Harbor seal'})
h = open(OUT).read()
# gray fox colors; murrelet colors for the swift model
h = h.replace('fox(){const g=new THREE.Group(),c="#C9682E"', 'fox(){const g=new THREE.Group(),c="#8C8780"', 1)
h = re.sub(r'(fox:\{name:"Gray fox",color:")#[0-9A-Fa-f]{6}', r'\g<1>#8C8780', h, count=1)
h = re.sub(r'swift:\["#3A3A3A",\s*"#FFFFFF",\s*null\]', 'swift:["#6B5A48","#B9A890",null]', h, count=1)
h = re.sub(r'(swift:\{name:"Marbled murrelet",color:")#[0-9A-Fa-f]{6}', r'\g<1>#6B5A48', h, count=1)
CUST = {
 'salamander': ('Pacific giant salamander', '#7A5A3C', 'One of the largest land salamanders in North America, marbled brown and up to about a foot long. It lives in Fern Canyon and the creeks of Prairie Creek; look near Home Creek, especially on wet nights, and never handle it.', 2.4,
  '''BUILD.salamander=function(){const g=new THREE.Group(),c="#7A5A3C",dk="#3E2E22";part(g,SPH,c,0,0.16,0,0.5,0.13,0.17);part(g,SPH,dk,-0.1,0.24,0.06,0.18,0.05,0.08,0);part(g,SPH,dk,0.2,0.23,-0.05,0.14,0.05,0.07,0);
   part(g,SPH,c,0.55,0.18,0,0.2,0.11,0.16);part(g,SPH,"#111",0.62,0.26,0.1,0.035,0.035,0.035,0);part(g,SPH,"#111",0.62,0.26,-0.1,0.035,0.035,0.035,0);
   const t=part(g,CONE,c,-0.75,0.13,0,0.1,0.6,0.1);rot(t,0,0,Math.PI/2);
   [[0.3,0.2],[0.3,-0.2],[-0.3,0.2],[-0.3,-0.2]].forEach(([x,z])=>part(g,SPH,c,x,0.07,z*1.15,0.08,0.06,0.12));return g;};'''),
 'slug': ('Pacific banana slug', '#E4C33A', 'A bright yellow slug up to about 9 inches long, the best-known animal of the redwood floor. Common along the James Irvine Trail on damp days; watch your step.', 2.6,
  '''BUILD.slug=function(){const g=new THREE.Group(),c="#E4C33A";part(g,SPH,c,0,0.13,0,0.6,0.12,0.15);part(g,SPH,"#CDA92A",0.1,0.2,0,0.25,0.07,0.12,0);
   [1,-1].forEach(sd=>{const e=part(g,CYL,c,0.58,0.3,0.05*sd,0.02,0.2,0.02,0);rot(e,0.3*sd,0,-0.4);part(g,SPH,"#3A3020",0.62,0.4,0.08*sd,0.03,0.03,0.03,0);});return g;};'''),
 'plover': ('Western snowy plover', '#D8CBB2', 'Rare here: a federally threatened shorebird, sparrow-sized and sand-colored, that runs along the upper beach and nests in open sand. Seen on Gold Bluffs Beach; keep out of roped-off areas.', 3.0,
  '''BUILD.plover=function(){const g=new THREE.Group(),c="#D8CBB2",lt="#F6F3EC";part(g,SPH,c,0,0.32,0,0.28,0.17,0.17);part(g,SPH,lt,0.05,0.26,0,0.22,0.12,0.15,0);
   part(g,SPH,c,0.24,0.47,0,0.12,0.11,0.11);part(g,SPH,"#2A2A2A",0.2,0.38,0.12,0.06,0.04,0.03,0);part(g,SPH,"#2A2A2A",0.2,0.38,-0.12,0.06,0.04,0.03,0);
   const b=part(g,CONE,"#222",0.38,0.46,0,0.025,0.1,0.025,0);rot(b,0,0,-Math.PI/2);part(g,SPH,"#111",0.3,0.5,0.07,0.02,0.02,0.02,0);
   part(g,CYL,"#5A5550",0.02,0.1,0.05,0.015,0.2,0.015,0);part(g,CYL,"#5A5550",0.02,0.1,-0.05,0.015,0.2,0.015,0);const t=part(g,CONE,c,-0.3,0.34,0,0.07,0.16,0.05);rot(t,0,0,Math.PI/2);return g;};'''),
}
assert h.count('const WILD={\n') == 1 and h.count('Object.assign(BUILD,GENTLE);') == 1 and h.count('const SCALE={') == 1
for k, (nm, col, sm, sc, bj) in CUST.items():
    h = h.replace('const WILD={\n', 'const WILD={\n ' + k + ':{name:"' + nm + '",color:"' + col + '",sum:"' + sm.replace('"', '\\"') + '"},\n', 1)
    h = h.replace('Object.assign(BUILD,GENTLE);', 'Object.assign(BUILD,GENTLE);\n' + bj, 1)
    h = h.replace('const SCALE={', 'const SCALE={' + k + ':' + str(sc) + ',', 1)
CPH = {k: v for k, v in PH.get('animal', {}).items() if k in CUST}
if CPH:
    m = re.search(r'const PHOTOS=(\{.*?\});\n', h, re.S)
    if m:
        db = json.loads(m.group(1)); db.setdefault('animal', {}).update(CPH)
        h = h[:m.start(1)] + json.dumps(db, ensure_ascii=False) + h[m.end(1):]
    else: print('PHOTOS block not found')
open(OUT, 'w').write(h)
print('visible sheet?', len(re.findall(r'>[^<]*\bsheet\b[^<]*<', h, re.I)), 'fox', 'c="#8C8780"' in h, 'swift', '"#6B5A48","#B9A890"' in h)
for k in R: print(k, round(R[k]['mi'], 2), round(R[k]['gain']), round(R[k]['hi']))
