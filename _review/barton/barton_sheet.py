from lib import *
from mk_sheet import build
import sys, json, os
import numpy as np

os.chdir('/home/claude/parks')
p = Park('barton', 30.2565, -97.798)
ZIL = (7794, 2836); SPY = (3359, 458); GAI = (-3760, -4554); TWIN = (-4717, -2752); SCU = (-8020, 1912)
HOLB = (-9756, 5186); TEND = (-8553, 6806); T360 = (-825, -4579)
R = {}
R['C'] = route_xy(p, ZIL, (1551, -903), (-4115, -5906), TWIN, SCU, HOLB, TEND)
CAMP = tuple(p.at_mile(R['C'], 0.75)[0])
R['A'] = route_xy(p, SPY, (3456, 216), CAMP, (3456, 216), SPY)
R['B'] = route_xy(p, GAI, TWIN, SCU, TWIN, GAI)
for k in R: Park.smooth_E(R[k], 9); p.describe(R[k], k)

am = lambda k, mi: tuple(p.at_mile(R[k], mi)[0])
ST = snap_stops(p, R, {
    'S1': (*CAMP, 'AC'), 'S2': (*TWIN, 'BC'), 'S3': (*SCU, 'BC'),
    'A1': (*SPY, 'A'),
    'B1': (*GAI, 'B'),
    'C1': (*ZIL, 'C'), 'C2': (*am('C', 2.25), 'C'), 'C3': (*am('C', 2.5), 'C'), 'C4': (*T360, 'C'),
    'C5': (*am('C', 7.15), 'C'), 'C6': (*TEND, 'C'),
})
TILE = (-14300, 12300, -10600, 11400)
GRID = (-14700, 12700, -11000, 11800)
if 'plot' in sys.argv:
    from plot import plot
    plot(p, (-11000, 9000, -7000, 8000), 'barton/routes2.png', routes=R, stops=ST, title='ABC', grid=1000)
    sys.exit()

STEP = 150
b64, NX, NN = p.dem_b64(*GRID, STEP=STEP)
RIDGE = int(np.percentile(p.grid, 75))
print('grid', NX, NN, NX * NN, p.grid.min(), p.grid.max(), 'p75', RIDGE)

