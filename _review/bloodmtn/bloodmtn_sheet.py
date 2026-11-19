from lib import *
from mk_sheet import build
import sys, json, os, re, glob, shutil
import numpy as np

os.chdir('/home/claude/parks')
# origin: Blood Mountain summit (OSM peak node, 1355 m)
p = Park('bloodmtn', 34.7400, -83.9372)
# Byron Herbert Reece Trail, rerouted route opened June 6, 2026 (OSM way 1546306916, from the A.T. to the trailhead)
BRW = [p.xy(q) for w in p.W if str(w['id']) == '1546306916' for q in w['p']]
TH = tuple(round(v) for v in BRW[-1])      # Byron Reece trailhead / parking on US 19/129
BRJ = tuple(round(v) for v in BRW[0])      # new junction with the A.T., a quarter mile trail-south of Flatrock Gap
BRM = [tuple(round(v) for v in BRW[int(len(BRW) * f)]) for f in (0.25, 0.5, 0.75)]
FG = (2632, -1614)      # Flatrock Gap: east end of the Freeman Trail on the A.T. (OSM way 31275923)
BG = (-3250, -944)      # Bird Gap: west end of the Freeman Trail on the A.T.
SUM = (55, -107)        # Blood Mountain peak node
SG = (-2075, 283)       # Slaughter Gap: Slaughter Creek Trail meets the A.T. (OSM way 31275591 end)
DRJ = (-1222, 693)      # Duncan Ridge Trail leaves the A.T. (OSM way 389310570 end)
SLAB = (234, -569)      # OSM viewpoint on the summit rock slabs, A.T. south of the summit
FRM = (-150, -2950)     # Freeman Trail, south side of the mountain
NG = (5855, -1752)      # Walasi-Yi Center breezeway at Neel Gap (A.T. ways 1346025502/1346026444)
up = [TH] + BRM[::-1] + [BRJ]; dn = up[::-1]
R = {}
R['A'] = route_xy(p, *up, FG, *dn)
R['B'] = route_xy(p, *up, SUM, *dn)
R['C'] = route_xy(p, *up, FG, BG, SUM, *dn)
for k in R: Park.smooth_E(R[k], 9); p.describe(R[k], k)

def near(r, q):
    pt = min(r['pts'], key=lambda t: math.hypot(t[0] - q[0], t[1] - q[1])); return (round(pt[0]), round(pt[1]))
FRMT = near(R['C'], FRM)
ST = snap_stops(p, R, {
    'S1': (*TH, 'ABC'), 'S2': (*BRM[1], 'ABC'), 'S3': (*BRJ, 'ABC'), 'S4': (*FG, 'AC'),
    'S5': (*SLAB, 'BC'), 'S6': (*SUM, 'BC'),
    'C1': (*FRMT, 'C'), 'C2': (*BG, 'C'), 'C3': (*SG, 'C'), 'C4': (*DRJ, 'C'),
})
TILE = (-5200, 6300, -5200, 3800)
GRID = (-5450, 6550, -5450, 4050)
if 'plot' in sys.argv:
    from plot import plot
    plot(p, (-4400, 6400, -4200, 2400), 'bloodmtn/routes3.png', routes=R, stops=ST, title='bloodmtn', grid=500); sys.exit()

STEP = 75
b64, NX, NN = p.dem_b64(*GRID, STEP=STEP)
EL = [p.elev(x, n) for x in range(TILE[0], TILE[1], 300) for n in range(TILE[2], TILE[3], 300)]
print('grid', NX, NN, NX * NN, 'elev pct', [round(float(np.percentile(EL, q))) for q in (5, 50, 75, 90, 99)])
RIDGE = int(round(float(np.percentile(EL, 75)), -1))

