from lib import *
from mk_sheet import build
import sys, json, os
import numpy as np

os.chdir('/home/claude/parks')
p = Park('lostmine', 29.262, -103.290)
R = {}
TH = (-3373, 3153); LMJ = (-4311, 2608); BLW = (-4993, 1069); BLE = (-3655, 1264); PJ = (-4156, 2373)
EJ = (-2312, -3661); TOP = (-4866, -5795); LTH = (1159, 4550); LEND = (7154, 2055)
SADDLE = (4161, 2978); JFLAT = (-2157, 707); BMEAD = (-1877, -745)
R['A'] = route_xy(p, TH, LMJ, BLW, BLE, PJ, TH)
R['B'] = route_xy(p, LTH, LEND, LTH)
R['C'] = route_xy(p, TH, PJ, BLE, EJ, TOP, EJ, BLE, PJ, TH)
for k in R: Park.smooth_E(R[k], 9); p.describe(R[k], k)

am = lambda k, mi: p.at_mile(R[k], mi)[0]
ST = snap_stops(p, R, {
    'S1': (*TH, 'AC'), 'S2': (*LMJ, 'AC'), 'S3': (*BLE, 'AC'),
    'A1': (*BLW, 'A'), 'A2': (-4400, 960, 'A'),
    'B1': (*LTH, 'B'), 'B2': (*SADDLE, 'B'), 'B3': (*am('B', 1.5), 'B'), 'B4': (*am('B', 2.05), 'B'), 'B5': (*LEND, 'B'),
    'C1': (*JFLAT, 'C'), 'C2': (*BMEAD, 'C'), 'C3': (*am('C', 2.3), 'C'), 'C4': (*EJ, 'C'), 'C5': (*TOP, 'C'),
})
TILE = (-9250, 11750, -9650, 8350)
GRID = (-9650, 12150, -10050, 8750)
if 'plot' in sys.argv:
    from plot import plot
    plot(p, (-7000, 9000, -8000, 6500), 'lostmine/routes.png', routes=R, stops=ST, title='ABC', grid=1000)
    sys.exit()

STEP = 100
b64, NX, NN = p.dem_b64(*GRID, STEP=STEP)
RIDGE = int(np.percentile(p.grid, 75))
print('grid', NX, NN, NX * NN, p.grid.min(), p.grid.max(), 'p75', RIDGE)

