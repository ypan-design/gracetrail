from lib import *
from mk_sheet import build
import sys, json, os, math
import numpy as np

os.chdir('/home/claude/parks')
p = Park('welchdickey', 43.9040, -71.5886)
# key points, local feet (x east, n north from 43.9040, -71.5886); all from OSM
TH = (0, 30)            # Welch-Dickey (Orris Road) trailhead lot; USFS gives 43.90459, -71.58897
VIEW = (3159, 2800)     # OSM tourism=viewpoint: the open ledges on Welch's south shoulder (~1.3 mi)
WEL = (3382, 5523)      # Welch Mountain, OSM peak (794 m)
DIC = (2609, 6925)      # Dickey Mountain, OSM peak (833 m)
DLG = (660, 5472)       # open granite slabs on the Dickey (west) arm, ~2,250 ft (route vertex)
JP = (3420, 4560)       # upper south ridge of Welch, open ledge with jack pine (route vertex, ~2,350 ft)


def mkroute(pts):
    E = [p.elev(*q) for q in pts]
    cum = [0.0]
    for i in range(1, len(pts)): cum.append(cum[-1] + math.dist(pts[i - 1], pts[i]))
    gain = sum(max(0, E[i] - E[i - 1]) for i in range(1, len(E)))
    return dict(pts=pts, E=E, cum=cum, segs=[], gain=gain, mi=cum[-1] / 5280, lo=min(E), hi=max(E))


def out_back(r):
    r2 = mkroute(r['pts'] + r['pts'][-2::-1]); r2['segs'] = r['segs']; return r2


R = {}
upA = route_xy(p, TH, VIEW)
upB = route_xy(p, TH, DIC)
R['A'] = out_back(upA)
R['B'] = out_back(upB)
R['C'] = route_xy(p, TH, VIEW, WEL, DIC, TH)
UP = {'A': upA, 'B': upB, 'C': R['C']}
for k in R: Park.smooth_E(R[k], 9); p.describe(R[k], k)
for k in ('A', 'B'): Park.smooth_E(UP[k], 9)

ST = snap_stops(p, R, {
    'S1': TH + ('ABC',), 'S2': VIEW + ('AC',), 'S3': DLG + ('BC',), 'S4': DIC + ('BC',),
    'C1': WEL + ('C',),
})
TILE = (-2000, 5400, -1900, 9100)
GRID = (-2300, 5700, -2200, 9400)
if 'plot' in sys.argv:
    from plot import plot
    plot(p, TILE, 'welchdickey/routes.png', routes=R, stops=ST, title='welchdickey', grid=500)
    sys.exit()

STEP = 50
b64, NX, NN = p.dem_b64(*GRID, STEP=STEP)
_T = np.array([[p.elev(x, n) for x in range(TILE[0], TILE[1], 200)] for n in range(TILE[2], TILE[3], 200)])
RIDGE = int(round(float(np.percentile(_T, 75)), -1))
print('grid', NX, NN, NX * NN, 'p75', RIDGE, _T.min(), _T.max())

