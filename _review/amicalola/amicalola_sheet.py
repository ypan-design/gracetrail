from lib import *
from mk_sheet import build
import sys, json, os
import numpy as np

os.chdir('/home/claude/parks')
p = Park('amicalola', 34.5673, -84.2441)   # origin = Amicalola Falls (OSM waterway=waterfall node 346428568, top of the falls)
WR = (-1396, -719)    # West Ridge Falls Access trailhead (OSM way 259931802 start, by the park road)
BRG = (-300, -178)    # footbridge across the falls (OSM footway 317132223 between the two staircases)
VC = (-1498, -3514)   # stone arch at the Visitor Center, start of the Approach Trail (OSM)
POOL = (-760, -1286)  # Reflection Pool (OSM natural=water 259931806)
BASE = (-397, -657)   # foot of the lower staircase (OSM steps 317132222)
TOP = (-62, 63)       # top-of-the-falls overlook (OSM viewpoint)
LOT = (165, -48)
ER = (139, -168)      # upper end of the East Ridge Trail by the top-of-falls parking (OSM)
LFJ = (733, 823)      # Len Foote Hike Inn Trail leaves the Approach Trail (OSM way 31275631 start)
BENCH = (3247, 1374)  # OSM bench + viewpoint on the Hike Inn Trail
VIEW = (9133, 6813)   # OSM viewpoint on the Hike Inn Trail
INN = (10664, 9206)   # Hike Inn Trail at the inn
INNB = (10797, 9053)  # Len Foote Hike Inn building (OSM way 259931789, Nominatim centre)
LODGE = (413, -708)   # Amicalola Falls Lodge (OSM way 259931787)
R = {}
R['A'] = route_xy(p, WR, (-396, -178), (-217, -179))
R['B'] = route_xy(p, VC, (-1089, -2564), POOL, BASE, (-192, -213), (-396, -178), TOP, LOT, ER, (84, -802), (-36, -2194), (-1045, -3573), (-1559, -3481))
R['C'] = route_xy(p, TOP, LOT, (348, 463), LFJ, (3237, 1503), (5114, 7387), (7666, 7193), (9833, 8060), INN)
for k in R: Park.smooth_E(R[k], 9); p.describe(R[k], k)
ST = snap_stops(p, R, {
    'S1': (BRG[0], BRG[1], 'AB'), 'S2': (TOP[0], TOP[1], 'BC'),
    'A1': (WR[0], WR[1], 'A'),
    'B1': (VC[0], VC[1], 'B'), 'B2': (POOL[0], POOL[1], 'B'), 'B3': (BASE[0], BASE[1], 'B'), 'B4': (120, -1150, 'B'),
    'C1': (LFJ[0], LFJ[1], 'C'), 'C2': (BENCH[0], BENCH[1], 'C'), 'C3': (VIEW[0], VIEW[1], 'C'), 'C4': (INN[0], INN[1], 'C'),
})
TILE = (-6650, 15750, -8450, 13950)
GRID = (-7000, 16100, -8800, 14300)
if 'plot' in sys.argv:
    from plot import plot
    plot(p, TILE, 'amicalola/routes.png', routes=R, stops=ST, title='amicalola', grid=1000)
    plot(p, (-2000, 900, -3800, 700), 'amicalola/routesAB.png', routes=R, stops=ST, title='A B', grid=250)
    sys.exit()

STEP = 110
b64, NX, NN = p.dem_b64(*GRID, STEP=STEP)
RIDGE = int(round(float(np.percentile(p.grid, 75)), -1))
print('grid', NX, NN, NX * NN, p.grid.min(), p.grid.max(), 'p75', RIDGE)

def way_pts(wid):
    w = p.WID.get(wid)
    return [[round(a), round(b)] for a, b in (p.xy(q) for q in w['p'])] if w else []
FALL = [q for q in way_pts('31213081') if q[1] > -700]
UPST = way_pts('259931804'); LOST = way_pts('317132222')
POOLP = way_pts('259931806')
print('fall pts', len(FALL), 'stairs', len(UPST), len(LOST), 'pool', len(POOLP))