S = lambda i: ST[i]
stops = [
 dict(id='S1', trails=['A', 'C'], x=S('S1')[0], n=S('S1')[1], name='Chisos Basin Trailhead', desc='Beside the Chisos Basin Visitor Center and the lodge, at about 5,400 ft in a bowl ringed by peaks. The Window, Laguna Meadows, Pinnacles and Basin Loop routes all start here; the short paved Window View Trail loops a low hill next door.'),
 dict(id='S2', trails=['A', 'C'], x=S('S2')[0], n=S('S2')[1], name='Laguna Meadows–Pinnacles junction', desc='About 0.3 mile out the trail forks. Laguna Meadows Trail heads southwest; Pinnacles Trail climbs southeast toward Emory Peak.'),
 dict(id='S3', trails=['A', 'C'], x=S('S3')[0], n=S('S3')[1], name='Basin Loop junction', desc='About 0.6 mile up the Pinnacles Trail the Basin Loop joins from the west. Loop hikers turn down here; the Emory Peak route keeps climbing.'),
 dict(id='A1', trails=['A'], x=S('A1')[0], n=S('A1')[1], name='Laguna Meadows junction', desc='The Basin Loop leaves the Laguna Meadows Trail and turns east across the slope. Going counterclockwise, as here, is the easier direction.'),
 dict(id='A2', trails=['A'], x=S('A2')[0], n=S('A2')[1], name='Basin Loop crossing', desc='The trail climbs gently through shady pine, oak and juniper, with views across the basin to the Window and the peaks around it. The arroyos here are good bear and mountain lion habitat; look for tracks.'),
 dict(id='B1', trails=['B'], x=S('B1')[0], n=S('B1')[1], name='Lost Mine Trailhead', desc='At mile 5.1 on the Chisos Basin Road, just below Panther Pass, at about 5,700 ft. The lot holds about 15 cars and often fills by 8 or 9 a.m. from November through April; do not park along the road. A short paved walk leads to an information panel.'),
 dict(id='B2', trails=['B'], x=S('B2')[0], n=S('B2')[1], name='Juniper Canyon overlook', desc='A low saddle about a mile up, with benches. Casa Grande rises to the west, and Juniper Canyon drops east toward the Northeast Rim and the desert. A good turnaround for a 2-mile hike.'),
 dict(id='B3', trails=['B'], x=S('B3')[0], n=S('B3')[1], name='Upper switchbacks', desc='Past the saddle the trail climbs steeply in switchbacks and stone steps. Looking back west you can see Carter Peak and the notch of the Window. Stay on the switchbacks to protect the slope.'),
 dict(id='B4', trails=['B'], x=S('B4')[0], n=S('B4')[1], name='Ridge top', desc='The trail tops out on the ridge between Pine Canyon and Juniper Canyon. Lost Mine Peak rises to the northeast; the grade eases as the path follows the ridge over slickrock.'),
 dict(id='B5', trails=['B'], x=S('B5')[0], n=S('B5')[1], name='End of the trail', desc='About 6,850 ft, where the ridge drops away steeply. Views down upper Pine Canyon and out to the Sierra del Carmen in Mexico. Turn around here.'),
 dict(id='C1', trails=['C'], x=S('C1')[0], n=S('C1')[1], name='Juniper Flat', desc='A grassy, open flat with backcountry campsites and a view of Casa Grande. The grade eases for a while.'),
 dict(id='C2', trails=['C'], x=S('C2')[0], n=S('C2')[1], name='Boulder Meadow', desc='A backcountry camping area among big boulders and trees. Beyond it the trail turns southwest and steepens.'),
 dict(id='C3', trails=['C'], x=S('C3')[0], n=S('C3')[1], name='The Pinnacles', desc='Switchbacks climb a ridge past volcanic rock pinnacles and hoodoos, with views back to Casa Grande and Toll Mountain.'),
 dict(id='C4', trails=['C'], x=S('C4')[0], n=S('C4')[1], name='Emory Peak junction', desc='The saddle between Emory Peak and Toll Mountain, about 3.5 miles up, with a toilet and bear-proof food boxes. Boot Canyon Trail continues toward the South Rim; turn right for Emory Peak.'),
 dict(id='C5', trails=['C'], x=S('C5')[0], n=S('C5')[1], name='Emory Peak summit', desc='7,825 ft, the highest point in Big Bend National Park, named for William H. Emory of the 1852 boundary survey. The last 25 ft is a scramble up an exposed rock face with no rails. Radio antennas and a solar panel share the top; the view takes in the whole park.'),
]
stops, order = renumber(p, R, stops)
print(order, [(s['id'], s['name']) for s in stops])
trails = [
 dict(id='A', name='Chisos Basin Loop', short='Basin Loop', official=2.0, unit='loop', route='Loop', time='1–1.5 hr', level='Moderate', color='--tA',
      desc='A short loop from the Chisos Basin Trailhead. It follows the Laguna Meadows Trail up into the woods, crosses the slope through pine, oak and juniper, and returns down the Pinnacles Trail, with views of the Window and the peaks ringing the basin. Counterclockwise is the easier direction.', anchors=p.anchors(R['A'], every=40)),
 dict(id='B', name='Lost Mine Trail', short='Lost Mine', official=4.8, unit='round trip', route='Out and back', time='3 hr', level='Moderate', color='--tB',
      desc='The park’s classic introduction to the Chisos Mountains. From Panther Pass the trail climbs through juniper, oak and pine to a saddle overlooking Juniper Canyon, then switchbacks steeply up to a long ridge with views of Pine Canyon and the Sierra del Carmen in Mexico. The name comes from a legend of a Spanish mine sealed somewhere in these peaks; none has ever been found.', anchors=p.anchors(R['B'], every=60)),
 dict(id='C', name='Emory Peak Trail', short='Emory Peak', official=10.0, unit='round trip', route='Out and back', time='6–8 hr', level='Strenuous', color='--tC',
      desc='The climb to the highest point in the park. The Pinnacles Trail rises from the Chisos Basin past Juniper Flat and Boulder Meadow, then switchbacks up past rock pinnacles to the saddle below Toll Mountain. A 1.5-mile spur climbs to the summit, ending in a 25-ft scramble up exposed rock. Do not go up the last mile when thunderstorms threaten, especially July to September.', anchors=p.anchors(R['C'])),
]

