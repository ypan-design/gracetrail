from lib import *
from mk_sheet import build
import sys, json, os
import numpy as np

os.chdir('/home/claude/parks')
p = Park('kaaterskill', 42.1932, -74.0630)   # origin = Kaaterskill Falls (Wikipedia coordinates, top of the upper fall)
TH = (-60, 920)        # Laurel House Road parking area (end of road, toilets)
PLAT = (-141, 272)     # viewing platform (OSM viewpoint)
BR = (300, 200)        # footbridge over Spruce Creek above the falls
TOP = (26, -326)       # Escarpment Trail meets the yellow Kaaterskill Falls Trail (top of the stone staircase)
LJ = (-402, 22)        # foot of the staircase, yellow trail junction
MP = (-224, 72)        # pool between the two tiers (OSM viewpoint)
LAY = (-1400, -1521)   # Layman's Monument (OSM historic=monument)
SUN = (734, -2486)     # Sunset Rock (OSM viewpoint 0.13 mi before Inspiration Point; DEC mile 1.75 vs 1.9)
IP = (1091, -3018)     # Inspiration Point (OSM viewpoint)
YJ = (4557, -3014)     # Escarpment Trail meets Yellow Horse Trail (OSM way ends)
R = {}
R['A'] = route_xy(p, TH, PLAT)
R['B'] = route_xy(p, TH, BR, TOP, LJ, MP)
R['C'] = route_xy(p, TH, BR, TOP, LAY, SUN, IP, (4300, -3080), YJ, (3653, -2869), (858, -2208), (642, -535), TH)
for k in R: Park.smooth_E(R[k], 9); p.describe(R[k], k)
ST = snap_stops(p, R, {
    'S1': (TH[0], TH[1], 'ABC'), 'A1': (PLAT[0], PLAT[1], 'A'),
    'S2': (BR[0], BR[1], 'BC'), 'S3': (TOP[0], TOP[1], 'BC'),
    'B1': (LJ[0], LJ[1], 'B'), 'B2': (MP[0], MP[1], 'B'),
    'C1': (LAY[0], LAY[1], 'C'), 'C2': (SUN[0], SUN[1], 'C'), 'C3': (IP[0], IP[1], 'C'), 'C4': (YJ[0], YJ[1], 'C'),
})
TILE = (-3100, 6100, -4600, 2400)
GRID = (-3400, 6400, -4900, 2700)
if 'plot' in sys.argv:
    from plot import plot
    plot(p, TILE, 'kaaterskill/routes.png', routes=R, stops=ST, title='kaaterskill', grid=500)
    plot(p, (-700, 600, -500, 1000), 'kaaterskill/routesAB.png', routes=R, stops=ST, title='A B', grid=100)
    sys.exit()

STEP = 50
b64, NX, NN = p.dem_b64(*GRID, STEP=STEP)
RIDGE = int(round(float(np.percentile(p.grid, 75)), -1))
print('grid', NX, NN, NX * NN, p.grid.min(), p.grid.max(), 'p75', RIDGE)

