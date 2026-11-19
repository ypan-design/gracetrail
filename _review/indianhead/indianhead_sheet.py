import sys, os, json
sys.path.insert(0, '/home/claude/parks'); os.chdir('/home/claude/parks')
from indianhead_routes import *
from mk_sheet import build
import numpy as np

p = ih_park()
R = ih_routes(p)
for k in R: print(k, 'falls', p.mile_of(R[k], *RF), 'IH', p.mile_of(R[k], *IH))

# Gill Brook falls: Artists Falls is about 0.35 mile up the Gill Brook Trail and Gill Brook Falls about 0.8 mile (myhikes mileage);
# the stop sits about 0.45 mile up the trail, in the middle of the string of falls.
mGB = p.mile_of(R['C'], *GBJ)[0]
GBF = tuple(p.at_mile(R['C'], mGB + 0.45)[0])
gbs = [p.xy(q) for w in p.W if w['n'] == 'Gill Brook' for q in w['p']]
GBW = min(gbs, key=lambda q: math.dist(q, GBF))
GBW = (round(GBW[0]), round(GBW[1]))
print('gill brook falls', GBF, 'stream point', GBW, round(math.dist(GBW, GBF)))

ST = snap_stops(p, R, {
    'S1': (*PK, 'ABC'), 'S2': (*LR0, 'ABC'), 'S3': (*IHJ, 'ABC'), 'S4': (*DAM, 'AC'), 'S5': (*RF, 'AC'),
    'S6': (*RIDGE, 'BC'), 'S7': (*IH, 'BC'), 'S8': (*GBJ, 'CB'), 'S9': (*GBF, 'CB'),
    'B1': (*FH, 'B'), 'C1': (*NO, 'C'), 'C2': (*GW, 'C'),
})
TILE = (-22000, 6200, -21200, 7000)
GRID = (-22600, 6800, -21800, 7600)
STEP = 150
b64, NX, NN = p.dem_b64(*GRID, STEP=STEP)
gi = p.grid
RIDGE_FT = int(round(float(np.percentile(gi, 75)), -1))
print('grid', NX, NN, NX * NN, gi.min(), gi.max(), 'p75', RIDGE_FT)