pa = place_along
A_ = lambda k, f, s=1, o=240: pa(p, R[k], f, s, o)
an = []
an += [f'{{k:"bear",path:{js(A_("C",[.17],1,420)[0]+A_("C",[.19],1,420)[0])},per:30}}']
an += [f'{{k:"bear",path:{js(A_("B",[.30],-1,450)[0]+A_("B",[.32],-1,450)[0])},per:32,ph:0.5}}']
an += [f'{{k:"lion",path:{js(A_("A",[.42],-1,420)[0]+A_("A",[.45],-1,420)[0])},per:26}}']
an += [f'{{k:"deer",path:{js(A_("B",[.12],1,380)[0]+A_("B",[.14],1,380)[0])},per:26}}', f'{{k:"deer",path:{js(A_("C",[.30],-1,420)[0]+A_("C",[.32],-1,420)[0])},per:28,ph:0.4}}']
an += [f'{{k:"javelina",at:{js(A_("A",[.08],1,380)[0])},flock:3}}']
an += [f'{{k:"fox",path:{js(A_("C",[.08],1,380)[0]+A_("C",[.10],1,380)[0])},per:24}}']
an += [f'{{k:"squirrel",at:{js(A_("C",[.40],1,220)[0])},hop:true}}', f'{{k:"squirrel",at:{js(A_("B",[.42],1,220)[0])},hop:true}}']
an += [f'{{k:"coyote",path:{js(A_("B",[.82],1,420)[0]+A_("B",[.85],1,420)[0])},per:24,ph:0.2}}']
an += [f'{{k:"snake",path:{js(A_("B",[.06],-1,260)[0]+A_("B",[.07],-1,260)[0])},per:30}}']
animals_js = '[\n ' + ',\n '.join(an) + '\n]'

g = {s['name']: s for s in stops}
th, lth, sad, ej = g['Chisos Basin Trailhead'], g['Lost Mine Trailhead'], g['Juniper Canyon overlook'], g['Emory Peak junction']
lm = """  gate(%(tx)d,%(tn)d,0.6);gate(%(lx)d,%(ln)d,2.2);
  // Chisos Basin Visitor Center and lodge
  house(-3250,3000,1.2,0.3);house(-2870,3260,1.3,0.9);house(-2700,3180,1.0,0.9);
  bench(%(bx)d,%(bn)d,0.4);bench(%(bx2)d,%(bn2)d,1.4);
  // Emory Peak junction: toilet and bear boxes
  {const q=G(-2370,-3768);part(world,box,"#8A7358",q.x,q.y+0.5,q.z,0.7,1.0,0.7,1.06);part(world,box,"#5E5A52",q.x,q.y+1.05,q.z,0.85,0.12,0.85,1.06);
   const r=G(%(ex)d,%(en)d);part(world,box,"#7C858C",r.x+0.6,r.y+0.25,r.z+0.4,0.9,0.5,0.5,1.06);part(world,box,"#7C858C",r.x+0.6,r.y+0.25,r.z-0.3,0.9,0.5,0.5,1.06);}
  // Emory Peak summit block, radio antennas and solar panel (exaggerated)
  {const q=G(-4795,-5860);part(world,box,"#A79C8C",q.x,q.y+0.5,q.z,1.6,1.0,1.2,1.06);part(world,box,"#B5AA99",q.x+0.3,q.y+1.1,q.z-0.1,0.9,0.4,0.8,1.06);
   part(world,cyl,"#D0D4D8",q.x-0.3,q.y+2.6,q.z+0.2,0.07,3.2,0.07,1.06);part(world,cyl,"#D0D4D8",q.x+0.4,q.y+2.2,q.z-0.2,0.06,2.4,0.06,1.06);
   part(world,box,"#C23B2A",q.x-0.3,q.y+4.25,q.z+0.2,0.16,0.16,0.16,1.06);
   const sp=part(world,box,"#2F4A73",q.x+0.2,q.y+1.45,q.z+0.45,1.0,0.06,0.6,1.06);rot(sp,0.5,0,0);}
""" % dict(tx=th['x'] + 60, tn=th['n'] + 40, lx=lth['x'] - 60, ln=lth['n'] + 40, bx=sad['x'] + 50, bn=sad['n'] + 40, bx2=sad['x'] - 50, bn2=sad['n'] - 30, ex=ej['x'], en=ej['n'])

def wid(i):
    return i if i in p.WID else int(i)
def ck(ids, minor):
    try: return p.creek([wid(i) for i in ids], GRID, minor=minor)
    except Exception as ex: print('creek err', ex); return None
creeks = [c for c in [dict(id='oak', **(ck(['1344836026'], True) or {}))] if c.get('pts')]