S = lambda i: ST[i]
stops = [
 dict(id='S1', trails=['A', 'B'], x=S('S1')[0], n=S('S1')[1], name='Bridge across the falls', desc='A footbridge spans the middle of the falls, the closest view of the cascade. The level West Ridge Falls Access Trail ends here; from the bridge, stairs climb to the top of the falls and drop toward the base. Stay on the trails and stairs: leaving them in the waterfall corridor is prohibited.'),
 dict(id='S2', trails=['B', 'C'], x=S('S2')[0], n=S('S2')[1], name='Top of the falls', desc='An overlook where Little Amicalola Creek goes over the edge, with a view down the falls and out over the valley. Parking is close by. The blue-blazed Approach Trail continues north from here toward Springer Mountain.'),
 dict(id='A1', trails=['A'], x=S('A1')[0], n=S('A1')[1], name='West Ridge Falls Access trailhead', desc='Parking off the park road on the west ridge. The 0.3-mile trail has a recycled-tire surface and is wheelchair accessible, the easiest way to a close view of the falls.'),
 dict(id='B1', trails=['B'], x=S('B1')[0], n=S('B1')[1], name='Visitor Center and stone arch', desc='The Approach Trail to the Appalachian Trail starts at a stone archway by the Visitor Center. Thru-hikers register here before heading for Springer Mountain, about 8.5 miles away.'),
 dict(id='B2', trails=['B'], x=S('B2')[0], n=S('B2')[1], name='Reflection Pool', desc='A small pool on Little Amicalola Creek below the falls, with a parking area and picnic tables. Past the pool, a steep paved path climbs toward the base of the falls.'),
 dict(id='B3', trails=['B'], x=S('B3')[0], n=S('B3')[1], name='Foot of the stairs', desc='The staircase starts here: about 175 steps to the bridge at mid-falls, then about 425 more to the top, some 600 in all. Expect spray on the bridge after rain.'),
 dict(id='B4', trails=['B'], x=S('B4')[0], n=S('B4')[1], name='East Ridge Trail', desc='The return leg follows part of an old roadbed, once the approach to the Appalachian Trail, down from the top of the falls to the Visitor Center. Rocky and loose in places. The park announced erosion repairs for this trail in 2025.'),
 dict(id='C1', trails=['C'], x=S('C1')[0], n=S('C1')[1], name='Hike Inn Trail junction', desc='The lime-green-blazed Len Foote Hike Inn Trail (Forest Service Trail 174) leaves the blue-blazed Approach Trail and heads northeast into the Chattahoochee National Forest.'),
 dict(id='C2', trails=['C'], x=S('C2')[0], n=S('C2')[1], name='Bench overlook', desc='A bench at a small opening in the forest, a good first rest on the way to the inn.'),
 dict(id='C3', trails=['C'], x=S('C3')[0], n=S('C3')[1], name='Ridge overlook', desc='A viewpoint on the last ridges before the inn, where the trail winds above the headwaters of Cochrans Creek.'),
 dict(id='C4', trails=['C'], x=S('C4')[0], n=S('C4')[1], name='Len Foote Hike Inn', desc='A backcountry lodge reachable only on foot, opened in November 1998 at about 3,100 feet. It has 20 guest rooms, family-style meals, solar hot water and composting toilets; overnight stays need a reservation. Its granite Star Base, designed by Fernbank Science Center, lines up with the sunrise at the spring and fall equinoxes.'),
]
stops, order = renumber(p, R, stops)
print(order, [(s['id'], s['name']) for s in stops])
trails = [
 dict(id='A', name='West Ridge Falls Access Trail', short='West Ridge', official=0.6, unit='round trip', route='Out and back', time='20–30 min', level='Easy', color='--tA',
      desc='The easy way to the falls: a nearly level, wheelchair-accessible path with a recycled-tire surface, 0.3 mile each way from the West Ridge parking area to the bridge across the middle of the falls.', anchors=p.anchors(R['A'])),
 dict(id='B', name='Amicalola Falls Loop', short='Falls Loop', official=2.0, unit='loop', route='Loop', time='1–2 hr', level='Moderate', color='--tB',
      desc='From the stone arch at the Visitor Center, the blue-blazed Approach Trail follows the creek to the Reflection Pool and the base of the falls, then climbs about 600 steps past the bridge to the top. The loop returns down the rocky East Ridge Trail. About 750 feet of climbing, most of it on the stairs.', anchors=p.anchors(R['B'])),
 dict(id='C', name='Len Foote Hike Inn Trail', short='Hike Inn', official=10.0, unit='round trip', route='Out and back', time='5–6 hr', level='Moderate', color='--tC',
      desc='From the top of the falls, the Approach Trail climbs past the lodge road to the lime-green-blazed Hike Inn Trail, which winds about 5 miles through hardwood forest along the ridges to the Len Foote Hike Inn. Return the same way, or continue 1 mile past the inn to the Approach Trail and loop back (longer and hillier).', anchors=p.anchors(R['C'])),
]