S = lambda i: ST[i]
stops = [
 dict(id='S1', trails=['A', 'C'], x=S('S1')[0], n=S('S1')[1], name='Campbell’s Hole and the Flats', desc='About 0.75 mile up the creek from Zilker Park. Campbell’s Hole is a big, deep swimming hole in a bend of the creek, and the Flats are shallow limestone ledges beside it under shade trees. Both hold water only after good rains; there are no lifeguards.'),
 dict(id='S2', trails=['B', 'C'], x=S('S2')[0], n=S('S2')[1], name='Twin Falls', desc='Two small falls side by side over a limestone ledge, just upstream of the MoPac bridges, around mile 5 of the greenbelt. They run only when Barton Creek is flowing; in a dry spell the ledge is bare rock.'),
 dict(id='S3', trails=['B', 'C'], x=S('S3')[0], n=S('S3')[1], name='Sculpture Falls', desc='Wide limestone ledges carved by the water, with pools above and below the falls, around mile 6.25. A popular swimming spot when the creek is up. The rock is slippery; wear water shoes.'),
 dict(id='A1', trails=['A'], x=S('A1')[0], n=S('A1')[1], name='Spyglass trailhead', desc='Street parking at 1601 Spyglass Drive, with a composting restroom nearby. A short, steep path drops to the creek; turn left (downstream) for Campbell’s Hole and the Flats.'),
 dict(id='B1', trails=['B'], x=S('B1')[0], n=S('B1')[1], name='Gaines / Twin Falls access', desc='Limited free parking on the southbound MoPac service road at 3918 S MoPac Expy. No restrooms. A rocky descent of about half a mile leads to Twin Falls.'),
 dict(id='C1', trails=['C'], x=S('C1')[0], n=S('C1')[1], name='Zilker trailhead', desc='Mile 0, at 2212 William Barton Drive beside Barton Springs Pool. The first stretch is wide, flat crushed granite. The lot is free on weekdays and $7 on weekends and holidays from March through September.'),
 dict(id='C2', trails=['C'], x=S('C2')[0], n=S('C2')[1], name='Gus Fruh', desc='A deep, quiet swimming hole around mile 2.25, about a quarter mile below the Gus Fruh access on Barton Hills Drive. It fills only after rain.'),
 dict(id='C3', trails=['C'], x=S('C3')[0], n=S('C3')[1], name='Urban Assault Wall', desc='About 90 feet tall, the highest climbing wall on the greenbelt, at an open bend of the creek near mile 2.5. The limestone is loose in places; climbers wear helmets.'),
 dict(id='C4', trails=['C'], x=S('C4')[0], n=S('C4')[1], name='Loop 360 trailhead', desc='A free lot with composting restrooms at 3753 S Capital of Texas Hwy (northbound), the busiest access to the middle of the greenbelt. The trail passes under the Loop 360 bridge here.'),
 dict(id='C5', trails=['C'], x=S('C5')[0], n=S('C5')[1], name='Hill of Life', desc='The steepest part of the greenbelt: about 300 feet of climb in half a mile, on loose, rocky, sunny trail. Mountain bikers use it too; listen for riders coming down.'),
 dict(id='C6', trails=['C'], x=S('C6')[0], n=S('C6')[1], name='Trail’s End trailhead', desc='The west end of the main trail, at 1712 Camp Craft Road. Paid street parking from 8 a.m. to 8 p.m.; cars parked on Camp Craft Road itself can be towed. Two composting restrooms nearby.'),
]
stops, order = renumber(p, R, stops)
print(order, [(s['id'], s['name']) for s in stops])
trails = [
 dict(id='A', name='Campbell’s Hole from Spyglass', short='Campbell’s Hole', official=round(R['A']['mi'], 1), unit='round trip', route='Out and back', time='30–45 min', level='Easy', color='--tA',
      desc='The shortest way to the water near downtown. From Spyglass Drive a steep path drops to the creek, then the main trail runs downstream along the bluffs to Campbell’s Hole and the Flats. Return the same way.', anchors=p.anchors(R['A'], every=40)),
 dict(id='B', name='Twin Falls and Sculpture Falls', short='Twin & Sculpture Falls', official=3.2, unit='round trip', route='Out and back', time='1.5–2 hr', level='Moderate', color='--tB',
      desc='From the MoPac service road, a rocky trail drops to Twin Falls, then follows Barton Creek upstream under limestone bluffs and through juniper and oak to Sculpture Falls. The falls only run when the creek is flowing, usually after spring or fall rains.', anchors=p.anchors(R['B'], every=60)),
 dict(id='C', name='Barton Creek Greenbelt Trail', short='Greenbelt Trail', official=7.5, unit='one way', route='One way', time='3.5–4.5 hr', level='Moderate', color='--tC',
      desc='The whole main trail, from Zilker Park up Barton Creek past every swimming hole and both falls to Trail’s End on Camp Craft Road. It follows the creek bed for most of the way, with several creek crossings that can be impassable after heavy rain, and ends with the steep Hill of Life. Most people hike it with a car shuttle or in pieces from the seven access points.', anchors=p.anchors(R['C'])),
]

pa = place_along
A_ = lambda k, f, s=1, o=240: pa(p, R[k], f, s, o)
an = []
an += [f'{{k:"coyote",path:{js(A_("C",[.17],1,320)[0]+A_("C",[.19],1,320)[0])},per:26}}']
an += [f'{{k:"fox",path:{js(A_("C",[.47],-1,320)[0]+A_("C",[.49],-1,320)[0])},per:24}}']
an += [f'{{k:"raccoon",path:{js(A_("C",[.06],-1,160)[0]+A_("C",[.075],-1,160)[0])},per:20}}']
an += [f'{{k:"squirrel",at:{js(A_("A",[.3],1,160)[0])},hop:true}}', f'{{k:"squirrel",at:{js(A_("C",[.33],1,220)[0])},hop:true}}', f'{{k:"squirrel",at:{js(A_("C",[.72],-1,220)[0])},hop:true}}']
an += [f'{{k:"deer",path:{js(A_("C",[.60],1,380)[0]+A_("C",[.62],1,380)[0])},per:28}}', f'{{k:"deer",path:{js(A_("B",[.18],-1,380)[0]+A_("B",[.2],-1,380)[0])},per:30,ph:0.4}}']
an += [f'{{k:"armadillo",path:{js(A_("C",[.26],1,260)[0]+A_("C",[.27],1,260)[0])},per:22}}']
an += [f'{{k:"bobcat",path:{js(A_("C",[.88],-1,360)[0]+A_("C",[.9],-1,360)[0])},per:26}}']
an += [f'{{k:"snake",path:{js(A_("C",[.54],1,200)[0]+A_("C",[.55],1,200)[0])},per:30}}']
an += [f'{{k:"turtle",at:{js(A_("C",[.11],-1,90)[0])}}}', f'{{k:"turtle",at:{js(A_("B",[.3],-1,110)[0])}}}']
an += [f'{{k:"heron",at:{js(A_("C",[.38],-1,110)[0])}}}', f'{{k:"egret",at:{js(A_("C",[.78],1,110)[0])}}}']
animals_js = '[\n ' + ',\n '.join(an) + '\n]'

