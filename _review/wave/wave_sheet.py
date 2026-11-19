from lib import *
from mk_sheet import build
import sys, json, os, re
import numpy as np

os.chdir('/home/claude/parks')
p = Park('wave', 37.01907, -112.02478)
R = {}
# OSM: Wire Pass Trail (68169742), The Wave Trail via Wire Pass (191946470), Buckskin Gulch Trail (942941021)
TH = (0, 0); JCT = (1947, 281); CONF = (6394, 303); WAVE = (5362, -8412)    # The Wave = OSM node, 36.9959 N 112.0063 W
TURN = (8791, -4171); SLOT = (4959, 773); WASH2 = (4200, -1250)
SECOND = (4778, -9374); DINO = (4334, -7220)
R['A'] = route_xy(p, TH, CONF)
R['B'] = route_xy(p, TH, CONF, TURN)
R['C'] = route_xy(p, TH, WAVE)
for k in R: Park.smooth_E(R[k], 9); p.describe(R[k], k)
am = lambda k, mi: p.at_mile(R[k], mi)[0]
GAIN = {}
for k in R:
    E = R[k]['E']; g = R[k]['gain']; GAIN[k] = int(round((2 * g - (E[-1] - E[0])) / 10.0) * 10)
print('round-trip gain', GAIN)

ST = snap_stops(p, R, {
    'S1': (*TH, 'ABC'), 'S2': (*JCT, 'ABC'), 'S3': (*SLOT, 'AB'), 'S4': (*CONF, 'AB'),
    'B1': (*am('B', 2.45), 'B'), 'B2': (*TURN, 'B'),
    'C1': (*WASH2, 'C'), 'C2': (*am('C', 2.55), 'C'), 'C3': (*WAVE, 'C'),
})
TILE = (-3300, 12000, -11800, 4300)
GRID = (-3600, 12300, -12100, 4600)
if 'plot' in sys.argv:
    from plot import plot
    plot(p, (-1500, 10500, -10000, 2000), 'wave/routes2.png', routes=R, stops=ST, title='wave', grid=500)
    sys.exit()

STEP = 90
b64, NX, NN = p.dem_b64(*GRID, STEP=STEP)
RIDGE = int(np.percentile(p.grid, 75))
print('grid', NX, NN, NX * NN, p.grid.min(), p.grid.max(), 'p75', RIDGE)