S = lambda i: ST[i]
stops = [
 dict(id='S1', trails=['A', 'B', 'C'], x=S('S1')[0], n=S('S1')[1], name='St. Huberts parking area',
      desc='The Adirondack Mountain Reserve hiker lot on Route 73, across the road from the Roaring Brook Falls trailhead for Giant Mountain. From May 1 to October 31 everyone needs a free reservation from hikeamr.org, whether driving, biking, dropped off or walking in; there are 70 a day. Dogs are not allowed anywhere on AMR land.'),
 dict(id='S2', trails=['A', 'B', 'C'], x=S('S2')[0], n=S('S2')[1], name='Gate house and Lake Road',
      desc='Walk up the road past the Ausable Club golf course; at about half a mile turn left between two tennis courts onto Lake Road. Sign the register at the gate house before the wooden gate. The reserve, formed in 1887, is private land; the public may walk its roads and trails under a conservation easement with New York State.'),
 dict(id='S3', trails=['A', 'B', 'C'], x=S('S3')[0], n=S('S3')[1], name='Indian Head Trail junction',
      desc='The foot trail to Indian Head leaves Lake Road at the top of the last hill before Lower Ausable Lake, just over 3 miles past the gate. It starts flat, then climbs steadily into steep ground with a ladder, reaching the ridge in 0.8 mile.'),
 dict(id='S4', trails=['A', 'C'], x=S('S4')[0], n=S('S4')[1], name='Lower Ausable Lake Dam',
      desc='Lake Road ends at the dam at the north end of Lower Ausable Lake, with the cliffs of Indian Head and the Sawteeth rising on either side of the water. Cross the footbridge below the dam and follow the signs for Rainbow Falls.'),
 dict(id='S5', trails=['A', 'C'], x=S('S5')[0], n=S('S5')[1], name='Rainbow Falls',
      desc='Cascade Brook drops about 150 feet off a cliff into a pool at the head of a deep, narrow gorge. The short path up the gorge is steep and slippery in places. The falls are on private reserve land, open to hikers under the easement.'),
 dict(id='S6', trails=['B', 'C'], x=S('S6')[0], n=S('S6')[1], name='Ridge junction',
      desc='Three trails meet on the ridge: the Indian Head Trail from Lake Road, the short walk out to Indian Head, the Fish Hawk Cliffs Trail and the blue-marked Indian Head Crossover Trail down to Gill Brook.'),
 dict(id='S7', trails=['B', 'C'], x=S('S7')[0], n=S('S7')[1], name='Indian Head',
      desc='Open rock ledges at about 2,700 feet, high above Lower Ausable Lake. The view runs straight down the lake between Mount Colvin on the left and the Sawteeth on the right, toward Upper Ausable Lake. The ledges end in sheer cliffs; stay back from the edge.'),
 dict(id='S8', trails=['C', 'B'], x=S('S8')[0], n=S('S8')[1], name='Gill Brook Trail junction',
      desc='The red-marked Gill Brook Trail leaves Lake Road and climbs beside the brook. It runs close to the road, so it is an easy way to add the waterfalls to a walk up or down the valley.'),
 dict(id='S9', trails=['C', 'B'], x=S('S9')[0], n=S('S9')[1], name='Gill Brook falls',
      desc='Gill Brook drops through a string of falls and cascades right beside the trail: Artists Falls, Gorge Falls (about 20 feet), Plunge Falls (about 15 feet), Gill Brook Falls (about 30 feet, best seen from downstream) and Upper Gill Brook Falls. The rocks are slick, and icy in cold weather.'),
 dict(id='B1', trails=['B'], x=S('B1')[0], n=S('B1')[1], name='Fish Hawk Cliffs',
      desc='A second set of ledges at about 2,600 feet, reached by a steep drop from Indian Head and a climb of about a quarter mile. It looks back across at Indian Head and down onto Lower Ausable Lake.'),
 dict(id='C1', trails=['C'], x=S('C1')[0], n=S('C1')[1], name='North Outlook',
      desc='A short spur off the Indian Head Crossover Trail to a ledge looking north over the valley to the mountains beyond.'),
 dict(id='C2', trails=['C'], x=S('C2')[0], n=S('C2')[1], name='Gothic Window',
      desc='A small opening in the trees on the north slope of Indian Head, framing Gothics on a clear day. From here the Indian Head Trail drops steeply back to Lake Road, with a ladder on the way.'),
]
stops, order = renumber(p, R, stops)
print(order, [(s['id'], s['name']) for s in stops])
trails = [
 dict(id='A', name='Rainbow Falls', short='Rainbow Falls', official=8.5, unit='round trip', route='Out and back', time='4–5 hr', level='Moderate', color='--tA',
      desc='Follows the Ausable Club road and then the gravel Lake Road for just over 3 miles to the dam at Lower Ausable Lake; the road climbs steadily. Cross the footbridge below the dam and follow the signs up the Cascade Brook gorge to the foot of Rainbow Falls. Return the same way. About 1,100 feet of climbing, almost all of it on the road.', anchors=p.anchors(R['A'])),
 dict(id='B', name='Indian Head and Fish Hawk Cliffs', short='Indian Head', official=9.4, unit='loop', route='Loop', time='5–6 hr', level='Strenuous', color='--tB',
      desc='Up Lake Road to the Indian Head Trail, a steady then steep climb with a ladder to the ridge. Walk out to the Indian Head ledges over Lower Ausable Lake, drop steeply and climb to Fish Hawk Cliffs, then descend the Gill Brook Trail past its waterfalls to Lake Road. About 1,675 feet of climbing; long for a full day.', anchors=p.anchors(R['B'])),
 dict(id='C', name='Indian Head and Rainbow Falls', short='Indian Head + Rainbow Falls', official=10.1, unit='round trip', route='Lollipop', time='5–6 hr', level='Strenuous', color='--tC',
      desc='Climbs the Gill Brook Trail past its falls, crosses on the blue-marked Indian Head Crossover Trail past the North Outlook to the Indian Head ledges, then drops on the Indian Head Trail past the Gothic Window to Lake Road. Add Rainbow Falls beyond the dam and walk Lake Road back. About 1,800 feet of climbing.', anchors=p.anchors(R['C'])),
]