S = lambda i: ST[i]
def st(i, trs, name, desc): return dict(id=i, trails=list(trs), x=S(i)[0], n=S(i)[1], name=name, desc=desc)
stops = [
 st('S1', 'ABC', 'Orris Road trailhead', 'A large Forest Service lot at about 1,040 ft on Orris Road in Thornton, with vault toilets and no water. Day-use fee: $5 per vehicle. The loop splits a few yards past the lot; the Welch side goes right, across a brook.'),
 st('S2', 'AC', 'Welch Ledges', 'About 1.3 miles up, the trail leaves hardwoods and conifers for a broad open ledge on Welch’s south shoulder, with views down the Mad River valley to Sandwich Dome. A good turnaround for a short hike.'),
 st('S3', 'BC', 'Dickey slabs', 'Long, open granite slabs on Dickey’s southwest arm, with views across the valley to Welch. The bare rock is slick when wet and icy from fall to spring; go slowly on the way down.'),
 st('S4', 'BC', 'Dickey Mountain', '2,734 ft, the high point of the loop. Open ledges look north to Franconia Ridge and Franconia Notch. Shortly before the summit, coming from Welch, an unmarked 0.2-mile spur leads to a ledge with a northern outlook.'),
 st('C1', 'C', 'Welch Mountain', '2,605 ft. A bare rocky summit with a 360-degree view: Sandwich Dome, the Tripyramids and the gateway to Waterville Valley. The upper ledges hold one of New Hampshire’s five surviving stands of jack pine. Fragile sub-alpine plants are fenced off; stay on the rock and the marked trail. From here it is 0.5 mile, down a short dip and up, to Dickey.'),
]
stops, order = renumber(p, R, stops)
print(order, [(s['id'], s['name'], s['x'], s['n']) for s in stops])
trails = [
 dict(id='A', name='Welch Ledges', short='Welch Ledges', official=2.6, unit='round trip', route='Out and back', time='1.5–2 hr', level='Moderate', color='--tA',
      desc='The first part of the loop’s Welch side: across a brook and up through birch, beech and maple, then conifers, to the broad open ledge 1.3 miles in. Big views for about 800 ft of climbing. Return the same way.', anchors=p.anchors(R['A'])),
 dict(id='B', name='Dickey Mountain via the Dickey side', short='Dickey Mountain', official=4.0, unit='round trip', route='Out and back', time='2.5–3 hr', level='Moderate', color='--tB',
      desc='The loop’s west side, out and back: 2.0 miles through hardwoods and up long granite slabs on Dickey’s southwest arm to the open summit, the higher of the two. Steady and ledgy rather than steep. Return the same way.', anchors=p.anchors(R['B'])),
 dict(id='C', name='Welch-Dickey Loop', short='Welch-Dickey Loop', official=4.4, unit='loop', route='Loop', time='3–4 hr', level='Strenuous', color='--tC',
      desc='One of the most popular short hikes in the White Mountains: up the Welch Ledges to Welch Mountain (2.0 mi), 0.5 mile over to Dickey Mountain, then 2.0 miles down Dickey’s slabs back to the lot. Much of it is on bare granite with short scrambles and jagged drop-offs. Most people hike it counterclockwise, climbing the steep Welch ledges and descending Dickey. Slippery when wet; traction needed when icy.', anchors=p.anchors(R['C'])),
]

pa = place_along
def A_(k, f, s=1, o=400): return pa(p, UP[k], [f], s, o)[0]
def path(k, f, s=1, o=450, d=0.05): return js(A_(k, f, s, o) + A_(k, f + d, s, o))
an = []
an += [f'{{k:"bear",path:{path("C",.82,1,650,.04)},per:34}}']
an += [f'{{k:"squirrel",at:{js(A_("C",.33,1,300))},hop:true}}', f'{{k:"squirrel",at:{js(A_("C",.8,-1,300))},hop:true}}']
an += [f'{{k:"chipmunk",at:{js(A_("C",.12,-1,260))},hop:true}}', f'{{k:"chipmunk",at:{js(A_("B",.25,1,280))},hop:true}}']
an += [f'{{k:"snake",path:{path("C",.62,1,320,.02)},per:30}}']
animals_js = '[\n ' + ',\n '.join(an) + '\n]'

