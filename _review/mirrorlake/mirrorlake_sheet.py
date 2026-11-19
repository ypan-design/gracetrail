from lib import *
from mk_sheet import build
import sys, json, os, re, math
import numpy as np

os.chdir('/home/claude/parks')
exec(open('/home/claude/parks/mirrorlake_routes.py').read())
for k in R: Park.smooth_E(R[k], 25); p.describe(R[k], k)

VP = (2727, 3082)     # OSM viewpoint on the west shore of Mirror Lake (direction 45)
AHW = (6750, 3916)    # Ahwiyah Point (OSM peak)
HD = (7699, 2185)     # Half Dome summit (OSM peak)

def nearest(r, q, lo=0.0, hi=1.0):
    P = r['pts']; n = len(P)
    best = min(range(int(lo * n), int(hi * n)), key=lambda i: math.dist((P[i][0], P[i][1]), q))
    return (P[best][0], P[best][1])
RF = nearest(R['B'], AHW, 0.55, 0.95)      # point on the south-side trail below Ahwiyah Point
CV = nearest(R['C'], (5150, 9300), 0.5, 1.0)  # mid-climb on the Snow Creek switchbacks
print('RF', RF, 'CV', CV)

ST = snap_stops(p, R, {
    'S1': (TH[0], TH[1], 'ABC'), 'S2': (VP[0], VP[1], 'ABC'), 'S3': (SCJ[0], SCJ[1], 'BC'),
    'B1': (EB[0], EB[1], 'B'), 'B2': (RF[0], RF[1], 'B'),
    'C1': (CV[0], CV[1], 'C'), 'C2': (SJ[0], SJ[1], 'C'), 'C3': (FB[0], FB[1], 'C'),
})
TILE = (-4200, 11000, -3300, 15500)
GRID = (-4500, 11300, -3600, 15800)
if 'plot' in sys.argv:
    from plot import plot
    plot(p, (-1000, 9500, -800, 13000), 'mirrorlake/routes.png', routes=R, stops=ST, title='mirrorlake', grid=1000)
    plot(p, (1800, 4200, 1800, 4400), 'mirrorlake/routes_lake.png', routes=R, stops=ST, title='lake', grid=250)
    sys.exit()

STEP = 100
b64, NX, NN = p.dem_b64(*GRID, STEP=STEP)
RIDGE = int(round(float(np.percentile(p.grid, 75)), -1))
print('grid', NX, NN, NX * NN, p.grid.min(), p.grid.max(), 'p75', RIDGE)