S = lambda i: ST[i]
stops = [
 dict(id='S1', trails=['A', 'B', 'C'], x=S('S1')[0], n=S('S1')[1], name='Wire Pass Trailhead', desc='A dirt lot on House Rock Valley Road, 8.3 miles south of US 89, with a trail register. The road is unpaved and can be impassable when wet. Wire Pass and Buckskin Gulch need a $6 day-use permit per person; it does not cover The Wave.'),
 dict(id='S2', trails=['A', 'B', 'C'], x=S('S2')[0], n=S('S2')[1], name='Coyote Buttes sign', desc='About half a mile down Coyote Wash, a sign on the right marks the route to Coyote Buttes North. Trail C turns right here and climbs out of the wash; A and B stay in the wash toward Wire Pass.'),
 dict(id='S3', trails=['A', 'B'], x=S('S3')[0], n=S('S3')[1], name='Wire Pass narrows', desc='Around mile 1.3 the wash pinches into a slot only a few feet wide between walls 100 to 200 ft high. A 7–8 ft drop over a chockstone usually has a log ladder, which floods can wash away; a short bypass path climbs around it.'),
 dict(id='S4', trails=['A', 'B'], x=S('S4')[0], n=S('S4')[1], name='Buckskin Gulch confluence', desc='Wire Pass ends in Buckskin Gulch, 1.7 miles from the trailhead, where the canyon widens into a big alcove. Ancestral Puebloan petroglyphs, including animal figures, are pecked into the wall on the right. The turnaround for Trail A.'),
 dict(id='B1', trails=['B'], x=S('B1')[0], n=S('B1')[1], name='Buckskin narrows', desc='Turning right (downstream), the walls of Buckskin Gulch close in within the first mile, with flood debris jammed 15 ft or more above the floor. After rain the floor can hold mud and pools.'),
 dict(id='B2', trails=['B'], x=S('B2')[0], n=S('B2')[1], name='Narrows open to the sun', desc='About 2.8 miles from the trailhead the slot opens up and lets sunlight in, a common turnaround for day hikers. Buckskin continues about 12 more miles to the Paria River; going farther overnight needs a separate permit.'),
 dict(id='C1', trails=['C'], x=S('C1')[0], n=S('C1')[1], name='Second wash', desc='The route crosses a sage flat and an old sandy road to a second dry wash. The Coyote Buttes North permit area begins just past it, and the route climbs slickrock to a saddle.'),
 dict(id='C2', trails=['C'], x=S('C2')[0], n=S('C2')[1], name='Sand dune below the crack', desc='Past the twin buttes, the route heads almost due south toward a dark crack in the cliff ahead and climbs a steep sand dune. The Wave lies just below that crack.'),
 dict(id='C3', trails=['C'], x=S('C3')[0], n=S('C3')[1], name='The Wave', desc='Two troughs in Jurassic Navajo Sandstone, the larger about 62 by 118 ft, carved mostly by wind into thin red, orange and cream bands. After rain, potholes here can hold tadpole shrimp for a few days. Dinosaur tracks lie about a third of a mile northwest, and the Second Wave sits just above to the southwest.'),
]
stops, order = renumber(p, R, stops)
print(order, [(s['id'], s['name']) for s in stops])
trails = [
 dict(id='A', name='Wire Pass to Buckskin Gulch', short='Wire Pass', official=3.4, unit='round trip', route='Out and back', time='2 hr', level='Moderate', color='--tA',
      desc='Down the sandy bed of Coyote Wash for about a mile, then through the narrow slot of Wire Pass, past a short ladder or bypass at a chockstone drop, to its meeting with Buckskin Gulch and a petroglyph panel. Return the same way. Day-use permit required; never enter with rain in the forecast.', anchors=p.anchors(R['A'], every=40)),
 dict(id='B', name='Buckskin Gulch narrows via Wire Pass', short='Buckskin', official=5.6, unit='round trip', route='Out and back', time='3–4 hr', level='Moderate', color='--tB',
      desc='Trail A, then downstream (right) into Buckskin Gulch, one of the longest slot canyons in the world, through dim narrows to where the walls open to the sun about 2.8 miles in. The turnaround is your choice; mud and cold pools are common. Day-use permit required; flash floods are deadly here.', anchors=p.anchors(R['B'], every=40)),
 dict(id='C', name='The Wave (Coyote Buttes North)', short='The Wave', official=6.4, unit='round trip', route='Out and back', time='4–6 hr', level='Strenuous', color='--tC',
      desc='A lottery permit is required. The BLM’s suggested route leaves Coyote Wash at the Coyote Buttes sign and crosses open sand and slickrock with no trail or markers, past twin buttes and up a sand dune to The Wave. Permit holders get a route guide with photos and GPS points. No shade or water; people have died here in summer heat.', anchors=p.anchors(R['C'], every=40)),
]