S = lambda i: ST[i]
stops = [
 dict(id='S1', trails=['A', 'B', 'C'], x=S('S1')[0], n=S('S1')[1], name='Laurel House Road parking', desc='The main DEC parking area for the falls, at the end of Laurel House Road off North Lake Road, with a seasonal portable toilet. It fills early on summer and fall weekends. The Laurel House hotel stood near here; it once dammed the creek and charged visitors to watch the water released over the falls.'),
 dict(id='A1', trails=['A'], x=S('A1')[0], n=S('A1')[1], name='Viewing platform', desc='An overlook platform above the gorge with a view of the falls and the valley, 0.3 mile from the parking area on a firm crushed-stone path built in 2016. Stay behind the railings: people have died falling from the ledges around the falls.'),
 dict(id='S2', trails=['B', 'C'], x=S('S2')[0], n=S('S2')[1], name='Spruce Creek footbridge', desc='A footbridge over Spruce Creek a short way above the falls, leading to the blue-marked Escarpment Trail. Entering the water within 150 feet upstream of the top of the falls is prohibited.'),
 dict(id='S3', trails=['B', 'C'], x=S('S3')[0], n=S('S3')[1], name='Top of the stone staircase', desc='The Escarpment Trail meets the yellow-marked Kaaterskill Falls Trail. A long stone staircase, built in 2016, drops from here toward the falls; the Escarpment Trail continues downhill toward Layman’s Monument.'),
 dict(id='B1', trails=['B'], x=S('B1')[0], n=S('B1')[1], name='Foot of the staircase', desc='The bottom of the stairs. A short spur leads to the pool between the two tiers; the yellow trail continues down past the lower fall to Bastion Falls on Route 23A, where the Molly Smith parking area is now closed.'),
 dict(id='B2', trails=['B'], x=S('B2')[0], n=S('B2')[1], name='Pool below the upper fall', desc='The pool between the two tiers, with a close view of the upper fall, the longer drop at about 180 feet; the two drops total about 260 feet. Rocks are slick, and flash floods can happen here: move to higher ground if the water rises.'),
 dict(id='C1', trails=['C'], x=S('C1')[0], n=S('C1')[1], name='Layman’s Monument', desc='A stone monument to Frank D. Layman, a firefighter who died fighting a forest fire here on August 10, 1900. The trail turns sharply here and follows the rim of Kaaterskill Clove.'),
 dict(id='C2', trails=['C'], x=S('C2')[0], n=S('C2')[1], name='Sunset Rock', desc='One of several ledges along the rim, usually marked by a sign, with a view south over Kaaterskill Clove toward Kaaterskill High Peak.'),
 dict(id='C3', trails=['C'], x=S('C3')[0], n=S('C3')[1], name='Inspiration Point', desc='A broad, exposed ledge with old carved inscriptions in the rock and a wide view west and south over Kaaterskill Clove. Keep well back from the edge.'),
 dict(id='C4', trails=['C'], x=S('C4')[0], n=S('C4')[1], name='Yellow Horse Trail junction', desc='About 0.75 mile past Inspiration Point the Escarpment Trail meets the yellow-marked Yellow Horse Trail, a flat old wood road that leads back toward the falls. The Escarpment Trail continues north to Boulder Rock and the Catskill Mountain House site.'),
]
stops, order = renumber(p, R, stops)
print(order, [(s['id'], s['name']) for s in stops])
trails = [
 dict(id='A', name='Kaaterskill Falls viewing platform', short='Viewing platform', official=0.6, unit='round trip', route='Out and back', time='20–30 min', level='Easy', color='--tA',
      desc='The easiest way to see the falls: a firm crushed-stone path, at least 5 feet wide with grades of no more than 10%, from the Laurel House Road parking area to an overlook platform above the gorge. 0.3 mile each way.', anchors=p.anchors(R['A'])),
 dict(id='B', name='Kaaterskill Falls Trail to the pools', short='Kaaterskill Falls', official=1.4, unit='round trip', route='Out and back', time='1–1.5 hr', level='Moderate', color='--tB',
      desc='Crosses Spruce Creek above the falls, follows the Escarpment Trail a short way and descends a long stone staircase to the pools at the base of the upper fall, about 0.7 mile from the parking area. The climb back up the stairs is the hard part. Nine people died at the falls between 1988 and 2021; stay on the trail and off the ledges.', anchors=p.anchors(R['B'])),
 dict(id='C', name='Escarpment Trail loop to Inspiration Point', short='Inspiration Point', official=3.9, unit='loop', route='Loop', time='2–3 hr', level='Moderate', color='--tC',
      desc='Follows the blue Escarpment Trail down a rocky stretch to Layman’s Monument, then along the rim of Kaaterskill Clove past several ledges to Sunset Rock and Inspiration Point, with views of Kaaterskill High Peak. It returns on the yellow Yellow Horse Trail, a flat former wood road, and the Schutt Road Trail. Junctions can be confusing; carry a map.', anchors=p.anchors(R['C'])),
]

pa = place_along
A_ = lambda k, f, s=1, o=240: pa(p, R[k], [f], s, o)[0]
an = []
an += [f'{{k:"bear",path:{js(A_("C",.20,-1,420)+A_("C",.23,-1,420))},per:34}}', f'{{k:"bear",path:{js(A_("C",.80,1,380)+A_("C",.83,1,380))},per:36,ph:0.5}}']
an += [f'{{k:"deer",path:{js(A_("C",.45,1,320)+A_("C",.48,1,320))},per:28}}', f'{{k:"deer",path:{js(A_("C",.90,-1,300)+A_("C",.93,-1,300))},per:26,ph:0.4}}']
an += [f'{{k:"turkey",path:{js(A_("C",.70,-1,260)+A_("C",.72,-1,260))},per:26}}']
an += [f'{{k:"chipmunk",at:{js(A_("A",.35,-1,140))},hop:true}}', f'{{k:"chipmunk",at:{js(A_("B",.55,-1,130))},hop:true}}', f'{{k:"chipmunk",at:{js(A_("C",.42,1,160))},hop:true}}']
animals_js = '[\n ' + ',\n '.join(an) + '\n]'