species_extra = {
 'blueberry': 'blueberry:{name:"Lowbush blueberry",latin:"Vaccinium angustifolium",color:"#4A5FA8",shape:"berry",bloom:[5,6],fruit:[7,8],sum:"A knee-high shrub in the cracks and edges of the open ledges on both summits. White bell flowers in late spring, berries in summer, red leaves in fall.",rule:(d,e,g,s)=>e>1700&&g<0.8}',
 'sheeplaurel': 'sheeplaurel:{name:"Sheep laurel",latin:"Kalmia angustifolia",color:"#D9558E",shape:"dome",bloom:[6,7],sum:"A low evergreen shrub with rings of small deep-pink flowers in early summer, common around the open ledges. The leaves are poisonous to livestock.",rule:(d,e,g,s)=>e>1500&&g<0.9}',
 'rhodora': 'rhodora:{name:"Rhodora",latin:"Rhododendron canadense",color:"#C46BB8",shape:"dome",bloom:[5,6],sum:"A small native azalea whose rose-purple flowers open before the leaves in late May and early June, in damp pockets on the ledges.",rule:(d,e,g,s)=>e>1600&&g<0.6}',
 'cinquefoil': 'cinquefoil:{name:"Three-toothed cinquefoil",latin:"Sibbaldia tridentata",color:"#F5F3EA",shape:"cup",bloom:[6,7,8],sum:"A low mat of small white flowers and three-toothed leaves in the thin soil of the summit ledges; the leaves turn red in fall.",rule:(d,e,g,s)=>e>2100&&g<0.8}',
 'trillium': 'trillium:{name:"Painted trillium",latin:"Trillium undulatum",color:"#F4EEF0",shape:"cup",bloom:[5,6],sum:"Three white petals with a red V at the center, in the shady conifer and hardwood woods on the lower trail in late May and June.",rule:(d,e,g,s)=>e<1900&&g<0.5}',
 'ladyslipper': 'ladyslipper:{name:"Pink lady’s slipper",latin:"Cypripedium acaule",color:"#D96A9C",shape:"tube",bloom:[5,6],sum:"A native orchid with a single pink pouch on a leafless stalk, under pines and oaks along the lower and middle trail in late spring. Don’t pick it.",rule:(d,e,g,s)=>e>1100&&e<2300&&g<0.6}',
 'harlequin': 'harlequin:{name:"Rock harlequin",latin:"Capnoides sempervirens",color:"#E58AA6",shape:"tube",bloom:[5,6,7,8],sum:"Small pink-and-yellow tubular flowers on blue-green leaves, growing from cracks in the granite and on recently burned ground.",rule:(d,e,g,s)=>e>1800&&g>0.2}',
}

lm = f'''  gate({TH[0] + 70},{TH[1] + 120},0.2);
  // jack pine stand on Welch's upper south ridge: drawn large, with serotinous cones
  {{const pts=[[{JP[0] + 90},{JP[1] - 40}],[{JP[0] + 160},{JP[1] + 70}],[{JP[0] - 70},{JP[1] + 140}]];pts.forEach(([x,n],i)=>{{const g=new THREE.Group();g.position.copy(G(x,n));g.rotation.y=i*0.9;g.scale.set(1.7,1.7,1.7);world.add(g);
    const t=part(g,cyl,"#6A5240",0,0.7,0,0.09,1.4,0.09,1.04);rot(t,0,0,0.12*(i-1));
    part(g,new THREE.ConeGeometry(0.55,0.9,7),"#4F6B3A",0.08,1.35,0,1,1,1,1.05);part(g,new THREE.ConeGeometry(0.42,0.75,7),"#5C7A44",0.12,1.85,0.05,1,1,1,1.05);
    part(g,new THREE.SphereGeometry(0.4,8,6),"#56703F",-0.35,1.15,0.1,1,0.6,1,1.05);
    part(g,new THREE.ConeGeometry(0.08,0.2,6),"#8A6A3E",0.3,1.55,0.3,1,1,1,0);}});}}
  // Welch Ledges: broad open granite slab (OSM viewpoint), drawn as a raised tilted slab
  {{const q=G({VIEW[0] - 60},{VIEW[1] - 40});const m=part(world,box,"#D8D2C4",q.x,q.y+0.15,q.z,3.4,0.35,2.2,1.06);rot(m,0.08,0.5,0.1);}}
  // Dickey slabs on the southwest arm
  {{const q=G({DLG[0] + 80},{DLG[1] - 60});const m=part(world,box,"#D5CFC1",q.x,q.y+0.15,q.z,3.0,0.32,1.8,1.06);rot(m,0.1,-0.6,0.12);}}
'''