S = lambda i: ST[i]
def st(i, trails, name, desc): return dict(id=i, trails=list(trails), x=S(i)[0], n=S(i)[1], name=name, desc=desc)
stops = [
 st('S1', 'ABC', 'Mirror Lake trailhead', 'Valley shuttle stop 17, on the road between Upper Pines and Happy Isles, at about 4,000 feet. There is no parking here: park at Curry Village or elsewhere in the east valley and ride the free shuttle. No drinking water at the trailhead or on the trail.'),
 st('S2', 'ABC', 'Mirror Lake', 'A pool in Tenaya Creek behind a natural dam of rockfall boulders, at the end of the first, paved mile. Exhibits here tell how ice and sand were once taken from the lake. It holds water mostly in spring and early summer, when calm water reflects Mount Watkins and the canyon walls; by late summer it is largely a meadow.'),
 st('S3', 'BC', 'Snow Creek Trail junction', 'Past the lake the loop follows Tenaya Creek up the canyon to where the Snow Creek Trail turns off and starts its long series of switchbacks up the north wall.'),
 st('B1', 'B', 'Tenaya Creek bridges', 'At the east end of the loop the trail crosses Tenaya Creek on footbridges and turns back down the canyon on the south side. Do not try to rock-hop the creek: it runs fast and deep in spring.'),
 st('B2', 'B', 'Ahwiyah Point rockfall', 'On March 28, 2009, about 115,000 tons of granite fell some 1,800 feet from Ahwiyah Point, beside Half Dome, flattening hundreds of trees and burying part of this trail. The loop was rebuilt along the edge of the talus and reopened in October 2012.'),
 st('C1', 'C', 'Tenaya Canyon views', 'The Snow Creek Trail climbs out of Tenaya Canyon in dozens of tight switchbacks on open, sunny granite. Half Dome, the Quarter Domes and Clouds Rest come into view early and get better with every turn.'),
 st('C2', 'C', 'Snow Creek junction', 'Near the top of the climb, about 2,700 feet above the valley, the trail reaches a junction near Snow Creek. Turn right for the footbridge; the other branch heads west toward North Dome.'),
 st('C3', 'C', 'Snow Creek footbridge', 'A footbridge over Snow Creek just below the rim, the usual turnaround for a day hike. Snow Creek Falls is downstream but not visible from the trail. Return the same way.'),
]
stops, order = renumber(p, R, stops)
print(order, [(s['id'], s['name']) for s in stops])
trails = [
 dict(id='A', name='Mirror Lake', short='Mirror Lake', official=2.0, unit='round trip', route='Out and back', time='1 hr', level='Easy', color='--tA',
      desc='A paved service road, closed to cars, runs a mile up the west side of Tenaya Creek to Mirror Lake, with Half Dome rising straight above. Leashed pets, bikes and strollers are allowed on this paved mile. Come back the same way.', anchors=p.anchors(R['A'])),
 dict(id='B', name='Mirror Lake Loop', short='Mirror Lake Loop', official=5.0, unit='loop', route='Loop', time='2–3 hr', level='Easy to moderate', color='--tB',
      desc='From the end of the paved road, a dirt trail follows Tenaya Creek up the canyon past the lake, crosses the creek on footbridges at the east end and returns on the south side, under Half Dome and across the 2009 Ahwiyah Point rockfall. The south side stays icy long after the north side clears in winter.', anchors=p.anchors(R['B'])),
 dict(id='C', name='Snow Creek Trail', short='Snow Creek', official=9.4, unit='round trip', route='Out and back', time='6–7 hr', level='Strenuous', color='--tC',
      desc='Past Mirror Lake, the Snow Creek Trail leaves the canyon floor and climbs about 2,700 feet in steep switchbacks up the north wall of Tenaya Canyon to a footbridge over Snow Creek near the rim. Hot and exposed on summer afternoons: start early and carry plenty of water. Come back the same way.', anchors=p.anchors(R['C'])),
]
for t in trails:
    r = R[t['id']]; A = t['anchors']
    for s_ in stops:
        if t['id'] not in s_['trails']: continue
        m0, e0, _ = p.mile_of(r, s_['x'], s_['n'])
        k = next((i for i, a in enumerate(A) if a[3] >= m0), len(A))
        if k < len(A) and abs(A[k][3] - m0) < 1e-4: A[k][0], A[k][1] = s_['x'], s_['n']
        else: A.insert(k, [s_['x'], s_['n'], e0, round(m0, 3)])

pa = place_along
A_ = lambda k, f, s=1, o=240: pa(p, R[k], f, s, o)
def path(k, f, s=1, o=300, d=0.02): return js(A_(k, [f], s, o)[0] + A_(k, [f + d], s, o)[0])
an = []
an += [f'{{k:"bear",path:{path("B",.62,1,420)},per:30}}', f'{{k:"bear",path:{path("C",.8,-1,480,.015)},per:32,ph:0.4}}']
an += [f'{{k:"deer",path:{path("A",.45,-1,320)},per:26}}', f'{{k:"deer",path:{path("B",.85,1,380,.015)},per:28,ph:0.5}}']
an += [f'{{k:"coyote",path:{path("B",.35,-1,360)},per:24}}']
an += [f'{{k:"squirrel",at:{js(A_("A",[.55],-1,200)[0])},hop:true}}', f'{{k:"squirrel",at:{js(A_("C",[.97],-1,200)[0])},hop:true}}']
an += [f'{{k:"snake",path:{path("C",.62,1,220,.01)},per:30}}']
an += [f'{{k:"bobcat",path:{path("C",.3,1,330)},per:28,ph:0.2}}']
animals_js = '[\n ' + ',\n '.join(an) + '\n]'

