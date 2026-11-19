from lib import *
from mk_sheet import build
import sys, json, random, re, glob, os, math
import numpy as np

# Origin near Tom's Thumb Trailhead, McDowell Sonoran Preserve, Scottsdale (local feet: x east, n north)
p = Park('tomsthumb', 33.69579, -111.80227)
def mid(wid, f=0.5):
    q = p.WID[str(wid)]['p']; return tuple(round(v) for v in p.xy(q[int(len(q) * f)]))

TH = (167, -482)           # trail start by the trailhead building (OSM Tom's Thumb Trail way 1443747184 / Marcus Landslide Trail 330616272)
MR = (2248, -567)          # Mushroom Rock Scenic Point (OSM viewpoint)
BJ = (4465, -4141)         # Marcus Landslide Trail meets the Boulder Trail (toward McDowell Mountain Regional Park)
LT = (4065, -4661)         # Marcus Landslide Loop trailhead (OSM attraction at 4072,-4658)
HH = (-836, -2756)         # Harris's Hawk Vista (OSM viewpoint)
RR = (-632, -3365)         # Raven Roost Scenic View (OSM viewpoint)
VV = (-642, -4555)         # Vulture View Scenic Point (OSM viewpoint)
PF = (-593, -5367)         # Prairie Falcon Overlook (OSM viewpoint)
EJ = (-521, -6057)         # Tom's Thumb Trail meets the East End Trail (high saddle)
TS = (-1993, -5912)        # Tom's Thumb spur leaves the Tom's Thumb Trail
TT = (-2742, -5142)        # end of the Tom's Thumb spur at the base of the Thumb (OSM peak at -2765,-5085)
LJ = (-2156, -6425)        # Lookout Trail junction
LK = (-3045, -8316)        # The Lookout (OSM viewpoint, 1,176 m)
THUMB = (-2765, -5085); LOOKOUT = (-3046, -8316); MUSH = (2248, -567)

R = {}
R['A'] = route_xy(p, TH, mid(330616272, .5), BJ, LT, mid(1518318408, .3), mid(1518318408, .5), mid(1518318408, .75), LT, BJ, mid(330616272, .5), TH)
R['B'] = route_xy(p, TH, EJ, TS, TT, TS, EJ, TH)
R['C'] = route_xy(p, TH, EJ, TS, LJ, LK, LJ, TS, EJ, TH)
for k in R: Park.smooth_E(R[k], 9); p.describe(R[k], k)

ST = snap_stops(p, R, {
    'TH': (*TH, 'ABC'),
    'HH': (*HH, 'BC'), 'RR': (*RR, 'BC'), 'VV': (*VV, 'BC'), 'PF': (*PF, 'BC'), 'EJ': (*EJ, 'BC'), 'TS': (*TS, 'BC'),
    'A1': (*MR, 'A'), 'A2': (*BJ, 'A'), 'A3': (*LT, 'A'),
    'B1': (*TT, 'B'),
    'C1': (*LJ, 'C'), 'C2': (*LK, 'C'),
})
for k, v in ST.items(): print('snap', k, v)
TILE = (-6500, 7900, -11600, 2800)
if 'plot' in sys.argv:
    from plot import plot
    plot(p, (-4500, 6000, -9500, 1500), 'tomsthumb/routes.png', routes=R, stops=ST, title='tomsthumb'); sys.exit()

STEP = 75
GRID = (-6800, 8200, -11900, 3100)
b64, NX, NN = p.dem_b64(*GRID, STEP=STEP)
EL = [p.elev(x, n) for x in range(TILE[0], TILE[1], 300) for n in range(TILE[2], TILE[3], 300)]
RIDGE = int(round(float(np.percentile(EL, 75)) / 10) * 10)
print('grid', NX, NN, NX * NN, 'elev pct', [round(float(np.percentile(EL, q))) for q in (5, 50, 75, 90, 99)], 'ridge', RIDGE)
for k, q in [('VV', VV), ('PF', PF), ('EJ', EJ), ('TT', THUMB), ('LK', LOOKOUT)]: print('elev', k, round(p.elev(*q)))

