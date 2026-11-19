from lib import *
from mk_sheet import build
import sys, json, os
import numpy as np

os.chdir('/home/claude/parks')
p = Park('yscanyon', 44.7177, -110.4965)   # origin near the brink of the Lower Falls
WTH = (-995, -3630)      # Wapiti Lake Trailhead, South Rim Drive at Chittenden Bridge (OSM trail end)
BLF_TH = (-590, 497)     # Brink of the Lower Falls Trail leaves the North Rim Trail (OSM way 24066562 end)
BLF = (50, 180)          # Brink of the Lower Falls viewpoint (OSM)
UFV = (-190, -1112)      # Upper Falls View (OSM viewpoint)
UT = (338, -407)         # top of Uncle Tom's Trail on the South Rim Trail (OSM way junction)
AP = (4421, 1298)        # Artist Point (OSM viewpoint)
BUF = (-823, -1694)      # Brink of the Upper Falls (OSM viewpoint)
CRY = (-1256, -702)      # Crystal Falls overlook (OSM viewpoint)
LRJ = (2211, 1374)       # North Rim Trail junction with the Lookout Point / Red Rock Point trails (OSM)
GV = (3140, 1852)        # Grand View spur leaves the North Rim Trail (OSM way 75088154)
IP = (6910, 2537)        # Inspiration Point (OSM viewpoint)
R = {}
R['A'] = route_xy(p, BLF_TH, BLF, BLF_TH)
R['B'] = route_xy(p, WTH, (-487, -2150), UFV, UT, (676, -396), (3653, 385), AP)
R['C'] = route_xy(p, WTH, (-1415, -3523), (-1416, -2438), BUF, CRY, BLF_TH, (1267, 1240), LRJ, (2571, 1435), GV, (5481, 4205), IP)
for k in R: Park.smooth_E(R[k], 9); p.describe(R[k], k)
ST = snap_stops(p, R, {
    'S1': (WTH[0], WTH[1], 'BC'), 'S2': (BLF_TH[0], BLF_TH[1], 'AC'),
    'A1': (BLF[0], BLF[1], 'A'),
    'B1': (UFV[0], UFV[1], 'B'), 'B2': (UT[0], UT[1], 'B'), 'B3': (AP[0], AP[1], 'B'),
    'C1': (BUF[0], BUF[1], 'C'), 'C2': (CRY[0], CRY[1], 'C'), 'C3': (LRJ[0], LRJ[1], 'C'), 'C4': (GV[0], GV[1], 'C'), 'C5': (IP[0], IP[1], 'C'),
})
TILE = (-4400, 9700, -6400, 6900)
GRID = (-4700, 10000, -6700, 7200)
if 'plot' in sys.argv:
    from plot import plot
    plot(p, TILE, 'yscanyon/routes2.png', routes=R, stops=ST, title='yscanyon', grid=500)
    sys.exit()

STEP = 75
b64, NX, NN = p.dem_b64(*GRID, STEP=STEP)
RIDGE = int(round(float(np.percentile(p.grid, 75)), -1))
print('grid', NX, NN, NX * NN, p.grid.min(), p.grid.max(), 'p75', RIDGE)