pa = place_along
A_ = lambda k, f, s=1, o=240: pa(p, R[k], [f], s, o)[0]
an = []
an += [f'{{k:"bear",path:{js(A_("C",.18,-1,600)+A_("C",.21,-1,600))},per:36}}', f'{{k:"bear",path:{js(A_("C",.72,1,600)+A_("C",.75,1,600))},per:38,ph:0.5}}']
an += [f'{{k:"deer",path:{js(A_("C",.34,1,450)+A_("C",.37,1,450))},per:28}}', f'{{k:"deer",path:{js(A_("C",.55,-1,420)+A_("C",.57,-1,420))},per:26,ph:0.4}}']
an += [f'{{k:"bobcat",path:{js(A_("C",.30,1,420)+A_("C",.32,1,420))},per:30}}']
an += [f'{{k:"coyote",path:{js(A_("C",.60,1,500)+A_("C",.63,1,500))},per:30,ph:0.3}}']
an += [f'{{k:"fox",path:{js(A_("B",.08,-1,260)+A_("B",.10,-1,260))},per:26,ph:0.6}}']
an += [f'{{k:"raccoon",path:{js(A_("B",.70,1,260)+A_("B",.72,1,260))},per:24}}']
an += [f'{{k:"marmot",at:{js([LODGE[0] + 260, LODGE[1] - 420])}}}']
an += [f'{{k:"squirrel",at:{js(A_("A",.30,-1,220))},hop:true}}', f'{{k:"squirrel",at:{js(A_("C",.80,1,300))},hop:true}}']
an += [f'{{k:"chipmunk",at:{js(A_("B",.62,1,180))},hop:true}}', f'{{k:"chipmunk",at:{js(A_("C",.40,-1,260))},hop:true}}']
an += [f'{{k:"snake",path:{js(A_("B",.22,1,200)+A_("B",.24,1,200))},per:30}}']
an += [f'{{k:"turtle",at:{js(A_("B",.83,-1,220))}}}']
an += [f'{{k:"heron",at:{js([POOL[0] - 60, POOL[1] - 110])}}}']
an += [f'{{k:"otter",path:{js([-1265, -2315] + [-1434, -2511])},per:22}}']
animals_js = '[\n ' + ',\n '.join(an) + '\n]'