# ---- Mirror Lake (OSM water polygon 62002226), drawn flat on the terrain
lake = [p.xy(q) for q in p.WID['62002226']['p']]
if lake[0] == lake[-1]: lake = lake[:-1]
lake = [[round(x), round(n)] for x, n in lake]

bn = {s['name']: s for s in stops}
th, ml, eb, rf, fb, sj = [bn[k] for k in ('Mirror Lake trailhead', 'Mirror Lake', 'Tenaya Creek bridges', 'Ahwiyah Point rockfall', 'Snow Creek footbridge', 'Snow Creek junction')]
def heading(r, q, d=60):
    P = r['pts']; i = min(range(len(P)), key=lambda j: math.dist((P[j][0], P[j][1]), q))
    a = P[max(0, i - 3)]; b = P[min(len(P) - 1, i + 3)]
    return math.atan2(b[0] - a[0], b[1] - a[1])
EBH = heading(R['B'], EB); FBH = heading(R['C'], FB); NBH = heading(R['B'], NB)
RP = []
for f, s_, o in ((-0.012, -1, 160), (-0.004, -1, 260), (0.004, -1, 140), (0.012, -1, 300), (0.0, 1, 120), (0.009, 1, 200)):
    m0 = p.mile_of(R['B'], rf['x'], rf['n'])[0] / R['B']['mi']
    RP.append(A_('B', [min(.99, max(0, m0 + f))], s_, o)[0])

lm = '''  // trailhead: shuttle-stop sign
  {const q=G(%(thx)d,%(thn)d);part(world,cyl,"#5A4632",q.x,q.y+1.1,q.z,0.08,2.2,0.08,0);part(world,box,"#2F5E46",q.x,q.y+2.0,q.z,1.6,0.7,0.12,1.06);part(world,box,"#F2EEE4",q.x,q.y+2.0,q.z+0.07,1.3,0.45,0.02,1.06);}
  // Mirror Lake interpretive exhibit
  {const q=G(%(mlx)d,%(mln)d);const g=new THREE.Group();g.position.copy(q);g.rotation.y=0.8;world.add(g);
   part(g,box,"#6B4F3A",-0.45,0.45,0,0.12,0.9,0.12,0);part(g,box,"#6B4F3A",0.45,0.45,0,0.12,0.9,0.12,0);part(g,box,"#7A5C3E",0,1.0,0,1.3,0.75,0.16,1.06);part(g,box,"#E8E1CF",0,1.0,0.09,1.1,0.55,0.03,1.06);}
  // footbridges (exaggerated): north-side bridge, east-end bridge over Tenaya Creek, Snow Creek footbridge
  function fbridge(x,n,ry,len){const q=G(x,n,0.05);const g=new THREE.Group();g.position.copy(q);g.rotation.y=ry;world.add(g);
    part(g,box,"#8A6A4A",0,0.35,0,0.9,0.16,len,1.06);
    for(const s of [-0.42,0.42]){part(g,box,"#6B4F3A",s,0.7,0,0.07,0.07,len,0);for(let i=0;i<5;i++)part(g,box,"#6B4F3A",s,0.52,-len/2+i*len/4,0.08,0.4,0.08,0);}
    part(g,box,"#9C9488",0,0.15,-len/2,1.2,0.35,0.4,1.06);part(g,box,"#9C9488",0,0.15,len/2,1.2,0.35,0.4,1.06);}
  fbridge(%(nbx)d,%(nbn)d,%(nbh).3f,2.0);fbridge(%(ebx)d,%(ebn)d,%(ebh).3f,2.4);fbridge(%(fbx)d,%(fbn)d,%(fbh).3f,2.2);
  // Ahwiyah Point rockfall: granite blocks along the rebuilt trail
  %(rocks)s.forEach(([x,n],i)=>{const q=G(x,n);const s=0.55+((i*37)%%5)*0.18;const m=part(world,new THREE.DodecahedronGeometry(1,0),i%%2?"#CFCAC0":"#BDB7AC",q.x,q.y+s*0.5,q.z,s*1.3,s,s*1.1,1.04);if(m)m.rotation.set(i*0.7,i*1.3,i*0.4);});
  // Half Dome summit marker (exaggerated) on the OSM summit
  {const q=G(%(hdx)d,%(hdn)d);part(world,cyl,"#6B6258",q.x,q.y+1.6,q.z,0.1,3.2,0.1,0);part(world,box,"#C8553D",q.x+0.45,q.y+2.9,q.z,0.9,0.55,0.06,1.06);}
''' % dict(thx=th['x'] + 80, thn=th['n'] - 80, mlx=ml['x'] - 90, mln=ml['n'] - 60,
           nbx=NB[0], nbn=NB[1], nbh=NBH, ebx=EB[0], ebn=EB[1], ebh=EBH, fbx=FB[0], fbn=FB[1], fbh=FBH,
           rocks=js([[round(a), round(b)] for a, b in RP]), hdx=HD[0], hdn=HD[1])