S = lambda i: ST[i]
stops = [
 dict(id='S1', trails=['A', 'B', 'C'], x=S('S1')[0], n=S('S1')[1], name='Byron Reece trailhead', desc='A small paved lot on US 19/129, about 0.6 mile north of the Walasi-Yi Center at Neel Gap, with restrooms. It fills early on busy days, and hikers may not park at Walasi-Yi. The trail starts at the far end of the parking loop.'),
 dict(id='S2', trails=['A', 'B', 'C'], x=S('S2')[0], n=S('S2')[1], name='Byron Herbert Reece Trail', desc='Rerouted and reopened on June 6, 2026: a narrow path of about 1.3 miles through the Blood Mountain Wilderness, built by hand by the Konnarock Trail Crew and Georgia Appalachian Trail Club volunteers. It replaced the old 0.8-mile trail, which had become wide and eroded and is now closed to recover. Expect few signs or blazes.'),
 dict(id='S3', trails=['A', 'B', 'C'], x=S('S3')[0], n=S('S3')[1], name='Appalachian Trail junction', desc='The new trail meets the white-blazed A.T. about a quarter mile southwest of Flatrock Gap, not at the Freeman Trail as the old route did. Turn right and uphill for Blood Mountain, left for Flatrock Gap and the Freeman Trail.'),
 dict(id='S4', trails=['A', 'C'], x=S('S4')[0], n=S('S4')[1], name='Flatrock Gap', desc='A gap on the A.T. where the Freeman Trail begins, heading around the south side of Blood Mountain. The A.T. continues northeast down to Neel Gap. Trail A turns around here.'),
 dict(id='S5', trails=['B', 'C'], x=S('S5')[0], n=S('S5')[1], name='Summit rock slabs', desc='Above the switchbacks the A.T. crosses open rock outcrops with views to the south and east. Follow the white blazes painted on the rock: about half a mile below the summit the trail turns sharply off the slabs into the woods, a turn that is easy to miss on the way down.'),
 dict(id='S6', trails=['B', 'C'], x=S('S6')[0], n=S('S6')[1], name='Blood Mountain summit', desc='4,458 ft, the highest point of the Appalachian Trail in Georgia, with wide views from the summit rocks. The two-room stone shelter was built by the Civilian Conservation Corps in 1934, is kept up by the Georgia Appalachian Trail Club and has been on the National Register of Historic Places since 2013. The name may come from a legendary battle between the Cherokee and Muscogee, or from the red lichen and Catawba rhododendron on top.'),
 dict(id='C1', trails=['C'], x=S('C1')[0], n=S('C1')[1], name='Freeman Trail', desc='For 1.8 miles the blue-blazed Freeman Trail curves around the south side of the mountain without climbing much, but the footing is very rocky the whole way. Ferns cover the south-facing slopes.'),
 dict(id='C2', trails=['C'], x=S('C2')[0], n=S('C2')[1], name='Bird Gap', desc='The Freeman Trail rejoins the A.T. here. A blue-blazed side trail runs about half a mile down to Woods Hole Shelter. Turn right on the A.T. for the climb to the summit, about 1.2 miles away.'),
 dict(id='C3', trails=['C'], x=S('C3')[0], n=S('C3')[1], name='Slaughter Gap', desc='The Slaughter Creek Trail arrives here after climbing 2.7 miles from Lake Winfield Scott, the main approach from the south side of the mountain.'),
 dict(id='C4', trails=['C'], x=S('C4')[0], n=S('C4')[1], name='Duncan Ridge Trail junction', desc='The blue-blazed Duncan Ridge National Recreation Trail leaves the A.T. here and follows a long ridge west for about 20 miles. Stay on the white blazes for the summit.'),
]
stops, order = renumber(p, R, stops)
print(order, [(s['id'], s['name']) for s in stops])
trails = [
 dict(id='A', name='Byron Reece Trail to Flatrock Gap', short='Flatrock Gap', official=3.1, unit='round trip', route='Out and back', time='1.5–2 hr', level='Moderate', color='--tA',
      desc='The start of every Blood Mountain hike from the Byron Reece lot, on the trail rerouted in 2026: a narrow, hand-built path through hardwood forest up to the Appalachian Trail, then a short walk along the A.T. to Flatrock Gap, where the Freeman Trail begins. Return the same way.', anchors=p.anchors(R['A'])),
 dict(id='B', name='Blood Mountain via the Byron Reece Trail', short='Blood Mountain', official=4.8, unit='round trip', route='Out and back', time='3–4 hr', level='Strenuous', color='--tB',
      desc='The most popular hike to the highest point of the A.T. in Georgia. The Byron Reece Trail climbs to the A.T., which switchbacks up rock steps and crosses open slabs to the summit, its 1934 stone shelter and wide views. About 4.8 miles round trip on the new 2026 route; older guides list 4.3 miles.', anchors=p.anchors(R['B'])),
 dict(id='C', name='Blood Mountain Loop via the Freeman Trail', short='Freeman Loop', official=7.0, unit='loop', route='Loop', time='4–5 hr', level='Strenuous', color='--tC',
      desc='Up the Byron Reece Trail to Flatrock Gap, around the south side of the mountain on the very rocky Freeman Trail to Bird Gap, then up the A.T. past Slaughter Gap to the summit and down over the rock slabs. About 7 miles with the 2026 reroute; older guides list about 6.', anchors=p.anchors(R['C'])),
]