def ck(ids, minor):
    try: return p.creek(ids, GRID, minor=minor)
    except Exception as ex: print('creek err', ex); return None
cr = ck([i if i in p.WID else int(i) for i in ['1384176561']], False)
creeks = [dict(id='barton', **cr)] if cr else []
CK = [[q[0], q[1]] for q in (cr['pts'] if cr else []) if TILE[0] + 250 < q[0] < TILE[1] - 250 and TILE[2] + 250 < q[1] < TILE[3] - 250]  # ribbon only on the terrain

g = {s['name']: s for s in stops}
def at(nm): return g[nm]['x'], g[nm]['n']
lm = """  gate(%d,%d,0.5);gate(%d,%d,0.9);gate(%d,%d,2.1);gate(%d,%d,1.2);gate(%d,%d,0.6);
  // Loop 360 trailhead composting restrooms
  {const q=G(%d,%d);part(world,box,"#8A7358",q.x+1.2,q.y+0.6,q.z,1.0,1.2,0.8,1.06);part(world,box,"#5E5A52",q.x+1.2,q.y+1.26,q.z,1.2,0.14,1.0,1.06);}
  // Barton Creek: a flat ribbon of water along the OSM centerline
  const CK=%s;
  const U=G(100,0).x-G(0,0).x;
  for(let i=0;i<CK.length-1;i++){const a=G(CK[i][0],CK[i][1]),b=G(CK[i+1][0],CK[i+1][1]);
    const L=Math.hypot(b.x-a.x,b.z-a.z);const m=part(world,box,"#7FB3C8",(a.x+b.x)/2,Math.max(a.y,b.y)+0.04,(a.z+b.z)/2,L+0.02,0.06,0.7*U,0);rot(m,0,-Math.atan2(b.z-a.z,b.x-a.x),0);}
  // falls: a solid limestone ledge across the creek with white water spilling over it (exaggerated)
  function falls(x,n,w,tw){let bi=0,bd=1e18;for(let i=0;i<CK.length-1;i++){const d=Math.hypot(CK[i][0]-x,CK[i][1]-n);if(d<bd){bd=d;bi=i;}}
    const a=G(CK[bi][0],CK[bi][1]),b=G(CK[bi+1][0],CK[bi+1][1]),ang=-Math.atan2(b.z-a.z,b.x-a.x);const q=G(x,n);
    const grp=new THREE.Group();grp.position.set(q.x,q.y,q.z);grp.rotation.y=ang;grp.scale.set(2,2,2);world.add(grp);
    part(grp,box,"#D8CDB2",0.0,0.55,0,0.9,1.1,w,1.06);part(grp,box,"#CFC3A6",-0.8,0.5,0,0.75,1.0,w*1.05,1.06);part(grp,box,"#9CC6D6",-0.8,1.05,0,0.75,0.12,w*0.95,1.06);
    part(grp,box,"#CBBF9F",0.85,0.2,0,0.8,0.4,w*1.15,1.06);
    const cw=(tw?[[-1,0.24],[1,0.24]]:[[-0.32,0.3],[0,0.3],[0.32,0.3]]);
    cw.forEach(([s,k])=>{part(grp,box,"#F7FBFD",0.52,0.62,s*w*(tw?0.22:1),0.16,1.0,w*k,1.06);part(grp,new THREE.SphereGeometry(1,8,6),"#FFFFFF",1.05,0.45,s*w*(tw?0.22:1),0.35,0.18,w*k*0.7,1.06);});
    part(grp,box,"#8FBFD2",1.9,0.05,0,1.6,0.08,w*1.3,0);}
  falls(%d,%d,2.4,true);falls(%d,%d,3.4,false);
""" % (*at('Zilker trailhead'), *at('Spyglass trailhead'), *at('Gaines / Twin Falls access'), *at('Loop 360 trailhead'), *at('Trail’s End trailhead'),
       *at('Loop 360 trailhead'), js(CK), *at('Twin Falls'), *at('Sculpture Falls'))

