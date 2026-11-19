from lib import *
from mk_sheet import build
import sys, json, os, math
import numpy as np

os.chdir('/home/claude/parks')
p = Park('calfcreek', 37.7988, -111.4121)   # origin = BLM coordinates of the Lower Calf Creek Falls Trail
# all points below are OSM way ends / nodes in the local frame (ft)
UTH = (-7382, 22089)    # Upper Calf Creek Falls Trail start, rim parking off UT-12
UJ = (-10829, 20230)    # fork: side trail to the base of the falls (OSM way 1160933389 start)
UBASE = (-11370, 20422) # base of Upper Calf Creek Falls (end of the side trail)
UFALL = (-11458, 20483) # OSM "Upper Calf Creek Fall"
ETH = (-2156, -8361)    # Escalante River trailhead (Escalante Natural Bridge Trail start, by the UT-12 bridge)
NB = (-9365, -9642)     # OSM Escalante Natural Bridge
ARCH = (-10840, -8892)  # OSM Cliff House Arch
HANDS = (-2798, -7807)  # OSM 100 Hands Panel
LTH = (-445, -1131)     # Lower Calf Creek Falls Trail start, Calf Creek Recreation Area
LFALL = (-2393, 11105)  # OSM Lower Calf Creek Falls (head of the "Lower Calf Creek" waterway)
R = {}
R['A'] = route_xy(p, UTH, UJ, UBASE)
R['B'] = route_xy(p, ETH, NB, ARCH)
R['C'] = route_xy(p, LTH, LFALL)
for k in R: Park.smooth_E(R[k], 9); p.describe(R[k], k)
print('B mile at bridge', p.mile_of(R['B'], *NB), 'arch', p.mile_of(R['B'], *ARCH), 'hands', p.mile_of(R['B'], *HANDS))
# Lower Calf Creek stops placed by trail mileage (hikingwalking.com: granary 0.9 mi, pictographs 1.4 mi; total 2.9 one way)
GRAN = p.at_mile(R['C'], 0.9)[0]
PICT = p.at_mile(R['C'], 1.4)[0]
ST = snap_stops(p, R, {
    'A1': (UTH[0], UTH[1], 'A'), 'A2': (UJ[0], UJ[1], 'A'), 'A3': (UBASE[0], UBASE[1], 'A'),
    'B1': (ETH[0], ETH[1], 'B'), 'B2': (NB[0], NB[1], 'B'), 'B3': (ARCH[0], ARCH[1], 'B'),
    'C1': (LTH[0], LTH[1], 'C'), 'C2': (GRAN[0], GRAN[1], 'C'), 'C3': (PICT[0], PICT[1], 'C'), 'C4': (LFALL[0], LFALL[1], 'C'),
})
TILE = (-16400, 5600, -14800, 27200)
GRID = (-16700, 5900, -15100, 27500)
if 'plot' in sys.argv:
    from plot import plot
    plot(p, (-12500, -6500, 19000, 23000), 'calfcreek/plotA.png', routes=R, stops=ST, title='A', grid=500)
    plot(p, (-12000, -1000, -11000, -6500), 'calfcreek/plotB.png', routes=R, stops=ST, title='B', grid=1000)
    plot(p, (-4500, 2000, -2500, 12000), 'calfcreek/plotC.png', routes=R, stops=ST, title='C', grid=1000)
    sys.exit()


def flow_dir(name, x, n):
    # downstream unit direction of a named OSM waterway near (x, n)
    best = None
    for w in p.W:
        if w.get('n') != name: continue
        ps = [p.xy(q) for q in w['p']]
        for a, b in zip(ps, ps[1:]):
            d = math.hypot((a[0] + b[0]) / 2 - x, (a[1] + b[1]) / 2 - n)
            if best is None or d < best[0]: best = (d, a, b)
    if best is None: return (0.0, -1.0)
    # look a few hundred feet downstream to smooth the direction
    _, a, b = best
    dx, dn = b[0] - a[0], b[1] - a[1]; l = math.hypot(dx, dn) or 1
    return (round(dx / l, 3), round(dn / l, 3))