# --- Lower Ausable Lake (OSM way 139128979)
WAY = lambda i: next(w for w in p.W if str(w['id']) == i)['p']
LAKE = [[round(v) for v in p.xy(q)] for q in WAY('139128979')]
WJ = [{'o': LAKE, 'h': []}]
dam = [[round(v) for v in p.xy(q)] for q in WAY('490141240')]
print('lake pts', len(LAKE), 'dam', dam)
extra_js = '''
TRAILS.forEach(T=>{const g={A:1100,B:1675,C:1796}[T.id];if(g)T.gain=g;});
// out-and-backs and spurs: report the first (outbound) mile for a stop
mileOf=function(T,x,n){let b=null;T.pts.forEach(p=>{const d=Math.hypot(p.x-x,p.n-n);if(!b||d<b.d)b={d,m:p.m,e:p.e};});if(!b||b.d>=260)return null;const f=T.pts.find(p=>Math.hypot(p.x-x,p.n-n)<b.d+60);return {d:b.d,m:f.m,e:f.e};};
(function(){const mat=new THREE.MeshLambertMaterial({color:"#8FC6DA",side:THREE.DoubleSide});const edge=new THREE.LineBasicMaterial({color:"#5E9FB8"});
  waterP().forEach(Q=>{const sh=new THREE.Shape(Q.o.map(([x,n])=>new THREE.Vector2(x,n)));
    Q.h.forEach(H=>{sh.holes.push(new THREE.Path(H.map(([x,n])=>new THREE.Vector2(x,n))));});
    const geo=new THREE.ShapeGeometry(sh);const pa=geo.attributes.position;
    for(let i=0;i<pa.count;i++){const x=pa.getX(i),n=pa.getY(i);const v=G(x,n,0.1);pa.setXYZ(i,v.x,v.y,v.z);}
    pa.needsUpdate=true;geo.computeVertexNormals();const m=new THREE.Mesh(geo,mat);m.renderOrder=1;world.add(m);
    [Q.o].concat(Q.h).forEach(P=>{const ring=P.concat([P[0]]).map(([x,n])=>G(x,n,0.13));world.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints(ring),edge));});});
})();
'''
WATER_FN = ('function waterP(){return waterP.c||(waterP.c=%s);}\n' % js(WJ) +
            'function inLake(x,n){const ins=P=>{let c=false;for(let i=0,j=P.length-1;i<P.length;j=i++){const a=P[i],b=P[j];if((a[1]>n)!==(b[1]>n)&&x<(b[0]-a[0])*(n-a[1])/(b[1]-a[1])+a[0])c=!c;}return c;};'
            'for(const Q of waterP()){if(ins(Q.o)&&!Q.h.some(ins))return true;}return false;}\n')

# --- animals: spread along the three routes (A and C share Lake Road; B and C share Indian Head)
pa = place_along
A_ = lambda k, f, s=1, o=240: pa(p, R[k], [f], s, o)[0]
an = []
an += [f'{{k:"deer",path:{js(A_("A",.12,1,300)+A_("A",.14,1,300))},per:28}}', f'{{k:"deer",path:{js(A_("B",.84,-1,320)+A_("B",.86,-1,320))},per:30,ph:0.4}}']
an += [f'{{k:"bear",path:{js(A_("C",.20,-1,520)+A_("C",.23,-1,520))},per:36}}']
an += [f'{{k:"moose",path:{js(A_("A",.43,-1,520)+A_("A",.45,-1,520))},per:44}}']
an += [f'{{k:"chipmunk",at:{js(A_("A",.17,-1,150))},hop:true}}', f'{{k:"chipmunk",at:{js(A_("C",.42,1,160))},hop:true}}']
an += [f'{{k:"squirrel",at:{js(A_("B",.40,1,170))},hop:true}}', f'{{k:"squirrel",at:{js(A_("C",.30,1,170))},hop:true}}']
an += [f'{{k:"snake",path:{js(A_("A",.22,1,150)+A_("A",.23,1,150))},per:32}}']
an += [f'{{k:"turtle",path:{js(A_("A",.485,1,260)+A_("A",.49,1,260))},per:60}}']
an += [f'{{k:"beaver",path:{js(A_("A",.455,1,330)+A_("A",.46,1,330))},per:40}}']
an += [f'{{k:"otter",path:{js(A_("B",.62,1,260)+A_("B",.64,1,260))},per:30}}']
an += [f'{{k:"turkey",path:{js(A_("B",.93,1,260)+A_("B",.95,1,260))},per:26}}']
an += [f'{{k:"heron",at:{js(A_("A",.40,-1,260))}}}']
animals_js = '[\n ' + ',\n '.join(an) + '\n]'