pa = place_along
A_ = lambda k, f, s=1, o=240: pa(p, R[k], f, s, o)
def path(k, f, s, o, d=.02): return js(A_(k, [f], s, o)[0] + A_(k, [f + d], s, o)[0])
def at(k, f, s, o): return js(A_(k, [f], s, o)[0])
an = []
an += [f'{{k:"bear",path:{path("C",.33,-1,480)},per:34}}', f'{{k:"bear",path:{path("C",.55,1,460)},per:36,ph:0.5}}']
an += [f'{{k:"deer",path:{path("C",.42,-1,380)},per:28}}', f'{{k:"deer",path:{path("B",.10,1,380)},per:30,ph:0.6}}']
an += [f'{{k:"turkey",at:{at("C",.26,1,340)},flock:2}}']
an += [f'{{k:"grouse",at:{at("C",.50,-1,280)}}}', f'{{k:"grouse",at:{at("A",.36,-1,260)},ph:0.4}}']
an += [f'{{k:"squirrel",at:{at("B",.20,-1,260)}}}', f'{{k:"chipmunk",at:{at("B",.47,1,220)}}}']
an += [f'{{k:"raccoon",at:{at("C",.37,1,300)}}}']
an += [f'{{k:"snake",path:{path("C",.69,1,200)},per:30}}']
an += [f'{{k:"turtle",at:{at("A",.10,-1,260)}}}']
an += [f'{{k:"salamander",at:{at("C",.29,-1,220)}}}', f'{{k:"salamander",at:{at("C",.90,1,240)}}}']
BUILDX = '''BUILD.grouse=function(){const g=new THREE.Group(),c="#8A6A4A",dk="#3A2C20",lt="#C9AE8A";
  part(g,SPH,c,0,0.55,0,0.46,0.36,0.3);part(g,SPH,lt,0.12,0.45,0,0.3,0.24,0.24,0);
  part(g,SPH,c,0.4,0.88,0,0.17,0.17,0.15);part(g,CONE,dk,0.36,1.08,0,0.07,0.16,0.06);part(g,SPH,dk,0.3,0.72,0.12,0.1,0.12,0.08,0);part(g,SPH,dk,0.3,0.72,-0.12,0.1,0.12,0.08,0);
  const bk=part(g,CONE,"#3A3A3A",0.6,0.86,0,0.04,0.1,0.04,0);rot(bk,0,0,-Math.PI/2);part(g,SPH,"#111",0.5,0.92,0.1,0.03,0.03,0.03,0);part(g,SPH,"#111",0.5,0.92,-0.1,0.03,0.03,0.03,0);
  const tl=part(g,SPH,"#7A5C3E",-0.48,0.72,0,0.08,0.36,0.4);rot(tl,0,0,0.5);part(g,SPH,dk,-0.6,0.95,0,0.05,0.08,0.38,0);
  part(g,CYL,"#6B5A48",0.05,0.14,0.1,0.03,0.28,0.03,0);part(g,CYL,"#6B5A48",0.05,0.14,-0.1,0.03,0.28,0.03,0);return g;};
BUILD.salamander=function(){const g=new THREE.Group(),c="#1F1F24",f="#D8D6C8";
  part(g,SPH,c,0,0.14,0,0.5,0.12,0.15);part(g,SPH,c,0.56,0.15,0,0.17,0.1,0.14);const t=part(g,SPH,c,-0.78,0.11,0.06,0.48,0.07,0.08);rot(t,0,0.2,0);
  [[0.3,0.2],[0.3,-0.2],[-0.3,0.2],[-0.3,-0.2]].forEach(([x,z])=>part(g,SPH,c,x,0.06,z*1.1,0.12,0.04,0.07));
  [[0.2,0.05],[-0.1,-0.06],[-0.3,0.07],[0.05,-0.09],[0.4,0.02],[-0.5,0.0],[-0.85,0.05]].forEach(([x,z])=>part(g,SPH,f,x,0.25,z,0.035,0.02,0.035,0));
  part(g,SPH,"#111",0.66,0.22,0.08,0.03,0.03,0.03,0);part(g,SPH,"#111",0.66,0.22,-0.08,0.03,0.03,0.03,0);return g;};
SCALE.grouse=1.9;SCALE.salamander=2.8;'''
animals_js = '(()=>{' + BUILDX + 'return [\n ' + ',\n '.join(an) + '\n];})()'