pa = place_along
A_ = lambda k, f, s=1, o=240: pa(p, R[k], f, s, o)
an = []
an += [f'{{k:"bighorn",at:{js(A_("B",[.80],1,500)[0])}}}', f'{{k:"bighorn",at:{js([2600, -6000])}}}']
an += [f'{{k:"deer",path:{js([-1200, -2600, -900, -2100])},per:30}}']
an += [f'{{k:"squirrel",at:{js(A_("A",[.15],-1,260)[0])},hop:true}}', f'{{k:"squirrel",at:{js(A_("C",[.62],1,300)[0])},hop:true}}']
an += [f'{{k:"snake",path:{js(A_("C",[.40],-1,280)[0]+A_("C",[.42],-1,280)[0])},per:30}}']
an += [f'{{k:"lizard",at:{js(A_("C",[.88],1,330)[0])},rock:true}}', f'{{k:"lizard",at:{js(A_("A",[.55],1,300)[0])}}}']
an += [f'{{k:"leopard",at:{js(A_("C",[.25],1,320)[0])}}}']
LIZ = """BUILD.lizard=function(c,b){c=c||"#B49A6E";b=b||"#5E7FA8";const g=new THREE.Group();
  part(g,SPH,c,0,0.16,0,0.55,0.13,0.22);part(g,SPH,b,0,0.12,0,0.4,0.08,0.24);part(g,SPH,c,0.6,0.2,0,0.2,0.12,0.15);
  part(g,SPH,"#111",0.68,0.27,0.09,0.03,0.03,0.03,0);part(g,SPH,"#111",0.68,0.27,-0.09,0.03,0.03,0.03,0);
  const tail=new THREE.Group();tail.position.set(-0.5,0.14,0);g.add(tail);const t=part(tail,CONE,c,-0.45,0,0,0.09,0.95,0.09);rot(t,0,0,Math.PI/2);g.userData.tail=tail;
  [[0.3,0.24],[0.3,-0.24],[-0.3,0.24],[-0.3,-0.24]].forEach(([x,z])=>{const l=part(g,CYL,c,x,0.07,z,0.04,0.2,0.04);rot(l,z>0?0.9:-0.9,0,0);});return g;};
BUILD.leopard=function(){const g=BUILD.lizard("#CDB98F","#E8DCC0");[[0.25,0.1],[-0.1,-0.1],[-0.3,0.12],[0.05,0.15],[0.4,-0.1]].forEach(([x,z])=>part(g,SPH,"#6B4A2E",x,0.26,z,0.06,0.03,0.06,0));return g;};
SCALE.lizard=1.5;SCALE.leopard=1.5;"""
animals_js = '(()=>{' + LIZ + 'return [\n ' + ',\n '.join(an) + '\n];})()'

g = {s['name']: s for s in stops}
th, cf, jc = g['Wire Pass Trailhead'], g['Buckskin Gulch confluence'], g['Coyote Buttes sign']
# Signature features at their OSM / BLM positions, drawn large on purpose.
lm = """  gate(%(tx)d,%(tn)d,1.2);
  // The Wave (OSM node): nested swirl of thin red / orange / cream sandstone bands around a trough, long axis ~N-S
  {const g=new THREE.Group();g.position.copy(G(%(wx)d,%(wn)d));g.rotation.y=0.2;world.add(g);
    const C=["#C8553A","#F2D9B8","#E07A45","#F7E6CC","#B9462F","#EFC59A","#D8693E","#F5E3C6"];
    for(let i=0;i<C.length;i++){const s=1-i*0.1;const m=part(g,new THREE.TorusGeometry(1.7*s,0.32,8,28),C[i],0,0.3+i*0.16,0,1,1,1.6,1.06);rot(m,Math.PI/2,0,0);}
    part(g,new THREE.SphereGeometry(1,24,10,0,Math.PI*2,0,Math.PI/2),"#E9B98A",0,0.2,0,1.0,0.35,1.7,1.06);}
  // The Second Wave (OSM): smaller banded swell, above and southwest of The Wave
  {const g=new THREE.Group();g.position.copy(G(%(sx)d,%(sn)d));g.rotation.y=-0.4;world.add(g);
    ["#E7A774","#F6E6CF","#D9823F","#F2D6B3","#C9653A"].forEach((c,i)=>{const s=1-i*0.15;part(g,new THREE.SphereGeometry(1,20,10,0,Math.PI*2,0,Math.PI/2),c,0,0.05+i*0.14,-i*0.12,2.0*s,0.38,1.4*s,1.06);});}
  // Coyote Buttes sign at the turn out of Coyote Wash
  {const q=G(%(jx)d,%(jn)d);part(world,box,"#7A5A3C",q.x,q.y+0.9,q.z,0.12,1.8,0.12,1.06);part(world,box,"#8B6A48",q.x,q.y+1.7,q.z,1.1,0.55,0.1,1.06);}
  // Petroglyph panel at the Wire Pass / Buckskin confluence: a tall varnished wall with pecked figures
  {const g=new THREE.Group();g.position.copy(G(%(cx)d,%(cn)d));g.rotation.y=-0.6;world.add(g);
    part(g,box,"#A8543A",0,1.3,0,2.4,2.6,0.5,1.06);part(g,box,"#5A3226",0,1.3,0.26,2.0,1.8,0.04,0);
    [[-0.6,1.6],[0,1.9],[0.6,1.4],[-0.3,0.9],[0.4,0.8]].forEach(([x,y])=>{part(g,box,"#E9D2B4",x,y,0.3,0.32,0.08,0.03,0);part(g,box,"#E9D2B4",x+0.12,y+0.1,0.3,0.06,0.2,0.03,0);});}
""" % dict(tx=th['x'] + 80, tn=th['n'] - 60, wx=WAVE[0], wn=WAVE[1], sx=SECOND[0], sn=SECOND[1],
           jx=jc['x'] + 40, jn=jc['n'] - 50, cx=cf['x'] + 90, cn=cf['n'] + 60)

