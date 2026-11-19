from lib import *
from mk_sheet import build
import sys, json, os, math
import numpy as np

os.chdir('/home/claude/parks')
p = Park('humpback', 37.96828, -78.8966)
# key points (local feet, x east / n north from 37.96828, -78.8966); all from OSM
VC = (-803, 1601)       # Humpback Rocks Visitor Center, north end of the Mountain Farm Trail (OSM way end; building at -824,1632)
CABIN = (-631, 1129)    # historic log house of the Mountain Farm (OSM building historic=yes)
FARMS = (-276, 360)     # south end of the Mountain Farm Trail, by the Parkway below Humpback Gap (OSM way end)
TH = (12, 121)          # Humpback Gap parking / trailhead, MP 6.0 (OSM; info board at 9,5)
ROCKS = (-1160, -2541)  # Humpback Rocks, 949 m (OSM peak node, end of the spur)
ATJ = (-1380, -3460)    # Humpback Rocks Trail meets the Appalachian Trail (OSM way end = AT vertex)
PEAK = (-584, -7109)    # Humpback Mountain, 1,099 m (OSM peak node); AT passes 170 ft west
R = {}
R['A'] = route_xy(p, VC, FARMS)
R['B'] = route_xy(p, TH, ROCKS)
R['C'] = route_xy(p, TH, ROCKS, ATJ, PEAK)
for k in R: Park.smooth_E(R[k], 9); p.describe(R[k], k)
ST = snap_stops(p, R, {
    'A1': (VC[0], VC[1], 'A'), 'A2': (CABIN[0], CABIN[1], 'A'), 'A3': (FARMS[0], FARMS[1], 'A'),
    'S1': (TH[0], TH[1], 'BC'), 'S2': (ROCKS[0], ROCKS[1], 'BC'),
    'C1': (ATJ[0], ATJ[1], 'C'), 'C2': (PEAK[0], PEAK[1], 'C'),
})
TILE = (-4400, 2600, -9300, 3700)
GRID = (-4700, 2900, -9600, 4000)
if 'plot' in sys.argv:
    from plot import plot
    plot(p, TILE, 'humpback/routes.png', routes=R, stops=ST, title='humpback', grid=1000)
    sys.exit()

STEP = 60
b64, NX, NN = p.dem_b64(*GRID, STEP=STEP)
T_ = p.grid[int((TILE[2] - GRID[2]) / STEP):int((TILE[3] - GRID[2]) / STEP), int((TILE[0] - GRID[0]) / STEP):int((TILE[1] - GRID[0]) / STEP)]
RIDGE = int(round(float(np.percentile(T_, 75)), -1))
print('grid', NX, NN, NX * NN, p.grid.min(), p.grid.max(), 'p75', RIDGE)
for k, (x, n) in {'PEAK': PEAK, 'ROCKS': ROCKS, 'TH': TH, 'VC': VC}.items(): print(k, round(p.elev(x, n)))

S = lambda i: ST[i]
def st(i, trs, name, desc): return dict(id=i, trails=list(trs), x=S(i)[0], n=S(i)[1], name=name, desc=desc)
stops = [
 st('A1', 'A', 'Humpback Rocks Visitor Center', 'The visitor center at Parkway milepost 5.8, with a small museum of mountain life. Restrooms and drinking water are open seasonally. The Mountain Farm Trail starts by the building.'),
 st('A2', 'A', 'Mountain Farm', 'A cluster of 1890s farm buildings moved here when the Parkway was built: a log cabin with a stone chimney, barn, spring house, root cellar, chicken house and hog pen, inside split-rail fences. Staffed in summer; in winter you can still walk through.'),
 st('A3', 'A', 'Back fence', 'The farm trail ends at a fence above the Parkway. From here you can cross the road and climb to the Humpback Gap trailhead, about 0.2 mile, which is how many hikers start when the gap lot is full.'),
 st('S1', 'BC', 'Humpback Gap trailhead', 'The small lot at Humpback Gap, milepost 6.0, fills early on weekends; overflow parking is at the visitor center. Wagoners on the old Howardsville Turnpike once camped at this gap. The blue-blazed trail starts behind the kiosk.'),
 st('S2', 'BC', 'Humpback Rocks', 'A craggy greenstone outcrop at 3,080 feet, reached by a short spur off the main trail. Views west over the Shenandoah Valley and north toward Shenandoah National Park. The ledges drop off sharply; watch your footing.'),
 st('C1', 'C', 'Appalachian Trail junction', 'Just past the Rocks spur, the blue-blazed trail meets the white-blazed Appalachian Trail. Turn right (south) for Humpback Mountain. Left (north) descends past a spring and back to the gap, a 4-mile loop.'),
 st('C2', 'C', 'Humpback Mountain', 'The summit, 3,606 feet, about a mile south on the Appalachian Trail and the high point of the hike. Rock ledges along this stretch look east over the Rockfish Valley and west to the Shenandoah Valley.'),
]
stops, order = renumber(p, R, stops)
print(order, [(s['id'], s['name']) for s in stops])
trails = [
 dict(id='A', name='Mountain Farm Trail', short='Mountain Farm', official=0.25, unit='one way', route='One way', time='20–30 min', level='Easy', color='--tA',
      desc='A short, gently sloping gravel path from the visitor center through an outdoor museum of an 1890s mountain farm. Wheelchairs can manage it. In summer, interpreters in period dress show farm life without electricity or plumbing.', anchors=p.anchors(R['A'])),
 dict(id='B', name='Humpback Rocks Trail', short='Humpback Rocks', official=2.0, unit='round trip', route='Out and back', time='1–3 hr', level='Strenuous', color='--tB',
      desc='One of the most popular hikes on the Blue Ridge Parkway: about a mile up the blue-blazed trail from Humpback Gap, climbing roughly 800 feet on wooden and rock steps, with benches to rest on. A spur leads out onto the Rocks. Steep, rocky and crowded on weekends; the way down is the hardest on knees.', anchors=p.anchors(R['B'])),
 dict(id='C', name='Humpback Mountain via the Appalachian Trail', short='Humpback Mountain', official=4.0, unit='round trip', route='Out and back', time='3–4 hr', level='Strenuous', color='--tC',
      desc='Past the Rocks, the trail joins the Appalachian Trail and follows the ridge south about a mile to the 3,606-foot summit of Humpback Mountain, with far fewer people. Return the same way, or turn north on the Appalachian Trail at the junction for a gentler descent to the gap.', anchors=p.anchors(R['C'])),
]