def flow_dir_span(name, x, n, span=500):
    for w in p.W:
        if w.get('n') != name: continue
        ps = [p.xy(q) for q in w['p']]
        i = int(np.argmin([math.hypot(q[0] - x, q[1] - n) for q in ps]))
        j = i
        while j < len(ps) - 1 and math.hypot(ps[j][0] - ps[i][0], ps[j][1] - ps[i][1]) < span: j += 1
        if j == i: continue
        dx, dn = ps[j][0] - ps[i][0], ps[j][1] - ps[i][1]; l = math.hypot(dx, dn) or 1
        return (round(dx / l, 3), round(dn / l, 3))
    return flow_dir(name, x, n)


LDIR = flow_dir_span('Lower Calf Creek', *LFALL)
UDIR = flow_dir_span('Upper Calf Creek', *UFALL)
EDIR = flow_dir_span('Escalante River', *NB, span=1500)
print('flow dirs lower', LDIR, 'upper', UDIR, 'escalante', EDIR)

STEP = 150
b64, NX, NN = p.dem_b64(*GRID, STEP=STEP)
RIDGE = int(round(float(np.percentile(p.grid, 75)), -1))
print('grid', NX, NN, NX * NN, p.grid.min(), p.grid.max(), 'p75', RIDGE)

S = lambda i: ST[i]
stops = [
 dict(id='A1', trails=['A'], x=S('A1')[0], n=S('A1')[1], name='Upper Calf Creek Falls trailhead', desc='A small parking area on the slickrock rim at the end of a rough 0.1-mile spur road off the west side of UT-12, between mileposts 80 and 81. The trailhead is unsigned. Below it the route drops steeply down white Navajo sandstone, marked by cairns of dark volcanic stones.'),
 dict(id='A2', trails=['A'], x=S('A2')[0], n=S('A2')[1], name='Fork above the falls', desc='After crossing flatter sandy ground the trail splits. The left branch leads down to the base of the falls; the main trail continues upstream to clear pools just above the lip of the falls.'),
 dict(id='A3', trails=['A'], x=S('A3')[0], n=S('A3')[1], name='Upper Calf Creek Falls', desc='Calf Creek drops about 88 feet over a cliff at the head of its canyon into a large pool, often deep enough to swim. The falls are quieter than the lower falls, and the creek below runs down the canyon to Lower Calf Creek Falls.'),
 dict(id='B1', trails=['B'], x=S('B1')[0], n=S('B1')[1], name='Escalante River trailhead', desc='Paved access just north of the UT-12 bridge over the Escalante River, 13.3 miles east of Escalante. A short path west along the foot of the cliff north of the river passes several rock art panels, among them the Bighorn Sheep and 100 Hands panels, about 30 feet up the wall.'),
 dict(id='B2', trails=['B'], x=S('B2')[0], n=S('B2')[1], name='Escalante Natural Bridge', desc='A sandstone bridge about 130 feet high with a 125-foot span over a side canyon that drains into the river, on the south side of the canyon. The largest natural bridge in the monument. Getting here takes four shin-deep fords of the Escalante River.'),
 dict(id='B3', trails=['B'], x=S('B3')[0], n=S('B3')[1], name='Cliff House Arch', desc='About half a mile and two more fords past the bridge, a skyline arch sits high on the canyon rim, with an ancient cliff dwelling in the wall below it.'),
 dict(id='C1', trails=['C'], x=S('C1')[0], n=S('C1')[1], name='Calf Creek Recreation Area', desc='The trailhead, in the BLM campground and day-use area on UT-12 about 15 miles east of Escalante, with restrooms and drinking water. A numbered guide at the start explains 24 posts along the trail. Parking is limited and fills early in summer.'),
 dict(id='C2', trails=['C'], x=S('C2')[0], n=S('C2')[1], name='Granary', desc='A small stone storage structure, built 800 to 1,000 years ago, tucked in an alcove high on the canyon wall. Binoculars help. Another granary sits farther on, about halfway up a wall in a side canyon to the east.'),
 dict(id='C3', trails=['C'], x=S('C3')[0], n=S('C3')[1], name='Pictographs', desc='Large red human figures painted on a smooth cliff across the canyon, about 1,000 years old and attributed to the Fremont people. Three of them appear to hold hands and wear headdresses. View them from the trail; the sites are protected by federal law.'),
 dict(id='C4', trails=['C'], x=S('C4')[0], n=S('C4')[1], name='Lower Calf Creek Falls', desc='A 126-foot waterfall pouring down a moss-streaked wall into a pool with a sandy beach. Rocks fall from the overhanging cliff without warning and can land well out in the pool and on the shore; BLM warned visitors in June 2025 after boulders narrowly missed swimmers.'),
]
stops, order = renumber(p, R, stops)
print(order, [(s['id'], s['name']) for s in stops])
trails = [
 dict(id='A', name='Upper Calf Creek Falls', short='Upper Falls', official=2.0, unit='round trip', route='Out and back', time='1–2 hr', level='Hard', color='--tA',
      desc='A short, steep route from an unsigned rim parking area off UT-12. It descends about 560 feet, first down open slickrock marked by cairns, then across sand to a fork: one branch to the base of the 88-foot falls, the other to pools above them. The climb back out is in full sun; carry water.', anchors=p.anchors(R['A'])),
 dict(id='B', name='Escalante Natural Bridge and Cliff House Arch', short='Natural Bridge', official=4.2, unit='round trip', route='Out and back', time='2–3 hr', level='Moderate', color='--tB',
      desc='A sandy, mostly level trail up the Escalante River from the UT-12 bridge, through open benches of sagebrush below Navajo sandstone cliffs, with cottonwoods and willows along the water. Four shin-deep fords lead to the natural bridge at 1.6 miles (3.2 miles round trip); two more fords reach the skyline arch and cliff dwelling. Fords can be dangerous at high water.', anchors=p.anchors(R['B'])),
 dict(id='C', name='Lower Calf Creek Falls', short='Lower Falls', official=6.0, unit='round trip', route='Out and back', time='3–4 hr', level='Moderate', color='--tC',
      desc='The most popular hike in the Escalante canyons. A sandy trail follows Calf Creek up its canyon past ancient granaries, red pictographs and beaver ponds to a 126-foot waterfall. Little elevation change, but the soft sand and lack of shade make it tiring in summer heat. Bring plenty of water; the creek is not safe to drink untreated.', anchors=p.anchors(R['C'])),
]