species_extra = {
 'wvdatura': 'wvdatura:{name:"Sacred datura",latin:"Datura wrightii",color:"#F4F1E6",shape:"tube",bloom:[5,6,7,8,9],sum:"Big white trumpet flowers that open at dusk and wilt by late morning, on a sprawling gray-green plant in sandy washes. Every part is poisonous.",rule:(d,e,g,s)=>g<0.35&&d>60}',
 'wvplume': 'wvplume:{name:"Apache plume",latin:"Fallugia paradoxa",color:"#F7F3EA",shape:"cup",bloom:[4,5,6],sum:"A twiggy shrub of the washes with white rose-like flowers, followed by feathery pink seed plumes that catch the light.",rule:(d,e,g,s)=>g<0.4&&d>80}',
 'wvpear': 'wvpear:{name:"Plains pricklypear",latin:"Opuntia polyacantha",color:"#F2D33C",shape:"pad",bloom:[5,6],sum:"Low mats of spiny pads in the sand with yellow, sometimes pink, cup-shaped flowers in late spring.",rule:(d,e,g,s)=>g<0.6&&d>120}',
 'wvpenst': 'wvpenst:{name:"Firecracker penstemon",latin:"Penstemon eatonii",color:"#D7262E",shape:"tube",bloom:[4,5,6],sum:"Stems of narrow scarlet tubes that hummingbirds visit, growing out of sand and rocky ground in spring.",rule:(d,e,g,s)=>g>0.1&&d>90}',
 'wvpaint': 'wvpaint:{name:"Wyoming paintbrush",latin:"Castilleja linariifolia",color:"#E9483A",shape:"spike",bloom:[5,6,7,8],sum:"Thin stems tipped with scarlet bracts, often growing up through sagebrush and other shrubs it partly feeds on.",rule:(d,e,g,s)=>g<0.5&&d>110}',
 'wvprince': 'wvprince:{name:"Desert prince’s plume",latin:"Stanleya pinnata",color:"#F1D23A",shape:"spike",bloom:[4,5,6,7],sum:"Tall spikes of yellow, feathery flowers on soils rich in selenium; a reliable sign of seleniferous ground.",rule:(d,e,g,s)=>g<0.45&&d>140}',
 'wvhedge': 'wvhedge:{name:"Engelmann’s hedgehog cactus",latin:"Echinocereus engelmannii",color:"#C2338A",shape:"pad",bloom:[4,5],sum:"Clumps of spiny upright stems topped with big magenta flowers in spring, tucked among rocks.",rule:(d,e,g,s)=>g>0.15&&d>160}',
}
tree_rule = """if(mk<0.25){type=null;}
    else if(cd<230){type=tr()<.4?"conifer":"shrub";p=0.12;}
    else if(g>0.8)type=null;
    else{type=tr()<.3?"conifer":"shrub";p=0.02+cl*.02;}"""