lm = f'''  gate({S('A1')[0]},{S('A1')[1]},1.0);
  // ---- Amicalola Falls: water ribbon down the OSM falls centreline (way 31213081), exaggerated in width, with volume
  const fallTex=stripeTex("#9AD4EA","#FFFFFF",64,128,40,9,18);fallTex.repeat.set(1,3);
  const fallMat=new THREE.MeshBasicMaterial({{map:fallTex}});
  const rings=[],mist=[];
  const FALL={js(FALL)};
  for(let i=0;i<FALL.length-1;i++){{const a=G(FALL[i][0],FALL[i][1],0.32),b=G(FALL[i+1][0],FALL[i+1][1],0.32);
    const L=a.distanceTo(b);const m=new THREE.Mesh(new THREE.BoxGeometry(1.0,0.34,L+0.16),fallMat);
    m.position.copy(a).add(b).multiplyScalar(0.5);m.lookAt(b);world.add(m);
    const sd=new THREE.Vector3().subVectors(b,a).normalize();const px=new THREE.Vector3(-sd.z,0,sd.x).normalize();
    if(i%2==0)[1,-1].forEach(s=>{{part(world,ico,s>0?"#6E685F":"#837D72",m.position.x+px.x*0.68*s,m.position.y,m.position.z+px.z*0.68*s,0.26,0.34,0.26);}});
    const fm=part(world,box,"#FFFFFF",a.x,a.y+0.19,a.z,1.1,0.08,0.18,0);fm.lookAt(b.x,a.y+0.19,b.z);
  }}
  // two steep tiers drawn as near-vertical sheets of water with a rock face behind (top of the falls and the drop below the bridge)
  function tier(x,n,dx,dn,w,h){{const F=G(x,n,0.1);const g=new THREE.Group();g.position.copy(F);g.rotation.y=Math.atan2(dx,-dn);world.add(g);
    const wt=new THREE.Mesh(new THREE.BoxGeometry(w,h,0.2),fallMat);wt.position.set(0,h/2-0.2,0.05);g.add(wt);
    part(g,box,"#5E5A54",0,h/2-0.3,-0.32,w+0.4,h,0.4,1.04);[1,-1].forEach(s=>part(g,ico,"#77726A",s*(w/2+0.25),h*0.35,-0.1,0.35,h*0.4,0.35));}}
  tier(FALL[0][0],FALL[0][1],FALL[1][0]-FALL[0][0],FALL[1][1]-FALL[0][1],1.0,1.6);
  tier(FALL[3][0],FALL[3][1],FALL[4][0]-FALL[3][0],FALL[4][1]-FALL[3][1],1.0,1.3);
  {{const q=G(FALL[FALL.length-1][0],FALL[FALL.length-1][1],0.05);
    const pool=new THREE.Mesh(new THREE.CylinderGeometry(0.75,0.75,0.12,18),new THREE.MeshBasicMaterial({{color:"#9CD3E0"}}));pool.position.copy(q);world.add(pool);
    const wf=new THREE.Group();wf.position.copy(q);world.add(wf);
    for(let i=0;i<2;i++){{const rg=new THREE.Mesh(new THREE.RingGeometry(0.4,0.5,24),new THREE.MeshBasicMaterial({{color:"#FFFFFF",transparent:true,side:THREE.DoubleSide}}));rg.rotation.x=-Math.PI/2;rg.position.set(0,0.14,0);wf.add(rg);rings.push(rg);}}
    for(let i=0;i<4;i++){{const m=new THREE.Mesh(new THREE.SphereGeometry(0.14,8,6),new THREE.MeshBasicMaterial({{color:"#FFFFFF",transparent:true}}));wf.add(m);mist.push({{m,ph:i/4,x:(i%3-1)*0.3}});}}}}
  // ---- footbridge across the middle of the falls (OSM footway 317132223, west to east), drawn longer than real
  {{const a=G(-420,-178,0.55),b=G(-130,-182,0.55);const g=new THREE.Group();g.position.copy(a).add(b).multiplyScalar(0.5);g.lookAt(b);world.add(g);
    const L=a.distanceTo(b)*1.15;part(g,box,"#8A6A4C",0,0,0,0.42,0.08,L,1.06);
    [1,-1].forEach(s=>{{part(g,box,"#5C4636",0.2*s,0.24,0,0.04,0.04,L,0);for(let k=-3;k<=3;k++)part(g,box,"#5C4636",0.2*s,0.12,k*L/7,0.04,0.24,0.04,0);}});
    [[-1,1],[1,1],[-1,-1],[1,-1]].forEach(([s,t])=>part(g,cyl,"#6B4F3A",0.16*s,-0.45,t*L*0.42,0.05,0.9,0.05,0));}}
  // ---- the staircases (OSM steps 259931804 upper, 317132222 lower): wooden treads, exaggerated
  function stairs(P){{for(let i=0;i<P.length-1;i++){{const a=G(P[i][0],P[i][1],0.12),b=G(P[i+1][0],P[i+1][1],0.12);const d=a.distanceTo(b);const n=Math.max(1,Math.round(d/0.12));
    for(let k=0;k<n;k++){{const t=(k+0.5)/n;const q=a.clone().lerp(b,t);const s=part(world,box,"#7A5535",q.x,q.y,q.z,0.46,0.09,0.1,0);s.lookAt(b.x,q.y,b.z);}}}}}}
  stairs({js(UPST)});stairs({js(LOST)});
  // ---- Reflection Pool (OSM outline)
  {{const P={js(POOLP)};const sh=new THREE.Shape();P.forEach((q,i)=>{{const v=G(q[0],q[1]);i?sh.lineTo(v.x,-v.z):sh.moveTo(v.x,-v.z);}});
    const y=Math.min(...P.map(q=>G(q[0],q[1]).y))+0.06;const m=new THREE.Mesh(new THREE.ShapeGeometry(sh),new THREE.MeshBasicMaterial({{color:"#8CC8DA"}}));m.rotation.x=-Math.PI/2;m.position.y=y;world.add(m);
    const ed=new THREE.Mesh(new THREE.ExtrudeGeometry(sh,{{depth:0.1,bevelEnabled:false}}),new THREE.MeshBasicMaterial({{color:"#7FB9CB"}}));ed.rotation.x=-Math.PI/2;ed.position.y=y-0.1;world.add(ed);}}
  // ---- stone arch at the Visitor Center (start of the Approach Trail), the trail passing through it to the north-east; exaggerated
  {{const q=G({VC[0]},{VC[1]});const g=new THREE.Group();g.position.copy(q);g.rotation.y=Math.atan2(0.68,-0.73)+Math.PI/2;g.scale.setScalar(1.3);world.add(g);
    [1,-1].forEach(s=>{{part(g,box,"#9A9184",0.55*s,0.5,0,0.32,1.0,0.36,1.06);part(g,box,"#B3AA9C",0.55*s,1.05,0,0.4,0.1,0.44,1.06);}});
    const ar=new THREE.Mesh(new THREE.TorusGeometry(0.55,0.16,8,16,Math.PI),new THREE.MeshLambertMaterial({{color:"#A39A8C"}}));ar.position.set(0,1.05,0);g.add(ar);
    part(g,box,"#2F6FB5",0,1.45,0.2,0.32,0.18,0.03,0);}}
  // ---- Amicalola Falls Lodge on the ridge (OSM), and the Len Foote Hike Inn (OSM) with its Star Base
  house({LODGE[0]},{LODGE[1]},0.75,0.6);house({LODGE[0] + 170},{LODGE[1] + 110},0.55,0.6);
  house({INNB[0]},{INNB[1]},0.6,0.3);house({INNB[0] + 150},{INNB[1] + 40},0.45,0.3);house({INNB[0] + 50},{INNB[1] - 150},0.45,1.2);
  {{const q=G({INNB[0] - 230},{INNB[1] - 120});const g=new THREE.Group();g.position.copy(q);g.scale.setScalar(1.1);world.add(g);
    part(g,cyl,"#BDB6AA",0,0.06,0,0.9,0.12,0.9,1.04);for(let k=0;k<8;k++){{const a=k*Math.PI/4;part(g,box,"#8E877B",Math.cos(a)*0.75,0.35,Math.sin(a)*0.75,0.18,0.6,0.12,1.06).rotation.y=-a;}}
    part(g,box,"#7A746A",0,0.5,0,0.2,0.9,0.2,1.06);}}
  // ---- lime-green blaze post where the Hike Inn Trail leaves the Approach Trail
  {{const q=G({S('C1')[0] + 40},{S('C1')[1] - 30});const g=new THREE.Group();g.position.copy(q);g.scale.setScalar(1.8);world.add(g);
    part(g,cyl,"#6B4F3A",0,0.7,0,0.06,1.4,0.06,0);part(g,box,"#E9E1D2",0,1.25,0,0.7,0.3,0.05,1.06);part(g,box,"#8DC63F",0,1.25,0.04,0.14,0.22,0.02,0);}}
  bench({S('C2')[0] + 60},{S('C2')[1] - 40},0.4);
  anim.water={{fallTex,rings,mist}};
'''