extra_js = '''
TRAILS.forEach(T=>{const g={A:100,B:200,C:2700}[T.id];if(g)T.gain=g;});
// out-and-back: report the outbound mile for a stop
mileOf=function(T,x,n){let b=null;T.pts.forEach(p=>{const d=Math.hypot(p.x-x,p.n-n);if(!b||d<b.d)b={d,m:p.m,e:p.e};});if(!b||b.d>=260)return null;const f=T.pts.find(p=>Math.hypot(p.x-x,p.n-n)<b.d+60);return {d:b.d,m:f.m,e:f.e};};
function lakeP(){return lakeP.c||(lakeP.c=%s);}
function inLake(x,n){for(const P of lakeP()){let c=false;for(let i=0,j=P.length-1;i<P.length;j=i++){const a=P[i],b=P[j];if((a[1]>n)!==(b[1]>n)&&x<(b[0]-a[0])*(n-a[1])/(b[1]-a[1])+a[0])c=!c;}if(c)return true;}return false;}
(function(){const mat=new THREE.MeshLambertMaterial({color:"#5AA7CF",side:THREE.DoubleSide});const edge=new THREE.LineBasicMaterial({color:"#5E9FB8"});
  lakeP().forEach(P=>{const sh=new THREE.Shape(P.map(([x,n])=>new THREE.Vector2(x,n)));const geo=new THREE.ExtrudeGeometry(sh,{depth:1,bevelEnabled:false});const pa=geo.attributes.position;
    let lo=-1e9;P.forEach(([x,n])=>{lo=Math.max(lo,G(x,n,0).y);});
    for(let i=0;i<pa.count;i++){const x=pa.getX(i),n=pa.getY(i);const z0=pa.getZ(i);const v=G(x,n,0);pa.setXYZ(i,v.x,z0>0.5?lo+0.45:v.y-0.05,v.z);}
    pa.needsUpdate=true;geo.computeVertexNormals();geo.computeBoundingSphere();const m=new THREE.Mesh(geo,mat);m.renderOrder=1;world.add(m);
    const ring=P.concat([P[0]]).map(([x,n])=>{const v=G(x,n,0);v.y=lo+0.46;return v;});world.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints(ring),edge));});
})();
''' % js([lake])

creeks = []
for nm, minor in (('Tenaya Creek', False), ('Snow Creek', True), ('Merced River', False)):
    ids = [w['id'] for w in p.W if w.get('n') == nm and w['k'] in ('river', 'stream')]
    c = p.creek(ids, GRID, minor=minor) if ids else None
    if c and c.get('pts'): creeks.append(dict(id=re.sub(r'\W', '', nm.lower()), **c))
print('creeks', [c['id'] for c in creeks])