S = lambda i: ST[i]
def st(i, trails, name, desc): return dict(id=i, trails=list(trails), x=S(i)[0], n=S(i)[1], name=name, desc=desc)
stops = [
 st('S1', 'BC', 'Wapiti Lake Trailhead', 'A parking area on South Rim Drive just east of Chittenden Bridge over the Yellowstone River. The South Rim Trail starts a few steps away; the North Rim Trail starts across the bridge on the west bank.'),
 st('S2', 'AC', 'Brink of the Lower Falls trailhead', 'Where the Brink of the Lower Falls Trail leaves the North Rim Trail, beside the Brink of the Lower Falls parking area on North Rim Drive.'),
 st('A1', 'A', 'Brink of the Lower Falls', 'A platform at the very lip of the Lower Falls, where the Yellowstone River drops 308 feet into the canyon. The trail down drops about 600 feet in switchbacks; the climb back is steep.'),
 st('B1', 'B', 'Upper Falls View', 'The first viewpoint on South Rim Drive, with a straight-on view of the 109-foot Upper Falls. Crystal Falls on Cascade Creek is visible across the canyon from the trail just east of here.'),
 st('B2', 'B', 'Uncle Tom’s Trail (closed)', 'Top of the steel staircase that once dropped toward the base of the Lower Falls. Begun in 1896 by Herbert “Uncle Tom” Richardson, it has been closed since 2019 over structural safety concerns, and the park does not plan to reopen it.'),
 st('B3', 'B', 'Artist Point', 'A viewing platform on the south wall about a mile downstream of the Lower Falls, looking up the yellow and orange canyon to the falls. One of the most photographed views in Yellowstone; the second viewing area is wheelchair accessible.'),
 st('C1', 'C', 'Brink of the Upper Falls', 'A short spur and a stone platform right beside the 109-foot Upper Falls, where the river pours over the edge a few yards away.'),
 st('C2', 'C', 'Crystal Falls overlook', 'A rim viewpoint over Crystal Falls, where Cascade Creek drops about 130 feet toward the Yellowstone River just before it joins it.'),
 st('C3', 'C', 'Lookout Point & Red Rock Point', 'A short spur leads to Lookout Point and its classic view of the Lower Falls. From there the Red Rock Point trail drops about 500 feet in under 0.4 mile on switchbacks, steps and boardwalk for a closer view.'),
 st('C4', 'C', 'Grand View', 'A viewpoint down the canyon and the river. Paved, accessible walks run from Lookout Point to Grand View.'),
 st('C5', 'C', 'Inspiration Point', 'The end of the trail, on a point jutting into the canyon with a long view downstream and a distant look back at the Lower Falls. The overlook was rebuilt with a larger viewing area and reopened in 2018.'),
]
stops, order = renumber(p, R, stops)
print(order, [(s['id'], s['name']) for s in stops])
trails = [
 dict(id='A', name='Brink of the Lower Falls', short='Brink of Lower Falls', official=0.7, unit='round trip', route='Out and back', time='30–45 min', level='Strenuous', color='--tA',
      desc='A paved trail that switchbacks about 600 feet down the canyon wall in 0.4 mile to a platform at the top of the 308-foot Lower Falls. Short but very steep coming back up; the park advises against it for people with heart, lung or other health conditions. Closed in winter.', anchors=p.anchors(R['A'])),
 dict(id='B', name='South Rim Trail to Artist Point', short='South Rim Trail', official=2.1, unit='one way', route='One way', time='1–1.5 hr', level='Easy', color='--tB',
      desc='From Chittenden Bridge the trail climbs briefly, then follows the south rim past Upper Falls View, the top of the closed Uncle Tom’s Trail and several views of the Lower Falls to Artist Point. Small ups and downs, steep drop-offs. Walk back the same way or use a car at Artist Point.', anchors=p.anchors(R['B'])),
 dict(id='C', name='North Rim Trail to Inspiration Point', short='North Rim Trail', official=3.8, unit='one way', route='One way', time='2–3 hr', level='Moderate', color='--tC',
      desc='Crosses Chittenden Bridge and follows the north rim past the brinks of both falls, Crystal Falls, Lookout Point and Grand View to Inspiration Point. Some stretches run beside North Rim Drive, others through quiet lodgepole forest. Sources give 3.2–3.8 miles depending on start; the side trails down to the falls add steep climbs.', anchors=p.anchors(R['C'])),
]

pa = place_along
A_ = lambda k, f, s=1, o=240: pa(p, R[k], [f], s, o)[0]
an = []
an += [f'{{k:"bison",path:{js(A_("C",.05,-1,700)+A_("C",.07,-1,700))},per:44}}', f'{{k:"bison",path:{js(A_("B",.10,1,900)+A_("B",.12,1,900))},per:46,ph:0.4}}']
an += [f'{{k:"elk",path:{js(A_("C",.62,1,520)+A_("C",.64,1,520))},per:36}}']
an += [f'{{k:"moose",path:{js(A_("C",.84,1,420)+A_("C",.86,1,420))},per:40}}']
an += [f'{{k:"grizzly",path:{js(A_("B",.55,-1,1100)+A_("B",.58,-1,1100))},per:40}}']
an += [f'{{k:"bear",path:{js(A_("C",.74,-1,700)+A_("C",.77,-1,700))},per:38,ph:0.3}}']
an += [f'{{k:"coyote",path:{js(A_("B",.85,-1,800)+A_("B",.88,-1,800))},per:26}}']
an += [f'{{k:"squirrel",at:{js(A_("C",.45,1,160))}}}', f'{{k:"chipmunk",at:{js(A_("B",.32,-1,160))},hop:true}}', f'{{k:"chipmunk",at:{js(A_("C",.95,1,170))},hop:true}}']
animals_js = '[\n ' + ',\n '.join(an) + '\n]'