stop_photos = {}; flower_photos = {}; animal_photos = {}
SPM = {}
for page in os.listdir('/home/claude/site/out'):
    f = '/home/claude/site/out/%s/index.html' % page
    if not os.path.exists(f): continue
    for m in re.findall(r'\{"f":"\.\./photos/sp_[^}]*\}', open(f).read()):
        try: d = json.loads(m); SPM.setdefault(d['f'].split('/')[-1][:-4], d)
        except Exception: pass
def sp(*fs): return [SPM[f] for f in fs if f in SPM]
MP = '/mnt/files/gtb/photos/wave/photos_meta.json'
MM = {m['f']: m for v in json.load(open(MP)).values() for m in v} if os.path.exists(MP) else {}
def ph(*fs): return [dict(MM['../photos/' + f + '.jpg']) for f in fs if '../photos/' + f + '.jpg' in MM]
nm = {s['name']: s['id'] for s in stops}
stop_photos = {nm['Wire Pass narrows']: ph('pl_wave_wirepass_3', 'pl_wave_wirepass_1', 'pl_wave_wirepass_2'),
               nm['Buckskin Gulch confluence']: ph('pl_wave_wirepass_0'),
               nm['Buckskin narrows']: ph('pl_wave_buckskin_1', 'pl_wave_buckskin_3'),
               nm['The Wave']: ph('pl_wave_wave_0', 'pl_wave_wave_3', 'pl_wave_wave_1')}
CAND = ['sp_datura', 'sp_gcdatura', 'sp_nar_datura', 'sp_apacheplume', 'sp_plainspear', 'sp_gcpenstemon', 'sp_penstemon_sed', 'sp_wyobrush', 'sp_princesplume', 'sp_hedgehog', 'sp_muledeer', 'sp_gccondor', 'sp_nar_condor',
        'sp_gcbighorn', 'sp_nar_bighorn', 'sp_wtantsquirrel', 'sp_gbrattler', 'sp_westrattle', 'sp_raven', 'sp_redtail', 'sp_wtswift', 'sp_gcswift', 'sp_pinyonjay']
for c in CAND:
    print('SPM', c, [(k, v['t'][:50]) for k, v in SPM.items() if k.startswith(c + '_')][:4])
def spp(prefix, n=2): return [SPM[k] for k in sorted(SPM) if k.startswith(prefix + '_')][:n]
exec(open('/home/claude/parks/wave_phsel.py').read()) if os.path.exists('/home/claude/parks/wave_phsel.py') else None
if not flower_photos:
    flower_photos = {'wvdatura': spp('sp_datura'), 'wvplume': spp('sp_apacheplume'), 'wvpear': spp('sp_plainspear'), 'wvpenst': [],
                     'wvpaint': spp('sp_wyobrush'), 'wvprince': spp('sp_princesplume'), 'wvhedge': spp('sp_hedgehog')}
if not animal_photos:
    animal_photos = {'bighorn': spp('sp_gcbighorn'), 'deer': spp('sp_muledeer'), 'squirrel': spp('sp_wtantsquirrel'), 'snake': spp('sp_gbrattler'),
                     'condor': spp('sp_gccondor'), 'raven': spp('sp_raven'), 'hawk': spp('sp_redtail'), 'swift': spp('sp_wtswift'), 'jay': spp('sp_pinyonjay'),
                     'lizard': ph('sp_spinylizard_0', 'sp_spinylizard_3'), 'leopard': ph('sp_leopardlizard_1', 'sp_leopardlizard_3', 'sp_leopardlizard_0')}