species_extra = {
 'cedarsage': 'cedarsage:{name:"Cedar sage",latin:"Salvia roemeriana",color:"#D7263D",shape:"tube",bloom:[3,4,5,6],sum:"A low sage with round leaves and slender scarlet flowers, growing in the shade of juniper and oak along the greenbelt. Hummingbirds visit it in spring.",rule:(d,e,g,s)=>d>60&&g<0.9&&s<0.3}',
 'mtlaurel': 'mtlaurel:{name:"Texas mountain laurel",latin:"Dermatophyllum secundiflorum",color:"#7A4FB0",shape:"berry",bloom:[2,3,4],sum:"An evergreen shrub or small tree whose drooping purple flower clusters smell like grape soda in early spring. The red seeds in its pods are poisonous.",rule:(d,e,g,s)=>d>120&&g>0.1&&g<1.0}',
 'turkscap': 'turkscap:{name:"Turk’s cap",latin:"Malvaviscus arboreus var. drummondii",color:"#D8392B",shape:"tube",bloom:[5,6,7,8,9,10,11],sum:"A shade-loving shrub with red hibiscus-like flowers that never fully open. Common in the creekside woods; hummingbirds and butterflies use it all summer.",rule:(d,e,g,s)=>d<500&&g<0.6}',
 'redbuckeye': 'redbuckeye:{name:"Red buckeye",latin:"Aesculus pavia",color:"#C8322C",shape:"spike",bloom:[3,4],sum:"A small understory tree near the creek with upright spikes of red tubular flowers in early spring, one of the first hummingbird flowers of the year.",rule:(d,e,g,s)=>d<350&&g<0.7}',
 'firewheel': 'firewheel:{name:"Firewheel",latin:"Gaillardia pulchella",color:"#D9542B",shape:"cup",bloom:[4,5,6,7],sum:"Also called Indian blanket. Red daisies tipped with yellow, in sunny openings and along the trail edges in late spring.",rule:(d,e,g,s)=>d>150&&g<0.4}',
 'twistflower': 'twistflower:{name:"Bracted twistflower",latin:"Streptanthus bracteatus",color:"#A779C9",shape:"spike",bloom:[4,5],sum:"Rare: a lavender mustard of the Edwards Plateau, listed as threatened by the U.S. Fish and Wildlife Service in 2023. The City of Austin names it among the endangered species of the greenbelt. Look, never pick.",rule:(d,e,g,s)=>d>120&&g>0.2&&g<0.9&&s>-0.2}',
 'rupicola': 'rupicola:{name:"Twist-leaf yucca",latin:"Yucca rupicola",color:"#F1EBCF",shape:"yucca",bloom:[4,5,6],sum:"A low yucca of the Hill Country whose leaves twist as they age. It sends up a stalk of creamy bell flowers in late spring on rocky slopes.",rule:(d,e,g,s)=>d>150&&g>0.15&&s>-0.1}',
}
tree_rule = """if(mk<0.25){type=null;}
    else if(cd<170){const r0=tr();type=r0<.45?"syc":r0<.85?"oak":"shrub";p=0.16;}
    else if(g>1.1)type=null;
    else{const r0=tr();type=r0<.5?"conifer":r0<.85?"oak":"shrub";p=0.06+cl*.03;}"""

PH = json.load(open('/home/claude/parks/barton/photos.json')) if os.path.exists('/home/claude/parks/barton/photos.json') else {'stop': {}, 'flower': {}, 'animal': {}}
nm = {s['name']: s['id'] for s in stops}
stop_photos = {nm[k]: v for k, v in PH['stop'].items() if k in nm}