creeks = []
CK = ['31213081', '1315738792', '1315735402', '1315735403', '1315735404', '1315735405', '109334956']
for i, wid in enumerate(CK):
    c = p.creek([wid], GRID, minor=True)
    if c: creeks.append(dict(id=f"fall{i}", **c))
for nm in ['Little Amicalola Creek', 'Cochrans Creek', 'Anderson Creek', 'Nimblewill Creek', 'Bucktown Creek', 'Amicalola Creek']:
    for i, wid in enumerate([w['id'] for w in p.W if w.get('n') == nm and (w.get('tags') or {}).get('waterway')]):
        c = p.creek([wid], GRID, minor=nm != 'Amicalola Creek')
        if c: creeks.append(dict(id=f"{nm.split()[0].lower()}{i}", **c))
print('creeks', len(creeks))

species_extra = {
 'laurel_am': 'laurel_am:{name:"Mountain laurel",latin:"Kalmia latifolia",color:"#F4C6D4",shape:"dome",bloom:[5,6],sum:"An evergreen shrub of the dry ridges and slopes around the falls, covered in clusters of white-to-pink cup-shaped flowers in late spring.",rule:(d,e,g,s)=>d>150&&e>2200}',
 'rhodo_am': 'rhodo_am:{name:"Great rhododendron",latin:"Rhododendron maximum",color:"#F6E1EA",shape:"dome",bloom:[6,7],sum:"Tall evergreen thickets along Little Amicalola Creek and the stairs, with big pale-pink to white flower clusters in early summer.",rule:(d,e,g,s)=>d<450}',
 'flame_am': 'flame_am:{name:"Flame azalea",latin:"Rhododendron calendulaceum",color:"#F28C28",shape:"dome",bloom:[4,5],sum:"A native deciduous azalea with vivid orange to yellow flowers in spring, scattered along the forested ridges.",rule:(d,e,g,s)=>d>250&&e>2500}',
 'betsy_am': 'betsy_am:{name:"Little sweet Betsy",latin:"Trillium cuneatum",color:"#7A2638",shape:"cup",bloom:[3,4],sum:"A trillium with three maroon petals held upright over mottled leaves, common in the rich, shady coves in early spring.",rule:(d,e,g,s)=>d<600&&g<0.6}',
 'bloodroot_am': 'bloodroot_am:{name:"Bloodroot",latin:"Sanguinaria canadensis",color:"#F7F5EE",shape:"cup",bloom:[3],sum:"One of the first spring wildflowers: a single white flower that opens on sunny March days, wrapped in one lobed leaf. The root bleeds red sap.",rule:(d,e,g,s)=>d<500&&s<0.35}',
 'cardinal_am': 'cardinal_am:{name:"Cardinal flower",latin:"Lobelia cardinalis",color:"#C8102E",shape:"spike",bloom:[7,8,9],sum:"Spikes of brilliant red flowers on wet creek banks in late summer, visited by hummingbirds.",rule:(d,e,g,s)=>d<180}',
 'jewel_am': 'jewel_am:{name:"Jewelweed",latin:"Impatiens capensis",color:"#F08A24",shape:"tube",bloom:[7,8,9],sum:"Orange spotted flowers dangling over damp ground by the creek in summer; ripe seed pods burst when touched.",rule:(d,e,g,s)=>d<220&&e<2400}',
}