EXTRA = {
 'pacdogwood': 'pacdogwood:{name:"Pacific dogwood",latin:"Cornus nuttallii",color:"#F4F2E8",shape:"dome",bloom:[4,5],sum:"A small understory tree whose big white flower bracts light up the shade along Tenaya Creek below Mirror Lake from late April, peaking in May. The leaves turn pink and red in fall.",rule:(d,e,g,s)=>d<260&&e<4400&&g<0.5}',
 'azalea': 'azalea:{name:"Western azalea",latin:"Rhododendron occidentale",color:"#F6D7DF",shape:"dome",bloom:[5,6,7],sum:"A streamside shrub with fragrant white-and-pink flowers, often with a yellow blotch, in June in Yosemite Valley. Look on the wet banks of Tenaya Creek.",rule:(d,e,g,s)=>d<180&&e<4600&&g<0.5}',
 'wildginger': 'wildginger:{name:"Hartweg\'s wild ginger",latin:"Asarum hartwegii",color:"#5A2E2A",shape:"pad",bloom:[5,6],sum:"A low ground cover of mottled, heart-shaped leaves that smell of ginger, with brownish-purple flowers hidden underneath in May and June, in the shady forest of Tenaya Canyon between Mirror Lake and the Snow Creek Trail.",rule:(d,e,g,s)=>e<4500&&d<400&&g<0.4}',
 'bracken': 'bracken:{name:"Bracken fern",latin:"Pteridium aquilinum",color:"#6E9A4A",shape:"fern",bloom:[5,6,7,8,9],sum:"A tall, coarse fern that carpets the meadow edges and open forest around Mirror Lake. For centuries Native people gathered bracken here; its roots gave black fibers for basket patterns.",rule:(d,e,g,s)=>e<4600&&g<0.35&&d<700}',
 'mtpride': 'mtpride:{name:"Mountain pride",latin:"Penstemon newberryi",color:"#D9407A",shape:"spike",bloom:[6,7,8],sum:"A low, woody penstemon that covers granite cracks with rose-pink tubular flowers in summer, visited by hummingbirds. Look on the rocky switchbacks of the Snow Creek Trail.",rule:(d,e,g,s)=>g>0.35&&e>4600&&d>150}',
 'lessingia': 'lessingia:{name:"Sierra lessingia",latin:"Lessingia leptoclada",color:"#B48AD8",shape:"cup",bloom:[7,8,9,10],sum:"Small lavender flowers that bloom late in the season, when little else does, on dry, open flats and talus in Yosemite Valley, peaking around Labor Day.",rule:(d,e,g,s)=>e<4500&&d>80&&g<0.6}',
}

def page_photos():
    out = {}
    import glob
    for f in glob.glob('/home/claude/site/out/*/index.html'):
        h = open(f).read()
        for x in set(re.findall(r'\{"f":"\.\./photos/sp_[^{}]*\}', h)):
            try: m = json.loads(x); out.setdefault(m['f'].split('/')[-1], m)
            except Exception: pass
    return out
PP = page_photos()
pick = lambda *fs: [PP[f] for f in fs if f in PP]
PH = json.load(open('mirrorlake/photos.json')) if os.path.exists('mirrorlake/photos.json') else {}
idof = {s['name']: s['id'] for s in stops}
stop_photos = {idof[nm]: v for nm, v in PH.get('stop', {}).items() if nm in idof}
flower_photos = dict(PH.get('flower', {}))
for k, fs in [('pacdogwood', ['sp_pacdogwood_1.jpg', 'sp_pacdogwood_2.jpg', 'sp_pacdogwood_3.jpg']), ('azalea', ['sp_azalea_0.jpg', 'sp_azalea_1.jpg', 'sp_azalea_2.jpg']),
              ('bracken', ['sp_bracken_1.jpg', 'sp_bracken_2.jpg', 'sp_bracken_3.jpg']), ('mtpride', ['sp_mtpride_1.jpg', 'sp_mtpride_2.jpg', 'sp_mtpride_3.jpg']),
              ('lessingia', ['sp_lessingia_0.jpg', 'sp_lessingia_1.jpg', 'sp_lessingia_2.jpg'])]:
    if pick(*fs): flower_photos.setdefault(k, pick(*fs))
animal_photos = dict(PH.get('animal', {}))
for k, fs in [('bear', ['sp_bear_0.jpg']), ('deer', ['sp_muledeer_0.jpg', 'sp_muledeer_1.jpg']), ('raven', ['sp_raven_1.jpg']), ('coyote', ['sp_coyote_0.jpg']),
              ('squirrel', ['sp_calgsquirrel_3.jpg', 'sp_calgsquirrel_1.jpg']), ('steller', ['sp_stellersjay_0.jpg', 'sp_stellersjay_1.jpg']),
              ('woodpecker', ['sp_acornwp_0.jpg']), ('snake', ['sp_nprattle_0.jpg', 'sp_nprattle_2.jpg']), ('kingfisher', ['sp_hl_kingfisher_0.jpg', 'sp_hl_kingfisher_1.jpg']),
              ('bobcat', ['sp_bobcat_0.jpg']), ('peregrine', ['sp_yoseperegrine_1.jpg', 'sp_yoseperegrine_2.jpg']), ('swift', ['sp_wtswift_1.jpg', 'sp_wtswift_2.jpg'])]:
    if pick(*fs): animal_photos.setdefault(k, pick(*fs))
