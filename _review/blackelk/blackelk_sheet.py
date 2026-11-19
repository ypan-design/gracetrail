from lib import *
from mk_sheet import build
from fauna import TREE_RULES
import sys, json, math, os
import numpy as np

os.chdir('/home/claude/parks')
p = Park('blackelk', 43.846292, -103.559901)   # origin = Sylvan Lake day-use parking (hmdb.org marker page, Trail #9 trailhead)
EX = json.load(open('blackelk/blackelk_extra.json'))

def cen(P): return (round(sum(q[0] for q in P) / len(P)), round(sum(q[1] for q in P) / len(P)))
XY = lambda lon, lat: tuple(round(v) for v in p.xy((lon, lat)))

# ---------- key points (local feet: x east, n north), all from OSM
BR = (-290, -28)        # footbridge to the swimming beach (OSM way 509518984, Sylvan Lake Trail); Trail #9 starts across it
DAM = XY(-103.566123, 43.847158)      # Sylvan Lake Dam (OSM/GNIS node 357095101, NID SD02151)
SGT = XY(-103.5661046, 43.8475248)    # Sunday Gulch Trailhead marker (OSM node 6433373387)
LTH = (1930, -1110)     # Little Devils Tower Trailhead lot on the Needles Highway (OSM toilets + lot, start of Trail No. 4)
LDT = (5677, 2127)      # Little Devil's Tower (OSM peak node, ele 2134 m)
SUM = XY(-103.5310254, 43.8659985)    # Black Elk Peak (OSM peak node 357094463)
nd = {}
for x in EX['summit']['elements']:
    if x['type'] == 'node': nd[x['id']] = (x['lon'], x['lat'])
TWP = [XY(*nd[i]) for x in EX['summit']['elements'] if x['type'] == 'way' and x['id'] == 683526804 for i in x['nodes']]
TW = cen(TWP[:-1])      # Black Elk Peak Lookout (OSM building/tower way 683526804)
POND = [p.xy(q) for q in p.WID['224160234']['p']]   # CCC reservoir just below the lookout (OSM natural=water)
LAKE = [XY(*q) for q in EX['36350630']]             # Sylvan Lake outer shore (OSM relation 158872, outer way 36350630)
print('DAM', DAM, 'SGT', SGT, 'SUM', SUM, 'TW', TW, 'POND', cen(POND), 'lake n', len(LAKE))

R = {}
R['A'] = route_xy(p, BR, (-1000, 420), DAM, (-1000, -480), BR)
R['B'] = route_xy(p, LTH, LDT)
R['C'] = route_xy(p, BR, SUM)
for k in R: Park.smooth_E(R[k], 9); p.describe(R[k], k)

def M(k, mi):
    c = np.array(R[k]['cum']); i = int(np.argmin(abs(c - mi * 5280))); q = R[k]['pts'][i]; return (round(q[0]), round(q[1]))

# Trail 3 (Norbeck) meets Trail 9: nearest point of Trail 3 to route C
T3 = [p.xy(q) for w in p.W if w.get('n') == 'Trail No. 3 (Norbeck)' for q in w['p']]
PC = np.array(R['C']['pts'])
j3 = min(T3, key=lambda q: np.min(np.hypot(PC[:, 0] - q[0], PC[:, 1] - q[1])))
J3 = (round(j3[0]), round(j3[1]))
# LDT spur leaves Trail No. 4: first point of the OSM spur way 89144347
SPJ = tuple(round(v) for v in p.xy(p.WID['89144347']['p'][0]))
print('J3', J3, 'mile', p.mile_of(R['C'], *J3)[:2], 'SPJ', SPJ, 'mile', p.mile_of(R['B'], *SPJ)[:2])