bn = {s['name']: s for s in stops}
th, pl, lay, sun, ip = [bn[k] for k in ('Laurel House Road parking', 'Viewing platform', 'Layman’s Monument', 'Sunset Rock', 'Inspiration Point')]
lm = f'''  gate({th['x'] + 40},{th['n'] + 60},2.8);
  // Kaaterskill Falls: two tiers on Spruce Creek, water flowing west-northwest (OSM creek); upper tier at the Wikipedia point,
  // lower tier below the middle pool. Drawn exaggerated, with volume (water slab + rock wall behind).
  const fallTex=stripeTex("#9ED3E8","#FFFFFF",64,128,22,9,14);fallTex.repeat.set(1,1.5);
  const fallMat=new THREE.MeshBasicMaterial({{map:fallTex}});
  const rings=[],mist=[];
  function fall(x,n,dx,dn,w,h,sc){{const F=G(x,n);const d=new THREE.Vector3(dx,0,-dn).normalize();
    const wf=new THREE.Group();wf.position.copy(F);wf.rotation.y=Math.atan2(d.x,d.z);wf.scale.setScalar(sc);world.add(wf);
    const wt=new THREE.Mesh(new THREE.BoxGeometry(w,h,0.22),fallMat);wt.position.set(0,h/2,-0.25);wf.add(wt);
    part(wf,box,"#6F6B64",0,h/2,-0.62,w+0.9,h+0.25,0.55,1.04);
    part(wf,box,"#A39E93",0,h+0.1,-0.45,w+1.2,0.22,0.95,1.05);
    for(let i=0;i<3;i++){{part(wf,ico,i%2?"#9A958A":"#85817A",-(w/2+0.55)-i*0.15,h*(0.75-i*0.22),-0.3+i*0.25,0.55,h*0.3,0.5);part(wf,ico,i%2?"#85817A":"#9A958A",(w/2+0.55)+i*0.15,h*(0.72-i*0.2),-0.3+i*0.25,0.52,h*0.28,0.5);}}
    const pool=new THREE.Mesh(new THREE.CylinderGeometry(1,1,0.12,18),new THREE.MeshBasicMaterial({{color:"#9CD3E0"}}));pool.position.set(0,0.06,0.55);pool.scale.set(w*0.9+0.5,1,0.75);wf.add(pool);
    for(let i=0;i<2;i++){{const rg=new THREE.Mesh(new THREE.RingGeometry(0.45,0.55,24),new THREE.MeshBasicMaterial({{color:"#FFFFFF",transparent:true,side:THREE.DoubleSide}}));rg.rotation.x=-Math.PI/2;rg.position.set(0,0.14,0.45);wf.add(rg);rings.push(rg);}}
    for(let i=0;i<4;i++){{const m=new THREE.Mesh(new THREE.SphereGeometry(0.16,8,6),new THREE.MeshBasicMaterial({{color:"#FFFFFF",transparent:true}}));wf.add(m);mist.push({{m,ph:i/4,x:(i%3-1)*0.35}});}}
    return wf;}}
  fall(-150,55,-1,0.3,1.1,3.8,1);
  fall(-330,100,-1,0.15,1.3,1.9,1);
  fall(-2030,-650,-0.7,-0.7,1.2,0.9,0.8);   // Bastion Falls at the Route 23A hairpin
  // viewing platform (deck on posts with railing), facing the falls
  {{const q=G({pl['x']},{pl['n']});const g=new THREE.Group();g.position.copy(q);g.rotation.y=Math.atan2(-0.1,-0.9);g.scale.setScalar(1.3);world.add(g);
   part(g,box,"#9C7653",0,0.35,0,1.3,0.12,0.9,1.06);[[-0.6,-0.4],[0.6,-0.4],[-0.6,0.4],[0.6,0.4]].forEach(([a,b])=>part(g,box,"#6B4F3A",a,0.15,b,0.08,0.35,0.08,0));
   part(g,box,"#5C4636",0,0.62,0.42,1.3,0.06,0.06,0);part(g,box,"#5C4636",-0.63,0.62,0,0.06,0.06,0.9,0);part(g,box,"#5C4636",0.63,0.62,0,0.06,0.06,0.9,0);}}
  // Layman's Monument: tapered fieldstone pillar with a plaque
  {{const q=G({lay['x']},{lay['n']});const g=new THREE.Group();g.position.copy(q);g.scale.setScalar(1.6);world.add(g);
   part(g,new THREE.CylinderGeometry(0.28,0.55,1.7,4),"#8C877C",0,0.85,0,1,1,1,1.06).rotation.y=Math.PI/4;
   part(g,new THREE.ConeGeometry(0.3,0.35,4),"#7A766C",0,1.87,0,1,1,1,1.06).rotation.y=Math.PI/4;part(g,box,"#D9D4C8",0,1.0,0.36,0.32,0.4,0.04,0);}}
  // Sunset Rock and Inspiration Point: open rock ledges with a trail sign
  function ledge(x,n,ry){{const q=G(x,n);const g=new THREE.Group();g.position.copy(q);g.rotation.y=ry;g.scale.setScalar(1.4);world.add(g);
   part(g,box,PAL.stone,0,0.18,0,2.0,0.36,1.3,1.06);part(g,ico,PAL.rock,-0.7,0.45,-0.35,0.55,0.4,0.5);
   part(g,cyl,"#6B4F3A",0.75,0.6,-0.3,0.05,0.9,0.05);part(g,box,"#E9E1D2",0.75,1.0,-0.3,0.55,0.26,0.05,1.06);}}
  ledge({sun['x']},{sun['n']},0.3);ledge({ip['x']},{ip['n']},0.6);
  anim.water={{fallTex,rings,mist}};
'''