pa = place_along
A_ = lambda k, f, s=1, o=400: pa(p, R[k], [f], s, o)[0]
def path(k, f, s=1, o=500, d=0.04): return js(A_(k, f, s, o) + A_(k, f + d, s, o))
an = []
an += [f'{{k:"bear",path:{path("C",.72,1,700)},per:34}}', f'{{k:"bear",path:{path("B",.28,1,700)},per:36,ph:0.5}}']
an += [f'{{k:"deer",path:{path("A",.5,-1,750,.2)},per:26}}', f'{{k:"deer",path:{path("C",.9,-1,600)},per:30,ph:0.4}}']
an += [f'{{k:"turkey",at:{js(A_("C",.6,-1,550))},flock:3}}']
an += [f'{{k:"chipmunk",at:{js(A_("B",.25,1,280))},hop:true}}', f'{{k:"chipmunk",at:{js(A_("C",.82,1,260))},hop:true}}']
an += [f'{{k:"squirrel",at:{js(A_("A",.75,-1,300))},hop:true}}', f'{{k:"squirrel",at:{js(A_("C",.5,1,320))},hop:true}}']
an += [f'{{k:"snake",path:{path("B",.8,1,260,.02)},per:30}}']
animals_js = '[\n ' + ',\n '.join(an) + '\n]'

species_extra = {
 'laurel': 'laurel:{name:"Mountain laurel",latin:"Kalmia latifolia",color:"#F1C9D6",shape:"dome",bloom:[5,6],sum:"An evergreen shrub with clusters of white to pale pink cup-shaped flowers in late spring and early summer, thick along the Appalachian Trail on the ridge.",rule:(d,e,g,s)=>e>2600&&g<0.9}',
 'rosebay': 'rosebay:{name:"Rosebay rhododendron",latin:"Rhododendron maximum",color:"#F3D6E2",shape:"dome",bloom:[6,7],sum:"Tall evergreen thickets with white to pale pink flower clusters in early summer, in the moister hollows below the ridge.",rule:(d,e,g,s)=>e<3000&&s<0.2}',
 'azalea': 'azalea:{name:"Pinxter flower",latin:"Rhododendron periclymenoides",color:"#F2A3C6",shape:"tube",bloom:[4,5],sum:"A deciduous azalea with fragrant pink, long-stamened flowers in spring, before the leaves are full. Common at the lower elevations of the Parkway.",rule:(d,e,g,s)=>e<2700&&g<0.8}',
 'trillium': 'trillium:{name:"Trillium",latin:"Trillium spp.",color:"#F4F0E6",shape:"cup",bloom:[4,5],sum:"Three-petaled white wildflowers on the forest floor in April and May.",rule:(d,e,g,s)=>g<0.6&&s<0.25}',
 'firepink': 'firepink:{name:"Fire pink",latin:"Silene virginica",color:"#D8263A",shape:"tube",bloom:[4,5,6],sum:"Bright red, notched petals on thin stems, along rocky trail banks from April into June.",rule:(d,e,g,s)=>g>0.35}',
 'columbine': 'columbine:{name:"Wild columbine",latin:"Aquilegia canadensis",color:"#D9452F",shape:"tube",bloom:[5,6,7],sum:"Nodding red-and-yellow flowers that grow from cracks in rock outcrops; hummingbirds feed on them.",rule:(d,e,g,s)=>e>2900&&g>0.4}',
}