ST = snap_stops(p, R, {
    'S1': (*BR, 'AC'), 'A1': (*SGT, 'A'), 'A2': (*DAM, 'A'),
    'B1': (*LTH, 'B'), 'B2': (*SPJ, 'B'), 'B3': (*LDT, 'B'),
    'C1': (*M('C', 0.75), 'C'), 'C2': (*J3, 'C'), 'C3': (*SUM, 'C'),
})
TILE = (-5400, 12000, -4600, 10600)
GRID = (-5700, 12300, -4900, 10900)
band = 0.2 * min(TILE[1] - TILE[0], TILE[3] - TILE[2])
def clear(x, n): return min(x - TILE[0], TILE[1] - x, n - TILE[2], TILE[3] - n) - band
for k in R: print('trail', k, 'band clearance', round(min(clear(*q) for q in R[k]['pts'])))
print('summit clearance', round(clear(*SUM)), 'lake clearance', round(min(clear(*q) for q in LAKE)))
if 'plot' in sys.argv:
    from plot import plot
    plot(p, TILE, '/home/claude/parks/blackelk/routes.png', routes=R, stops=ST, title='blackelk', grid=1000)
    plot(p, (-2200, 800, -1400, 1100), '/home/claude/parks/blackelk/routesA.png', routes=R, stops=ST, title='A', grid=250)
    sys.exit()

STEP = 90
b64, NX, NN = p.dem_b64(*GRID, STEP=STEP)
RIDGE = int(round(float(np.percentile(p.grid, 75)), -1))
print('grid', NX, NN, NX * NN, p.grid.min(), p.grid.max(), 'p75', RIDGE)

S = lambda i: ST[i]
stops = [
 dict(id='S1', trails=['A', 'C'], x=S('S1')[0], n=S('S1')[1], name='Sylvan Lake day-use area', desc='Sylvan Lake sits at 6,145 ft in Custer State Park. The Sylvan Lake Shore Trail circles the water from here, and Trail #9 to Black Elk Peak begins just across the footbridge to the swimming beach. Parking is limited and fills early in summer.'),
 dict(id='A1', trails=['A'], x=S('A1')[0], n=S('A1')[1], name='Sunday Gulch Trailhead', desc='On the north shore near the dam, the Sunday Gulch Trail drops into the gulch below the lake: a 4-mile loop with boulder scrambles beside small waterfalls, where the park says many rescues happen.'),
 dict(id='A2', trails=['A'], x=S('A2')[0], n=S('A2')[1], name='Sylvan Lake Dam', desc='Theodore Reder dammed Sunday Gulch Creek to make the lake. Behind the dam the trail threads between granite boulders, and climbers often top out on the formations around the shore.'),
 dict(id='B1', trails=['B'], x=S('B1')[0], n=S('B1')[1], name='Little Devils Tower Trailhead', desc='A small lot on the Needles Highway (SD 87) about a mile east of Sylvan Lake, start of Trail #4. The highway closes to cars with the first snow until April 1 or later.'),
 dict(id='B2', trails=['B'], x=S('B2')[0], n=S('B2')[1], name='Little Devils Tower spur', desc='Leave Trail #4 at the post marked “LDT” for the spur to the tower. The last stretch is a rock scramble up steep, exposed granite, following painted marks.'),
 dict(id='B3', trails=['B'], x=S('B3')[0], n=S('B3')[1], name='Little Devils Tower', desc='A granite pinnacle with wide views of the Cathedral Spires, Black Elk Peak and the southern Black Hills. Mountain goats are sometimes seen on the rocks. Trail B turns around here.'),
 dict(id='C1', trails=['C'], x=S('C1')[0], n=S('C1')[1], name='Saddle at the park boundary', desc='About three quarters of a mile in, Trail #9 crosses a saddle at the Custer State Park boundary into the Black Elk Wilderness, which is sacred to many American Indians. Fill out the free wilderness registration.'),
 dict(id='C2', trails=['C'], x=S('C2')[0], n=S('C2')[1], name='Norbeck Trail #3 junction', desc='At about 2.8 miles Trail #3 (Norbeck) comes in from the east; stay on Trail #9 for the summit. Near the top, the left fork is for hikers and the right fork for horses.'),
 dict(id='C3', trails=['C'], x=S('C3')[0], n=S('C3')[1], name='Black Elk Peak', desc='The highest point in South Dakota, 7,242 ft. The stone fire lookout, a small dam and a pumphouse were built by the Civilian Conservation Corps in 1938–1940 and are on the National Register of Historic Places; stone and metal stairs climb into the tower. Trail C turns around here.'),
]
stops, order = renumber(p, R, stops)
print(order, [(s['id'], s['name']) for s in stops])
trails = [
 dict(id='A', name='Sylvan Lake Shore Trail', short='Sylvan Lake', official=1.0, unit='loop', route='Loop', time='1 hr', level='Easy', color='--tA',
      desc='A short loop around Sylvan Lake under granite boulders and spires, past the Sunday Gulch Trailhead and over the dam at the west end, where the path squeezes between rocks. Mostly level, with a few rocky steps on the far side.', anchors=p.anchors(R['A'])),
 dict(id='B', name='Little Devils Tower', short='Little Devils Tower', official=3.0, unit='round trip', route='Out and back', time='2–4 hr', level='Strenuous', color='--tB',
      desc='From the trailhead on the Needles Highway, Trail #4 climbs through pine and spruce to the Little Devils Tower spur, which ends in a scramble up exposed granite to the top. The park lists 1.5 miles one way.', anchors=p.anchors(R['B'])),
 dict(id='C', name='Black Elk Peak via Trail #9', short='Black Elk Peak', official=7.0, unit='round trip', route='Out and back', time='4–6 hr', level='Moderate', color='--tC',
      desc='The most traveled and shortest route to the top of South Dakota: Trail #9 leaves Sylvan Lake, crosses into the Black Elk Wilderness and climbs past granite outcrops to the stone fire lookout on Black Elk Peak. The park lists 3.3 miles one way; most hikers log about 7 miles round trip.', anchors=p.anchors(R['C'])),
]