print('photos', {k: len(v) for k, v in stop_photos.items()}, {k: len(v) for k, v in flower_photos.items()}, {k: len(v) for k, v in animal_photos.items()})
print('meta check', {k: [m.get('t','')[:50] for m in v] for k, v in list(flower_photos.items()) + list(animal_photos.items())})

cfg = dict(
    title='Mirror Lake', aria='Mirror Lake, the Mirror Lake Loop and the Snow Creek Trail in Tenaya Canyon, Yosemite National Park',
    h1='Mirror Lake &amp; Snow Creek',
    canyons=creeks, trails=trails, stops=stops, order=order,
    species=['pacdogwood', 'azalea', 'wildginger', 'bracken', 'mtpride', 'lessingia'], species_extra=EXTRA,
    flora={'A': ['pacdogwood', 'bracken', 'lessingia'], 'B': ['pacdogwood', 'azalea', 'wildginger', 'bracken'], 'C': ['wildginger', 'mtpride', 'bracken']},
    wild=['bear', 'deer', 'coyote', 'bobcat', 'squirrel', 'snake', 'steller', 'woodpecker', 'raven', 'kingfisher', 'swift', 'peregrine'],
    wild_sum={'bear': ('Black bear', 'Often brown or cinnamon despite the name. Bears forage along Tenaya Creek and in the oaks of the east valley; keep food within arm’s reach and never leave a pack unattended.'),
              'deer': ('Mule deer', 'Big-eared deer that graze the meadow around Mirror Lake and the forest edges of Tenaya Canyon, mostly at dawn and dusk.'),
              'coyote': ('Coyote', 'A lean, gray-tan wild dog that hunts rodents in the valley meadows and along the canyon floor. Never feed one.'),
              'squirrel': ('California ground squirrel', 'A brown, speckled squirrel common along the paved road and at the lake. Fed squirrels turn bold and can bite: keep snacks put away.'),
              'snake': ('Northern Pacific rattlesnake', 'The park’s only venomous snake. The park warns of rattlesnakes on the sunny Snow Creek switchbacks: watch where you step and sit, and give it room.'),
              'steller': ("Steller's jay", 'A dark blue, black-crested jay, loud and common in the oaks and conifers of the canyon floor.'),
              'woodpecker': ('Acorn woodpecker', 'A noisy black, white and red woodpecker of the valley’s black oaks that stores acorns in holes it drills in trees.'),
              'raven': 'Big black birds that ride the updrafts off the canyon walls and patrol the trailhead and the lake for scraps.',
              'bobcat': ('Bobcat', 'A short-tailed wild cat with tufted ears that hunts ground squirrels, wood rats and gophers in the valley meadows and forest edges. Seen most often at dawn and dusk.'),
              'swift': ('White-throated swift', 'Fast black-and-white birds that race along the granite walls of Tenaya Canyon catching insects, often in noisy groups.'),
              'peregrine': ('Peregrine falcon', 'Rare here: peregrines vanished from Yosemite between 1949 and 1975 and returned to nest on El Capitan in 1978; the park now has the highest peregrine nesting density in the Sierra Nevada. Watch the cliffs above the valley for one diving after swifts and swallows.'),
              'kingfisher': ('Belted kingfisher', 'A blue-gray bird with a shaggy crest that rattles along Tenaya Creek and the Merced River and plunges for small fish.')},
    grid=GRID, step=STEP, dem_b64=b64, tile=TILE, ve=1.15, ridge_ft=RIDGE,
    palette={"ground": "#B9E0C9", "groundN": "#A1CFB5", "conifer": "#2E5A3C", "oak": "#4C7A36", "rock": "#D8D4CB", "rockDeep": "#C4BFB5", "ridge": "#E3E0D8"},
    rock_all_aspects=True,
    tree_rule='''if(inLake(x,n)){type=null;}
    else if(mk<0.25){type="conifer";p=0.05;}
    else if(cd<200){type=tr()<.45?"oak":"conifer";p=0.32;}
    else if(g>0.8)type=null;
    else if(e<4600){const r0=tr();type=r0<.5?"oak":r0<.85?"conifer":"shrub";p=0.26+cl*.2;}
    else{const r0=tr();type=r0<.75?"conifer":r0<.9?"shrub":"oak";p=0.2+cl*.2;}''',
    landmarks=lm, animals_js=animals_js, extra_js=extra_js,
    overview=dict(h2='Mirror Lake and Tenaya Canyon',
                  p='Mirror Lake sits in Tenaya Canyon at the east end of Yosemite Valley, right below Half Dome. A rockfall a few hundred years ago dammed Tenaya Creek with boulders, and in spring and early summer the creek backs up into a calm pool that reflects the cliffs; by late summer it is mostly meadow. A is the paved mile to the lake, B loops up the canyon and back on the far side of the creek, and C climbs the Snow Creek Trail up the north wall. Pick a trail to focus the model; click anything on it for a quick note.',
                  numbers='All three trails start up the same paved road, so the shared stops carry plain numbers: 2, Mirror Lake, is on A, B and C. Lettered stops belong to one trail: C3 is the third stop only on Trail C.',
                  wild_h='Wildlife in Tenaya Canyon',
                  note='Mirror Lake trailhead, shuttle stop 17, east Yosemite Valley, Yosemite National Park, California. No parking at the trailhead: park at Curry Village and walk or ride the free Valleywide or East Valley shuttle (7 am to 10 pm). Vault toilets at 0.5 mile and at the lake; no drinking water. Leashed pets, bikes and strollers only on the first paved mile. Entrance fee $35 per vehicle for seven days, plus $100 per person for non-US residents 16 and older; no entry reservation is listed for 2026. Status (November 2026): the trails are open; Tioga and Glacier Point roads are closed for the winter, and from about November to spring the trails can be icy or snowy, especially the south side of the loop. Check nps.gov/yose for conditions. Terrain from USGS elevation data, stylized; not for navigation.'),
    links={'A': [('Mirror Lake Trail · NPS', 'https://www.nps.gov/yose/planyourvisit/mirrorlaketrail.htm'), ('Yosemite Valley day hikes · NPS', 'https://www.nps.gov/yose/planyourvisit/valleyhikes.htm')],
           'B': [('Mirror Lake Trail · NPS', 'https://www.nps.gov/yose/planyourvisit/mirrorlaketrail.htm'), ('Mirror Lake Loop reopens (2012) · NPS', 'https://www.nps.gov/yose/learn/news/mirrorlakeloopopens.htm'), ('Mirror Lake · Yosemite Hikes', 'https://www.yosemitehikes.com/yosemite-valley/mirror-lake/mirror-lake.htm')],
           'C': [('Snow Creek Trail · NPS', 'https://www.nps.gov/yose/planyourvisit/snowcreektrail.htm'), ('Snow Creek Trail · Yosemite Hikes', 'https://www.yosemitehikes.com/tioga-road/snow-creek/snow-creek.htm'), ('Current conditions · NPS', 'https://www.nps.gov/yose/planyourvisit/conditions.htm')]},
    viewaz={'all': 6.0, 'A': 6.0, 'B': 6.0, 'C': 6.0},
    zoomcap={'A': 4.0, 'B': 2.8, 'C': 2.4},
    stop_photos=stop_photos, flower_photos=flower_photos, animal_photos=animal_photos,
)
json.dump({k: {'mi': R[k]['mi'], 'gain': R[k]['gain'], 'lo': R[k]['lo'], 'hi': R[k]['hi']} for k in R}, open('mirrorlake/stats.json', 'w'))
os.makedirs('/home/claude/site/out/yosemite-mirror-lake', exist_ok=True)
print(build(cfg, '/home/claude/site/out/yosemite-mirror-lake/index.html'))