xy = lambda lon, lat: tuple(round(v) for v in p.xy([lon, lat]))
# summit shelter: drawn large; long axis along the summit ridge (A.T. bearing at the summit)
r6 = R['B']; i6 = min(range(len(r6['pts'])), key=lambda i: math.hypot(r6['pts'][i][0] - SUM[0], r6['pts'][i][1] - SUM[1]))
q0, q1 = r6['pts'][max(0, i6 - 6)], r6['pts'][min(len(r6['pts']) - 1, i6 + 6)]
SAZ = math.atan2(q1[0] - q0[0], q1[1] - q0[1])
SH = (SUM[0] + 70, SUM[1] + 40)
lm = f'''  gate({TH[0] - 50},{TH[1] + 40},0.5);
  // Blood Mountain shelter: two-room CCC stone cabin (1934) on the summit, drawn exaggerated
  {{const a=G({SH[0]},{SH[1]}),b=G({SH[0]}+Math.sin({SAZ:.3f})*100,{SH[1]}+Math.cos({SAZ:.3f})*100);const g=new THREE.Group();g.position.copy(a);g.rotation.y=Math.atan2(b.x-a.x,b.z-a.z);world.add(g);
    part(g,box,"#8E8A82",0,0.75,0,2.0,1.5,3.4,1.06);
    [[-1.01,0.35],[1.01,0.35],[-1.01,1.1],[1.01,1.1]].forEach(([x,y])=>part(g,box,"#77736B",x,y,0,0.04,0.12,3.3,0));
    part(g,box,"#3F3A35",1.01,0.55,-0.8,0.06,0.9,0.6,0);part(g,box,"#3F3A35",1.01,0.55,0.8,0.06,0.9,0.6,0);
    const r1=part(g,box,"#5B4B3E",0.62,1.85,0,1.4,0.12,3.7,1.06);rot(r1,0,0,-0.58);const r2=part(g,box,"#5B4B3E",-0.62,1.85,0,1.4,0.12,3.7,1.06);rot(r2,0,0,0.58);
    part(g,box,"#8E8A82",0,1.75,1.62,1.2,0.6,0.2,0);part(g,box,"#8E8A82",0,1.75,-1.62,1.2,0.6,0.2,0);
    part(g,box,"#7C776E",0.5,2.3,1.2,0.35,0.9,0.35,1.06);}}
  // summit rocks
  rock({SUM[0] - 60},{SUM[1] - 30},1.3);rock({SLAB[0] + 40},{SLAB[1]},1.0);
  bench({SUM[0] - 30},{SUM[1] + 60},0.9);
'''

def reuse(prefixes):
    out = {}
    for f in glob.glob('/home/claude/site/out/*/index.html'):
        src = open(f).read()
        if not any(pr in src for pr in prefixes): continue
        m = re.search(r'const PHOTOS=(\{.*?\});\n', src, re.S)
        if not m: continue
        def walk(o):
            if isinstance(o, dict):
                if 'f' in o and isinstance(o['f'], str):
                    fn = o['f'].split('/')[-1]
                    for pr in prefixes:
                        if fn.startswith(pr) and fn not in [x['f'].split('/')[-1] for x in out.get(pr, [])]:
                            out.setdefault(pr, []).append(dict(o, f='../photos/' + fn))
                else:
                    for v in o.values(): walk(v)
            elif isinstance(o, list):
                for v in o: walk(v)
        walk(json.loads(m.group(1)))
    return out