stop_photos = {k: v for k, v in stop_photos.items() if v}; flower_photos = {k: v for k, v in flower_photos.items() if v}; animal_photos = {k: v for k, v in animal_photos.items() if v}
print('photos', {k: len(v) for k, v in {**stop_photos, **flower_photos, **animal_photos}.items()})

WILDX = ('WILD.lizard={name:"Desert spiny lizard",color:"#7E8F5A",sum:"The animal hikers here see most: a stocky, spiny lizard with a dark collar that basks on boulders and juniper trunks on warm days, then darts into cracks."};'
         'WILD.leopard={name:"Long-nosed leopard lizard",color:"#A88A5A",sum:"A long, slim lizard with dark spots that hunts other lizards and insects on open sand and among the shrubs. In early summer, females carry orange spots and bars."};')
SP = ['wvdatura', 'wvplume', 'wvpear', 'wvpenst', 'wvpaint', 'wvprince', 'wvhedge']
cfg = dict(
    title='The Wave · Coyote Buttes North', aria='Wire Pass, Buckskin Gulch and The Wave from the Wire Pass Trailhead in the Paria Canyon–Vermilion Cliffs Wilderness', h1='The Wave · Coyote Buttes',
    canyons=[dict(id=i, **c) for i, c in [('coyote', p.creek(['330220219'], GRID, minor=True)), ('buckskin', p.creek(['589106958'], GRID, minor=False))] if c],
    trails=trails, stops=stops, order=order,
    species=SP, species_extra=species_extra,
    flora={'A': ['wvdatura', 'wvplume', 'wvpear', 'wvpaint'], 'B': ['wvdatura', 'wvplume', 'wvprince', 'wvpenst'], 'C': ['wvpear', 'wvpenst', 'wvpaint', 'wvprince', 'wvhedge']},
    wild=['bighorn', 'deer', 'squirrel', 'snake', 'condor', 'raven', 'hawk', 'swift', 'jay'],
    wild_sum={'bighorn': ('Desert bighorn sheep', 'The BLM lists them among the animals that roam the canyons and plateaus of the Vermilion Cliffs. They keep to steep rock and are seldom seen; a sighting on the slickrock is luck.'),
              'deer': ('Mule deer', 'Big-eared deer that browse the sagebrush and juniper flats around House Rock Valley, mostly at dawn and dusk.'),
              'squirrel': ('White-tailed antelope ground squirrel', 'A small ground squirrel with a white side stripe that runs with its tail curled over its back, active by day even in heat.'),
              'snake': ('Western rattlesnake', 'Recorded along these routes; it shelters under shrubs and in rock cracks. Watch where you put your hands and feet, especially on warm evenings.'),
              'condor': ('California condor', 'Rare here: condors have been released in the Vermilion Cliffs since 1996, from a species that fell to 22 birds in the 1980s; they soar over Coyote Buttes and the Paria Plateau, and hikers have recorded them here.'),
              'raven': ('Common raven', 'A year-round resident that rides the updrafts over the buttes and checks the trailhead for crumbs. Do not feed it.'),
              'hawk': ('Red-tailed hawk', 'One of the 20-plus raptors recorded in the monument; it circles over the open sand flats hunting rodents and rabbits.'),
              'swift': ('White-throated swift', 'Fast black-and-white birds that race along the cliff faces and slot rims catching insects.'),
              'jay': ('Pinyon jay', 'Dusty-blue jays that travel in noisy flocks through the pinyon and juniper on the plateaus, caching pine nuts.')},
    grid=GRID, step=STEP, dem_b64=b64, tile=TILE, ve=2.2, ridge_ft=RIDGE,
    palette='redrock', tree_rule=tree_rule, trees_anywhere=True, rock_all_aspects=True,
    landmarks=lm, animals_js=animals_js,
    zoomcap={'A': 3.0, 'B': 2.8, 'C': 2.6},
    overview=dict(h2='The Wave and Wire Pass',
                  p='On the Utah–Arizona line in the Paria Canyon–Vermilion Cliffs Wilderness, one trailhead serves two famous hikes. A follows Coyote Wash through the Wire Pass slot to Buckskin Gulch, B carries on into the Buckskin narrows, and C crosses open slickrock to The Wave, a bowl of banded Navajo Sandstone that needs a lottery permit. Pick a trail to focus the model; click anything on it for a quick note.',
                  numbers='Plain numbers mark spots shared by more than one trail: 1 and 2 are on all three, 3 and 4 on A and B. Lettered stops belong to one trail: C2 is the second stop on Trail C. Mileage is from the trailhead on the way out.',
                  wild_h='Wildlife around Coyote Buttes',
                  note='Wire Pass Trailhead, House Rock Valley Road, 8.3 miles south of US 89 between Kanab and Page. Wire Pass and Buckskin Gulch: day-use permit, $6 per person and $6 per dog, sunrise to sunset, sold at the trailhead or on Recreation.gov. The Wave (Coyote Buttes North): permit only, by the advanced lottery about four months ahead or the daily lottery for the next few days, entered on a phone from inside a geofenced area nearby; up to 64 people a day, $7 per person, group limit 6. The road is unpaved and can be impassable when wet. No water and no shade; the BLM warns of extreme heat May through September and flash floods in the slots. Terrain from USGS elevation data, stylized; not for navigation.'),
    links={'A': [('Wire Pass · BLM', 'https://www.blm.gov/visit/search-details/16450/2'), ('Wire Pass Trail · Hiking Project', 'https://www.hikingproject.com/trail/7047442/wire-pass-trail')],
           'B': [('Buckskin Gulch · BLM', 'https://blm.gov/visit/buckskin-gulch'), ('Buckskin Gulch via Wire Pass · Live and Let Hike', 'https://liveandlethike.com/2021/06/04/buckskin-gulch-via-wire-pass-paria-canyon-vermilion-cliffs-wilderness-ut/')],
           'C': [('Coyote Buttes North (The Wave) · BLM', 'https://www.blm.gov/programs/recreation/permits-and-passes/lotteries-and-permit-systems/arizona/coyote-buttes-north'), ('Permits · Recreation.gov', 'https://recreation.gov/permits/274309'), ('Route and sites · thewave.info', 'https://thewave.info/CoyoteButtesNorthCode/Map.html')]},
    extra_js=WILDX + '\nTRAILS.forEach(T=>{const g=' + json.dumps(GAIN) + '[T.id];if(g)T.gain=g;});\n// out-and-back: report the outbound mile for a stop\nmileOf=function(T,x,n){let b=null;T.pts.forEach(p=>{const d=Math.hypot(p.x-x,p.n-n);if(!b||d<b.d)b={d,m:p.m,e:p.e};});if(!b||b.d>=260)return null;const f=T.pts.find(p=>Math.hypot(p.x-x,p.n-n)<b.d+60);return {d:b.d,m:f.m,e:f.e};};',
    viewaz={'all': 0.6, 'A': 0.95, 'B': 0.6, 'C': 0.6},
    stop_photos=stop_photos, flower_photos=flower_photos, animal_photos=animal_photos,
)
json.dump({k: {'mi': R[k]['mi'], 'gain': R[k]['gain'], 'rt_gain': GAIN[k], 'lo': R[k]['lo'], 'hi': R[k]['hi']} for k in R}, open('wave/stats.json', 'w'))
os.makedirs('/home/claude/site/out/the-wave', exist_ok=True)
print(build(cfg, '/home/claude/site/out/the-wave/index.html'))
h = open('/home/claude/site/out/the-wave/index.html').read()
print('lizard in ANIMALS', h.count('"lizard"'), 'WILD.lizard', h.count('WILD.lizard'))