def cairn(x, n):
    return ('  {const g=new THREE.Group();g.position.copy(G(%d,%d));g.scale.set(1.9,1.9,1.9);world.add(g);'
            '[[0.85,0.35],[0.65,0.3],[0.48,0.28],[0.33,0.26],[0.2,0.22]].reduce((y,[r,h])=>{part(g,new THREE.CylinderGeometry(r,r*1.1,h,9),"#B9B2A6",0,y+h/2,0,1,1,1,1.06);return y+h;},0);'
            'part(g,cyl,"#6B4F3A",0.95,0.6,0,0.05,1.2,0.05,0);part(g,box,"#F4F1E8",0.95,1.1,0,0.08,0.3,0.6,1.06);}\n' % (x, n))


lm += '  // summit cairns with sign posts on Welch and Dickey (OSM peaks)\n' + cairn(*WEL) + cairn(*DIC)

TREE_RULE = """if(g>1.0)type=null;
    else if(e>2350){type=tr()<.55?"conifer":"shrub";p=0.04;}
    else if(e>1750&&g>0.4){type=tr()<.6?"conifer":"shrub";p=0.08;}
    else if(e>1750){type=tr()<.65?"conifer":"shrub";p=0.14;}
    else{const r0=tr();type=r0<.4?"conifer":r0<.75?"oak":r0<.88?"gold":"shrub";p=0.2+cl*.2;}"""
PH = json.load(open('welchdickey/photos.json')) if os.path.exists('welchdickey/photos.json') else {}
NOTE = ('White Mountain National Forest, Pemigewasset Ranger District. Orris Road, Thornton, New Hampshire: from I-93 exit 28 take NH 49 about 6 miles '
        'toward Waterville Valley, turn left onto Upper Mad River Road for 0.6–0.7 mile, then right onto Orris Road for 0.6 mile to the lot. '
        'Day-use fee $5 per vehicle (or a White Mountain National Forest pass); vault toilets, no water. Leashed dogs allowed. '
        'Status (November 2026): open, no closures listed. The bare ledges ice up from fall through spring; carry traction. '
        'Terrain from USGS elevation data, stylized; not for navigation.')