pa = place_along
A_ = lambda k, f, s=1, o=240: pa(p, R[k], [f], s, o)[0]
an = []
an += [f'{{k:"beaver",at:{js(A_("C",.78,1,90))}}}', f'{{k:"beaver",at:{js(A_("B",.60,-1,110))}}}']
an += [f'{{k:"deer",path:{js(A_("C",.30,1,520)+A_("C",.34,1,520))},per:28}}', f'{{k:"deer",path:{js(A_("A",.22,-1,650)+A_("A",.30,-1,650))},per:26,ph:0.4}}']
an += [f'{{k:"squirrel",at:{js(A_("A",.72,1,300))},hop:true}}', f'{{k:"squirrel",at:{js(A_("C",.10,-1,240))},hop:true}}']
an += [f'{{k:"chipmunk",at:{js(A_("B",.30,1,220))},hop:true}}', f'{{k:"chipmunk",at:{js(A_("C",.55,1,240))},hop:true}}']
an += [f'{{k:"turkey",path:{js(A_("B",.80,1,600)+A_("B",.84,1,600))},per:30}}', f'{{k:"turkey",at:{js(A_("C",.18,1,620))}}}']
an += [f'{{k:"heron",at:{js(A_("B",.50,-1,140))}}}']
animals_js = '[\n ' + ',\n '.join(an) + '\n]'