PH = json.load(open('amicalola/ph_meta.json'))
RU = json.load(open('amicalola/reuse.json'))
def pick(key, files):
    return [m for f in files for m in PH.get(key, []) if m['f'].endswith('_' + f)]
stop_photos = {
  '1': pick('BRG', ['brg_0.jpg', 'brg_1.jpg']) + pick('STAIRS', ['stairs_0.jpg']),
  '2': pick('BRG', ['brg_3.jpg']) + pick('STAIRS', ['stairs_1.jpg']),
  'B3': pick('TOP', ['top_1.jpg']) + pick('STAIRS', ['stairs_2.jpg']) + pick('BRG', ['brg_2.jpg']),
  'C4': pick('INN', ['inn_0.jpg', 'inn_4.jpg', 'inn_1.jpg']),
}
flower_photos = {'laurel_am': [RU['sp_hk_mtlaurel']], 'rhodo_am': [RU['sp_rhodomax_tm'], RU['sp_sm_rosebay']], 'flame_am': [RU['sp_cd_flame']],
                 'bloodroot_am': [RU['sp_wg_bloodroot']], 'cardinal_am': [RU['sp_hk_cardflower']], 'jewel_am': [RU['sp_wg_jewelweed']],
                 'betsy_am': pick('sp:amic_sweetbetsy', ['sweetbetsy_1.jpg', 'sweetbetsy_2.jpg', 'sweetbetsy_3.jpg'])}
animal_photos = {'bear': [RU['sp_sm_bear']], 'deer': [RU['sp_wg_deer']], 'bobcat': [RU['sp_bobcat']], 'coyote': [RU['sp_coyote']],
                 'raccoon': [RU['sp_raccoon']], 'otter': [RU['sp_riverotter']], 'squirrel': [RU['sp_hk_graysquirrel']], 'chipmunk': [RU['sp_hk_echipmunk']],
                 'turtle': [RU['sp_smboxturtle']], 'heron': [RU['sp_gbheron_dl']], 'woodpecker': [RU['sp_hk_pileated']], 'hawk': [RU['sp_gm_bwhawk']],
                 'vulture': [RU['sp_tvulture']], 'snake': pick('sp:amic_copperhead', ['copperhead_2.jpg', 'copperhead_3.jpg']),
                 'marmot': pick('sp:amic_groundhog', ['groundhog_2.jpg', 'groundhog_1.jpg'])}
print('photos', {k: len(v) for k, v in stop_photos.items()}, {k: len(v) for k, v in flower_photos.items()}, {k: len(v) for k, v in animal_photos.items()})