bn = {s['name']: s for s in stops}
th, s2, blf, ufv, ap, buf, cry, lr, gv, ip = [bn[k] for k in ('Wapiti Lake Trailhead', 'Brink of the Lower Falls trailhead', 'Brink of the Lower Falls', 'Upper Falls View', 'Artist Point', 'Brink of the Upper Falls', 'Crystal Falls overlook', 'Lookout Point & Red Rock Point', 'Grand View', 'Inspiration Point')]
LF, UF = (54, 102), (-860, -1750)    # OSM: Lower / Upper Yellowstone Falls
CF = (-1268, -364)                   # Crystal Falls (GNIS point via Natural Atlas: 44.7167, -110.5014), on Cascade Creek flowing south
lm = f'''  gate({th['x'] + 60},{th['n'] - 60},2.6);gate({s2['x'] - 60},{s2['n'] + 50},1.6);
  // Waterfalls drawn exaggerated, with volume: water slab, rock lip, plunge pool, mist. Direction = river flow (from OSM).
  const fallTex=stripeTex("#9ED3E8","#FFFFFF",64,128,22,9,14);fallTex.repeat.set(1,1.5);
  const fallMat=new THREE.MeshBasicMaterial({{map:fallTex}});
  const rings=[],mist=[];
  function fall(x,n,dx,dn,w,h,sc){{const F=G(x,n);const d=new THREE.Vector3(dx,0,-dn).normalize();
    const wf=new THREE.Group();wf.position.copy(F);wf.rotation.y=Math.atan2(d.x,d.z);wf.scale.setScalar(sc);world.add(wf);
    const wt=new THREE.Mesh(new THREE.BoxGeometry(w,h,0.22),fallMat);wt.position.set(0,h/2,-0.25);wf.add(wt);
    part(wf,box,"#C9A66B",0,h/2,-0.62,w+0.9,h+0.25,0.55,1.04);
    part(wf,box,"#E2C98F",0,h+0.1,-0.45,w+1.2,0.22,0.95,1.05);
    {{const ch=new THREE.Mesh(new THREE.BoxGeometry(w,0.06,1.6),fallMat);ch.position.set(0,h+0.24,-1.0);wf.add(ch);}}
    for(let i=0;i<3;i++){{part(wf,ico,i%2?"#D9B77A":"#C79A5B",-(w/2+0.55)-i*0.15,h*(0.75-i*0.22),-0.3+i*0.25,0.55,h*0.3,0.5);part(wf,ico,i%2?"#C79A5B":"#E0C48A",(w/2+0.55)+i*0.15,h*(0.72-i*0.2),-0.3+i*0.25,0.52,h*0.28,0.5);}}
    const pool=new THREE.Mesh(new THREE.CylinderGeometry(1,1,0.12,18),new THREE.MeshBasicMaterial({{color:"#7FC4C9"}}));pool.position.set(0,0.06,0.55);pool.scale.set(w*0.9+0.5,1,0.75);wf.add(pool);
    for(let i=0;i<2;i++){{const rg=new THREE.Mesh(new THREE.RingGeometry(0.45,0.55,24),new THREE.MeshBasicMaterial({{color:"#FFFFFF",transparent:true,side:THREE.DoubleSide}}));rg.rotation.x=-Math.PI/2;rg.position.set(0,0.14,0.45);wf.add(rg);rings.push(rg);}}
    for(let i=0;i<4;i++){{const m=new THREE.Mesh(new THREE.SphereGeometry(0.16,8,6),new THREE.MeshBasicMaterial({{color:"#FFFFFF",transparent:true}}));wf.add(m);mist.push({{m,ph:i/4,x:(i%3-1)*0.35}});}}
    return wf;}}
  fall({LF[0]},{LF[1]},1,-0.15,1.4,5.2,1.25);       // Lower Falls, 308 ft, river flowing east into the canyon
  fall({UF[0]},{UF[1]},0.45,0.9,1.3,2.2,1.1);        // Upper Falls, 109 ft, river flowing north-northeast
  fall({CF[0]},{CF[1]},0.1,-1,0.7,2.5,0.85);          // Crystal Falls on Cascade Creek, about 130 ft
  // viewing platforms: deck on posts with a railing, facing the falls or the canyon
  function deck(x,n,ry,sc){{const q=G(x,n);const g=new THREE.Group();g.position.copy(q);g.rotation.y=ry;g.scale.setScalar(sc);world.add(g);
   part(g,box,"#B8AE9C",0,0.35,0,1.4,0.16,1.0,1.06);[[-0.62,-0.42],[0.62,-0.42],[-0.62,0.42],[0.62,0.42]].forEach(([a,b])=>part(g,box,"#8C8476",a,0.15,b,0.1,0.35,0.1,0));
   part(g,box,"#5C564C",0,0.64,0.48,1.4,0.07,0.07,0);part(g,box,"#5C564C",-0.68,0.64,0,0.07,0.07,1.0,0);part(g,box,"#5C564C",0.68,0.64,0,0.07,0.07,1.0,0);}}
  const toward=(a,b)=>Math.atan2(b[0]-a[0],-(b[1]-a[1]));
  deck({blf['x']},{blf['n']},toward([{blf['x']},{blf['n']}],[{LF[0]},{LF[1]}]),1.4);
  deck({buf['x']},{buf['n']},toward([{buf['x']},{buf['n']}],[{UF[0]},{UF[1]}]),1.3);
  deck({ap['x']},{ap['n']},toward([{ap['x']},{ap['n']}],[{LF[0]},{LF[1]}]),1.8);
  deck({ufv['x']},{ufv['n']},toward([{ufv['x']},{ufv['n']}],[{UF[0]},{UF[1]}]),1.3);
  deck({cry['x']},{cry['n']},toward([{cry['x']},{cry['n']}],[{CF[0]},{CF[1]}]),1.1);
  deck(2048,1159,toward([2048,1159],[{LF[0]},{LF[1]}]),1.4);    // Lookout Point (OSM)
  deck(3225,1795,toward([3225,1795],[4421,1298]),1.3);           // Grand View (OSM)
  deck({ip['x']},{ip['n']},toward([{ip['x']},{ip['n']}],[{LF[0]},{LF[1]}]),1.8);
  anim.water={{fallTex,rings,mist}};
'''