S = lambda i: ST[i]
def st(k, trails, name, desc): return dict(id=k, trails=list(trails), x=S(k)[0], n=S(k)[1], name=name, desc=desc)
stops = [
 st('TH', 'ABC', 'Tom’s Thumb Trailhead', 'The first McDowell Sonoran Conservancy trailhead on the north side of the McDowell Mountains, at 23015 N. 128th St. Parking for cars and horse trailers, restrooms, a shade ramada and interpretive signs, but no drinking water. All three hikes start here.'),
 st('HH', 'BC', 'Harris’s Hawk Vista', 'After the Feldspar Trail junction the climb begins, and a short spur leads to the first named viewpoint, looking north over the desert toward the trailhead.'),
 st('RR', 'BC', 'Raven Roost', 'A viewpoint between the switchbacks, on the steepest part of the climb. The trail here is loose gravel over granite.'),
 st('VV', 'BC', 'Vulture View', 'A viewpoint near the top of the climb, about 3,670 feet up, where most of the elevation gain is behind you.'),
 st('PF', 'BC', 'Prairie Falcon Overlook', 'A last viewpoint on the ridge before the trail dips briefly toward the East End Trail junction.'),
 st('EJ', 'BC', 'East End junction', 'The high saddle where the steep, rugged East End Trail heads south toward East End, the McDowells’ second-highest ridge. The Tom’s Thumb Trail turns west here through big granite boulders.'),
 st('TS', 'BC', 'Tom’s Thumb spur', 'A three-way junction among granite boulders. The short spur to Tom’s Thumb climbs to the right; the Tom’s Thumb Trail continues past the Lookout Trail junction and down the far side of the mountains toward Windgate Pass.'),
 st('A1', 'A', 'Mushroom Rock', 'A viewpoint by one of the mushroom-shaped granite boulders along the trail. The shape comes from weathering that eats away the rock just below the ground surface.'),
 st('A2', 'A', 'Edge of the landslide', 'The Marcus Landslide Trail meets the Boulder Trail near the gated boundary with McDowell Mountain Regional Park. From here the route turns back west, toward the mountains, and climbs onto the slide.'),
 st('A3', 'A', 'Marcus Landslide Loop', 'A 0.7-mile loop on top of the slide mass, among boulders as big as cars and cottages. About 500,000 years ago some 26 billion pounds of rock broke off the East End ridge and slid about a mile; it is the second-largest landslide known in Arizona.'),
 st('B1', 'B', 'Tom’s Thumb', 'A 140-foot plug of granite on the ridge, the preserve’s best-known landmark and a popular rock-climbing spot. The base looks out over the north Scottsdale desert, and on clear days to downtown Phoenix. Falcons nest here; routes on the north side close seasonally while they raise their young.'),
 st('C1', 'C', 'Lookout Trail junction', 'Just past the Thumb spur, the narrow, rocky Lookout Trail branches south along the crest.'),
 st('C2', 'C', 'The Lookout', 'A viewpoint on a cliff at about 3,860 feet, with wide views east and west. On the way the trail crosses the boundary between the McDowells’ granite and older metamorphic rock.'),
]
stops, order = renumber(p, R, stops)
print(order, [(s['id'], s['name']) for s in stops])
trails = [
 dict(id='A', name='Marcus Landslide Trail', short='Marcus Landslide', official=3.7, unit='round trip', route='Out and back + loop', time='1.5–2 hr', level='Easy', color='--tA',
      desc='A gentle walk east along the base of the mountains past mushroom-shaped boulders and interpretive signs to the edge of the Marcus Landslide, then onto the slide itself for a 0.7-mile loop among huge boulders. The conservancy rates it gentle, with about 300 feet of gain. Return the same way. A good spring wildflower walk.', anchors=p.anchors(R['A'])),
 dict(id='B', name='Tom’s Thumb', short='Tom’s Thumb', official=4.2, unit='round trip', route='Out and back', time='2.5–3 hr', level='Strenuous', color='--tB',
      desc='The preserve’s signature climb: switchbacks over loose gravel past four named viewpoints to the high saddle, then west through granite boulders to the base of Tom’s Thumb. About 1,200 feet of gain, most of it in the first mile and a half. No shade and no water; return the same way.', anchors=p.anchors(R['B'])),
 dict(id='C', name='Lookout via Tom’s Thumb Trail', short='The Lookout', official=5.1, unit='round trip', route='Out and back', time='3–3.5 hr', level='Strenuous', color='--tC',
      desc='The same climb as Tom’s Thumb, then on past the Thumb spur onto the narrow, rocky Lookout Trail to a cliff-top viewpoint with views east and west. The conservancy rates it challenging, with many steep, loose sections. Return the same way.', anchors=p.anchors(R['C'])),
]