bn = {s['name']: s for s in stops}
g = lambda nm: (bn[nm]['x'], bn[nm]['n'])
pk, gh, ih, fh, no, gw, rf, ridge = [g(k) for k in ('St. Huberts parking area', 'Gate house and Lake Road', 'Indian Head', 'Fish Hawk Cliffs', 'North Outlook', 'Gothic Window', 'Rainbow Falls', 'Ridge junction')]
lm = f'''  gate({pk[0] - 60},{pk[1] + 40},1.6);
  // gate house at the start of Lake Road (register), with its wooden gate
  {{const q=G({LR0[0] - 90},{LR0[1] + 70});const g=new THREE.Group();g.position.copy(q);g.rotation.y=0.6;g.scale.setScalar(2.2);world.add(g);
   part(g,box,"#7A5A3E",0,0.4,0,1.0,0.8,0.8,1.06);part(g,new THREE.ConeGeometry(0.8,0.5,4),"#4E5A4A",0,1.05,0,1,1,0.85,1.06).rotation.y=Math.PI/4;
   part(g,box,"#E9E1D2",0.52,0.45,0,0.04,0.3,0.4,0);}}
  gate({LR0[0]},{LR0[1]},2.4);
  // Ausable Club clubhouse area and the golf course edge, on the walk in (simple houses)
  [[-1300,250,0.3],[-1700,420,0.5],[-2150,700,0.2]].forEach(([x,n,r],i)=>house(x,n,0.9+(i%2)*0.2,r));
  // Lower Ausable Lake Dam (OSM weir), concrete wall across the outlet
  {{const a=G({dam[0][0]},{dam[0][1]}),b=G({dam[-1][0]},{dam[-1][1]});const L=Math.hypot(b.x-a.x,b.z-a.z)+0.6;
   const g=new THREE.Group();g.position.set((a.x+b.x)/2,Math.max(a.y,b.y)+0.1,(a.z+b.z)/2);g.rotation.y=Math.atan2(-(b.z-a.z),b.x-a.x);g.scale.set(1,1.6,1.6);world.add(g);
   part(g,box,"#B9B4AA",0,0,0,L,0.5,0.45,1.06);part(g,box,"#8C877C",0,0.32,0,L,0.08,0.5,0);
   part(g,box,"#6B4F3A",0,0.15,0.55,L*0.9,0.06,0.3,0);}}
  // Rainbow Falls: Cascade Brook (flowing east) over the OSM cliff line, drawn exaggerated with a rock wall behind
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
  fall({RFC[0]},{RFC[1]},1,0.05,1.4,4.6,1.5);
  // Gill Brook falls (brook flows north toward Lake Road), smaller
  fall({GBW[0]},{GBW[1]},0.25,1,1.0,1.4,1.2);
  // summit ledges with a trail sign: Indian Head faces south-southwest down the lake, Fish Hawk Cliffs faces west-northwest toward Indian Head
  function ledge(x,n,ry,sc){{const q=G(x,n);const g=new THREE.Group();g.position.copy(q);g.rotation.y=ry;g.scale.setScalar(sc);world.add(g);
   part(g,box,PAL.stone,0,0.2,0,2.2,0.4,1.4,1.06);part(g,ico,PAL.rock,-0.8,0.5,-0.4,0.6,0.45,0.55);part(g,ico,"#9A948A",0.7,0.42,-0.45,0.5,0.36,0.5);
   part(g,cyl,"#6B4F3A",0.85,0.75,0.35,0.06,1.1,0.06);part(g,box,"#E9E1D2",0.85,1.25,0.35,0.65,0.3,0.06,1.06);}}
  ledge({ih[0]},{ih[1]},Math.atan2(-0.35,-1),2.4);
  ledge({FH[0]},{FH[1]},Math.atan2(-1,0.3),2.0);
  ledge({NO[0]},{NO[1]},Math.atan2(0.3,1),1.4);
  ledge({GW[0]},{GW[1]},Math.atan2(-1,0.5),1.3);
  // trail sign at the ridge junction
  {{const q=G({ridge[0]},{ridge[1]});part(world,cyl,"#6B4F3A",q.x,q.y+0.9,q.z,0.07,1.8,0.07,0);part(world,box,"#E9E1D2",q.x,q.y+1.6,q.z,0.9,0.28,0.06,1.06);}}
  anim.water={{fallTex,rings,mist}};
'''