# ---------- water: Sylvan Lake and the summit reservoir
lakes = [[[x, n] for x, n in LAKE[:-1]], [[round(x), round(n)] for x, n in POND[:-1]]]
lvl = [6145, round(float(np.percentile([p.elev(x, n) for x, n in POND], 20)))]
print('lake levels', lvl, 'dem at lake', round(float(np.percentile([p.elev(x, n) for x, n in LAKE], 20))))

creeks = []
for w in p.W:
    if w.get('k') == 'stream':
        c = p.creek([w['id']], GRID, minor=True)
        if c: creeks.append(dict(id='c' + w['id'], **c))
print('creeks', len(creeks))

GAIN = json.load(open('blackelk/gain.json')) if os.path.exists('blackelk/gain.json') else {}
extra_js = """
TRAILS.forEach(T=>{const g=%s[T.id];if(g)T.gain=g;});
function lakeP(){return lakeP.c||(lakeP.c=%s);}
function inLake(x,n){for(const P of lakeP()){let c=false;for(let i=0,j=P.length-1;i<P.length;j=i++){const a=P[i],b=P[j];if((a[1]>n)!==(b[1]>n)&&x<(b[0]-a[0])*(n-a[1])/(b[1]-a[1])+a[0])c=!c;}if(c)return true;}return false;}
(function(){const LV=%s;const mat=new THREE.MeshLambertMaterial({color:"#5FA9B8",side:THREE.DoubleSide});const edge=new THREE.LineBasicMaterial({color:"#3F8898"});
  lakeP().forEach((P,li)=>{const sh=new THREE.Shape(P.map(([x,n])=>new THREE.Vector2(x,n)));const geo=new THREE.ShapeGeometry(sh);const pa=geo.attributes.position;
    for(let i=0;i<pa.count;i++){const x=pa.getX(i),n=pa.getY(i);const v=Wv(x,n,LV[li]);v.y=Math.max(v.y,G(x,n,0.1).y);pa.setXYZ(i,v.x,v.y,v.z);}
    pa.needsUpdate=true;geo.computeVertexNormals();const m=new THREE.Mesh(geo,mat);m.renderOrder=1;world.add(m);
    const ring=P.concat([P[0]]).map(([x,n])=>{const v=Wv(x,n,LV[li]);v.y=Math.max(v.y,G(x,n,0.12).y);return v;});world.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints(ring),edge));});
})();
""" % (js(GAIN), js(lakes), js(lvl))