cfg = dict(
    title='Barton Creek Greenbelt', aria='Campbell’s Hole, Twin Falls and Sculpture Falls, and the Barton Creek Greenbelt Trail in Austin, Texas', h1='Barton Creek Greenbelt',
    canyons=creeks, trails=trails, stops=stops, order=order,
    species=['cedarsage', 'mtlaurel', 'turkscap', 'redbuckeye', 'firewheel', 'twistflower', 'rupicola'], species_extra=species_extra,
    flora={'A': ['turkscap', 'cedarsage', 'mtlaurel', 'firewheel'], 'B': ['cedarsage', 'redbuckeye', 'mtlaurel', 'turkscap', 'rupicola'], 'C': ['cedarsage', 'mtlaurel', 'turkscap', 'redbuckeye', 'firewheel', 'twistflower', 'rupicola']},
    wild=['coyote', 'fox', 'raccoon', 'squirrel', 'deer', 'armadillo', 'bobcat', 'snake', 'turtle', 'heron', 'egret', 'hawk', 'vulture', 'cardinal', 'kingfisher', 'bluebird'],
    wild_sum={'coyote': ('Coyote', 'The animal most often reported on the greenbelt. Usually seen alone at dawn or dusk on the trail or in the dry creek bed; keep dogs leashed.'),
              'fox': ('Gray fox', 'A small grizzled fox that can climb trees. Active mostly at night in the wooded draws; trail cameras catch it often.'),
              'raccoon': ('Raccoon', 'Hunts crayfish and frogs in the creek pools at night. Look for hand-shaped tracks in the mud by the water.'),
              'squirrel': ('Eastern fox squirrel', 'The big rusty-bellied squirrel of Austin’s oaks and pecans, busy along the trail all day.'),
              'deer': ('White-tailed deer', 'Browses the quieter upper greenbelt between MoPac and Trail’s End, mostly early and late in the day.'),
              'armadillo': ('Armadillo', 'An armored mammal that roots for grubs in the leaf litter at dusk. Listed on iNaturalist as the Mexican long-nosed armadillo, recently split from the nine-banded armadillo.'),
              'bobcat': ('Bobcat', 'A short-tailed wild cat that lives in the woods along the creek. Seen only now and then, usually at dawn or dusk.'),
              'snake': ('Western diamond-backed rattlesnake', 'Venomous; suns on rocks and ledges in warm months. Harmless watersnakes and ribbon snakes are far more common in the creek. Watch your step and give any snake room.'),
              'turtle': ('Red-eared slider', 'The pond slider, the turtle most often seen here, basks on logs and rocks in the deep pools. Texas cooters and softshells live here too.'),
              'heron': ('Great blue heron', 'Stands still in the shallow pools hunting fish and frogs. The smaller green heron and yellow-crowned night heron fish here too.'),
              'egret': ('Snowy egret', 'A slim white heron with black legs and yellow feet, wading the creek pools when the water is up.'),
              'hawk': ('Red-shouldered hawk', 'The loud hawk of the creek woods, with a barred rusty breast. Its piercing kee-ah call carries along the bluffs.'),
              'vulture': ('Black vulture', 'Groups soar over the bluffs and roost on cliff ledges and power poles. Its wingtips flash white.'),
              'cardinal': ('Northern cardinal', 'The most common bird on the greenbelt, singing from the brush all year.'),
              'kingfisher': ('Belted kingfisher', 'Rattles low along the creek when the pools hold water, then plunges headfirst for small fish.'),
              'bluebird': ('Golden-cheeked warbler', 'Rare here: the only bird that nests only in Texas, listed as endangered since 1990. It arrives in March to nest in old Ashe juniper and oak woods, using strips of juniper bark, and leaves in July. Listen for its buzzy song on the wooded slopes.')},
    grid=GRID, step=STEP, dem_b64=b64, tile=TILE, ve=4.5, ridge_ft=RIDGE,
    palette={"ground": "#E5DFC6", "groundN": "#DAD6BC", "rock": "#D8CEB4", "rockDeep": "#BEB295", "ridge": "#EEE8D5", "oak": "#5E7E45", "shrub": "#98A06A", "conifer": "#4A6A47"},
    tree_rule=tree_rule, trees_anywhere=True,
    landmarks=lm, animals_js=animals_js,
    zoomcap={'A': 7.0, 'B': 3.0, 'C': 2.4},
    overview=dict(h2='A limestone creek through the middle of Austin',
                  p='Barton Creek has cut a canyon of limestone bluffs from the Hill Country to Barton Springs. The greenbelt follows it for 7.5 miles through juniper and oak woods, with swimming holes and ledge falls that come alive after rain. A is a short walk from Spyglass to Campbell’s Hole, B links Twin Falls and Sculpture Falls, and C is the whole main trail from Zilker Park to Trail’s End. Pick a trail to focus the model; click anything on it for a quick note.',
                  numbers='Plain numbers mark spots on more than one trail: the swimming holes and falls are on the main trail too. Lettered stops belong to one trail: C4 is the fourth stop on Trail C. The official mile markers count from Zilker Park.',
                  wild_h='Wildlife on the greenbelt',
                  note='Barton Creek Greenbelt, City of Austin Parks and Recreation. Seven access points; the main ones are Zilker (2212 William Barton Dr), Spyglass (1601 Spyglass Dr), Loop 360 (3753 S Capital of Texas Hwy), Gaines (3918 S MoPac Expy) and Trail’s End (1712 Camp Craft Rd). All park areas close at 10 p.m. Dogs on a 6-ft leash. No trash cans on the trail: pack everything out. Water levels change quickly with rain and the city does not monitor them; check the USGS or LCRA gauges before you go. Endangered Barton Springs and Austin blind salamanders live in the springs at the trail’s east end. Terrain from USGS elevation data, stylized; not for navigation.'),
    links={'A': [('Barton Creek Greenbelt · Austin Parks and Recreation', 'https://www.austintexas.gov/parks/locations/barton-creek-greenbelt'), ('Spyglass access · The Outbound', 'https://www.theoutbound.com/texas/hiking/hike-the-barton-creek-greenbelt-trail')],
           'B': [('Twin Falls and Sculpture Falls · The Outbound', 'https://www.theoutbound.com/texas/hiking/hike-twin-falls-and-sculpture-falls-via-barton-creek-greenbelt-trail'), ('Greenbelt map · City of Austin', 'https://austintexas.gov/sites/default/files/files/Parks/GIS/Barton_Creek_GBelt_Web_Map_reduced.pdf')],
           'C': [('Barton Creek Greenbelt · Austin Parks and Recreation', 'https://www.austintexas.gov/parks/locations/barton-creek-greenbelt'), ('Barton Creek Greenbelt · TrailLink', 'https://www.traillink.com/trail/barton-creek-greenbelt/'), ('Barton Creek Greenbelt · Wikipedia', 'https://en.wikipedia.org/wiki/Barton_Creek_Greenbelt')]},
    extra_js=('TRAILS.forEach(T=>{const g={B:230}[T.id];if(g)T.gain=g;});\n'
              '// out-and-back: report the outbound mile for a stop\n'
              'mileOf=function(T,x,n){let b=null;T.pts.forEach(p=>{const d=Math.hypot(p.x-x,p.n-n);if(!b||d<b.d)b={d,m:p.m,e:p.e};});if(!b||b.d>=260)return null;const f=T.pts.find(p=>Math.hypot(p.x-x,p.n-n)<b.d+60);return {d:b.d,m:f.m,e:f.e};};'),
    viewaz={'all': 0.6, 'A': 0.6, 'B': 0.6, 'C': 0.6},
    stop_photos=stop_photos, flower_photos=PH['flower'], animal_photos=PH['animal'],
)
json.dump({k: {'mi': R[k]['mi'], 'gain': R[k]['gain'], 'lo': R[k]['lo'], 'hi': R[k]['hi']} for k in R}, open('barton/stats.json', 'w'))
os.makedirs('/home/claude/site/out/barton-creek-greenbelt', exist_ok=True)
OUT = '/home/claude/site/out/barton-creek-greenbelt/index.html'
print(build(cfg, OUT))
# post-process my own page: golden-cheeked warbler colors for the renamed bluebird (BIRDC is declared after extra_js)
h = open(OUT).read(); h2 = h.replace('bluebird:["#3D78C4", "#D98A4E", null]', 'bluebird:["#2E2E2E", "#F2D33A", "#F2D33A"]', 1)
print('warbler colors', h2 != h); open(OUT, 'w').write(h2)