# gain shown on the page: A is ~60 ft each way (Hiking Project); B is the loop's DEM gain (~750 ft, matches Hike the South);
# C is out and back, so climbing = gain going out + gain coming back (= loss going out).
EC = R['C'].get('E') or []
lossC = R['C']['gain'] - ((EC[-1] - EC[0]) if EC else 0)
gA, gB, gC = 60, int(round(R['B']['gain'], -1)), int(round(R['C']['gain'] + lossC, -1))
print('gains', gA, gB, gC)
CLR = FALL + [[-420, -178], [-130, -182]]
CLEAR = """(function(){const P=%s,m4=new THREE.Matrix4(),pv=new THREE.Vector3(),q=new THREE.Quaternion(),sc=new THREE.Vector3();
  const dseg=(x,n,a,b)=>{const vx=b[0]-a[0],vn=b[1]-a[1],L=vx*vx+vn*vn||1;let t=((x-a[0])*vx+(n-a[1])*vn)/L;t=Math.max(0,Math.min(1,t));return Math.hypot(x-a[0]-t*vx,n-a[1]-t*vn);};
  treeGroup.children.forEach(m=>{if(!m.isInstancedMesh)return;for(let i=0;i<m.count;i++){m.getMatrixAt(i,m4);m4.decompose(pv,q,sc);
    const x=pv.x/S+cx,n=-pv.z/S+cn;let d=1e9;for(let k=0;k<P.length-1;k++){if(k===%d)continue;d=Math.min(d,dseg(x,n,P[k],P[k+1]));}
    if(d<170){sc.setScalar(0);m4.compose(pv,q,sc);m.setMatrixAt(i,m4);}}m.instanceMatrix.needsUpdate=true;});})();""" % (js(CLR), len(FALL) - 1)