cfg = dict(
    title='Welch-Dickey Loop', aria='the Welch-Dickey Loop, Welch Mountain and Dickey Mountain in the White Mountains', h1='Welch-Dickey Loop · White Mountains',
    canyons=[], trails=trails, stops=stops, order=order,
    species=list(species_extra), species_extra=species_extra,
    flora={'A': ['ladyslipper', 'trillium', 'sheeplaurel', 'blueberry'], 'B': ['blueberry', 'rhodora', 'harlequin', 'ladyslipper'],
           'C': ['cinquefoil', 'blueberry', 'sheeplaurel', 'rhodora', 'harlequin', 'trillium']},
    wild=['bear', 'squirrel', 'chipmunk', 'snake', 'hawk', 'peregrine', 'vulture', 'raven', 'woodpecker'],
    wild_sum={'bear': ('Black bear', 'Lives in the hardwood forest on the lower slopes; hikers find its claw marks on the smooth gray bark of beech trees along the trail. Store food and keep dogs leashed.'),
              'squirrel': ('Red squirrel', 'A small, noisy squirrel of the spruce and pine on the ridges that chatters at hikers and leaves piles of cone scales on the rock.'),
              'chipmunk': ('Eastern chipmunk', 'Darts among the roots and boulders of the lower woods from spring to fall.'),
              'snake': ('Common garter snake', 'A harmless striped snake that suns on warm ledges on summer days. New Hampshire’s rare timber rattlesnake is not found here.'),
              'hawk': ('Broad-winged hawk', 'A small, stocky forest hawk that nests in these woods in summer; in September thousands pass over the White Mountains on migration.'),
              'peregrine': ('American kestrel', 'The smallest falcon, rust and blue-gray, sometimes seen passing over the open ledges or hovering above the valley.'),
              'vulture': ('Turkey vulture', 'Soars over the Mad River valley on tilted wings, spring to fall; groups ride the updrafts off the ledges.'),
              'raven': ('Common raven', 'Rides the wind over both summits, croaking and tumbling; often the only bird you hear on the bare rock.'),
              'woodpecker': ('Yellow-bellied sapsucker', 'A woodpecker of the hardwoods on the lower trail, heard by its stop-and-start tapping in spring. It drills neat rows of sap wells in birch and maple.')},
    grid=GRID, step=STEP, dem_b64=b64, tile=TILE, ve=1.7, ridge_ft=RIDGE,
    palette='east', tree_rule=TREE_RULE, trees_anywhere=True, rock_all_aspects=True,
    landmarks=lm, animals_js=animals_js,
    extra_js='TRAILS.forEach(T=>{const g={A:820,B:1700,C:1730}[T.id];if(g)T.gain=g;});\n// out-and-back: report the outbound mile for a stop\nmileOf=function(T,x,n){let b=null;T.pts.forEach(p=>{const d=Math.hypot(p.x-x,p.n-n);if(!b||d<b.d)b={d,m:p.m,e:p.e};});if(!b||b.d>=260)return null;const f=T.pts.find(p=>Math.hypot(p.x-x,p.n-n)<b.d+60);return {d:b.d,m:f.m,e:f.e};};',
    overview=dict(h2='Welch and Dickey, two granite summits',
                  p='Welch Mountain (2,605 ft) and Dickey Mountain (2,734 ft) stand at the gateway to Waterville Valley. Fires in the 1880s left their tops as bare granite ledges, so a short climb gives wide views. A climbs to the Welch Ledges, B goes up the Dickey side to the higher summit, and C is the full loop over both. Pick a trail to focus the model; click anything on it for a quick note.',
                  numbers='Plain numbers mark spots more than one trail passes: the trailhead is on all three, the Welch Ledges on A and C, and the Dickey slabs and summit on B and C. Lettered stops belong to one trail: C1 is the first stop only on Trail C.',
                  wild_h='Wildlife on Welch and Dickey',
                  note=NOTE),
    links={'A': [('Welch-Dickey Loop · USFS trail sheet', 'https://fs.usda.gov/Internet/FSE_DOCUMENTS/stelprdb5365159.pdf'), ('Welch-Dickey Trailhead · USFS', 'https://www.fs.usda.gov/r09/whitemountain/recreation/welch-dickey-trailhead')],
           'B': [('Welch-Dickey Loop · Hiking Project', 'https://www.hikingproject.com/trail/7010629/welch-dickey-mountain-loop'), ('Welch & Dickey · Hike New England', 'https://hikenewengland.com/WelchDickey100530.php')],
           'C': [('Welch-Dickey Trailhead · USFS', 'https://www.fs.usda.gov/r09/whitemountain/recreation/welch-dickey-trailhead'), ('Welch-Dickey Loop · Trail Finder', 'https://www.trailfinder.info/trails/trail/welch-dickey-loop-trail'), ('Welch-Dickey Loop · USFS trail sheet', 'https://fs.usda.gov/Internet/FSE_DOCUMENTS/stelprdb5365159.pdf')]},
    viewaz={'all': 0.5, 'A': 0.5, 'B': 0.3, 'C': 0.5},
    zoomcap={'A': 3.2, 'B': 2.8, 'C': 2.4},
    stop_photos=PH.get('stop', {}), flower_photos=PH.get('flower', {}), animal_photos=PH.get('animal', {}),
)
json.dump({k: {'mi': R[k]['mi'], 'gain': R[k]['gain'], 'lo': R[k]['lo'], 'hi': R[k]['hi']} for k in R}, open('welchdickey/stats.json', 'w'))
OUT = '/home/claude/site/out/welch-dickey/index.html'
os.makedirs(os.path.dirname(OUT), exist_ok=True)
print(build(cfg, OUT))