pa = place_along
P1 = lambda k, f, s=1, o=300: pa(p, R[k], [f], s, o)[0]
an = []
an += [f'{{k:"javelina",path:{js(P1("A",.12,-1,420)+P1("A",.15,-1,420))},per:26}}', f'{{k:"javelina",path:{js(P1("C",.08,-1,520)+P1("C",.1,-1,520))},per:28,ph:0.5}}']
an += [f'{{k:"deer",at:{js(P1("A",.3,1,600))},h:0.8}}', f'{{k:"deer",at:{js(P1("C",.4,1,520))},h:2.4}}']
an += [f'{{k:"coyote",path:{js(P1("A",.22,1,500)+P1("A",.25,1,500))},per:22}}']
an += [f'{{k:"turtle",at:{js(P1("A",.36,-1,260))},h:1.0,s:2.2}}']
an += [f'{{k:"gila",at:{js(P1("B",.08,1,260))},h:2.0,s:2.4}}']
an += [f'{{k:"quail",at:{js(P1("A",.05,1,320))},flock:3}}', f'{{k:"quail",at:{js(P1("B",.17,-1,340))},flock:3}}']
an += [f'{{k:"snake",path:{js(P1("B",.27,1,180)+P1("B",.29,1,180))},per:30}}']
animals_js = '[\n ' + ',\n '.join(an) + '\n]'

# saguaros on the lower desert slopes, away from trails, roads and houses
RD = [np.array([p.xy(q) for q in w['p']]) for w in p.W if w['k'] in ('residential', 'service', 'tertiary', 'secondary', 'unclassified', 'primary', 'parking', 'track')]
RDP = np.vstack(RD); TRP = np.vstack([np.array(R[k]['pts'])[:, :2] for k in R])
rng = random.Random(11); sag = []; tries = 0
IN = (TILE[0] + 2900, TILE[1] - 2900, TILE[2] + 2900, TILE[3] - 2900)
while len(sag) < 90 and tries < 40000:
    tries += 1
    x, n = rng.uniform(IN[0], IN[1]), rng.uniform(IN[2], IN[3])
    e = p.elev(x, n)
    if e > 3350 or n > -250: continue
    if np.hypot(*(RDP - (x, n)).T).min() < 200 or np.hypot(*(TRP - (x, n)).T).min() < 110: continue
    if any(math.dist((x, n), q[:2]) < 260 for q in sag): continue
    sag.append((round(x), round(n), round(1.7 + rng.random() * 1.1, 2), rng.randint(0, 3)))
print('saguaros', len(sag))