creeks = []
for nm, minor in [('Yellowstone River', False), ('Cascade Creek', True)]:
    for i, wid in enumerate([w['id'] for w in p.W if w.get('n') == nm and w['k'] in ('river', 'stream')]):
        c = p.creek([wid], GRID, minor=minor)
        if c: creeks.append(dict(id=f"{nm.split()[0].lower()}{i}", **c))
print('creeks', len(creeks))

SPX = {
 'fireweed_yc': 'fireweed_yc:{name:"Fireweed",latin:"Chamaenerion angustifolium",color:"#D9539A",shape:"spike",bloom:[7,8,9],sum:"Tall magenta spikes in openings and old burns in the lodgepole forest along both rims, blooming midsummer.",rule:(d,e,g,s)=>d>80&&g<0.8}',
 'lupine_yc': 'lupine_yc:{name:"Silky lupine",latin:"Lupinus sericeus",color:"#6E6BD3",shape:"spike",bloom:[6,7],sum:"Blue-purple pea flowers over silvery leaves, common in dry clearings and along trail edges in early summer.",rule:(d,e,g,s)=>d>100&&g<0.6}',
 'paint_yc': 'paint_yc:{name:"Indian paintbrush",latin:"Castilleja spp.",color:"#E0452F",shape:"spike",bloom:[6,7,8],sum:"Red-orange bracts, not petals, give paintbrush its color. Wyoming’s state flower; scattered in meadows and forest edges near the rims.",rule:(d,e,g,s)=>d>80&&g<0.7}',
 'yarrow_yc': 'yarrow_yc:{name:"Yarrow",latin:"Achillea millefolium",color:"#F3EFE2",shape:"dome",bloom:[6,7,8],sum:"Flat-topped clusters of tiny white flowers over ferny, aromatic leaves, along trail edges and dry openings.",rule:(d,e,g,s)=>d>60&&g<0.7}',
 'arnica_yc': 'arnica_yc:{name:"Heartleaf arnica",latin:"Arnica cordifolia",color:"#F2C523",shape:"cup",bloom:[6,7],sum:"Yellow daisy-like flowers over heart-shaped leaves, one of the most common wildflowers in the shade of Yellowstone’s lodgepole forests.",rule:(d,e,g,s)=>d>120&&g<0.5}',
 'harebell_yc': 'harebell_yc:{name:"Harebell",latin:"Campanula rotundifolia",color:"#7D86D9",shape:"cup",bloom:[7,8,9],sum:"Nodding blue bells on thin stems, often on rocky ground and dry slopes near the canyon rim late in summer.",rule:(d,e,g,s)=>g>0.3&&g<1.1}',
}