creeks = []
for nm, minor in [('Spruce Creek', True), ('Kaaterskill Creek', False)]:
    for i, wid in enumerate([w['id'] for w in p.W if w.get('n') == nm]):
        c = p.creek([wid], GRID, minor=minor)
        if c: creeks.append(dict(id=f"{nm.split()[0].lower()}{i}", **c))
print('creeks', len(creeks))

species_extra = {
 'laurel_ks': 'laurel_ks:{name:"Mountain laurel",latin:"Kalmia latifolia",color:"#F4C6D4",shape:"dome",bloom:[6],sum:"An evergreen shrub of the dry, rocky woods along the escarpment, covered in clusters of white-to-pink cup flowers in June.",rule:(d,e,g,s)=>d>150&&e>1700}',
 'hobble_ks': 'hobble_ks:{name:"Hobblebush",latin:"Viburnum lantanoides",color:"#F5F2EA",shape:"dome",bloom:[5],sum:"A sprawling shrub of the shady forest understory with flat clusters of white flowers in May and big heart-shaped leaves; its low branches root where they touch the ground.",rule:(d,e,g,s)=>d<700&&e>1800}',
 'trillium_ks': 'trillium_ks:{name:"Trillium",latin:"Trillium spp.",color:"#B5354A",shape:"cup",bloom:[5],sum:"Three-petaled spring wildflowers of the moist forest floor, common on Catskill trails in May.",rule:(d,e,g,s)=>d<500&&g<0.7}',
 'troutlily_ks': 'troutlily_ks:{name:"Trout lily",latin:"Erythronium americanum",color:"#F2C73A",shape:"cup",bloom:[4,5],sum:"A small yellow lily with nodding flowers and brown-mottled leaves, one of the first wildflowers of spring in the hardwood forest.",rule:(d,e,g,s)=>d<450&&s<0.3}',
 'foam_ks': 'foam_ks:{name:"Foamflower",latin:"Tiarella cordifolia",color:"#F3F0EA",shape:"spike",bloom:[5,6],sum:"Spikes of tiny white flowers over maple-like leaves, in damp shady spots near streams in late spring.",rule:(d,e,g,s)=>d<300}',
}