# boulders on the Marcus Landslide slide mass (around the loop)
LOOP = [p.xy(q) for q in p.WID['1518318408']['p']]
bld = []
for i in range(0, len(LOOP), max(1, len(LOOP) // 9)):
    x, n = LOOP[i]; bld.append((round(x + rng.uniform(-90, 90)), round(n + rng.uniform(-90, 90)), round(0.45 + rng.random() * 0.5, 2)))

th, lk, mr, lt = S('TH'), LOOKOUT, MUSH, S('A3')
lm = f'''  gate({th[0] + 40},{th[1] - 40},0.6);
  const GRAN="#CDBBA2",GRAN2="#B9A68C";
  // Tom's Thumb: a granite plug on the ridge (OSM peak), drawn much taller than life so it reads at this scale
  {{const q=G({THUMB[0]},{THUMB[1]});const g=new THREE.Group();g.position.set(q.x,q.y-0.1,q.z);world.add(g);
    part(g,new THREE.CylinderGeometry(0.75,1.1,3.8,9),GRAN,0,1.9,0,1,1,1,1.06);
    part(g,new THREE.SphereGeometry(0.79,10,8),GRAN,0.04,3.8,0,1,0.8,1,1.06);
    part(g,new THREE.SphereGeometry(1,9,7),GRAN2,0.9,0.45,0.3,0.75,0.6,0.7,1.06);
    part(g,new THREE.SphereGeometry(1,9,7),GRAN2,-0.8,0.4,-0.4,0.7,0.5,0.6,1.06);
    part(g,new THREE.SphereGeometry(1,9,7),GRAN,0.2,0.35,0.95,0.6,0.45,0.55,1.06);}}
  // The Lookout: viewpoint post and bench on the cliff top
  {{const q=G({lk[0]},{lk[1]});part(world,cyl,"#6B4F3A",q.x,q.y+0.7,q.z,0.08,1.4,0.08);part(world,box,"#5B3A26",q.x,q.y+1.35,q.z,1.0,0.44,0.1,1.06);}}
  bench({lk[0] + 70},{lk[1] + 50},0.4);
  // Mushroom Rock: weathered granite boulder with an undercut stem
  {{const q=G({mr[0]},{mr[1]});part(world,new THREE.CylinderGeometry(0.42,0.6,1.0,9),GRAN2,q.x,q.y+0.5,q.z,1,1,1,1.06);
    part(world,new THREE.SphereGeometry(1,10,8),GRAN,q.x,q.y+1.25,q.z,1.15,0.6,1.0,1.06);}}
  // interpretive sign at the start of the landslide loop
  {{const q=G({lt[0]},{lt[1]});part(world,cyl,"#6B4F3A",q.x,q.y+0.55,q.z,0.07,1.1,0.07);part(world,box,"#7A5233",q.x,q.y+1.05,q.z,1.0,0.5,0.1,1.06);}}
  // boulders on the slide mass
  {js(bld)}.forEach(([x,n,s])=>rock(x,n,s,"#C7B49A"));
  // saguaros
  function saguaro(x,n,h,i){{const q=G(x,n),c="#5E7F4A",g=new THREE.Group();g.position.copy(q);g.rotation.y=i*1.7;world.add(g);
    part(g,cyl,c,0,h/2,0,0.15,h,0.15,1.06);part(g,new THREE.SphereGeometry(0.15,8,6),c,0,h,0,1,1,1,1.06);
    const arms=[[1,0.45],[-1,0.6]].slice(0,i%3);
    arms.forEach(([sd,f])=>{{const a=part(g,cyl,c,0.2*sd,h*f,0,0.09,0.4,0.09,1.06);rot(a,0,0,Math.PI/2);part(g,cyl,c,0.38*sd,h*f+0.38,0,0.1,0.8,0.1,1.06);part(g,new THREE.SphereGeometry(0.1,8,6),c,0.38*sd,h*f+0.78,0,1,1,1,1.06);}});}}
  {js(sag)}.forEach(([x,n,h,i])=>saguaro(x,n,h,i));
'''

species_extra = {
 'saguaro': 'saguaro:{name:"Saguaro",latin:"Carnegiea gigantea",color:"#F4F0E2",shape:"spike",bloom:[4,5,6],fruit:[6,7],sum:"The tall branching cactus of the Sonoran Desert, scattered over the lower slopes and the landslide flats. Waxy white flowers open on the arm tips in late spring, followed by red fruit.",rule:(d,e,g,s)=>g<0.8&&e<3400}',
 'brittlebush': 'brittlebush:{name:"Brittlebush",latin:"Encelia farinosa",color:"#F2C230",shape:"dome",bloom:[2,3,4],sum:"A rounded silver-leaved shrub that turns the slopes yellow with daisies in early spring. Cottontails shelter under it.",rule:(d,e,g,s)=>g<0.7}',
 'teddybear': 'teddybear:{name:"Teddy bear cholla",latin:"Cylindropuntia bigelovii",color:"#E9E2B0",shape:"pad",bloom:[3,4,5],sum:"A fuzzy-looking cactus of dense golden spines. The joints break off at a touch and root where they fall, so plants grow in colonies. Keep your distance.",rule:(d,e,g,s)=>g<0.6&&s>-0.2}',
 'buckhorn': 'buckhorn:{name:"Buckhorn cholla",latin:"Cylindropuntia acanthocarpa",color:"#C9562E",shape:"pad",bloom:[4,5],sum:"A branching, jointed cactus with flowers from yellow to rusty red in spring, common beside the Tom’s Thumb Trail.",rule:(d,e,g,s)=>g<0.6}',
 'ocotillo': 'ocotillo:{name:"Ocotillo",latin:"Fouquieria splendens",color:"#E0442E",shape:"spike",bloom:[3,4,5],sum:"Long, thorny wands that stand bare most of the year, leaf out within days of rain and carry red flower spikes at the tips in spring.",rule:(d,e,g,s)=>g>0.15&&s>-0.1}',
 'paloverde': 'paloverde:{name:"Foothill palo verde",latin:"Parkinsonia microphylla",color:"#E9D33A",shape:"dome",bloom:[4,5],sum:"A small green-barked tree that photosynthesizes through its bark and drops its leaves in drought. Covered in pale yellow flowers in spring.",rule:(d,e,g,s)=>g<0.6}',
 'barrel': 'barrel:{name:"Fishhook barrel cactus",latin:"Ferocactus wislizeni",color:"#E8862E",shape:"cup",bloom:[7,8,9],fruit:[10,11,12],sum:"A stout, ribbed cactus that often leans south, with a ring of orange or yellow flowers on top in summer and yellow fruit after.",rule:(d,e,g,s)=>g>0.1&&s>0}',
}

# photo credits: this park's downloads + metadata of reused files already on the site
ALL = {}
for f in glob.glob('/home/claude/site/out/*/index.html'):
    for m in re.findall(r'\{"f":"\.\./photos/[^{}]*?\}', open(f, encoding='utf-8', errors='ignore').read()):
        try: d = json.loads(m); ALL.setdefault(d['f'].split('/')[-1], d)
        except Exception: pass
MP = '/mnt/files/gtb/photos/tomsthumb/photos_meta.json'
if os.path.exists(MP):
    for v in json.load(open(MP)).values():
        for x in v: ALL[x['f'].split('/')[-1]] = x
def ph(*fs):
    out = []
    for f in fs:
        if f in ALL: x = dict(ALL[f]); x['f'] = '../photos/' + f; out.append(x)
        else: print('MISSING photo meta', f)
    return out
KEEP = json.load(open('tomsthumb_keep.json')) if os.path.exists('tomsthumb_keep.json') else {}
stop_photos = {k: ph(*v) for k, v in KEEP.get('stops', {}).items() if v}
flower_photos = {'saguaro': ph('sp_saguaro_0.jpg', 'sp_saguaro_3.jpg', 'sp_saguaro_2.jpg'),
                 'brittlebush': ph('sp_brittlebush_0.jpg', 'sp_brittlebush_2.jpg'),
                 'teddybear': ph('sp_teddybearcholla_1.jpg', 'sp_teddybearcholla_2.jpg', 'sp_teddybearcholla_3.jpg'),
                 'ocotillo': ph('sp_ocotillo_0.jpg', 'sp_ocotillo_1.jpg', 'sp_ocotillo_3.jpg'),
                 'paloverde': ph('sp_paloverde_1.jpg', 'sp_paloverde_0.jpg'),
                 'barrel': ph('sp_barrel_1.jpg', 'sp_barrel_3.jpg')}
animal_photos = {'javelina': ph('sp_javelina_pp_0.jpg', 'sp_javelina_pp_4.jpg'), 'deer': ph('sp_muledeer_0.jpg', 'sp_muledeer_1.jpg'),
                 'coyote': ph('sp_coyote_0.jpg'), 'turtle': ph('sp_tortoise_0.jpg', 'sp_tortoise_2.jpg', 'sp_tortoise_3.jpg'),
                 'quail': ph('sp_gambelquail_0.jpg', 'sp_gambelquail_1.jpg'),
                 'woodpecker': ph('sp_gilawoodpecker_0.jpg', 'sp_gilawoodpecker_1.jpg', 'sp_gilawoodpecker_3.jpg'),
                 'hawk': ph('sp_harrishawk_0.jpg', 'sp_harrishawk_2.jpg', 'sp_harrishawk_4.jpg'), 'raven': ph('sp_raven_1.jpg'),
                 'vulture': ph('sp_vulture_sed_0.jpg', 'sp_vulture_sed_3.jpg'), 'peregrine': ph('sp_peregrine_0.jpg', 'sp_peregrine_2.jpg'),
                 'goldeneagle': ph('sp_goldeneagle_0.jpg', 'sp_goldeneagle_2.jpg')}
for k, v in KEEP.get('animals', {}).items(): animal_photos[k] = ph(*v)
for k, v in KEEP.get('flowers', {}).items(): flower_photos[k] = ph(*v)
animal_photos = {k: v for k, v in animal_photos.items() if v}; flower_photos = {k: v for k, v in flower_photos.items() if v}
GILA_PH = animal_photos.pop('gila', [])

WILD = ['javelina', 'deer', 'coyote', 'turtle', 'quail', 'snake', 'hawk', 'raven', 'vulture', 'woodpecker', 'peregrine', 'goldeneagle']
GILA_SUM = 'Rare here: a venomous lizard protected by Arizona law that spends about 95 percent of its life underground. Beaded black with pink-orange bands and seldom seen; if you meet one, admire it from a distance.'
cfg = dict(
    title='Tom’s Thumb · McDowell Sonoran Preserve', aria='Tom’s Thumb, the Lookout and the Marcus Landslide Trail in the McDowell Sonoran Preserve', h1='Tom’s Thumb',
    canyons=[], trails=trails, stops=stops, order=order,
    species=['saguaro', 'brittlebush', 'teddybear', 'buckhorn', 'ocotillo', 'paloverde', 'barrel'], species_extra=species_extra,
    flora={'A': ['saguaro', 'brittlebush', 'teddybear', 'paloverde', 'barrel'], 'B': ['saguaro', 'buckhorn', 'teddybear', 'ocotillo', 'brittlebush'], 'C': ['saguaro', 'buckhorn', 'ocotillo', 'barrel', 'paloverde', 'brittlebush']},
    wild=WILD,
    wild_sum={
     'javelina': ('Javelina', 'Collared peccaries travel in small herds through the desert flats below the mountains, mostly at dawn and dusk. Keep dogs leashed.'),
     'deer': ('Mule deer', 'Big-eared deer that browse the washes and lower slopes early and late in the day. Does give birth just before the summer monsoon.'),
     'coyote': ('Coyote', 'Seen crossing the open desert along the Marcus Landslide Trail, mostly early and late in the day; heard more often than seen.'),
     'turtle': ('Sonoran desert tortoise', 'Rare here: a Species of Greatest Conservation Need in Arizona, and the McDowell Sonoran Conservancy tracks the preserve’s tortoises with radio transmitters. It shelters in rock crevices and comes out mostly after rain. Never pick one up.'),
     'quail': ('Gambel’s quail', 'A plump desert quail with a forward-curling black topknot. Coveys run between the bushes near the trailhead and along the base of the mountains.'),
     'snake': ('Rattlesnake', 'Rattlesnakes live throughout the preserve and are protected there. They are out when it is between about 60 and 90 degrees; watch where you put your hands and feet, and give them room.'),
     'hawk': ('Harris’s hawk', 'A dark brown hawk with chestnut shoulders and a white-banded tail that nests in the preserve, often hunting in family groups. One of the trail’s viewpoints is named for it.'),
     'raven': ('Common raven', 'Big black birds that nest in the preserve and ride the updrafts along the ridge; Raven Roost is named for them.'),
     'vulture': ('Turkey vulture', 'Rocks side to side on raised wings over the ridge from spring to fall. Vulture View is named for it.'),
     'woodpecker': ('Gila woodpecker', 'A barred black-and-white woodpecker with a tan head that nests in holes it digs in saguaros. Its loud rolling call is common near the trailhead.'),
     'peregrine': ('Peregrine falcon', 'The fastest bird in a dive, seen around the cliffs and granite towers of the ridge. Falcons nest on Tom’s Thumb, so climbing routes on its north side close seasonally while they raise their young.'),
     'goldeneagle': ('Golden eagle', 'A huge brown eagle, seen now and then soaring over the McDowells.'),
    },
    grid=GRID, step=STEP, dem_b64=b64, tile=TILE, ve=1.7, ridge_ft=RIDGE,
    palette='desert', trees_anywhere=True, rock_all_aspects=True,
    tree_rule='''if(mk<0.25||g>0.9){type=null;}
    else{type=tr()<.3?"oak":"shrub";p=0.006+cl*.006;}''',
    landmarks=lm, animals_js=animals_js,
    zoomcap={'A': 3.0, 'B': 3.0, 'C': 2.8},
    extra_js='''TRAILS.forEach(T=>{const g={A:300,B:1200}[T.id];if(g)T.gain=g;});
// out-and-back: report the outbound mile for a stop
mileOf=function(T,x,n){let b=null;T.pts.forEach(p=>{const d=Math.hypot(p.x-x,p.n-n);if(!b||d<b.d)b={d,m:p.m,e:p.e};});if(!b||b.d>=260)return null;const f=T.pts.find(p=>Math.hypot(p.x-x,p.n-n)<b.d+60);return {d:b.d,m:f.m,e:f.e};};''',
    overview=dict(h2='A granite thumb above the Sonoran Desert',
                  p='The McDowell Sonoran Preserve covers more than 30,000 acres of desert and mountains on the northeast edge of Scottsdale. From Tom’s Thumb Trailhead, A is the gentle Marcus Landslide Trail across the second-largest landslide in Arizona, B the steep climb to Tom’s Thumb, a 140-foot granite plug on the ridge, and C carries on to the Lookout. Pick a trail to focus the model; click anything on it for a quick note.',
                  numbers='All three hikes start at the trailhead (1). B and C share the climb and its viewpoints, so those stops carry plain numbers. Lettered stops belong to one trail: C2 is the second stop on Trail C. All three are round trips, with stop mileage counted on the way out.',
                  wild_h='Wildlife in the McDowells',
                  note='Closed: effective November 18, 2026, the City of Scottsdale closed Tom’s Thumb Trailhead to all public access while crews remove boulders loosened by saturated soil after recent rain; it reopens when the work is done. Check scottsdaleaz.gov/preserve before you go. Normally: Tom’s Thumb Trailhead, 23015 N. 128th St., Scottsdale; the preserve is open every day sunrise to sunset, free. Restrooms, no drinking water. Dogs on a 6-foot handheld leash; no e-bikes. Little shade on any of these trails: carry plenty of water and avoid summer afternoons. Terrain from USGS elevation data, stylized; not for navigation.'),
    links={'A': [('Popular hikes from Tom’s Thumb Trailhead · McDowell Sonoran Conservancy', 'https://www.mcdowellsonoran.org/?p=6523'), ('Marcus Landslide Trail · Experience Scottsdale', 'https://www.experiencescottsdale.com/stories/post/marcus-landslide-trail-a-blast-from-the-past/'), ('Marcus Landslide · Arizona Geological Survey', 'https://azgs.arizona.edu/marcus-landslide-mcdowell-mountains-central-arizona')],
           'B': [('Tom’s Thumb Trail · Arizona Highways', 'https://arizonahighways.com/toms-thumb-trail'), ('Tom’s Thumb Trailhead · McDowell Sonoran Conservancy', 'https://mcdowellsonoran.org/toms/'), ('Tom’s Thumb Trail · HikeArizona', 'https://www.hikearizona.com/decoder.php?ZTN=733')],
           'C': [('Popular hikes from Tom’s Thumb Trailhead · McDowell Sonoran Conservancy', 'https://www.mcdowellsonoran.org/?p=6523'), ('Tom’s Thumb Trail to Lookout · 10Adventures', 'https://www.10adventures.com/hikes/phoenix/toms-thumb-trail-to-lookout/'), ('Scottsdale McDowell Sonoran Preserve · City of Scottsdale', 'https://scottsdaleaz.gov/Preserve')]},
    viewaz={'all': 3.64, 'A': 3.5, 'B': 3.74, 'C': 3.74},
    stop_photos=stop_photos, flower_photos=flower_photos, animal_photos=animal_photos,
)
json.dump({k: {'mi': R[k]['mi'], 'gain': R[k]['gain'], 'lo': R[k]['lo'], 'hi': R[k]['hi']} for k in R}, open('tomsthumb/stats.json', 'w'))
OUT = '/home/claude/site/out/toms-thumb/index.html'
os.makedirs(os.path.dirname(OUT), exist_ok=True)
print(build(cfg, OUT))
h = open(OUT).read()
for a, b in [('quail:{name:"California quail"', 'quail:{name:"Gambel’s quail"'), ('woodpecker:{name:"Acorn woodpecker"', 'woodpecker:{name:"Gila woodpecker"')]:
    if h.count(a) == 1: h = h.replace(a, b)
# Gila monster: no engine model, so add one (WILD entry, builder after the gentle animals, scale)
GILA_JS = '''BUILD.gila=function(){const g=new THREE.Group(),S=new THREE.SphereGeometry(1,12,9),M={};const mat=c=>M[c]||(M[c]=new THREE.MeshLambertMaterial({color:c}));
 const add=(c,x,y,z,sx,sy,sz)=>{const m=new THREE.Mesh(S,mat(c));m.position.set(x,y,z);m.scale.set(sx,sy,sz);g.add(m);return m;};
 const bk="#2A2320",pk="#E7865C";
 add(bk,0,0.17,0,0.48,0.14,0.21);[-0.3,-0.1,0.1,0.3].forEach(x=>add(pk,x,0.2,0,0.075,0.115,0.2));
 add(bk,0.55,0.17,0,0.19,0.11,0.14);add(pk,0.6,0.25,0,0.08,0.03,0.08);add("#111",0.66,0.21,0.09,0.025,0.025,0.025);add("#111",0.66,0.21,-0.09,0.025,0.025,0.025);
 add(bk,-0.6,0.14,0,0.26,0.09,0.11);add(pk,-0.62,0.16,0,0.06,0.08,0.1);add(bk,-0.88,0.11,0,0.13,0.055,0.065);
 [[0.3,0.2],[0.3,-0.2],[-0.3,0.2],[-0.3,-0.2]].forEach(([x,z])=>add(bk,x,0.06,z*1.15,0.08,0.06,0.1));
 return g;};
'''
gila_entry = ' gila:{name:"Gila monster",color:"#D9714A",sum:"%s"},\n' % GILA_SUM.replace('"', '\\"')
assert h.count('const WILD={\n') == 1 and h.count('Object.assign(BUILD,GENTLE);') == 1 and h.count('const SCALE={') == 1
h = h.replace('const WILD={\n', 'const WILD={\n' + gila_entry, 1)
h = h.replace('Object.assign(BUILD,GENTLE);', 'Object.assign(BUILD,GENTLE);\n' + GILA_JS, 1)
h = h.replace('const SCALE={', 'const SCALE={gila:2.4,', 1)
if GILA_PH:
    m = re.search(r'const PHOTOS=(\{.*?\});\n', h, re.S)
    if m:
        db = json.loads(m.group(1)); db.setdefault('animal', {})['gila'] = GILA_PH
        h = h[:m.start(1)] + json.dumps(db, ensure_ascii=False) + h[m.end(1):]
open(OUT, 'w').write(h)
print('visible sheet?', len(re.findall(r'>[^<]*\bsheet\b[^<]*<', h, re.I)))

hi = max(R[k]['hi'] for k in R)
lon, lat = p.ll(*TH)
RARE = [{"animal": "Gila monster", "why": "A venomous lizard protected by Arizona Game and Fish; it spends most of its life underground and is seldom seen.", "source": "https://kjzz.org/content/1872065/qaz-are-gila-monsters-legal-pets-arizona"},
        {"animal": "Sonoran desert tortoise", "why": "Protected in Arizona as a Species of Greatest Conservation Need; the McDowell Sonoran Conservancy radio-tracks the preserve's tortoises.", "source": "https://mcdowellsonoran.org/?p=10687"}]
summ = dict(name='Tom’s Thumb', folder='toms-thumb', city='Scottsdale', area='Scottsdale', state='AZ', region='Southwest', reg='sw',
            lat=round(lat, 5), lon=round(lon, 5), where='McDowell Sonoran Preserve, Scottsdale, Arizona', high=f'{int(round(hi / 10) * 10):,} ft',
            blurb='A steep climb to a 140-foot granite thumb on the McDowell Mountains ridge, a longer hike to the Lookout, and a gentle walk across a half-million-year-old landslide.',
            trails=[dict(id='A', name='Marcus Landslide Trail', mi=3.7, unit='round trip', level='Easy', gain_ft=300),
                    dict(id='B', name='Tom’s Thumb', mi=4.2, unit='round trip', level='Strenuous', gain_ft=1200),
                    dict(id='C', name='Lookout via Tom’s Thumb Trail', mi=5.1, unit='round trip', level='Strenuous', gain_ft=int(round(R['C']['gain'] / 10) * 10))],
            status='Closed: Tom’s Thumb Trailhead closed to all public access from Nov 18, 2026 while crews remove boulders loosened by recent rain; reopening date not announced.',
            rare=RARE,
            sources=['https://scottsdaleaz.gov/Preserve', 'https://mcdowellsonoran.org/toms/', 'https://www.mcdowellsonoran.org/?p=6523', 'https://www.mcdowellsonoran.org/?p=6629',
                     'https://arizonahighways.com/toms-thumb-trail', 'https://www.hikearizona.com/decoder.php?ZTN=733',
                     'https://www.10adventures.com/hikes/phoenix/toms-thumb-trail-to-lookout/',
                     'https://www.experiencescottsdale.com/stories/post/marcus-landslide-trail-a-blast-from-the-past/',
                     'https://azgs.arizona.edu/marcus-landslide-mcdowell-mountains-central-arizona',
                     'https://www.mountainproject.com/v/105798944',
                     'https://arizonahighways.com/archive/issues/chapter/Doc.1219.Chapter.9',
                     'https://www.mcdowellsonoran.org/wp-content/uploads/2024/07/Birds-of-the-McDowell-Sonoran-Preserve.pdf',
                     'https://mcdowellsonoran.org/?p=10687', 'https://scottsdaleaz.gov/preserve/rattlesnakes',
                     'https://kjzz.org/content/1872065/qaz-are-gila-monsters-legal-pets-arizona'])
json.dump(summ, open('tomsthumb/summary.json', 'w'), indent=1, ensure_ascii=False)
for nm, obj in [('tomsthumb_summary.json', summ), ('tomsthumb_rare.json', RARE)]:
    open('/home/claude/parks/' + nm, 'w').write(json.dumps(obj, indent=1, ensure_ascii=False)); open('/mnt/files/gtb/cfg/' + nm, 'w').write(json.dumps(obj, indent=1, ensure_ascii=False))
land = {"name": "Tom’s Thumb", "where": "McDowell Sonoran Preserve · Arizona", "href": "toms-thumb/", "lat": round(lat, 5), "lon": round(lon, 5),
        "grp": "sw", "reg": "sw", "st": "AZ", "status": "closed",
        "trails": [["A", "Marcus Landslide Trail", "3.7 mi round trip"], ["B", "Tom’s Thumb", "4.2 mi round trip"], ["C", "Lookout via Tom’s Thumb Trail", "5.1 mi round trip"]],
        "high": summ['high']}
open('/home/claude/parks/tomsthumb_landing.json', 'w').write(json.dumps(land, indent=1, ensure_ascii=False))
open('/mnt/files/gtb/cfg/tomsthumb_landing.json', 'w').write(json.dumps(land, indent=1, ensure_ascii=False))
print('done', summ['high'], {k: (R[k]['mi'], R[k]['gain']) for k in R})