# lookout faces: long axis of the OSM building footprint
TWa = max(((a, b) for a in TWP for b in TWP), key=lambda ab: math.dist(*ab))
tw_rot = -math.atan2(TWa[1][1] - TWa[0][1], TWa[1][0] - TWa[0][0])
lm = f"""  gate({BR[0] + 60},{BR[1] - 90},0.6);
  gate({LTH[0]},{LTH[1] - 60},0.2);
  // Sylvan Lake Dam: a granite-block wall across the outlet (OSM dam area)
  {{const d=G({DAM[0]},{DAM[1]});const g=new THREE.Group();g.position.copy(d);g.rotation.y=0.9;g.scale.setScalar(0.55);world.add(g);
   part(g,box,"#B9B2A4",0,0.5,0,4.2,1.0,0.9,1.05);part(g,box,"#A79F90",0,1.05,0,4.4,0.14,1.1,1.05);}}
  // granite spires around the lake shore
  [[-1121,585,0.42],[-1056,304,0.32],[-1335,-956,0.36],[-1600,420,0.3]].forEach(([x,n,s])=>{{const q=G(x,n);part(world,new THREE.ConeGeometry(0.9,4.5,6),"#C9C0B0",q.x,q.y+2.2*s,q.z,s,s,s,1.06);}});
  // Little Devils Tower: a cluster of granite pillars (OSM peak), drawn large
  {{const q=G({LDT[0]},{LDT[1]});const g=new THREE.Group();g.position.copy(q);g.scale.setScalar(1.5);world.add(g);
   [[0,0,1.0,5.2],[0.9,0.4,0.7,3.8],[-0.8,0.5,0.75,4.2],[0.3,-0.9,0.6,3.2],[-0.5,-0.7,0.55,2.6]].forEach(([x,z,r,h])=>{{part(g,new THREE.CylinderGeometry(r*0.55,r,h,6),"#CFC6B4",x,h/2,z,1,1,1,1.06);part(g,new THREE.SphereGeometry(r*0.58,6,4),"#D8D0BF",x,h,z,1,0.6,1,1.06);}});}}
  // Black Elk Peak Lookout (OSM): stone tower on the summit rocks, with lookout room and roof, drawn large
  {{const q=G({TW[0]},{TW[1]});const g=new THREE.Group();g.position.copy(q);g.rotation.y={tw_rot:.3f};g.scale.setScalar(1.8);world.add(g);
   part(g,ico,"#BDB5A6",0,0.4,0,2.4,1.1,2.0);
   part(g,box,"#8E8577",0,1.6,0,1.9,2.0,1.5,1.06);
   part(g,box,"#857C6E",0,3.3,0,1.3,1.6,1.3,1.06);
   part(g,box,"#E9E3D5",0,4.45,0,1.5,0.7,1.5,1.03);
   part(g,box,"#5D7B8C",0,4.5,0.76,1.2,0.4,0.03,0);part(g,box,"#5D7B8C",0,4.5,-0.76,1.2,0.4,0.03,0);part(g,box,"#5D7B8C",0.76,4.5,0,0.03,0.4,1.2,0);part(g,box,"#5D7B8C",-0.76,4.5,0,0.03,0.4,1.2,0);
   part(g,new THREE.ConeGeometry(1.25,0.7,4),"#6B4A38",0,5.15,0,1,1,1,1.03).rotation.y=Math.PI/4;
   part(g,cyl,"#5A4030",0,5.9,0,0.04,0.9,0.04,0);}}
"""