species_extra = {
 'havardagave': 'havardagave:{name:"Havard agave",latin:"Agave havardiana",color:"#F2C230",shape:"spike",bloom:[6,7,8],sum:"A big gray-blue century plant that grows only in and around the Chisos Mountains. After many years it sends up one tall stalk of yellow flowers, visited by endangered Mexican long-nosed bats, and then dies.",rule:(d,e,g,s)=>e>4800&&e<7200&&g>0.15&&s>-0.3&&d>100}',
 'mtsage': 'mtsage:{name:"Mountain sage",latin:"Salvia regla",color:"#E0482B",shape:"tube",bloom:[8,9,10],sum:"A shrubby sage whose orange-red flowers light up the shady woods in late summer and early fall, often under Texas madrones. Hummingbirds follow its bloom along the Chisos trails.",rule:(d,e,g,s)=>e>5600&&g<0.9&&s<0.2&&d>60}',
 'txmadrone': 'txmadrone:{name:"Texas madrone",latin:"Arbutus xalapensis",color:"#C9452E",shape:"berry",bloom:[2,3,4,10,11],sum:"One of the most distinctive trees in the Chisos. Its old bark peels away each year to show smooth white bark that turns pink and red. The red berries ripen in November and feed deer, bears and birds.",rule:(d,e,g,s)=>e>5400&&e<7400&&g>0.15&&d<600}',
 'bouvardia': 'bouvardia:{name:"Scarlet bouvardia",latin:"Bouvardia ternifolia",color:"#D3263A",shape:"tube",bloom:[7,8,9,10],sum:"Also called trompetilla. A low shrub with clusters of slender scarlet trumpets, one of the red flowers of the Chisos woods in late summer and fall.",rule:(d,e,g,s)=>e>5200&&g>0.1&&g<0.8&&d>80}',
}
tree_rule = """if(mk<0.25){type=null;}
    else if(cd<200){type=tr()<.6?"oak":"shrub";p=0.15;}
    else if(g>1.0)type=null;
    else if(e>6300){const r0=tr();type=r0<(south<0?.55:.3)?"conifer":r0<.8?"oak":"shrub";p=(south<0?0.08:0.035)+cl*.03;}
    else if(e>5200){const r0=tr();type=r0<.3?"conifer":r0<.65?"oak":"shrub";p=0.025+cl*.025+(south<-0.1?0.03:0);}
    else if(e>4600){type=tr()<.2?"oak":"shrub";p=0.012+cl*.01;}
    else{type="shrub";p=0.006;}"""

PH = json.load(open('/home/claude/parks/lostmine/photos.json')) if os.path.exists('/home/claude/parks/lostmine/photos.json') else {'stop': {}, 'flower': {}, 'animal': {}}
nm = {s['name']: s['id'] for s in stops}
stop_photos = {nm[k]: v for k, v in PH['stop'].items() if k in nm}