creeks = []
for nm, minor in [('East Branch Ausable River', False), ('Gill Brook', True), ('Cascade Brook', True), ('Pyramid Brook', True), ('Wedge Brook', True), ('Crystal Brook', True), ('Putnam Brook', True), ('Beede Brook', True), ('Roaring Brook', True), ('Icy Brook', True), ('Bennies Brook', True), ('Rooster Comb Brook', True), ('Wolfjaw Brook', True)]:
    for i, wid in enumerate([w['id'] for w in p.W if w.get('n') == nm and w['k'] in ('river', 'stream')]):
        c = p.creek([wid], GRID, minor=minor)
        if c: creeks.append(dict(id=f"{nm.split()[0].lower()}{i}", **c))
print('creeks', len(creeks))

species_extra = {
 'painted_ih': 'painted_ih:{name:"Painted trillium",latin:"Trillium undulatum",color:"#F4EEF0",shape:"cup",bloom:[5,6],sum:"Three wavy white petals with a crimson V at the center, in the acid soil under the conifers in late spring. Leave them be: picking the flower can kill the plant.",rule:(d,e,g,s)=>e>1900&&g<0.7}',
 'redtrillium_ih': 'redtrillium_ih:{name:"Red trillium",latin:"Trillium erectum",color:"#8E1F2F",shape:"cup",bloom:[5],sum:"A dark maroon trillium of the rich, moist hardwoods along the brooks in May. Its nickname, stinking Benjamin, comes from the flower’s carrion smell, which draws flies to pollinate it.",rule:(d,e,g,s)=>d<600&&e<2400}',
 'bunch_ih': 'bunch_ih:{name:"Bunchberry",latin:"Cornus canadensis",color:"#F7F5EE",shape:"cup",bloom:[6],sum:"A tiny dogwood only a few inches tall, with four white petal-like bracts over a whorl of leaves in June and a cluster of red berries in late summer. Carpets the forest floor under the spruce and fir.",rule:(d,e,g,s)=>e>1700}',
 'bluebead_ih': 'bluebead_ih:{name:"Bluebead lily",latin:"Clintonia borealis",color:"#E8D35A",shape:"tube",bloom:[6],sum:"Nodding yellow-green bells over two or three glossy leaves in June, followed by porcelain-blue berries in August. Common in the cool conifer woods along the upper trails.",rule:(d,e,g,s)=>e>1800}',
 'hobble_ih': 'hobble_ih:{name:"Hobblebush",latin:"Viburnum lantanoides",color:"#FFFFFF",shape:"dome",bloom:[5,6],sum:"A sprawling shrub with big round leaves and flat white flower clusters in May and June; its arching branches root where they touch the ground and can trip a hiker.",rule:(d,e,g,s)=>d<700}',
 'columbine_ih': 'columbine_ih:{name:"Red columbine",latin:"Aquilegia canadensis",color:"#D2453A",shape:"tube",bloom:[5,6],sum:"Nodding red and yellow flowers with long spurs, rooted in cracks of the rock ledges and cliffs in late spring. A favorite of hummingbirds.",rule:(d,e,g,s)=>g>0.55}',
 'gentian_ih': 'gentian_ih:{name:"Narrowleaf gentian",latin:"Gentiana linearis",color:"#4B4FC7",shape:"tube",bloom:[8,9],sum:"Clusters of deep blue, nearly closed bottle-shaped flowers in late summer, in damp openings and along the brooks.",rule:(d,e,g,s)=>d<400&&e>1500}',
}

# --- photos (Wikimedia Commons via gt6_photos; reused species photos already on the site)
PM = json.load(open('/mnt/files/gtb/photos/indianhead/photos_meta.json'))
def keep(key, files):
    out = []
    for f in files:
        for x in PM.get(key, []):
            if x['f'].endswith('/' + f): out.append(dict(x))
    return out
KEEP = json.load(open('/home/claude/parks/indianhead_keep.json')) if os.path.exists('/home/claude/parks/indianhead_keep.json') else {}
stop_photos = {}
for s in stops:
    L = []
    for key, files in KEEP.get('stops', {}).get(s['name'], []): L += keep(key, files)
    if L: stop_photos[s['id']] = L