bn = {s['name']: s for s in stops}
uth, eth, lth = [bn[k] for k in ('Upper Calf Creek Falls trailhead', 'Escalante River trailhead', 'Calf Creek Recreation Area')]
lm = f'''  gate({uth['x'] + 150},{uth['n'] + 120},0.5);gate({eth['x'] + 120},{eth['n'] + 80},0.3);gate({lth['x'] + 120},{lth['n'] - 120},0.2);
  // campground shelter at Calf Creek Recreation Area
  house({lth['x'] + 420},{lth['n'] - 380},0.9,0.4);
  // waterfalls: exaggerated in scale, solid water slab in front of a rock wall, pool on the downstream side.
  const fallTex=stripeTex("#E6F4F5","#FFFFFF",64,128,22,9,14);fallTex.repeat.set(1,1.5);
  const fallMat=new THREE.MeshBasicMaterial({{map:fallTex}});
  const rings=[],mist=[];
  function fall(x,n,dx,dn,w,h,sc){{const F=G(x,n);const d=new THREE.Vector3(dx,0,-dn).normalize();
    const wf=new THREE.Group();wf.position.copy(F);wf.rotation.y=Math.atan2(d.x,d.z);wf.scale.setScalar(sc);world.add(wf);
    const wt=new THREE.Mesh(new THREE.BoxGeometry(w,h,0.22),fallMat);wt.position.set(0,h/2,-0.25);wf.add(wt);
    part(wf,box,"#C98A5E",0,h/2,-0.62,w+0.9,h+0.25,0.55,1.04);
    part(wf,box,"#E7CDA8",0,h+0.1,-0.45,w+1.2,0.22,0.95,1.05);
    for(let i=0;i<3;i++){{part(wf,ico,i%2?"#D29A6C":"#B9774E",-(w/2+0.55)-i*0.15,h*(0.75-i*0.22),-0.3+i*0.25,0.55,h*0.3,0.5);part(wf,ico,i%2?"#B9774E":"#D29A6C",(w/2+0.55)+i*0.15,h*(0.72-i*0.2),-0.3+i*0.25,0.52,h*0.28,0.5);}}
    const pool=new THREE.Mesh(new THREE.CylinderGeometry(1,1,0.12,18),new THREE.MeshBasicMaterial({{color:"#8FCFD8"}}));pool.position.set(0,0.06,0.6);pool.scale.set(w*0.9+0.5,1,0.8);wf.add(pool);
    for(let i=0;i<2;i++){{const rg=new THREE.Mesh(new THREE.RingGeometry(0.45,0.55,24),new THREE.MeshBasicMaterial({{color:"#FFFFFF",transparent:true,side:THREE.DoubleSide}}));rg.rotation.x=-Math.PI/2;rg.position.set(0,0.14,0.5);wf.add(rg);rings.push(rg);}}
    for(let i=0;i<4;i++){{const m=new THREE.Mesh(new THREE.SphereGeometry(0.16,8,6),new THREE.MeshBasicMaterial({{color:"#FFFFFF",transparent:true}}));wf.add(m);mist.push({{m,ph:i/4,x:(i%3-1)*0.35}});}}
    return wf;}}
  fall({LFALL[0]},{LFALL[1]},{LDIR[0]},{LDIR[1]},0.8,2.6,1.0);   // Lower Calf Creek Falls, 126 ft
  fall({UFALL[0]},{UFALL[1]},{UDIR[0]},{UDIR[1]},0.8,2.0,1.0);   // Upper Calf Creek Falls, about 88 ft
  // Escalante Natural Bridge: a thick sandstone span across the mouth of a side canyon, parallel to the river
  const SAND="#EBCBA5",SAND2="#D7A578";
  {{const q=G({NB[0]},{NB[1]});const g=new THREE.Group();g.position.copy(q);g.rotation.y=Math.atan2({EDIR[0]},{-EDIR[1]})+Math.PI/2;world.add(g);
    g.scale.setScalar(1.5);part(g,new THREE.TorusGeometry(1.1,0.36,10,22,Math.PI),SAND,0,0.9,0,1,1.25,1.4,1.06);
    [-1,1].forEach(sd=>{{part(g,box,SAND2,sd*1.1,0.45,0,0.7,0.95,1.1,1.06);}});
    part(g,box,SAND,0,2.3,0,3.0,0.3,1.1,1.06);}}
  // Cliff House Arch: a skyline arch on the rim, small stone cliff dwelling in the wall below
  {{const q=G({ARCH[0]},{ARCH[1]});const g=new THREE.Group();g.position.copy(q);g.rotation.y=Math.atan2({EDIR[0]},{-EDIR[1]})+Math.PI/2;world.add(g);
    part(g,new THREE.TorusGeometry(0.55,0.17,8,18,Math.PI),SAND,0,0.75,0,1,1.1,1.4,1.06);
    [-1,1].forEach(sd=>part(g,box,SAND2,sd*0.55,0.38,0,0.3,0.76,0.4,1.06));
    part(g,box,"#B98A62",0,0.12,0.45,0.42,0.24,0.26,1.06);part(g,box,"#8E6545",0,0.12,0.59,0.1,0.14,0.02,0);}}
  // 100 Hands panel: a varnished rock face with red-painted hands, on the cliff north of the river
  {{const q=G({HANDS[0]},{HANDS[1]});const g=new THREE.Group();g.position.copy(q);g.rotation.y=Math.PI;world.add(g);
    part(g,box,"#9C6B4A",0,0.55,0,1.3,1.1,0.35,1.06);
    for(let i=0;i<7;i++)part(g,new THREE.SphereGeometry(1,6,5),"#B8322A",-0.48+i*0.16,0.55+((i%3)-1)*0.22,0.19,0.06,0.07,0.02,0);}}
  // Calf Creek pictographs: painted wall with three red figures, across the creek from the trail
  {{const q=G({PICT[0] - 180},{PICT[1]});const g=new THREE.Group();g.position.copy(q);g.rotation.y=Math.PI/2;world.add(g);
    part(g,box,"#A8714C",0,0.5,0,1.2,1.0,0.3,1.06);
    for(let i=0;i<3;i++){{part(g,box,"#B8322A",-0.32+i*0.32,0.5,0.16,0.08,0.38,0.02,0);part(g,new THREE.SphereGeometry(1,6,5),"#B8322A",-0.32+i*0.32,0.76,0.16,0.07,0.07,0.02,0);}}}}
  anim.water={{fallTex,rings,mist}};
'''