pa = place_along
A_ = lambda k, f, s=1, o=240: pa(p, R[k], [f], s, o)[0]
an = []
an += [f'{{k:"goat",path:{js(A_("C",.96,1,380)+A_("C",.98,1,400))},per:34}}', f'{{k:"goat",path:{js(A_("B",.93,-1,300)+A_("B",.95,-1,320))},per:36,ph:0.5}}']
an += [f'{{k:"bighorn",path:{js(A_("B",.55,1,500)+A_("B",.58,1,520))},per:38}}']
an += [f'{{k:"bison",path:{js(A_("B",.05,-1,700)+A_("B",.09,-1,740))},per:44}}']
an += [f'{{k:"deer",path:{js(A_("C",.27,-1,420)+A_("C",.3,-1,420))},per:28}}', f'{{k:"deer",path:{js(A_("C",.62,-1,420)+A_("C",.65,-1,420))},per:30,ph:0.5}}']
an += [f'{{k:"marmot",at:{js(A_("C",.88,-1,260))}}}', f'{{k:"marmot",at:{js(A_("B",.75,1,220))}}}']
an += [f'{{k:"chipmunk",at:{js(A_("A",.35,1,120))},hop:true}}', f'{{k:"chipmunk",at:{js(A_("C",.45,1,200))},hop:true}}', f'{{k:"chipmunk",at:{js(A_("B",.3,-1,180))},hop:true}}']
an += [f'{{k:"squirrel",at:{js(A_("C",.35,-1,220))},hop:true}}', f'{{k:"squirrel",at:{js(A_("B",.45,1,200))},hop:true}}']
an += [f'{{k:"snake",path:{js(A_("A",.7,-1,110)+A_("A",.72,-1,110))},per:30}}', f'{{k:"snake",path:{js(A_("C",.78,1,200)+A_("C",.8,1,200))},per:30,ph:0.5}}']
an += [f'{{k:"turtle",at:{js(A_("A",.15,1,90))}}}', f'{{k:"heron",at:{js(A_("A",.55,1,110))}}}']
animals_js = '[\n ' + ',\n '.join(an) + '\n]'

species_extra = {
 'fire_be': 'fire_be:{name:"Fireweed",latin:"Chamaenerion angustifolium",color:"#D2449A",shape:"spike",bloom:[7,8],sum:"Tall magenta spikes in sunny openings and old burns along Trail #9; the flower most often recorded around Black Elk Peak.",rule:(d,e,g,s)=>e>6200&&g<0.8}',
 'lily_be': 'lily_be:{name:"Wood lily",latin:"Lilium philadelphicum",color:"#E8622A",shape:"cup",bloom:[6,7],sum:"An upturned orange-red lily of open pine woods and meadows around Sylvan Lake and the Black Elk Wilderness. Please leave it unpicked.",rule:(d,e,g,s)=>g<0.6&&e>6100}',
 'berg_be': 'berg_be:{name:"Wild bergamot",latin:"Monarda fistulosa",color:"#B48AD0",shape:"dome",bloom:[7,8],sum:"Lavender pompom heads with a minty smell on dry, sunny slopes in midsummer.",rule:(d,e,g,s)=>s>0.2&&g<0.8}',
 'hare_be': 'hare_be:{name:"Harebell",latin:"Campanula petiolata",color:"#7D8CD8",shape:"cup",bloom:[7,8,9],sum:"Small nodding blue bells on thin stems among the granite and pine needles, blooming late into summer.",rule:(d,e,g,s)=>g>0.4}',
 'susan_be': 'susan_be:{name:"Black-eyed Susan",latin:"Rudbeckia hirta",color:"#F2B526",shape:"dome",bloom:[7,8],sum:"Golden daisies with dark centers in the meadows by the trailheads.",rule:(d,e,g,s)=>e<6600&&g<0.6}',
 'bear_be': 'bear_be:{name:"Kinnikinnick",latin:"Arctostaphylos uva-ursi",color:"#C8323A",shape:"berry",bloom:[5,6,8,9],sum:"A low evergreen mat under the pines, with pink bells in spring and red berries in late summer.",rule:(d,e,g,s)=>g>0.3&&g<0.9}',
}