RU = reuse(['sp_av_blackbear_', 'sp_av_wtdeer_', 'sp_av_pileated_', 'sp_er_turkey_', 'sp_gm_bluejay_', 'sp_firepink_', 'sp_cd_flame_', 'sp_echipmunk_bk_'])
print('reuse', {k: len(v) for k, v in RU.items()})
MP = 'bloodmtn/photos_meta.json'
if os.path.exists('/tmp/bloodmtn_ph/photos_meta.json'): shutil.copy('/tmp/bloodmtn_ph/photos_meta.json', MP)
M = json.load(open(MP))
def pick(key, nums):
    base = ('sp_' + key[3:]) if key.startswith('sp:') else 'pl_bloodmtn_' + key
    want = [f'{base}_{n}.jpg' for n in nums]
    return [m for m in M.get(key, []) if m['f'].split('/')[-1] in want]
ID = {s['name']: s['id'] for s in stops}
stop_photos = {
    ID['Blood Mountain summit']: pick('slabs', [1]),
    ID['Flatrock Gap']: pick('freeman', [2]),
    ID['Freeman Trail']: pick('freeman', [0]),
    ID['Bird Gap']: pick('freeman', [1]),
}
stop_photos = {k: v for k, v in stop_photos.items() if v}
flower_photos = {
    'bm_catawba': pick('sp:bm_catawba', [0, 1, 3]), 'bm_flame': RU.get('sp_cd_flame_', []), 'bm_laurel': pick('sp:bm_laurel', [1, 2, 3]),
    'bm_iris': pick('sp:bm_iris', [0, 1]), 'bm_firepink': RU.get('sp_firepink_', []), 'bm_ladyslipper': pick('sp:bm_ladyslipper', [0, 1, 2]),
    'bm_vasey': pick('sp:bm_vasey', [0, 1, 2]),
}
animal_photos = {
    'bear': RU.get('sp_av_blackbear_', []), 'deer': RU.get('sp_av_wtdeer_', []), 'turkey': RU.get('sp_er_turkey_', []),
    'grouse': pick('sp:bm_grouse', [0, 2, 3]), 'squirrel': pick('sp:bm_graysq', [0, 2, 3]), 'chipmunk': RU.get('sp_echipmunk_bk_', []),
    'raccoon': pick('sp:bm_raccoon', [0, 2, 3]), 'snake': pick('sp:bm_timber', [0, 1]), 'turtle': pick('sp:bm_boxturtle', [1, 2]),
    'salamander': pick('sp:bm_slimysal', [0, 2, 3]), 'woodpecker': RU.get('sp_av_pileated_', []), 'jay': RU.get('sp_gm_bluejay_', []),
    'hawk': pick('sp:bm_rshawk', [0, 1, 2]), 'vulture': pick('sp:bm_bvulture', [0, 1, 3]),
}
flower_photos = {k: v for k, v in flower_photos.items() if v}; animal_photos = {k: v for k, v in animal_photos.items() if v}