cfg = dict(
    title='Amicalola Falls', aria='Amicalola Falls and the Len Foote Hike Inn Trail in Amicalola Falls State Park, Georgia', h1='Amicalola Falls',
    canyons=creeks, trails=trails, stops=stops, order=order,
    species=list(species_extra), species_extra=species_extra,
    flora={'A': ['laurel_am', 'rhodo_am', 'betsy_am'], 'B': ['rhodo_am', 'cardinal_am', 'jewel_am', 'bloodroot_am', 'betsy_am'], 'C': ['laurel_am', 'flame_am', 'betsy_am', 'bloodroot_am']},
    wild=['bear', 'deer', 'bobcat', 'coyote', 'fox', 'raccoon', 'otter', 'marmot', 'squirrel', 'chipmunk', 'snake', 'turtle', 'heron', 'woodpecker', 'hawk', 'vulture'],
    wild_sum={'bear': ('Black bear', 'Black bears live throughout the North Georgia mountains and around the park. Mothers lead new cubs out in spring; keep food and trash secured and give any bear plenty of room.'),
              'deer': ('White-tailed deer', 'Common in the park’s hardwood forest and sheltering here through the winter; most often seen early and late in the day.'),
              'bobcat': ('Bobcat', 'A shy, short-tailed wild cat recorded in the park. Most active at dusk and dawn along the quiet ridges.'),
              'coyote': ('Coyote', 'Easy to mistake for a dog. Coyotes travel the trails toward the Appalachian Trail, mostly at night or early morning.'),
              'fox': ('Fox', 'Foxes hunt the forest edges along the trails, mostly late in the day and at night.'),
              'raccoon': ('Raccoon', 'Masked night foragers of the creek bottoms and picnic areas; keep food and trash secured.'),
              'otter': ('North American river otter', 'River otters have been photographed in Little Amicalola Creek below the falls. Look for them early in the morning in the pools and riffles.'),
              'marmot': ('Groundhog', 'The mammal most often reported in the park on iNaturalist. Watch for groundhogs grazing the grassy lawns and road edges near the lodge.'),
              'squirrel': ('Eastern gray squirrel', 'The everyday squirrel of the hardwood forest, busy with acorns and hickory nuts in fall.'),
              'chipmunk': ('Eastern chipmunk', 'A small striped ground squirrel that darts among the rocks and roots beside the trails, with a sharp chipping call.'),
              'snake': ('Eastern copperhead', 'A venomous snake with hourglass bands that blends into dead leaves; watch where you step and sit, especially near rocks and logs. Harmless common watersnakes sun at the Reflection Pool, and timber rattlesnakes have also been recorded in the park.'),
              'turtle': ('Eastern box turtle', 'A small land turtle with a high, patterned shell, seen crossing the trails after summer rains. Leave it where you find it.'),
              'heron': ('Great blue heron', 'A tall gray wading bird that fishes the Reflection Pool and the slow stretches of the creek.'),
              'woodpecker': ('Pileated woodpecker', 'A crow-sized woodpecker with a red crest; listen for its loud drumming and look for big rectangular holes in dead trees.'),
              'hawk': ('Broad-winged hawk', 'A small, stocky hawk that nests in the mountain forest in summer and migrates to South America in fall.'),
              'vulture': ('Turkey vulture', 'Rides the updrafts over the ridges on tilted wings; easiest to spot from the top of the falls.')},
    grid=GRID, step=STEP, dem_b64=b64, tile=TILE, ve=1.5, ridge_ft=RIDGE,
    palette={'ground': '#C4E5C8', 'groundN': '#ADD7B4', 'oak': '#4E7F3A', 'sycamore': '#9DBF4E', 'gold': '#E39A3C', 'ridge': '#BBDDBF', 'rock': '#B7B0A4', 'rockDeep': '#9C958A'}, trees='east',
    landmarks=lm, animals_js=animals_js,
    extra_js='TRAILS.forEach(T=>{const g={A:%d,B:%d,C:%d}[T.id];if(g)T.gain=g;});' % (gA, gB, gC) + CLEAR,
    overview=dict(h2='Georgia’s tallest waterfall and the way to the Appalachian Trail',
                  p='Amicalola Falls tumbles down the east side of Amicalola Mountain in a long chain of cascades; the park lists it at 729 feet, the tallest cascading waterfall in the Southeast. The name comes from Cherokee words for “tumbling water.” A walks the level West Ridge path to the bridge across the middle of the falls, B climbs about 600 steps from the creek to the top and loops back on the East Ridge Trail, and C follows the Hike Inn Trail 5 miles into the national forest to the Len Foote Hike Inn. Pick a trail to focus the model; click anything on it for a quick note.',
                  numbers='Plain numbers mark spots more than one trail passes: the bridge (A and B) and the top of the falls (B and C). Lettered stops belong to one trail: C4 is the fourth stop on Trail C.',
                  wild_h='Wildlife around Amicalola Falls',
                  note='Amicalola Falls State Park, 418 Amicalola Falls State Park Rd, Dawsonville, Georgia. A Georgia State Parks ParkPass is required to park ($10 a day since January 2026). Status (November 2026): open. The East Ridge Trail, the return leg of B, was slated for an erosion-repair closure announced in 2025; if it is closed, go back down the stairs. Overnight stays at the Hike Inn need a reservation. Stay on marked trails and stairs; leaving them in the waterfall corridor is prohibited. Terrain from USGS elevation data, stylized; not for navigation.'),
    links={'A': [('Amicalola Falls State Park trail map · Georgia State Parks (Digital Library of Georgia)', 'https://dlg.usg.edu/record/dlg_ggpd_s-ga-bn200-pp2-bm1-b2009-ba4-belec-p-btext'), ('West Ridge Falls Access Trail · Hiking Project', 'https://www.hikingproject.com/trail/7042982/west-ridge-falls-access-trail')],
           'B': [('Amicalola Falls Loop · Hike the South', 'https://hikethesouth.com/hikes/amicalola-falls-loop'), ('Base-of-the-Falls Trail · Hiking Project', 'https://www.hikingproject.com/trail/7063674/base-of-the-falls-trail'), ('Amicalola Falls · New Georgia Encyclopedia', 'https://www.georgiaencyclopedia.org/articles/geography-environment/amicalola-falls/')],
           'C': [('Len Foote Hike Inn Trail · Appalachian Trail Conservancy', 'https://appalachiantrail.org/hikes/len-foote-hike-inn-trail/'), ('Len Foote Hike Inn · Wikipedia', 'https://en.wikipedia.org/wiki/Len_Foote_Hike_Inn'), ('Appalachian Trail Gateway · Amicalola Falls State Park & Lodge', 'https://amicalolafallslodge.com/appalachian-trail-gateway/')]},
    viewaz={'all': 0.6, 'A': -0.75, 'B': -0.75, 'C': 0.6},
    zoomcap={'A': 7.0, 'B': 4.6, 'C': 2.4},
    stop_photos=stop_photos, flower_photos=flower_photos, animal_photos=animal_photos,
)
json.dump({k: {'mi': R[k]['mi'], 'gain': R[k]['gain'], 'lo': R[k]['lo'], 'hi': R[k]['hi']} for k in R} | {'shown_gain': [gA, gB, gC]}, open('amicalola/stats.json', 'w'))
os.makedirs('/home/claude/site/out/amicalola-falls', exist_ok=True)
print(build(cfg, '/home/claude/site/out/amicalola-falls/index.html'))