creeks = []
for nm, minor in [('Lower Calf Creek', True), ('Upper Calf Creek', True), ('Escalante River', False), ('Boulder Creek', True), ('Sand Creek', True), ('Willow Patch Creek', True)]:
    for i, wid in enumerate([w['id'] for w in p.W if w.get('n') == nm]):
        c = p.creek([wid], GRID, minor=minor)
        if c: creeks.append(dict(id=f"{nm.split()[0].lower()}{nm.split()[1].lower() if len(nm.split()) > 2 else ''}{i}", **c))
print('creeks', len(creeks), [c['id'] for c in creeks])

species_extra = {
 'pear_cc': 'pear_cc:{name:"Prickly pear",latin:"Opuntia spp.",color:"#F2C94A",shape:"pad",bloom:[5,6],sum:"Flat, spiny pads with yellow to pink flowers in late spring. Shallow roots and water-storing pads let it live on the dry benches above the creek.",rule:(d,e,g,s)=>d>220&&g<0.5}',
 'rabbit_cc': 'rabbit_cc:{name:"Rubber rabbitbrush",latin:"Ericameria nauseosa",color:"#E9C23A",shape:"dome",bloom:[8,9,10],sum:"A gray-green shrub of sandy flats that turns bright yellow in late summer and fall. Native peoples used it for dye.",rule:(d,e,g,s)=>d>260&&g<0.4}',
 'skunk_cc': 'skunk_cc:{name:"Skunkbush sumac",latin:"Rhus trilobata",color:"#D4553A",shape:"berry",bloom:[4,5],fruit:[6,7,8],sum:"A shrub with three-lobed leaves and sticky red berries, named for the smell of its crushed leaves. Its berries and branches were valued by Native Americans.",rule:(d,e,g,s)=>d<600&&g<0.6}',
 'mahonia_cc': 'mahonia_cc:{name:"Hollygrape",latin:"Mahonia spp.",color:"#F0CF3C",shape:"berry",bloom:[4,5],fruit:[6,7],sum:"Holly-like leaves, small yellow flowers in spring and grape-like blue berries. Its roots give a yellow dye.",rule:(d,e,g,s)=>d>120&&g<0.7}',
 'dogwood_cc': 'dogwood_cc:{name:"Red-osier dogwood",latin:"Cornus sericea",color:"#F4F1E6",shape:"dome",bloom:[5,6],sum:"A streamside shrub with smooth red bark and flat clusters of white flowers in spring, along Calf Creek near the falls.",rule:(d,e,g,s)=>d<200}',
 'horsetail_cc': 'horsetail_cc:{name:"Horsetail",latin:"Equisetum spp.",color:"#5F8F4A",shape:"fern",bloom:[],sum:"Jointed green stems in wet ground by the creek, a plant family as old as the dinosaurs. Pioneers used its gritty stems to scour pots.",rule:(d,e,g,s)=>d<140}',
}