species_extra = {
 'bm_catawba': 'bm_catawba:{name:"Catawba rhododendron",latin:"Rhododendron catawbiense",color:"#C8559A",shape:"dome",bloom:[5,6],sum:"Evergreen shrubs with big rose-purple flower clusters in late spring, thick on the upper slopes and around the summit rocks. One story says the mountain is named for its red-purple blooms and the red lichen on top.",rule:(d,e,g,s)=>e>3900&&d>120}',
 'bm_flame': 'bm_flame:{name:"Flame azalea",latin:"Rhododendron calendulaceum",color:"#F07A22",shape:"dome",bloom:[5,6],sum:"A deciduous azalea with orange to yellow flowers in late spring, on open ridges and forest edges along the A.T.",rule:(d,e,g,s)=>e>3300&&d>120&&g<0.7}',
 'bm_laurel': 'bm_laurel:{name:"Mountain laurel",latin:"Kalmia latifolia",color:"#F1C9D6",shape:"dome",bloom:[5,6],sum:"An evergreen shrub with cups of white-pink flowers in May and June, lining the trails on dry ridges and the approach to the summit.",rule:(d,e,g,s)=>d>160&&s>-0.3}',
 'bm_iris': 'bm_iris:{name:"Dwarf crested iris",latin:"Iris cristata",color:"#8A7BD8",shape:"cup",bloom:[4,5],sum:"A small woodland iris with pale violet petals marked white and gold, spreading in patches along the trail banks in spring.",rule:(d,e,g,s)=>g<0.6&&e<4000}',
 'bm_firepink': 'bm_firepink:{name:"Fire pink",latin:"Silene virginica",color:"#D8263A",shape:"tube",bloom:[4,5,6],sum:"Bright red, notched petals on thin stems, along rocky trail banks from April into June.",rule:(d,e,g,s)=>g>0.35}',
 'bm_ladyslipper': 'bm_ladyslipper:{name:"Pink lady’s slipper",latin:"Cypripedium acaule",color:"#E77FB0",shape:"tube",bloom:[4,5],sum:"A native orchid with a pink, pouch-shaped flower on a bare stalk above two pleated leaves, in dry oak and pine woods. Do not pick or dig it.",rule:(d,e,g,s)=>d>200&&g<0.7&&s>-0.2}',
 'bm_vasey': 'bm_vasey:{name:"Vasey’s trillium",latin:"Trillium vaseyi",color:"#7A1F2B",shape:"cup",bloom:[4,5],sum:"A large trillium of the southern Appalachians whose deep maroon flower nods below its three broad leaves. Look in rich, moist coves in late spring.",rule:(d,e,g,s)=>s<0.1&&g<0.6&&e<4100}',
}
cfg = dict(
    title='Blood Mountain', aria='Blood Mountain, the Byron Reece Trail and the Freeman Trail in the Chattahoochee National Forest, Georgia', h1='Blood Mountain · Georgia',
    canyons=[], trees_anywhere=True, trails=trails, stops=stops, order=order,
    species=list(species_extra), species_extra=species_extra,
    flora={'A': ['bm_iris', 'bm_ladyslipper', 'bm_laurel'], 'B': ['bm_catawba', 'bm_laurel', 'bm_flame', 'bm_firepink', 'bm_ladyslipper'],
           'C': ['bm_catawba', 'bm_flame', 'bm_vasey', 'bm_firepink']},
    wild=['bear', 'deer', 'turkey', 'squirrel', 'chipmunk', 'raccoon', 'snake', 'turtle', 'woodpecker', 'jay', 'hawk', 'vulture'],
    wild_sum={
     'bear': ('Black bear', 'Black bears are common in the Blood Mountain Wilderness, and encounters on these trails happen. From March 1 to June 1, overnight campers between Jarrard Gap and Neel Gap must carry a hard-sided bear canister.'),
     'deer': ('White-tailed deer', 'Common in the hardwood forest. Look for them along the quieter stretches early and late in the day.'),
     'turkey': ('Wild turkey', 'Flocks scratch through the leaf litter on the gentler slopes, like those along the Freeman Trail.'),
     'squirrel': ('Eastern gray squirrel', 'The everyday squirrel of the oak and hickory woods, busiest in fall when the acorns drop.'),
     'chipmunk': ('Eastern chipmunk', 'A small striped ground squirrel that darts between the rocks and logs, cheeks stuffed with seeds.'),
     'raccoon': ('Raccoon', 'Lives in the wilderness in smaller numbers, mostly near streams. Active at night; hang or store food at camp.'),
     'snake': ('Timber rattlesnake', 'Recorded on Blood Mountain, often near sunny rocks. Venomous but shy; watch where you put your hands and feet on the slabs and rocky trails. Copperheads live here too.'),
     'turtle': ('Eastern box turtle', 'A small land turtle with a high, patterned shell that can close up completely. Seen on the forest floor after summer rain; leave it where you find it.'),
     'woodpecker': ('Pileated woodpecker', 'A crow-sized woodpecker with a red crest. Listen for its loud laughing call and big rectangular holes in dead trees.'),
     'jay': ('Blue jay', 'Loud blue, white and black jays of the oak woods, often heard before they are seen.'),
     'hawk': ('Red-shouldered hawk', 'A forest hawk with rusty barred underparts. Its repeated kee-ah call carries through the hollows.'),
     'vulture': ('Black vulture', 'Soars on flat wings over the ridges, often in groups, riding the updrafts off the summit.'),
    },
    grid=GRID, step=STEP, dem_b64=b64, tile=TILE, ve=1.8, ridge_ft=RIDGE,
    palette='east', trees='east',
    landmarks=lm, animals_js=animals_js,
    extra_js='''WILD.grouse={name:"Ruffed grouse",color:"#8A6A4A",sum:"A chicken-sized forest bird listed among the wilderness wildlife. It often bursts up from the trail edge with a roar of wings; in spring males drum on logs, a low thump that speeds up."};
WILD.salamander={name:"Chattahoochee slimy salamander",color:"#2A2A30",sum:"Rare here: this salamander lives only in the Chattahoochee and Nantahala national forests of north Georgia and western North Carolina, and NatureServe rates it vulnerable. A black salamander with small pale flecks, out on damp nights, and one of the salamanders most often recorded around these trails on iNaturalist. Leave it under its log or rock."};
const _mo=mileOf;mileOf=function(T,x,n){if(T.id!=="A"&&T.id!=="B")return _mo(T,x,n);let b=null;T.pts.forEach(p=>{const d=Math.hypot(p.x-x,p.n-n);if(!b||d<b.d)b={d,m:p.m,e:p.e};});if(!b||b.d>=260)return null;const f=T.pts.find(p=>Math.hypot(p.x-x,p.n-n)<b.d+60);return {d:b.d,m:f.m,e:f.e};};''',
    overview=dict(h2='The highest point of the Appalachian Trail in Georgia',
                  p='Blood Mountain rises to 4,458 ft in the Blood Mountain Wilderness of the Chattahoochee National Forest, south of Blairsville. Its summit holds a 1934 stone shelter and open rock with long views, and the stretch of A.T. that crosses it is the busiest in Georgia. All three hikes start at the Byron Reece trailhead on US 19/129, on the trail rerouted in 2026: A walks to Flatrock Gap, B climbs to the summit, and C loops around the mountain on the Freeman Trail before going over the top. Pick a trail to focus the model; click anything on it for a quick note.',
                  numbers='Plain numbers mark spots on more than one trail: all three share the Byron Reece Trail, A and C share Flatrock Gap, and B and C share the summit. Lettered stops belong to one trail: C2 is the second stop on Trail C. A and B are round trips, with stop mileage counted on the way out.',
                  wild_h='Wildlife on Blood Mountain',
                  note='Blood Mountain Wilderness, Chattahoochee National Forest (Blue Ridge Ranger District). Byron Reece trailhead on US 19/129 near Neel Gap, south of Blairsville, Georgia. The lot is small and fills early on busy days; do not park at the Walasi-Yi Center. The Byron Herbert Reece Trail was rerouted in June 2026 and now meets the A.T. a quarter mile southwest of Flatrock Gap; the old trail is closed. Overnight campers on the A.T. between Jarrard Gap and Neel Gap must carry a hard-sided bear canister from March 1 to June 1. Dogs on leash. Terrain from USGS elevation data, stylized; not for navigation.'),
    links={'A': [('Byron Herbert Reece Trail reroute · Georgia Appalachian Trail Club', 'https://georgia-atclub.org/?p=16139'), ('Byron Herbert Reece Side Trail relocation · ATC', 'https://appalachiantrail.org/trail-updates/georgia-byron-herbert-reece-side-trail-relocation/')],
           'B': [('Byron Herbert Reece Trail reroute · ATC', 'https://appalachiantrail.org/news-stories/byron-herbert-reece-trail-reroute/'), ('Blood Mountain · Wikipedia', 'https://en.wikipedia.org/wiki/Blood_Mountain'), ('Bear canister requirement · GATC', 'https://georgia-atclub.org/alerts/bear-resistant-canisters-required/')],
           'C': [('Blood Mountain and Freeman Trail · ATC', 'https://appalachiantrail.org/hikes/blood-mountain-and-freeman-trail/'), ('Blood Mountain Loop · Atlanta Trails', 'https://www.atlantatrails.com/hiking-trails/blood-mountain-loop-hiking-appalachian-trail-freeman-trail/')]},
    viewaz={'all': 0.6, 'A': 0.6, 'B': 0.6, 'C': 0.6},
    zoomcap={'A': 3.4, 'B': 3.0, 'C': 2.4},
    stop_photos=stop_photos, flower_photos=flower_photos, animal_photos=animal_photos,
)
json.dump({k: {'mi': R[k]['mi'], 'gain': R[k]['gain'], 'lo': R[k]['lo'], 'hi': R[k]['hi']} for k in R}, open('bloodmtn/stats.json', 'w'))
OUT = '/home/claude/site/out/blood-mountain/index.html'
os.makedirs(os.path.dirname(OUT), exist_ok=True)
print(build(cfg, OUT))
print('done')