PH = json.load(open('kaaterskill/photos.json')) if os.path.exists('kaaterskill/photos.json') else {}
cfg = dict(
    title='Kaaterskill Falls', aria='Kaaterskill Falls and the Escarpment Trail in Catskill Park, New York', h1='Kaaterskill Falls',
    canyons=creeks, trails=trails, stops=stops, order=order,
    species=list(species_extra), species_extra=species_extra,
    flora={'A': ['laurel_ks', 'troutlily_ks', 'foam_ks'], 'B': ['hobble_ks', 'foam_ks', 'trillium_ks', 'troutlily_ks'], 'C': ['laurel_ks', 'hobble_ks', 'trillium_ks']},
    wild=['bear', 'deer', 'turkey', 'chipmunk', 'woodpecker', 'hawk', 'raven'],
    wild_sum={'bear': ('Black bear', 'Black bears live throughout the Catskills and are most active from spring through fall. Keep food packed away, never feed them, and give any bear plenty of room.'),
              'deer': ('White-tailed deer', 'Browses the hardwood forest on the plateau above the falls, most often seen early and late in the day.'),
              'turkey': ('Wild turkey', 'Flocks scratch through the leaf litter in the oak and beech woods along the Yellow Horse Trail.'),
              'chipmunk': ('Eastern chipmunk', 'A small striped ground squirrel that darts among the rocks and roots beside the trails, with a sharp chipping call.'),
              'woodpecker': ('Pileated woodpecker', 'A crow-sized woodpecker with a red crest; listen for its loud drumming and look for its big rectangular holes in dead trees.'),
              'hawk': ('Red-tailed hawk', 'Rides the updrafts along the escarpment and over Kaaterskill Clove.'),
              'raven': ('Common raven', 'Large black birds that soar and tumble along the cliffs of the clove; listen for their deep croaks.')},
    grid=GRID, step=STEP, dem_b64=b64, tile=TILE, ve=1.5, ridge_ft=2480,
    palette={'ground': '#C4E5C8', 'groundN': '#ADD7B4', 'oak': '#4E7F3A', 'sycamore': '#9DBF4E', 'gold': '#E39A3C', 'ridge': '#BBDDBF', 'rock': '#B7B0A4', 'rockDeep': '#9C958A'}, trees='east',
    landmarks=lm, animals_js=animals_js,
    extra_js='TRAILS.forEach(T=>{const g={A:130,B:250,C:519}[T.id];if(g)T.gain=g;});',
    overview=dict(h2='Kaaterskill Falls and the Catskill Escarpment',
                  p='Kaaterskill Falls drops about 260 feet in two tiers on Spruce Creek, at the head of Kaaterskill Clove in the northeastern Catskills. Thomas Cole painted it in 1826, and it became a favorite subject of the Hudson River School painters. A walks from the Laurel House Road parking area to the viewing platform above the falls, B goes down a stone staircase to the pools at the base of the upper fall, and C follows the blue Escarpment Trail along the rim of the clove to Inspiration Point and loops back on the Yellow Horse Trail. Pick a trail to focus the model; click anything on it for a quick note.',
                  numbers='Plain numbers mark spots more than one trail passes: the parking area, the footbridge and the top of the staircase. Lettered stops belong to one trail: C3 is the third stop on Trail C.',
                  wild_h='Wildlife around Kaaterskill Falls',
                  note='Kaaterskill Wild Forest, Catskill Park, New York (NYS DEC). Laurel House Road parking area, off North Lake Road near Haines Falls; no fee. Status (November 2026): open. The Molly Smith parking area on Route 23A is closed, and parking in the Route 23A pull-offs in Kaaterskill Clove is banned May through October (vehicles are ticketed and towed); use the Laurel House Road, Schutt Road or North–South Lake lots and move on if a lot is full. Kaaterskill Clove is closed from half an hour after sunset to half an hour before sunrise. No alcohol, glass, fires, stoves or audio devices at the falls; stay at least 6 feet from cliff edges. Flash floods can occur in the falls and clove. Terrain from USGS elevation data, stylized; not for navigation.'),
    links={'A': [('Kaaterskill Wild Forest · NYS DEC', 'https://dec.ny.gov/places/kaaterskill-wild-forest'), ('Kaaterskill Falls upper trailhead · Hike the Hudson Valley', 'https://hikethehudsonvalley.com/kaaterskill-falls-ii-upper-trailhead/')],
           'B': [('Kaaterskill Falls Trail · Hiking Project', 'https://www.hikingproject.com/trail/7025604/kaaterskill-falls-trail'), ('Kaaterskill Falls · Wikipedia', 'https://en.wikipedia.org/wiki/Kaaterskill_Falls'), ('Catskill backcountry information · NYS DEC', 'https://dec.ny.gov/things-to-do/hiking/catskill-backcountry-information')],
           'C': [('Escarpment Trail loop · Hiking Project', 'https://www.hikingproject.com/trail/7056777/easy-escarpment-trail-loop'), ('Catskill Escarpment Loop (South) · NY-NJ Trail Conference', 'https://secure.nynjtc.org/hike/print/2218'), ('Kaaterskill Falls & Inspiration Point loop · Take a Hike', 'https://takeahike.us/kaaterskill-falls-inspiration-point-loop-escarpment-trail-catskill-park/')]},
    viewaz={'all': 0.35, 'A': -1.3, 'B': -1.3, 'C': 0.35},
    zoomcap={'A': 4.2, 'B': 3.6, 'C': 2.4},
    stop_photos=PH.get('stop', {}), flower_photos=PH.get('flower', {}), animal_photos=PH.get('animal', {}),
)
json.dump({k: {'mi': R[k]['mi'], 'gain': R[k]['gain'], 'lo': R[k]['lo'], 'hi': R[k]['hi']} for k in R}, open('kaaterskill/stats.json', 'w'))
os.makedirs('/home/claude/site/out/kaaterskill-falls', exist_ok=True)
print(build(cfg, '/home/claude/site/out/kaaterskill-falls/index.html'))