lm = f'''  gate({VC[0] + 40},{VC[1] - 60},0.4);gate({TH[0] - 30},{TH[1] - 40},0.6);
  // visitor center (OSM building)
  house(-824,1660,1.0,0.5);
  // Mountain Farm: log cabin with stone chimney and shake roof (OSM historic building), split-rail fence
  {{const g=new THREE.Group();g.position.copy(G({CABIN[0]},{CABIN[1]}));g.rotation.y=0.45;g.scale.set(1.15,1.15,1.15);world.add(g);
   for(let i=0;i<6;i++)part(g,box,i%2?"#7A5838":"#8C6845",0,0.1+i*0.17,0,1.7,0.16,1.15,1.04);
   const r=part(g,roof,"#6E5A48",0,1.35,0,1.2,0.75,1.18,1.06);rot(r,0,Math.PI/2,0);
   part(g,box,"#9A948A",0.95,0.85,0,0.32,1.9,0.42,1.06);part(g,box,"#5E4632",0,0.4,0.6,0.35,0.6,0.04,0);}}
  [[-140,-120],[-200,-40],[-260,40],[-320,120]].forEach(([dx,dn],i)=>{{const q=G({CABIN[0]}+dx,{CABIN[1]}+dn);
    part(world,box,"#8A6A4A",q.x,q.y+0.25,q.z,0.06,0.5,0.06,0);part(world,box,"#9C7653",q.x,q.y+0.38,q.z,0.9,0.05,0.05,0).rotation.y=0.6;part(world,box,"#9C7653",q.x,q.y+0.22,q.z,0.9,0.05,0.05,0).rotation.y=0.6;}});
  // Humpback Rocks: a big greenstone outcrop, the hump drawn large so it reads along the trail
  {{const q=G({ROCKS[0]},{ROCKS[1]});const g=new THREE.Group();g.position.copy(q);g.rotation.y=0.3;world.add(g);
   part(g,ico,"#6F776A",0,0.7,0,2.0,1.3,1.4);part(g,ico,"#5E665A",0.9,0.5,0.5,1.2,0.9,1.0);part(g,ico,"#7C8476",-1.1,0.45,-0.3,1.1,0.8,0.9);
   part(g,ico,"#666E61",0.2,1.5,-0.2,1.0,0.7,0.8);part(g,box,"#747B6E",-0.4,1.1,0.4,1.4,0.35,1.0,1.04);}}
  // Humpback Mountain: stone cairn summit marker
  {{const q=G({PEAK[0]},{PEAK[1]});const g=new THREE.Group();g.position.copy(q);g.scale.set(1.8,1.8,1.8);world.add(g);
   [[0.9,0.35],[0.7,0.3],[0.52,0.28],[0.36,0.26],[0.22,0.22]].reduce((y,[r,h])=>{{part(g,new THREE.CylinderGeometry(r,r*1.1,h,9),"#8C8A82",0,y+h/2,0,1,1,1,1.06);return y+h;}},0);
   part(g,cyl,"#6B4F3A",0,1.85,0,0.05,0.9,0.05,0);part(g,box,"#F4F1E8",0.22,2.15,0,0.42,0.22,0.04,1.06);}}
'''

canyons = []
for nm in ('Rodes Creek', 'Mill Creek', 'Toms Branch'):
    ids = [w['id'] for w in p.W if w.get('n') == nm and w['k'] == 'stream']
    for i, wid in enumerate(ids):
        c = p.creek([wid], GRID, minor=True)
        if c: canyons.append(dict(id=f"{nm.split()[0].lower()}{i}", **c))
print('creeks', len(canyons))