tree_rule = 'if(cd<300){type=tr()<0.6?"syc":"oak";p=0.3;}\nelse if(mk<0.25||g>0.5){type=null;}\nelse{type=tr()<0.5?"conifer":"shrub";p=0.025;}'

PH = json.load(open('calfcreek/photos.json')) if os.path.exists('calfcreek/photos.json') else {}
cfg = dict(
    title='Lower Calf Creek Falls', aria='Lower Calf Creek Falls, Upper Calf Creek Falls and Escalante Natural Bridge in Grand Staircase-Escalante National Monument, Utah', h1='Calf Creek Falls &amp; Escalante Natural Bridge',
    canyons=creeks, trails=trails, stops=stops, order=order,
    species=list(species_extra), species_extra=species_extra,
    flora={'A': ['pear_cc', 'rabbit_cc', 'mahonia_cc'], 'B': ['rabbit_cc', 'skunk_cc', 'horsetail_cc', 'pear_cc'], 'C': ['pear_cc', 'skunk_cc', 'mahonia_cc', 'dogwood_cc', 'horsetail_cc', 'rabbit_cc']},
    wild=['beaver', 'deer', 'squirrel', 'chipmunk', 'turkey', 'heron', 'goldeneagle', 'hawk', 'vulture', 'swift', 'jay', 'raven', 'bluebird', 'woodpecker', 'kingfisher'],
    wild_sum={'beaver': ('American beaver', 'Beavers dam Calf Creek on the way to the lower falls; look for the ponds, marsh, a lodge and gnawed stumps. They live along the Escalante River too. Most active at dawn and dusk.'),
              'deer': ('Mule deer', 'Browses the sagebrush benches and creek bottoms in the early morning and evening.'),
              'squirrel': ('Rock squirrel', 'A big gray ground squirrel with a bushy tail, often seen on boulders by the trails and around the campground. Do not feed it.'),
              'chipmunk': ('Hopi chipmunk', 'A small orange-and-gray chipmunk of the Colorado Plateau that darts among the sandstone ledges and shrubs.'),
              'turkey': ('Wild turkey', 'Flocks forage in the creek bottoms and along the Escalante River.'),
              'heron': ('Great blue heron', 'Stands still in the shallows of the Escalante River and Calf Creek, waiting for fish.'),
              'goldeneagle': ('Golden eagle', 'Named in the Calf Creek trail guide; soars high over the canyon rims hunting rabbits and other small animals.'),
              'hawk': ('Red-tailed hawk', 'Circles over the slickrock and the open benches above the canyons.'),
              'vulture': ('Turkey vulture', 'Rides the warm air along the cliffs from spring to fall, rocking on wings held in a shallow V.'),
              'swift': ('White-throated swift', 'Fast black-and-white birds that race along the sandstone walls with high, chattering calls and nest in cracks in the cliffs.'),
              'jay': ('Woodhouse’s scrub-jay', 'A noisy blue-and-gray jay of the pinyon-juniper and the oak thickets along the trails.'),
              'raven': ('Common raven', 'Large black birds that soar and tumble along the canyon walls; listen for deep croaks.'),
              'bluebird': ('Western bluebird', 'A small blue-and-rust bird of the pinyon-juniper and the canyon, listed in the Calf Creek trail guide.'),
              'woodpecker': ('Downy woodpecker', 'The smallest North American woodpecker, tapping on the box elders and cottonwoods along the creek; named in the trail guide.'),
              'kingfisher': ('Belted kingfisher', 'Rattles up and down the water and dives for small fish from branches over the river and creek.')},
    grid=GRID, step=STEP, dem_b64=b64, tile=TILE, ve=2.0, ridge_ft=RIDGE,
    palette='redrock', tree_rule=tree_rule, rock_all_aspects=True,
    landmarks=lm, animals_js=animals_js,
    extra_js='TRAILS.forEach(T=>{const g={A:560}[T.id];if(g)T.gain=g;});',
    overview=dict(h2='Calf Creek and the Escalante River',
                  p='Calf Creek runs year round through a deep canyon of Navajo sandstone off Utah Highway 12, in Grand Staircase-Escalante National Monument, and drops over two waterfalls before it meets the Escalante River. C, the most popular hike here, follows the creek from the Calf Creek Recreation Area past 1,000-year-old granaries and pictographs to 126-foot Lower Calf Creek Falls. A drops off the slickrock rim to Upper Calf Creek Falls. B fords the Escalante River to Escalante Natural Bridge and a skyline arch. Pick a trail to focus the model; click anything on it for a quick note.',
                  numbers='The three trails start at different trailheads along UT-12 and share no stops, so every stop is lettered by its trail: C3 is the third stop on Trail C.',
                  wild_h='Wildlife around Calf Creek',
                  note='Grand Staircase-Escalante National Monument (BLM), Utah Highway 12 between Escalante and Boulder. Calf Creek Recreation Area is about 15 miles east of Escalante: $5 day-use fee per vehicle (Interagency passes accepted), open year round, restrooms and water, 13 first-come campsites; pets on leash. The Upper Calf Creek Falls and Escalante River trailheads are a few miles north and south on UT-12. Status (November 2026): open, no closures posted. Rockfall is a real hazard at Lower Calf Creek Falls; carry plenty of water, and pack out all trash and human waste. Terrain from USGS elevation data, stylized; not for navigation.'),
    links={'A': [('Upper Calf Creek Falls · Visit Utah', 'https://www.visitutah.com/places-to-go/parks-outdoors/grand-staircase-escalante/hiking/upper-calf-creek-falls'), ('Upper Calf Creek Falls · American Southwest', 'https://www.americansouthwest.net/utah/grand_staircase_escalante/upper_calf_creek.html')],
           'B': [('Escalante Natural Bridge · Visit Utah', 'https://visitutah.com/places-to-go/parks-outdoors/grand-staircase-escalante/hiking/escalante-natural-bridge'), ('Escalante Natural Bridge · Hiking Project', 'https://hikingproject.com/gem/580/escalante-natural-bridge'), ('100 Hands Panel · Road Trip Ryan', 'https://www.roadtripryan.com/go/t/utah/escalante/100-hands-panel')],
           'C': [('Lower Calf Creek Falls Trail · BLM', 'https://www.blm.gov/visit/lower-calf-creek-falls-trail'), ('Calf Creek trail guide · BLM', 'https://www.npshistory.com/publications/blm/grand-staircase-escalante/brochures/calf-creek-falls.pdf'), ('Falling rocks at Lower Calf Creek Falls · BLM', 'https://www.blm.gov/announcement/video-blm-warns-dangerous-falling-rocks-lower-calf-creek-falls')]},
    viewaz={'all': 0.35, 'A': 0.35, 'B': 0.35, 'C': 0.35},
    zoomcap={'A': 6.0, 'B': 4.0, 'C': 3.4},
    stop_photos=PH.get('stop', {}), flower_photos=PH.get('flower', {}), animal_photos=PH.get('animal', {}),
)
json.dump({k: {'mi': R[k]['mi'], 'gain': R[k]['gain'], 'lo': R[k]['lo'], 'hi': R[k]['hi']} for k in R}, open('calfcreek/stats.json', 'w'))
os.makedirs('/home/claude/site/out/lower-calf-creek-falls', exist_ok=True)
print(build(cfg, '/home/claude/site/out/lower-calf-creek-falls/index.html'))