cfg = dict(
    title='Lost Mine Trail', aria='the Chisos Basin Loop, Lost Mine Trail and Emory Peak Trail in the Chisos Mountains of Big Bend National Park', h1='Lost Mine Trail · Big Bend',
    canyons=creeks, trails=trails, stops=stops, order=order,
    species=['havardagave', 'mtsage', 'txmadrone', 'bouvardia'], species_extra=species_extra,
    flora={'A': ['txmadrone', 'mtsage', 'havardagave', 'bouvardia'], 'B': ['havardagave', 'txmadrone', 'mtsage', 'bouvardia'], 'C': ['txmadrone', 'mtsage', 'havardagave', 'bouvardia']},
    wild=['bear', 'lion', 'deer', 'javelina', 'fox', 'coyote', 'squirrel', 'snake', 'jay', 'woodpecker', 'peregrine', 'vulture'],
    wild_sum={'bear': ('Black bear', 'Rare here: bears had all but vanished from the Chisos by 1944, and returned on their own from Mexico’s Sierra del Carmen in the late 1980s; about 30 to 40 now live in the park. They are seen regularly throughout the Chisos. Use the bear boxes and never feed one.'),
              'lion': ('Mountain lion', 'Some lions keep their home range in the Chisos. Rarely seen; keep children close, and if you meet one, do not run.'),
              'deer': ('Carmen Mountains white-tailed deer', 'Rare here: a small, isolated race of white-tailed deer of these mountains, generally considered the smallest continental deer in North America. Found above about 4,000 ft in oak woods near water; look at dawn and dusk.'),
              'javelina': ('Javelina', 'Also called collared peccary. Small groups root through the brush and are often seen around the Chisos Basin. Keep food out of reach.'),
              'fox': ('Gray fox', 'The park’s most common carnivore, a small grizzled fox that can climb trees. Hunts mostly at night.'),
              'coyote': ('Coyote', 'Lives in nearly every habitat in the park, from desert to mountain woodland. Most active at dawn and dusk.'),
              'vulture': ('Turkey vulture', 'Found throughout the park from early March until autumn, when they leave for Central and South America.'),
              'squirrel': ('Rock squirrel', 'A big, bushy-tailed squirrel often seen on boulders in the higher Chisos.'),
              'snake': ('Rattlesnake', 'Rattlesnakes live in the park. Watch where you step and put your hands on rocky trail edges, and give any snake room.'),
              'jay': ('Mexican jay', 'Rare here: in Texas this jay lives almost only in the Chisos Mountains, at the northeastern edge of its range. Noisy blue-gray family groups gather around the Chisos Basin campground, visitor center and trailheads.'),
              'woodpecker': ('Acorn woodpecker', 'A clown-faced woodpecker of the higher Chisos woods, storing acorns in holes it drills in trees.'),
              'peregrine': ('Peregrine falcon', 'Rare here: called the signature bird of the Chisos, it nests on the high cliffs, and parts of the South Rim close each nesting season to protect it.')},
    grid=GRID, step=STEP, dem_b64=b64, tile=TILE, ve=1.5, ridge_ft=RIDGE,
    palette={"ground": "#ECDDC2", "groundN": "#DFD3B5", "rock": "#CDB89A", "rockDeep": "#B59D7E", "ridge": "#F1E6D2", "oak": "#6C8752", "shrub": "#A8A676", "conifer": "#46684A"},
    tree_rule=tree_rule, trees_anywhere=True, rock_all_aspects=True,
    landmarks=lm, animals_js=animals_js,
    zoomcap={'A': 4.5, 'B': 3.4, 'C': 2.8},
    overview=dict(h2='The Chisos Mountains, a sky island over the desert',
                  p='The Chisos are volcanic peaks rising out of the Chihuahuan Desert, a sky island cool enough on top for pinyon pine, oak, juniper and Texas madrone. A is the short Chisos Basin Loop. B is the Lost Mine Trail from Panther Pass to a ridge over Pine Canyon. C climbs the Pinnacles Trail to Emory Peak, the highest point in the park. Pick a trail to focus the model; click anything on it for a quick note.',
                  numbers='Plain numbers mark spots shared by A and C from the Chisos Basin Trailhead. Lettered stops belong to one trail: B2 is the second stop on Trail B.',
                  wild_h='Wildlife in the Chisos',
                  note='Big Bend National Park, Texas. The Chisos Basin is reached by the Chisos Basin Road, with sharp curves and grades up to 15%; it is not recommended for RVs over 24 ft or trailers over 20 ft. Lost Mine Trailhead is at mile 5.1 of that road, with parking for about 15 cars; the Basin Trailhead is by the Chisos Basin Visitor Center (open 8:30 a.m. to 4 p.m.). Entrance fee required. No pets on any trail. Carry about a liter of water per person per hour. Terrain from USGS elevation data, stylized; not for navigation.'),
    links={'A': [('Mountain hikes · NPS', 'https://home.nps.gov/bibe/planyourvisit/mountain_hikes.htm')],
           'B': [('Lost Mine Trail · NPS', 'https://www.nps.gov/places/lost-mine-trail.htm'), ('Hike the Lost Mine Trail · NPS', 'https://www.nps.gov/thingstodo/hike-the-lost-mine-trail.htm'), ('Lost Mine Trail · HikingWalking', 'https://hikingwalking.com/destinations/tx/tx_parks/big_bend/lost_mine')],
           'C': [('Emory Peak Trail · NPS', 'https://www.nps.gov/places/emory-peak-trail.htm'), ('Emory Peak · HikingWalking', 'https://hikingwalking.com/destinations/tx/tx_parks/big_bend/emory_peak')]},
    extra_js='TRAILS.forEach(T=>{const g={B:1100,C:2500}[T.id];if(g)T.gain=g;});\n// out-and-back: report the outbound mile for a stop\nmileOf=function(T,x,n){let b=null;T.pts.forEach(p=>{const d=Math.hypot(p.x-x,p.n-n);if(!b||d<b.d)b={d,m:p.m,e:p.e};});if(!b||b.d>=260)return null;const f=T.pts.find(p=>Math.hypot(p.x-x,p.n-n)<b.d+60);return {d:b.d,m:f.m,e:f.e};};',
    viewaz={'all': 3.6, 'A': 3.6, 'B': 3.8, 'C': 3.5},
    stop_photos=stop_photos, flower_photos=PH['flower'], animal_photos=PH['animal'],
)
json.dump({k: {'mi': R[k]['mi'], 'gain': R[k]['gain'], 'lo': R[k]['lo'], 'hi': R[k]['hi']} for k in R}, open('lostmine/stats.json', 'w'))
os.makedirs('/home/claude/site/out/big-bend-lost-mine', exist_ok=True)
print(build(cfg, '/home/claude/site/out/big-bend-lost-mine/index.html'))