flower_photos = {
 'painted_ih': [{"f": "../photos/sp_cascade_paintedtrillium_0.jpg", "by": "The Cosmonaut", "lic": "CC BY-SA 2.5 ca", "src": "https://commons.wikimedia.org/wiki/File:Trillium_undulatum.jpg", "t": "Trillium undulatum"},
                {"f": "../photos/sp_cascade_paintedtrillium_1.jpg", "by": "D. Gordon E. Robertson", "lic": "CC BY-SA 3.0", "src": "https://commons.wikimedia.org/wiki/File:Painted_Trillium.jpg", "t": "Painted Trillium"}],
 'bunch_ih': [{"f": "../photos/sp_ac_bunchberry_1.jpg", "by": "wackybadger", "lic": "BY-SA 2.0", "src": "https://www.flickr.com/photos/8584048@N05/9601730191", "t": "Bunchberry (Cornus canadensis)"},
              {"f": "../photos/sp_ac_bunchberry_2.jpg", "by": "wackybadger", "lic": "BY-SA 2.0", "src": "https://www.flickr.com/photos/8584048@N05/5916758143", "t": "Bunchberry (Cornus canadensis)"}],
 'bluebead_ih': [{"f": "../photos/sp_cascade_bluebead_0.jpg", "by": "Choess", "lic": "CC BY-SA 4.0", "src": "https://commons.wikimedia.org/wiki/File:Clintonia_borealis_maine.JPG", "t": "Clintonia borealis maine"},
                 {"f": "../photos/sp_cascade_bluebead_1.jpg", "by": "Daniel Estabrooks", "lic": "CC0", "src": "https://commons.wikimedia.org/wiki/File:Clintonia_borealis_302538198.jpg", "t": "Clintonia borealis 302538198"}],
 'hobble_ih': [{"f": "../photos/sp_hobblebush_fr_3.jpg", "by": "Nicholas_T", "lic": "BY 2.0", "src": "https://www.flickr.com/photos/14922165@N00/7451992144", "t": "Hobblebush"}],
 'gentian_ih': [{"f": "../photos/sp_cascade_gentian_0.jpg", "by": "peupleloup", "lic": "CC BY-SA 2.0", "src": "https://commons.wikimedia.org/wiki/File:Gentiana_linearis.jpg", "t": "Gentiana linearis"},
                {"f": "../photos/sp_cascade_gentian_3.jpg", "by": "peupleloup", "lic": "CC BY-SA 2.0", "src": "https://commons.wikimedia.org/wiki/File:Gentiana_linearis_(2840338499).jpg", "t": "Gentiana linearis (2840338499)"}],
}
for k, (key, files) in KEEP.get('flowers', {}).items(): flower_photos[k] = keep(key, files)
animal_photos = {
 'deer': [{"f": "../photos/sp_wtdeer_bk_0.jpg", "by": "James St. John", "lic": "BY 2.0", "src": "https://www.flickr.com/photos/47445767@N05/8269171051", "t": "Odocoileus virginianus (white-tailed deer)"}],
 'bear': [{"f": "../photos/sp_l22_blackbear_0.jpg", "by": "US Forest Service", "lic": "Public domain", "src": "https://commons.wikimedia.org/wiki/File:Ursus_americanus_-_Olympic_National_Forest_-_September_2017_01.jpg", "t": "Ursus americanus - Olympic National Forest - September 2017 01"}],
 'chipmunk': [{"f": "../photos/sp_echipmunk_bk_1.jpg", "by": "Gilles Gonthier", "lic": "BY 2.0", "src": "https://www.flickr.com/photos/46788399@N00/403563053", "t": "Tamia rayé -- Eastern chipmunk"}],
 'beaver': [{"f": "../photos/sp_beaver_2.jpg", "by": "GlacierNPS", "lic": "Public domain", "src": "https://commons.wikimedia.org/wiki/File:North_American_beaver_(Castor_canadensis)_(46677957975).jpg", "t": "North American beaver (Castor canadensis) (46677957975)"}],
 'loon': [{"f": "../photos/sp_cascade_loon_1.jpg", "by": "Cephas", "lic": "CC BY-SA 3.0", "src": "https://commons.wikimedia.org/wiki/File:Gavia_immer1_BS.jpg", "t": "Gavia immer1 BS"},
          {"f": "../photos/sp_cascade_loon_0.jpg", "by": "Art Weber/U.S. Fish and Wildlife Service", "lic": "Public domain", "src": "https://commons.wikimedia.org/wiki/File:Common_Loon_head_sideways.jpg", "t": "Common Loon head sideways"}],
 'jay': [{"f": "../photos/sp_gm_bluejay_0.jpg", "by": "Rhododendrites", "lic": "CC BY-SA 4.0", "src": "https://commons.wikimedia.org/wiki/File:Blue_jay_in_PP_(30960).jpg", "t": "Blue jay in PP (30960)"}],
}
for k, (key, files) in KEEP.get('animals', {}).items(): animal_photos[k] = keep(key, files)