PH = json.load(open('humpback/photos.json')) if os.path.exists('humpback/photos.json') else {}
cfg = dict(
    title='Humpback Rocks', aria='Humpback Rocks, Humpback Mountain and the Mountain Farm on the Blue Ridge Parkway', h1='Humpback Rocks',
    canyons=canyons, trails=trails, stops=stops, order=order,
    species=list(species_extra), species_extra=species_extra,
    flora={'A': ['azalea', 'trillium', 'rosebay'], 'B': ['laurel', 'firepink', 'columbine', 'trillium'], 'C': ['laurel', 'rosebay', 'columbine', 'firepink']},
    wild=['bear', 'deer', 'turkey', 'chipmunk', 'squirrel', 'snake', 'hawk', 'vulture', 'raven'],
    wild_sum={
        'bear': ('Black bear', 'Seen on and near the Humpback Rocks Trail every year, even with the crowds. Keep your distance, keep food packed away and never feed wildlife.'),
        'deer': ('White-tailed deer', 'Grazes the fields around the visitor center and farm and the Parkway shoulders early and late in the day.'),
        'turkey': ('Wild turkey', 'Flocks scratch through the oak leaves on the quieter slopes along the Appalachian Trail.'),
        'chipmunk': ('Eastern chipmunk', 'Darts among the rocks and roots beside the trail, cheeks full of seeds.'),
        'squirrel': ('Eastern gray squirrel', 'Busy in the oaks and hickories, especially in fall when the nuts drop.'),
        'snake': ('Timber rattlesnake', 'Lives on these rocky slopes and suns on warm ledges in summer. Look before you put a hand on a rock and give it room; copperheads live here too.'),
        'hawk': ('Broad-winged hawk', 'In September thousands stream south along the Blue Ridge; the Rockfish Gap hawk watch, a few miles north, counts them every fall.'),
        'vulture': ('Turkey vulture', 'Rides the updrafts along the ridge on tilted wings; often seen from the Rocks circling below eye level.'),
        'raven': ('Common raven', 'Croaks and tumbles in the wind around the outcrops on Humpback Rocks and the ridge.'),
    },
    grid=GRID, step=STEP, dem_b64=b64, tile=TILE, ve=1.6, ridge_ft=RIDGE,
    palette='east', trees='east', trees_anywhere=True,
    landmarks=lm, animals_js=animals_js,
    overview=dict(h2='Humpback Rocks on the Blue Ridge Parkway',
                  p='Humpback Rocks is a greenstone outcrop near the north end of the Blue Ridge Parkway in Virginia, six miles from Rockfish Gap and I-64. A is the short Mountain Farm Trail through an 1890s farm behind the visitor center. B is the steep mile up to the Rocks, one of the most popular hikes on the Parkway. C carries on along the Appalachian Trail to the summit of Humpback Mountain, 3,606 feet. Pick a trail to focus the model; click anything on it for a quick note.',
                  numbers='Plain numbers mark spots both B and C pass: the Humpback Gap trailhead and the Rocks. Lettered stops belong to one trail: C2 is the second stop on Trail C.',
                  wild_h='Wildlife around Humpback Rocks',
                  note='Blue Ridge Parkway, milepost 5.8 (visitor center and farm) and 6.0 (Humpback Gap trailhead), near Waynesboro and Lyndhurst, Virginia. No entrance fee. Humpback Gap parking is small and usually full on weekends; overflow at the visitor center. Visitor center, restrooms and water are seasonal; the farm is staffed in summer (10 am to 5 pm). Pets on a 6-foot leash. Status (November 2026): open; the Parkway is open from Rockfish Gap past Humpback Rocks, and the nearby Dobie Mountain Trail is permanently closed. Winter weather can close the road. Terrain from USGS elevation data, stylized; not for navigation.'),
    links={'A': [('Humpback Rocks Mountain Farm · NPS', 'https://www.nps.gov/places/humpback-rocks-mountain-farm.htm'), ('Humpback Rocks, milepost 5.8 · NPS', 'https://home.nps.gov/blri/planyourvisit/humpback-rocks-mp-5-8.htm')],
           'B': [('Humpback Rocks hike · NPS', 'https://www.nps.gov/thingstodo/humpback-rocks-hike.htm'), ('Humpback Rocks trailhead · NPS', 'https://www.nps.gov/places/humpback-rocks-trailhead.htm'), ('Humpback Rock · Wikipedia', 'https://en.wikipedia.org/wiki/Humpback_Rock')],
           'C': [('Humpback Rocks hiking trails · NPS', 'https://www.nps.gov/blri/planyourvisit/humpback-rocks-trails.htm'), ('Road status · NPS', 'https://www.nps.gov/blri/planyourvisit/roadclosures.htm'), ('Humpback Rocks route options · Go Hike Virginia', 'https://gohikevirginia.com/humpback-rocks/')]},
    extra_js='TRAILS.forEach(T=>{const g={A:40,B:800,C:1300}[T.id];if(g)T.gain=g;});',
    viewaz={'all': 0.35, 'A': 0.35, 'B': 0.35, 'C': 0.35},
    zoomcap={'A': 6.0, 'B': 3.6, 'C': 2.6},
    stop_photos=PH.get('stop', {}), flower_photos=PH.get('flower', {}), animal_photos=PH.get('animal', {}),
)
json.dump({k: {'mi': R[k]['mi'], 'gain': R[k]['gain'], 'lo': R[k]['lo'], 'hi': R[k]['hi']} for k in R}, open('humpback/stats.json', 'w'))
os.makedirs('/home/claude/site/out/humpback-rocks', exist_ok=True)
print(build(cfg, '/home/claude/site/out/humpback-rocks/index.html'))