PH = json.load(open('blackelk_photos.json')) if os.path.exists('blackelk_photos.json') else {}
NOTE = ('Sylvan Lake, Custer State Park, on SD 87 / SD 89 north of Custer, South Dakota. A Custer State Park entrance license is required to enter or park. '
        'Trail #9 and Trail #4 enter the Black Elk Wilderness (Black Hills National Forest), where a free registration is required; leave no trace and keep groups small. '
        'Status (November 2026): trails open. The Needles Highway, with the Little Devils Tower Trailhead, closes to cars with the first snow and reopens April 1 or later; it stays open to hikers and skiers when conditions allow. A December 2025 windstorm downed thousands of trees in the park; main trails were cleared, but watch for cracked trees and avoid the woods on windy days. Expect snow and ice on the upper trails in winter. '
        'Terrain from USGS elevation data, stylized; not for navigation.')
cfg = dict(
    title='Black Elk Peak', aria='Black Elk Peak, Little Devils Tower and Sylvan Lake in Custer State Park, Black Hills, South Dakota', h1='Black Elk Peak',
    canyons=creeks, trails=trails, stops=stops, order=order,
    species=list(species_extra), species_extra=species_extra,
    flora={'A': ['susan_be', 'hare_be', 'lily_be'], 'B': ['berg_be', 'hare_be', 'bear_be'], 'C': ['fire_be', 'lily_be', 'berg_be', 'bear_be', 'hare_be']},
    wild=['goat', 'bighorn', 'bison', 'deer', 'marmot', 'chipmunk', 'squirrel', 'snake', 'turtle', 'heron', 'osprey', 'eagle', 'nutcracker', 'woodpecker', 'vulture', 'hawk', 'bluebird'],
    wild_sum={
     'goat': ('Mountain goat', 'Rare here: the Black Hills herd, about 120 goats, descends from a few released at Custer State Park in 1924, far from their native northern Rockies. Look on the summit rocks of Black Elk Peak and Little Devils Tower, and stay well back.'),
     'bighorn': ('Bighorn sheep', 'Bighorn sheep live on the granite cliffs of Custer State Park and are sometimes seen around the Needles and the Cathedral Spires.'),
     'bison': ('American bison', 'Custer State Park’s bison herd roams the park, and the park warns they are common along its trails. Stay at least 100 yards away.'),
     'deer': ('White-tailed deer', 'White-tailed and mule deer browse the pine and spruce woods around Sylvan Lake, most often at dawn and dusk.'),
     'marmot': ('Yellow-bellied marmot', 'A big ground squirrel that suns on the granite near Black Elk Peak and Little Devils Tower.'),
     'chipmunk': ('Least chipmunk', 'The most often seen animal here: a small striped chipmunk that begs at the summit and darts across every trail.'),
     'squirrel': ('Red squirrel', 'A small, noisy squirrel of the spruce and pine woods; listen for its chatter and look for piles of cone scales.'),
     'snake': ('Western terrestrial garter snake', 'A harmless striped snake of the lake shore and damp meadows.'),
     'turtle': ('Painted turtle', 'Suns on logs and rocks at the edge of Sylvan Lake on warm days.'),
     'heron': ('Great blue heron', 'Stalks the shallows of Sylvan Lake for fish and frogs.'),
     'osprey': ('Osprey', 'A fish hawk that hovers over Sylvan Lake and dives feet-first for trout.'),
     'eagle': ('Bald eagle', 'Seen over Sylvan Lake and the high ridges, more often outside the summer crowds.'),
     'nutcracker': ('Clark’s nutcracker', 'A gray bird with black-and-white wings that caches pine seeds and visits the summit of Black Elk Peak.'),
     'woodpecker': ('Hairy woodpecker', 'Drums on pine and spruce along Trail #9; American three-toed woodpeckers live here too.'),
     'vulture': ('Turkey vulture', 'Rocks on tilted wings over the granite ridges in summer.'),
     'hawk': ('Red-tailed hawk', 'Circles over the open slopes and meadows around the Needles.'),
     'bluebird': ('Mountain bluebird', 'A sky-blue bird of open, sunny slopes and burned pine woods, perching on snags.')},
    grid=GRID, step=STEP, dem_b64=b64, tile=TILE, ve=1.8, ridge_ft=RIDGE,
    palette='forest', rock_all_aspects=True,
    tree_rule='if(inLake(x,n)||' + '||'.join(f'Math.hypot(x-({a}),n-({b}))<{r}' for a, b, r in [(TW[0], TW[1], 260), (LDT[0], LDT[1], 200)]) + '){type=null;}else ' + TREE_RULES['conifer'],
    landmarks=lm, animals_js=animals_js, extra_js=extra_js,
    overview=dict(h2='Black Elk Peak, Little Devils Tower and Sylvan Lake',
                  p='Black Elk Peak (7,242 ft), formerly Harney Peak, is the highest point in South Dakota, crowned by a stone fire lookout built in the 1930s. A circles Sylvan Lake among granite boulders, B climbs to the rock-scramble top of Little Devils Tower, and C follows Trail #9 from Sylvan Lake through the Black Elk Wilderness to the summit. Pick a trail to focus the model; click anything on it for a quick note.',
                  numbers='Plain numbers mark spots more than one trail passes: Sylvan Lake is on A and C. Lettered stops belong to one trail: C2 is the second stop on Trail C.',
                  wild_h='Wildlife around Sylvan Lake and Black Elk Peak',
                  note=NOTE),
    links={'A': [('Custer State Park trail guide · SD Game, Fish and Parks', 'https://gfp.sd.gov/userdocs/csp23trail_guide.pdf'), ('Sylvan Lake · Wikipedia', 'https://en.wikipedia.org/wiki/Sylvan_Lake_(South_Dakota)')],
           'B': [('Little Devils Tower Trail · Hiking Project', 'https://www.hikingproject.com/trail/7066634/little-devils-tower-trail'), ('Little Devils Tower Trail · Black Hills & Badlands', 'https://www.blackhillsbadlands.com/things-to-do/outdoors/trails/little-devils-tower-trail/')],
           'C': [('Black Elk Wilderness · USDA Forest Service', 'https://www.fs.usda.gov/r02/blackhills/wilderness'), ('Black Elk Peak · Hiking Project', 'https://www.hikingproject.com/gem/9214/black-elk-peak'), ('Black Elk Peak Loop · Live and Let Hike', 'https://liveandlethike.com/2025/05/31/black-elk-peak-loop-black-elk-wilderness-sd/')]},
    viewaz={'all': 0.5, 'A': 0.5, 'B': 0.5, 'C': 0.5},
    zoomcap={'A': 4.5, 'B': 3.0, 'C': 2.2},
    stop_photos=PH.get('stop', {}), flower_photos=PH.get('flower', {}), animal_photos=PH.get('animal', {}),
)
json.dump({k: {'mi': R[k]['mi'], 'gain': R[k]['gain'], 'lo': R[k]['lo'], 'hi': R[k]['hi']} for k in R}, open('blackelk/stats.json', 'w'))
OUT = '/home/claude/site/out/black-elk-peak/index.html'
os.makedirs(os.path.dirname(OUT), exist_ok=True)
print(build(cfg, OUT))
print(json.load(open('blackelk/stats.json')))