from fauna import TREE_RULES
cfg = dict(
    title='Indian Head &amp; Rainbow Falls', aria='Indian Head, Fish Hawk Cliffs and Rainbow Falls on the Adirondack Mountain Reserve, New York', h1='Indian Head &amp; Rainbow Falls',
    canyons=creeks, trails=trails, stops=stops, order=order,
    species=list(species_extra), species_extra=species_extra,
    flora={'A': ['hobble_ih', 'redtrillium_ih', 'gentian_ih', 'bunch_ih'], 'B': ['painted_ih', 'bluebead_ih', 'columbine_ih', 'bunch_ih', 'hobble_ih'], 'C': ['redtrillium_ih', 'gentian_ih', 'painted_ih', 'bluebead_ih', 'columbine_ih']},
    wild=['deer', 'bear', 'moose', 'chipmunk', 'squirrel', 'otter', 'beaver', 'snake', 'turtle', 'turkey', 'heron', 'loon', 'woodpecker', 'jay'],
    wild_sum={
     'deer': ('White-tailed deer', 'The deer most often seen on these trails, browsing along Lake Road and in the hardwoods of the valley early and late in the day.'),
     'bear': ('Black bear', 'Black bears live throughout the High Peaks. Keep food packed away, never feed them, and give any bear plenty of room; overnight campers in the Eastern High Peaks must carry a bear-resistant canister.'),
     'moose': ('Moose', 'Rare here: moose vanished from the Adirondacks in the 1800s and have only returned over the last few decades, with the state estimating more than 500 in the Adirondack Park. One was photographed on the shore of Upper Ausable Lake, just south of here. Watch the lake shores and wet meadows, and keep your distance.'),
     'chipmunk': ('Eastern chipmunk', 'A small striped ground squirrel that darts across Lake Road and over the rocks beside the trails.'),
     'squirrel': ('American red squirrel', 'A small, rusty squirrel of the spruce and fir that chatters loudly at hikers from the branches on the upper trails.'),
     'otter': ('American marten', 'A cat-sized, tree-climbing member of the weasel family with a bushy tail and a buff throat, living in the mature conifer forest. Seen now and then on these trails, more often in winter tracks.'),
     'beaver': ('American beaver', 'Beavers work the north end of Lower Ausable Lake near the dam; look for chewed stumps along the shore and the river below.'),
     'snake': ('Common garter snake', 'A small, harmless striped snake that suns on warm rocks and the edges of Lake Road in summer.'),
     'turtle': ('Common snapping turtle', 'A big, heavy-shelled turtle of the lake and the slow water near the dam. Do not handle it: it bites hard.'),
     'turkey': ('Wild turkey', 'Flocks forage in the open woods and along the road edges low in the valley, near the Ausable Club.'),
     'heron': ('Great blue heron', 'A tall gray heron that stalks the shallows of the river and the north end of Lower Ausable Lake for fish and frogs.'),
     'loon': ('Common loon', 'Rare here: the common loon is a Species of Special Concern in New York. Loons fish Lower Ausable Lake in summer; listen for their wailing calls from the dam and the Indian Head ledges.'),
     'woodpecker': ('Pileated woodpecker', 'A crow-sized woodpecker with a red crest. Listen for its loud drumming and look for big rectangular holes in dead trees.'),
     'jay': ('Blue jay', 'A loud, crested blue-and-white jay of the hardwood forest, often the first bird you hear on Lake Road.'),
    },
    grid=GRID, step=STEP, dem_b64=b64, tile=TILE, ve=1.8, ridge_ft=RIDGE_FT,
    palette='east', tree_rule='if(inLake(x,n)){type=null;}else ' + TREE_RULES['east'],
    landmarks=lm, animals_js=animals_js, extra_js=extra_js,
    stop_photos=stop_photos, flower_photos=flower_photos, animal_photos=animal_photos,
    overview=dict(h2='Lower Ausable Lake from Indian Head',
                  p='Indian Head is a rock knob on the Colvin Range, high above Lower Ausable Lake in the Adirondack High Peaks. All three hikes start from the St. Huberts parking area and walk the Adirondack Mountain Reserve’s Lake Road, a private gravel road open to hikers, up the valley of the East Branch of the Ausable River. A goes to Rainbow Falls beyond the dam, B climbs to Indian Head and Fish Hawk Cliffs and comes down past the Gill Brook falls, and C climbs Gill Brook to Indian Head, then adds Rainbow Falls. Pick a trail to focus the model; click anything on it for a quick note.',
                  numbers='Plain numbers mark spots more than one trail passes: the parking area, Lake Road, the dam, Rainbow Falls and Indian Head. Lettered stops belong to one trail: C2 is the second stop on Trail C.',
                  wild_h='Wildlife around the Ausable Lakes',
                  note='Adirondack Mountain Reserve (AMR), St. Huberts parking area, Route 73, Keene Valley, New York. Status (November 2026): open. From May 1 to October 31 a free parking reservation from hikeamr.org is required for everyone, including walkers, cyclists and drop-offs (70 a day); walk-ins without one are turned away. The reserve is private land open to hikers under a state conservation easement: stay on the roads and marked trails; no dogs. In winter bring microspikes or snowshoes; the Gill Brook Trail and the ladder ice up. Terrain from USGS elevation data, stylized; not for navigation.'),
    links={'A': [('Rainbow Falls · Lake Placid ADK', 'https://www.lakeplacid.com/hiking/rainbow-falls'), ('Rainbow Falls · Northern New York Waterfalls', 'https://nnywaterfalls.com/cascadebrook/rainbowfalls/'), ('AMR parking reservations · NYS DEC', 'https://dec.ny.gov/news/press-releases/2025/4/dec-and-adirondack-mountain-reserve-announce-start-of-2025-parking-reservation-system')],
           'B': [('Indian Head and Fish Hawk Cliffs · Lake Placid ADK', 'https://www.lakeplacid.com/hiking/indian-head-and-fish-hawk-cliffs'), ('Visiting the Adirondack Mountain Reserve · ADK', 'https://adk.org/?p=8255'), ('Hiker parking reservations · AMR', 'https://www.hikeamr.org/')],
           'C': [('Indian Head & Rainbow Falls · myHikes', 'https://myhikes.org/trails/indian-head-and-rainbow-falls'), ('AMR waterfalls · Northern New York Waterfalls', 'https://nnywaterfalls.com/ausableriver/amr'), ('AMR Waterfall Loop · Lake Placid ADK', 'https://www.lakeplacid.com/hiking/adirondack-mountain-reserve-amr-waterfall-loop')]},
    viewaz={'all': 5.3, 'A': 5.3, 'B': 5.3, 'C': 5.3},
    zoomcap={'A': 2.4, 'B': 3.0, 'C': 2.6},
)
OUT = '/home/claude/site/out/adirondack-indian-head/index.html'
json.dump({k: {'mi': R[k]['mi'], 'gain': R[k]['gain'], 'lo': R[k]['lo'], 'hi': R[k]['hi']} for k in R}, open('indianhead/stats.json', 'w'))
os.makedirs(os.path.dirname(OUT), exist_ok=True)
print(build(cfg, OUT))
# post-process my own page: water functions, blue terrain under the lake, no flowers in the water
h = open(OUT).read()
n0 = len(h)
h = h.replace('/* ================= landmarks + waterfall ================= */', WATER_FN + '/* ================= landmarks + waterfall ================= */', 1)
h = h.replace('if(mk<0.02)c=col(PAL.ground);else if(cd<140)c=col(PAL.riparian);', 'if(mk<0.02)c=col(PAL.ground);else if(inLake(mx,mn))c=col("#8FC6DA");else if(cd<140)c=col(PAL.riparian);', 1)
h = h.replace('if(!sp.rule(creekDist(x,n),e,g,s))continue;', 'if(inLake(x,n)||!sp.rule(creekDist(x,n),e,g,s))continue;')
print('post', len(h) - n0, h.count('function inLake'), h.count('inLake(mx,mn)'), h.count('inLake(x,n)||!sp.rule'))
open(OUT, 'w').write(h)