TREE = '''if(g>0.7)type=null;
    else if(mk<0.25){type="conifer";p=0.05;}
    else{type=tr()<.97?"conifer":"shrub";p=0.3+cl*.2;}'''
PH = json.load(open('yscanyon/photos.json')) if os.path.exists('yscanyon/photos.json') else {}
OSP_RARE = 'Rare here: this is one of two river canyons the park names as osprey nesting habitat, where they build on rock pinnacles in view of the rim; the park-wide population has declined, with 27 occupied nests monitored in 2023.'
cfg = dict(
    title='Grand Canyon of the Yellowstone', aria='The Grand Canyon of the Yellowstone with the Upper and Lower Falls, Yellowstone National Park, Wyoming', h1='Grand Canyon of the Yellowstone',
    canyons=creeks, trails=trails, stops=stops, order=order,
    species=list(SPX), species_extra=SPX,
    flora={'A': ['arnica_yc', 'harebell_yc', 'yarrow_yc'], 'B': ['lupine_yc', 'paint_yc', 'yarrow_yc', 'harebell_yc', 'arnica_yc'], 'C': ['fireweed_yc', 'lupine_yc', 'paint_yc', 'arnica_yc', 'yarrow_yc']},
    wild=['osprey', 'bison', 'elk', 'moose', 'grizzly', 'bear', 'coyote', 'squirrel', 'chipmunk', 'eagle', 'raven'],
    wild_sum={
     'osprey': ('Osprey', OSP_RARE + ' Look for their big stick nests, up to five feet across, on spires below Artist Point, Lookout Point and Grand View from late April to early September.'),
     'bison': ('American bison', 'Herds from nearby Hayden Valley graze the meadows south of the canyon and often walk the roads near Chittenden Bridge from spring through the fall rut. Stay at least 25 yards away.'),
     'elk': ('Elk', 'Graze the forest openings and meadows near both rims, mostly at dawn and dusk. Give them at least 25 yards, especially during the fall rut.'),
     'moose': ('Moose', 'Occasionally seen in the wet forest and meadows along the North Rim Trail between Grand View and Inspiration Point.'),
     'grizzly': ('Grizzly bear', 'Grizzlies hunt elk and bison calves in Hayden Valley in spring and early summer and range through the forest around the canyon. Carry bear spray and stay 100 yards away.'),
     'bear': ('Black bear', 'Black bears also live in the forests around Canyon. Keep food packed away and give any bear at least 100 yards.'),
     'coyote': ('Coyote', 'Nearly always seen in Hayden Valley just south of the canyon, and often trotting along the rim drives hunting voles.'),
     'squirrel': ('Red squirrel', 'A small, noisy squirrel of the lodgepole forest that chatters from tree trunks and piles pine cone scales on the ground.'),
     'chipmunk': ('Least chipmunk', 'A tiny striped chipmunk that darts among logs and rocks beside the rim trails. Do not feed it.'),
     'eagle': ('Bald eagle', 'Bald eagles fish along the Yellowstone River and are sometimes seen from the rim viewpoints with binoculars.'),
     'raven': ('Common raven', 'Big black birds that ride the updrafts over the canyon and patrol the overlook parking lots. Keep food packed away.'),
    },
    birds=['osprey', 'eagle', 'raven'],
    grid=GRID, step=STEP, dem_b64=b64, tile=TILE, ve=2.2, ridge_ft=RIDGE,
    palette={"ground": "#C9E2C4", "groundN": "#B3D3B0", "conifer": "#2F5A3E", "riparian": "#E4E9D8", "ridge": "#D9DDB8", "rock": "#E2C98F", "rockDeep": "#C79A5B"},
    tree_rule=TREE, rock_all_aspects=True,
    landmarks=lm, animals_js=animals_js,
    extra_js='TRAILS.forEach(T=>{const g={A:600}[T.id];if(g)T.gain=g;});',
    overview=dict(h2='Two waterfalls and a yellow canyon',
                  p='Below the Upper and Lower Falls, the Yellowstone River has cut a canyon of yellow, orange and white rock, softened and colored by old hot-spring activity. A drops down a steep switchback trail to the brink of the 308-foot Lower Falls. B follows the South Rim Trail from Chittenden Bridge to Artist Point. C follows the North Rim Trail past the brinks of both falls, Lookout Point and Grand View to Inspiration Point. Pick a trail to focus the model; click anything on it for a quick note.',
                  numbers='Plain numbers mark spots more than one trail passes: the Wapiti Lake Trailhead (B and C) and the Brink of the Lower Falls trailhead (A and C). Lettered stops belong to one trail: C3 is the third stop on Trail C. Falls and viewing platforms are drawn larger than life.',
                  wild_h='Wildlife around the canyon',
                  note='Yellowstone National Park, Wyoming. The rim viewpoints are on North Rim Drive and South Rim Drive, just south of Canyon Village; park entrance fee required. Status (November 2026): most park roads closed to regular vehicles on November 1, 2026, so the canyon can’t be reached by car until spring; snowcoach and snowmobile travel begins December 15. The Brink of the Lower Falls Trail is closed in winter. Uncle Tom’s Trail is permanently closed. Rims have steep, unfenced drop-offs; stay on trails. Stay 100 yards from bears and wolves and 25 yards from other wildlife. No pets on trails. Terrain from USGS elevation data, stylized; not for navigation.'),
    links={'A': [('Brink of the Lower Falls Trail · NPS', 'https://www.nps.gov/thingstodo/yell-trail-brink-of-the-lower-falls.htm'), ('Grand Canyon of the Yellowstone · NPS', 'https://www.nps.gov/thingstodo/yell-grand-canyon-of-the-yellowstone.htm')],
           'B': [('South Rim Trail · Noah Lang', 'https://noahlangphotography.com/blog/south-rim-trail-yellowstone-national-park'), ('Artist Point · Hikespeak', 'https://www.hikespeak.com/trails/artist-point-grand-canyon-of-the-yellowstone-river/'), ('Uncle Tom’s Trail closure · Cowboy State Daily', 'https://cowboystatedaily.com/2023/12/31/yellowstones-uncle-toms-trail-is-steep-exhilarating-and-permanently-closed')],
           'C': [('North Rim Trail · Hikespeak', 'https://www.hikespeak.com/trails/north-rim-trail-grand-canyon-of-the-yellowstone-river/'), ('North Rim Trail · Hiking Project', 'https://hikingproject.com/trail/7008885/north-rim-trail'), ('North Rim Trail · Teton Hiking Trails', 'https://www.tetonhikingtrails.com/north-rim-trail.htm')]},
    viewaz={'all': 3.7, 'A': 3.7, 'B': 3.7, 'C': 3.7},
    zoomcap={'A': 4.5, 'B': 3.2, 'C': 2.4},
    stop_photos=PH.get('stop', {}), flower_photos=PH.get('flower', {}), animal_photos=PH.get('animal', {}),
)
json.dump({k: {'mi': R[k]['mi'], 'gain': R[k]['gain'], 'lo': R[k]['lo'], 'hi': R[k]['hi']} for k in R}, open('yscanyon/stats.json', 'w'))
os.makedirs('/home/claude/site/out/yellowstone-grand-canyon', exist_ok=True)
print(build(cfg, '/home/claude/site/out/yellowstone-grand-canyon/index.html'))
