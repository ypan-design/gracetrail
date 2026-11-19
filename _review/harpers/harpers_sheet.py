from lib import *
from mk_sheet import build
import sys, json, os
import numpy as np

os.chdir('/home/claude/parks')
sys.path.insert(0, '/home/claude/parks')
p = Park('harpers', 39.3228, -77.7298, extra_kinds=('construction',))   # origin: Lower Town, Shenandoah Street
# 'construction' = the Byron footbridge stairway (OSM highway=construction while it is rebuilt)
LT = (-150, -30)       # Lower Town, Shenandoah Street
STP = (-422, -25)      # St. Peter's Roman Catholic Church (Wikipedia coordinates)
JR = (-1027, -102)     # Jefferson Rock (OSM viewpoint)
HC = (-1342, 358)      # Harper Cemetery (HMdb marker)
STO = (-1577, 361)     # Storer College (Wikipedia coordinates)
ATC = (-3022, 958)     # Appalachian Trail Conservancy visitor center, 799 Washington St (waymarking coordinates)
FBW, FBE = (271, 241), (979, 462)   # Goodloe Byron Memorial Footbridge ends (OSM way 10867588)
FB = (620, 350)
MHT = (-374, 2257)     # Maryland Heights trailhead on Harpers Ferry Road (start of the green trail, OSM)
NB = (272, 3324)       # Naval Battery (HMdb marker; 80 ft off the green trail)
SPLIT = (685, 2832)    # green trail splits into red Overlook Cliff and blue Stone Fort trails (OSM way ends)
OV = (1155, 904)       # Maryland Heights Overlook (OSM viewpoint)
SF = (3822, 6742)      # Stone Fort (OSM viewpoint; next to the Maryland Heights summit node, 1,457 ft)
P100 = (2995, 4543)    # 100-Pounder Battery (HMdb marker, 100 ft off the blue trail)
EBOT = (1376, 1845)    # blue trail's lower end on the red Overlook Cliff Trail
LH = (-2479, -5431)    # Loudoun Heights summit (OSM peak), what the 100-pounder covered
R = {}
R['A'] = route_xy(p, LT, STP, JR, (-1900, 150), ATC, STO, HC, JR, LT)
R['B'] = route_xy(p, LT, FBW, FBE, MHT, NB, SPLIT, (1805, 1879), OV)
R['C'] = route_xy(p, LT, FBW, FBE, MHT, NB, SPLIT, (3565, 6741), SF, (3835, 6866), P100, EBOT, OV)
for k in R: Park.smooth_E(R[k], 9); p.describe(R[k], k)
mSF = p.mile_of(R['C'], *SF)[0]
EXT = tuple(p.at_mile(R['C'], mSF - 0.1)[0])   # Exterior Fort wall, about 500 ft before the Stone Fort on the climb
ST = snap_stops(p, R, {
    'S1': (*LT, 'ABC'), 'S2': (*FB, 'BC'), 'S3': (*MHT, 'BC'), 'S4': (*NB, 'BC'), 'S5': (*SPLIT, 'BC'), 'S6': (*OV, 'BC'),
    'A1': (*STP, 'A'), 'A2': (*JR, 'A'), 'A3': (*ATC, 'A'), 'A4': (*STO, 'A'), 'A5': (*HC, 'A'),
    'C1': (*EXT, 'C'), 'C2': (*SF, 'C'), 'C3': (*P100, 'C'),
})
TILE = (-5400, 6200, -2500, 9300)
GRID = (-5700, 6500, -2800, 9600)
if 'plot' in sys.argv:
    from plot import plot
    plot(p, TILE, 'harpers/routes.png', routes=R, stops=ST, title='harpers', grid=1000)
    plot(p, (-3400, 1200, -600, 1400), 'harpers/routesA.png', routes=R, stops=ST, title='A', grid=250)
    sys.exit()

STEP = 60
b64, NX, NN = p.dem_b64(*GRID, STEP=STEP)
RIDGE = int(round(float(np.percentile(p.grid, 75)), -1))
print('grid', NX, NN, NX * NN, p.grid.min(), p.grid.max(), 'p75', RIDGE)

S = lambda i: ST[i]
stops = [
 dict(id='S1', trails=['A', 'B', 'C'], x=S('S1')[0], n=S('S1')[1], name='Lower Town',
      desc='The historic town on Shenandoah Street, where the Potomac and Shenandoah rivers meet. Parking here is very limited: park at the main visitor center, 171 Shoreline Drive, and take the free shuttle bus or walk the 1.6-mile Visitor Center to Lower Town Trail. Water and restrooms are in Lower Town; there are none on Maryland Heights.'),
 dict(id='A1', trails=['A'], x=S('A1')[0], n=S('A1')[1], name='St. Peter’s Church',
      desc='Stone steps cut into the hillside in 1810 climb from High Street past St. Peter’s Roman Catholic Church, built in 1833 and remodeled in 1896. It was the only church in town to escape destruction in the Civil War. The steps are steep; take care.'),
 dict(id='A2', trails=['A'], x=S('A2')[0], n=S('A2')[1], name='Jefferson Rock',
      desc='A shale slab balanced on a ledge above the rivers. Thomas Jefferson stood here on October 25, 1783, and called the passage of the Potomac through the Blue Ridge “perhaps one of the most stupendous scenes in Nature.” The four stone pillars under the slab were added between 1855 and 1860.'),
 dict(id='A3', trails=['A'], x=S('A3')[0], n=S('A3')[1], name='Appalachian Trail Conservancy',
      desc='The Appalachian Trail Conservancy visitor center at 799 Washington Street, called the trail’s psychological midpoint. Thru-hikers have had their photo taken on the front porch since 1979. Exhibits, a 10-foot 3-D map of the trail and a restroom. Open 9–5, Tuesday and Wednesday 10–4.'),
 dict(id='A4', trails=['A'], x=S('A4')[0], n=S('A4')[1], name='Storer College',
      desc='The campus of Storer College, a historically Black school that opened here in 1867 and closed in 1955. In 1906 it hosted the second conference of the Niagara Movement, forerunner of the NAACP. The walk back follows Fillmore Street past old Armory houses.'),
 dict(id='A5', trails=['A'], x=S('A5')[0], n=S('A5')[1], name='Harper Cemetery',
      desc='Robert Harper, who settled here in 1747 and gave the town its name, set aside this 4-acre burial ground; he died in 1782. Next to it stands Lockwood House, the birthplace of Storer College. The path drops back to Jefferson Rock and Lower Town.'),
 dict(id='S2', trails=['B', 'C'], x=S('S2')[0], n=S('S2')[1], name='Goodloe Byron Memorial Footbridge',
      desc='The Appalachian Trail crosses the Potomac into Maryland on this walkway attached to the railroad bridge, then a spiral stairway drops to the C&O Canal towpath; turn left and walk 0.3 mile upstream. Closed since July 27, 2026, for stairway construction. Meanwhile a shuttle runs from the main visitor center to C&O Canal Lock 34, about once an hour, 9 am to 5:30 pm.'),
 dict(id='S3', trails=['B', 'C'], x=S('S3')[0], n=S('S3')[1], name='Maryland Heights trailhead',
      desc='Cross the canal on a small wooden footbridge to Harpers Ferry Road; the trailhead is directly across the road. The green-blazed Maryland Heights Trail starts here. Trails are open daylight hours only.'),
 dict(id='S4', trails=['B', 'C'], x=S('S4')[0], n=S('S4')[1], name='Naval Battery',
      desc='The first Union fort on Maryland Heights, built in May 1862 about 300 feet above the river and armed with naval guns from the Washington Navy Yard, manned by about 300 sailors and Marines. Abandoned in September 1862, it later served as an ordnance depot. Its earthwork walls are still visible.'),
 dict(id='S5', trails=['B', 'C'], x=S('S5')[0], n=S('S5')[1], name='Trail split',
      desc='The green trail ends where the red-blazed Overlook Cliff Trail and the blue-blazed Stone Fort Trail begin. This old mountain road is the one Union troops retreated down on September 13, 1862, after holding the crest for about six hours; Harpers Ferry surrendered two days later.'),
 dict(id='S6', trails=['B', 'C'], x=S('S6')[0], n=S('S6')[1], name='Overlook Cliff',
      desc='Rock ledges at the top of the mountain’s 300-foot southern cliff, looking down on Lower Town, the meeting of the rivers and Loudoun Heights. The last half mile is a narrow, rocky descent. There are no railings. Peregrine falcons nest on these cliffs in spring, and some outcrops can close to protect them.'),
 dict(id='C1', trails=['C'], x=S('C1')[0], n=S('C1')[1], name='Exterior Fort',
      desc='Two parallel stone breastworks built in 1863, about 530 feet apart, enclosing roughly 3 acres with a Union campground. Troops held the mountain from May 1862 to July 1865. Steps lead from the walls up to the Stone Fort.'),
 dict(id='C2', trails=['C'], x=S('C2')[0], n=S('C2')[1], name='Stone Fort',
      desc='The massive stone foundation on the summit of Maryland Heights, about 1,450 feet. Union engineers built it in the winter of 1862–63 for an infantry blockhouse that was never finished; the garrison used it to store rations. Halfway point of the loop.'),
 dict(id='C3', trails=['C'], x=S('C3')[0], n=S('C3')[1], name='100-Pounder Battery',
      desc='A 100-pounder Parrott rifle stood here from 1863 on the highest and widest gun platform on the mountain, able to fire more than two miles in every direction. Soldiers hauled the 9,700-pound tube up 1,200 vertical feet. Past it the trail drops steeply over loose rock.'),
]
stops, order = renumber(p, R, stops)
print(order, [(s['id'], s['name']) for s in stops])
trails = [
 dict(id='A', name='Camp Hill and Appalachian Trail', short='Camp Hill', official=1.8, unit='loop', route='Loop', time='45 min–1 hr', level='Moderate', color='--tA',
      desc='From Lower Town the Appalachian Trail climbs stone steps past St. Peter’s Church to Jefferson Rock and follows the cliff edge above the Shenandoah to the Appalachian Trail Conservancy visitor center. The walk back follows town streets across the old Storer College campus and past Harper Cemetery. About 216 feet of climbing.', anchors=p.anchors(R['A'])),
 dict(id='B', name='Maryland Heights to Overlook Cliff', short='Overlook Cliff', official=4.5, unit='round trip', route='Out and back', time='3–3.5 hr', level='Moderate', color='--tB',
      desc='Crosses the Potomac on the Appalachian Trail footbridge, follows the C&O Canal towpath and climbs the green-blazed Maryland Heights Trail past Civil War batteries. The red-blazed Overlook Cliff Trail then drops half a mile over rock to the classic view of Harpers Ferry. About 1,150 feet of climbing. The footbridge is closed for now; see the note.', anchors=p.anchors(R['B'])),
 dict(id='C', name='Maryland Heights with the Stone Fort Trail', short='Stone Fort', official=6.2, unit='round trip', route='Lollipop', time='4–5 hr', level='Strenuous', color='--tC',
      desc='Adds the blue-blazed Stone Fort Trail: a steady climb past Union campgrounds and the Exterior Fort walls to the Stone Fort on the summit, then a steep, rocky descent past the 100-Pounder Battery to the Overlook Cliff Trail. Return the way you came. About 1,520 feet of climbing.', anchors=p.anchors(R['C'])),
]

# --- rivers: OSM water multipolygons (Potomac and Shenandoah), clipped to the tile
from harpers_watergeo import water
W = water((TILE[0] + 150, TILE[1] - 150, TILE[2] + 150, TILE[3] - 150))
WJ = [{'o': w['o'], 'h': w['h']} for w in W]
print('water', [(w['rid'], len(w['o']), len(w['h'])) for w in W])
extra_js = '''
TRAILS.forEach(T=>{const g={A:216,B:1154,C:1522}[T.id];if(g)T.gain=g;});
// loops and out-and-backs: report the first (outbound) mile for a stop
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

pa = place_along
A_ = lambda k, f, s=1, o=240: pa(p, R[k], [f], s, o)[0]
an = []
an += [f'{{k:"deer",path:{js(A_("C",.50,1,320)+A_("C",.53,1,320))},per:28}}', f'{{k:"deer",path:{js(A_("B",.62,-1,300)+A_("B",.65,-1,300))},per:30,ph:0.4}}']
an += [f'{{k:"chipmunk",at:{js(A_("A",.42,-1,120))},hop:true}}', f'{{k:"chipmunk",at:{js(A_("C",.66,-1,160))},hop:true}}', f'{{k:"chipmunk",at:{js(A_("B",.86,1,150))},hop:true}}']
an += [f'{{k:"raccoon",path:{js(A_("A",.72,1,160)+A_("A",.75,1,160))},per:22}}', f'{{k:"raccoon",path:{js(A_("C",.13,-1,200)+A_("C",.145,-1,200))},per:24,ph:0.5}}']
an += [f'{{k:"snake",path:{js(A_("C",.78,1,200)+A_("C",.795,1,200))},per:32}}', f'{{k:"snake",path:{js(A_("A",.30,1,110)+A_("A",.315,1,110))},per:32,ph:0.5}}']
an += [f'{{k:"squirrel",at:{js(A_("C",.58,1,180))},hop:true}}', f'{{k:"marmot",at:{js(A_("A",.86,1,150))}}}']
an += [f'{{k:"turtle",path:{js(A_("C",.40,-1,200)+A_("C",.41,-1,200))},per:60}}', f'{{k:"turtle",path:{js(A_("B",.47,1,220)+A_("B",.48,1,220))},per:60,ph:0.5}}']
animals_js = '[\n ' + ',\n '.join(an) + '\n]'

bn = {s['name']: s for s in stops}
g = lambda nm: (bn[nm]['x'], bn[nm]['n'])
jr, stp, atc, ov, sf, p100, ext, mht, lt = [g(k) for k in ('Jefferson Rock', 'St. Peter’s Church', 'Appalachian Trail Conservancy', 'Overlook Cliff', 'Stone Fort', '100-Pounder Battery', 'Exterior Fort', 'Maryland Heights trailhead', 'Lower Town')]
lm = f'''  gate({lt[0] + 60},{lt[1] - 70},0.3);gate({mht[0] + 40},{mht[1] - 60},0.8);
  // Lower Town: a few brick and stone houses along Shenandoah and High streets
  [[-330,-110,0.35],[-80,-120,0.4],[60,40,-0.6],[-260,110,0.3],[-560,-130,0.3]].forEach(([x,n,r],i)=>house(x,n,0.75+(i%2)*0.15,r));
  // Jefferson Rock: a shale slab on four stone pillars (OSM bare_rock), drawn large
  {{const q=G({JR[0]},{JR[1]});const g=new THREE.Group();g.position.copy(q);g.rotation.y=0.35;g.scale.setScalar(2.0);world.add(g);
   part(g,ico,"#8E887C",0,0.18,0,0.95,0.32,0.7);
   [[-0.45,-0.22],[0.45,-0.22],[-0.45,0.22],[0.45,0.22]].forEach(([a,b])=>part(g,box,"#A8A196",a,0.55,b,0.13,0.42,0.13,1.05));
   part(g,box,"#7E786E",0,0.84,0,1.35,0.18,0.75,1.06);}}
  // St. Peter's Church: stone nave and a tall spire
  {{const q=G({STP[0]},{STP[1]});const g=new THREE.Group();g.position.copy(q);g.rotation.y=0.25;g.scale.setScalar(1.9);world.add(g);
   part(g,box,"#9A8C7C",0,0.4,0,0.7,0.8,1.3,1.06);
   const rf=part(g,new THREE.CylinderGeometry(0.0,0.5,0.45,4,1),"#5A4E48",0,1.02,0,1,1,2.6,1.06);rf.rotation.y=Math.PI/4;rf.scale.set(1,1,2.6);
   part(g,box,"#9A8C7C",0,0.85,0.75,0.34,1.7,0.34,1.06);part(g,new THREE.ConeGeometry(0.24,1.1,4),"#4E4642",0,2.25,0.75,1,1,1,1.06).rotation.y=Math.PI/4;
   part(g,box,"#E9E4D8",0,2.95,0.75,0.03,0.3,0.03,0);part(g,box,"#E9E4D8",0,3.0,0.75,0.16,0.03,0.03,0);}}
  // Appalachian Trail Conservancy visitor center (white stone house with a porch)
  {{const q=G({ATC[0]},{ATC[1]});const g=new THREE.Group();g.position.copy(q);g.rotation.y=0.2;g.scale.setScalar(1.7);world.add(g);
   part(g,box,"#EEEBE3",0,0.4,0,1.2,0.8,0.8,1.06);part(g,new THREE.ConeGeometry(0.85,0.45,4),"#55606A",0,1.02,0,1,1,0.75,1.06).rotation.y=Math.PI/4;
   part(g,box,"#8E9AA3",0,0.42,0.5,1.1,0.05,0.25,0);[-0.5,0,0.5].forEach(a=>part(g,box,"#FFFFFF",a,0.2,0.6,0.05,0.4,0.05,0));}}
  // Goodloe Byron Memorial Footbridge on the railroad bridge piers (OSM way), across the Potomac
  {{const a=G({FBW[0]},{FBW[1]}),b=G({FBE[0]},{FBE[1]});const y=Math.max(a.y,b.y)+0.55;const L=Math.hypot(b.x-a.x,b.z-a.z);
   const g=new THREE.Group();g.position.set((a.x+b.x)/2,y,(a.z+b.z)/2);g.rotation.y=Math.atan2(-(b.z-a.z),b.x-a.x);world.add(g);
   part(g,box,"#6E7378",0,0,0,L,0.12,0.42,1.06);part(g,box,"#3F4447",0,0.2,0.2,L,0.05,0.04,0);part(g,box,"#3F4447",0,0.2,-0.2,L,0.05,0.04,0);
   part(g,box,"#5B4C44",0,0.34,-0.55,L,0.55,0.55,1.06);
   for(let i=0;i<5;i++){{const t=-L/2+L*(i+0.5)/5;const w=G({FBW[0]}+({FBE[0]}-{FBW[0]})*(i+0.5)/5,{FBW[1]}+({FBE[1]}-{FBW[1]})*(i+0.5)/5);const h=y-w.y+0.1;part(g,box,"#A39C90",t,-h/2,-0.25,0.35,h,0.9,1.05);}}}}
  // Naval Battery: three-sided earthwork with a naval gun
  {{const q=G({NB[0]},{NB[1]});const g=new THREE.Group();g.position.copy(q);g.rotation.y=Math.atan2(-0.4,0.9);g.scale.setScalar(1.6);world.add(g);
   part(g,box,"#8E9C62",0,0.18,0.55,1.4,0.36,0.3,1.05);part(g,box,"#8E9C62",-0.6,0.18,0,0.3,0.36,1.0,1.05);part(g,box,"#8E9C62",0.6,0.18,0,0.3,0.36,1.0,1.05);
   part(g,box,"#5C4636",0,0.16,0,0.4,0.2,0.5,1.05);const gun=part(g,cyl,"#2E3135",0,0.36,0.25,0.09,0.8,0.09,1.05);gun.rotation.x=Math.PI/2-0.15;}}
  // Overlook Cliff: bare rock ledge on top of the cliff, facing Lower Town (southwest)
  {{const q=G({OV[0]},{OV[1]});const g=new THREE.Group();g.position.copy(q);g.rotation.y=Math.atan2(-1,0.9);g.scale.setScalar(1.7);world.add(g);
   part(g,box,"#A8A196",0,0.15,0,1.8,0.3,1.1,1.06);part(g,ico,"#8E887C",-0.6,0.45,-0.3,0.55,0.4,0.5);part(g,ico,"#9A948A",0.55,0.38,-0.35,0.45,0.32,0.45);
   part(g,cyl,"#6B4F3A",0.75,0.6,0.3,0.05,0.9,0.05);part(g,box,"#E9E1D2",0.75,1.0,0.3,0.55,0.26,0.05,1.06);}}
  // Exterior Fort: dry-laid stone breastwork across the ridge
  {{const q=G({ext[0]},{ext[1]});const g=new THREE.Group();g.position.copy(q);g.rotation.y=0.5;g.scale.setScalar(1.6);world.add(g);
   for(let i=-3;i<=3;i++)part(g,box,i%2?"#A49D8F":"#968F82",i*0.42,0.2,(i%2)*0.04,0.44,0.4,0.32,1.05);}}
  // Stone Fort: square stone foundation on the summit
  {{const q=G({SF[0]},{SF[1]});const g=new THREE.Group();g.position.copy(q);g.rotation.y=0.3;g.scale.setScalar(2.0);world.add(g);
   [[0,-0.75,1.7,0.26],[0,0.75,1.7,0.26],[-0.75,0,0.26,1.3],[0.75,0,0.26,1.3]].forEach(([dx,dz,sx,sz])=>part(g,box,"#A49D8F",dx,0.32,dz,sx,0.64,sz,1.06));
   part(g,box,"#B7B0A4",0,0.1,0,1.3,0.2,1.3,0);part(g,cyl,"#D9D4C8",0,0.9,0,0.03,1.2,0.03,0);part(g,box,"#2F4E8C",0.22,1.35,0,0.42,0.26,0.02,0);}}
  // 100-Pounder Battery: gun platform with a big Parrott rifle aimed at Loudoun Heights
  {{const q=G({P100[0]},{P100[1]});const d=new THREE.Vector3({LH[0] - P100[0]},0,{-(LH[1] - P100[1])}).normalize();
   const g=new THREE.Group();g.position.copy(q);g.rotation.y=Math.atan2(d.x,d.z);g.scale.setScalar(1.8);world.add(g);
   part(g,new THREE.CylinderGeometry(0.9,1.0,0.25,16),"#9C9478",0,0.12,0,1,1,1,1.05);
   part(g,box,"#5C4636",0,0.42,0,0.5,0.32,0.8,1.05);
   const b=part(g,new THREE.CylinderGeometry(0.1,0.17,1.5,12),"#2E3135",0,0.68,0.25,1,1,1,1.05);b.rotation.x=Math.PI/2-0.08;}}
'''

creeks = []
for nm in ('Potomac River', 'Shenandoah River'):
    for i, wid in enumerate([w['id'] for w in p.W if w.get('n') == nm and w['k'] == 'river']):
        c = p.creek([wid], GRID, minor=False)
        if c: creeks.append(dict(id=f"{nm.split()[0].lower()}{i}", **c))
print('creeks', len(creeks))

species_extra = {
 'bluebell_hf': 'bluebell_hf:{name:"Virginia bluebells",latin:"Mertensia virginica",color:"#6E8FD8",shape:"tube",bloom:[4],sum:"Nodding clusters of sky-blue bells, pink in bud, carpeting the moist woods and river floodplains in April.",rule:(d,e,g,s)=>d<700&&e<360&&g<0.5}',
 'violet_hf': 'violet_hf:{name:"Bird-foot violet",latin:"Viola pedata",color:"#8D7AD6",shape:"cup",bloom:[4,5],sum:"A large, flat-faced violet named for its finely cut leaves, shaped like a bird’s foot. Look on dry, sunny, rocky ground in the woods in spring.",rule:(d,e,g,s)=>d>500&&g>0.2&&s>0}',
 'sunflower_hf': 'sunflower_hf:{name:"Woodland sunflower",latin:"Helianthus strumosus",color:"#F2C230",shape:"dome",bloom:[7,8,9],sum:"Yellow daisy-like flowers on tall stems at the edges of the forest in late summer.",rule:(d,e,g,s)=>d>300&&e>350}',
 'aster_hf': 'aster_hf:{name:"New England aster",latin:"Symphyotrichum novae-angliae",color:"#8E4FC9",shape:"dome",bloom:[9,10],sum:"Bushy stems crowded with purple, gold-centered flowers along the banks of the Potomac and Shenandoah in fall, busy with bees and butterflies.",rule:(d,e,g,s)=>d<600&&e<380}',
 'joepye_hf': 'joepye_hf:{name:"Joe-Pye weed",latin:"Eutrochium purpureum",color:"#C98DB3",shape:"dome",bloom:[7,8,9],sum:"A tall plant, often taller than a person, with domed heads of dusty-pink flowers along the riverbanks in late summer.",rule:(d,e,g,s)=>d<450&&e<340}',
}

# --- photos (Wikimedia Commons via gt6_photos; reused species photos from the site)
PM = json.load(open('/mnt/files/gtb/photos/harpers/photos_meta.json'))
def keep(key, files):
    out = []
    for f in files:
        for x in PM.get(key, []):
            if x['f'].endswith('/' + f): out.append(dict(x))
    return out
by_name = {
 'Jefferson Rock': keep('jr', ['pl_harpers_jr_0.jpg', 'pl_harpers_jr_2.jpg']),
 'St. Peter’s Church': keep('stpeter', ['pl_harpers_stpeter_1.jpg', 'pl_harpers_stpeter_2.jpg', 'pl_harpers_stpeter_3.jpg']),
 'Harper Cemetery': keep('harpercem', ['pl_harpers_harpercem_1.jpg', 'pl_harpers_harpercem_0.jpg', 'pl_harpers_harpercem_3.jpg']),
 'Storer College': keep('storer', ['pl_harpers_storer_0.jpg', 'pl_harpers_storer_3.jpg']),
 'Appalachian Trail Conservancy': keep('atc', ['pl_harpers_atc_1.jpg']),
 'Goodloe Byron Memorial Footbridge': keep('footbridge', ['pl_harpers_footbridge_1.jpg', 'pl_harpers_footbridge_0.jpg']) + keep('mdh', ['pl_harpers_mdh_0.jpg']),
 'Overlook Cliff': keep('overlook', ['pl_harpers_overlook_2.jpg', 'pl_harpers_overlook_1.jpg', 'pl_harpers_overlook_3.jpg']),
}
stop_photos = {s['id']: by_name[s['name']] for s in stops if by_name.get(s['name'])}
flower_photos = {
 'bluebell_hf': [{"f": "../photos/sp_bluebells_sr_0.jpg", "by": "Judy Gallagher", "lic": "BY 2.0", "src": "https://www.flickr.com/photos/52450054@N04/8647493804", "t": "Virginia Bluebells - Mertensia virginica, Merrimac Farm Wildlife Management Area, Aden, Virginia"},
                 {"f": "../photos/sp_bluebells_sr_2.jpg", "by": "Judy Gallagher", "lic": "BY 2.0", "src": "https://www.flickr.com/photos/52450054@N04/49704819983", "t": "Virginia Bluebells - Mertensia virginica, C. F. Phelps Wildlife Management Area, Sumerduck, Virginia"}],
 'violet_hf': keep('sp:birdfootviolet', ['sp_birdfootviolet_0.jpg', 'sp_birdfootviolet_2.jpg']),
 'sunflower_hf': keep('sp:woodsunflower', ['sp_woodsunflower_0.jpg', 'sp_woodsunflower_1.jpg']),
 'aster_hf': keep('sp:neaster', ['sp_neaster_4.jpg', 'sp_neaster_5.jpg']),
 'joepye_hf': keep('sp:joepye', ['sp_joepye_0.jpg', 'sp_joepye_2.jpg']),
}
animal_photos = {
 'deer': [{"f": "../photos/sp_wtdeer_bk_0.jpg", "by": "James St. John", "lic": "BY 2.0", "src": "https://www.flickr.com/photos/47445767@N05/8269171051", "t": "Odocoileus virginianus (white-tailed deer)"}],
 'snake': [{"f": "../photos/sp_hk_ratsnake_2.jpg", "by": "smashtonlee05", "lic": "BY 2.0", "src": "https://www.flickr.com/photos/166087957@N06/45001071614", "t": "Black rat snake (Pantherophis obsoletus)"}],
 'turtle': [{"f": "../photos/sp_smboxturtle_0.jpg", "by": "Jarek Tuszyński", "lic": "CC BY-SA 3.0", "src": "https://commons.wikimedia.org/wiki/File:Eastern_Box_Turtle_8679.jpg", "t": "Eastern Box Turtle 8679"},
            {"f": "../photos/sp_smboxturtle_1.jpg", "by": "Jasper Shide", "lic": "CC0", "src": "https://commons.wikimedia.org/wiki/File:Terrapene_carolina_ssp._carolina_-_Eastern_Box_Turtle_(6-01-23)_01.jpg", "t": "Terrapene carolina ssp. carolina - Eastern Box Turtle (6-01-23) 01"}],
 'raccoon': [{"f": "../photos/sp_raccoon_0.jpg", "by": "Harlequeen", "lic": "BY 2.0", "src": "https://www.flickr.com/photos/27887748@N00/491727233", "t": "Raccoon"}],
 'eagle': [{"f": "../photos/sp_baldeagle_0.jpg", "by": "Martin Falbisoner", "lic": "CC BY-SA 3.0", "src": "https://commons.wikimedia.org/wiki/File:Bald_Eagle_Head_sq.jpg", "t": "Bald Eagle Head sq"},
           {"f": "../photos/sp_baldeagle_1.jpg", "by": "Paul Friel", "lic": "CC BY 2.0", "src": "https://commons.wikimedia.org/wiki/File:Bald_Eagle_-_%22Helga%22_-_Haliaeetus_leucocephalus2.jpg", "t": "Bald Eagle - \"Helga\" - Haliaeetus leucocephalus2"}],
 'peregrine': [{"f": "../photos/sp_sm_peregrine_2.jpg", "by": "FurLined", "lic": "BY-SA 2.0", "src": "https://www.flickr.com/photos/8752533@N04/3875330734", "t": "Peregrine Falcon"}],
}

from fauna import TREE_RULES
cfg = dict(
    title='Maryland Heights, Harpers Ferry', aria='Maryland Heights, Jefferson Rock and the Appalachian Trail at Harpers Ferry National Historical Park', h1='Maryland Heights &amp; Harpers Ferry',
    canyons=creeks, trails=trails, stops=stops, order=order,
    species=list(species_extra), species_extra=species_extra,
    flora={'A': ['bluebell_hf', 'violet_hf', 'aster_hf'], 'B': ['bluebell_hf', 'joepye_hf', 'aster_hf', 'sunflower_hf'], 'C': ['violet_hf', 'sunflower_hf', 'joepye_hf']},
    wild=['deer', 'chipmunk', 'squirrel', 'marmot', 'raccoon', 'snake', 'turtle', 'eagle', 'peregrine', 'hawk', 'woodpecker', 'kingfisher'],
    wild_sum={
     'deer': ('White-tailed deer', 'Browses the oak woods on Maryland Heights and Camp Hill, most often seen early and late in the day.'),
     'chipmunk': ('Eastern chipmunk', 'A small striped ground squirrel that darts among the rocks and old stone walls of the Civil War forts.'),
     'raccoon': ('Raccoon', 'Lives along the rivers and in town; mostly out at night, but its tracks show up in the mud of the canal towpath.'),
     'snake': ('Black rat snake', 'A long, harmless black snake, often seen both on the mountains and in Lower Town. Copperheads and timber rattlesnakes also live in the park: watch where you put your hands on the rocks.'),
     'turtle': ('Eastern box turtle', 'A small land turtle with a high, patterned shell, often seen on the mountain trails and in Lower Town, especially after summer rain. Leave it where you find it.'),
     'squirrel': ('Southern flying squirrel', 'A small squirrel that glides between trees on folds of skin. It comes out at night, so you are more likely to hear it than see it.'),
     'marmot': ('Groundhog', 'A stout brown burrowing rodent of lawns, fields and forest edges, like the open grounds around Camp Hill; it whistles and dives into its burrow when startled.'),
     'hawk': ('Red-tailed hawk', 'A big, broad-winged hawk with a rusty tail; young birds are raised on Virginius Island, and adults circle over the rivers and ridges.'),
     'woodpecker': ('Pileated woodpecker', 'A crow-sized woodpecker with a red crest. Listen for its loud drumming and calls in the oak woods on Maryland Heights.'),
     'kingfisher': ('Belted kingfisher', 'A blue-gray, shaggy-crested bird that rattles loudly as it flies low over the rivers and the canal, then dives headfirst for fish.'),
     'eagle': ('Bald eagle', 'Bald eagles fish the Potomac and Shenandoah. Scan the rivers and the tall trees along the shore from the footbridge and the Overlook Cliff.'),
     'peregrine': ('Peregrine falcon', 'Rare here: the Maryland Heights cliff is one of only two natural nest sites in Maryland used by peregrines since reintroduction began in 1975. Peregrines nest again on the cliffs of Maryland Heights: in 2021 a chick fledged there for the first time in almost 70 years. Parts of the cliff can close in spring to protect the nest.'),
    },
    grid=GRID, step=STEP, dem_b64=b64, tile=TILE, ve=2.0, ridge_ft=RIDGE,
    palette='east', tree_rule='if(inLake(x,n)){type=null;}else ' + TREE_RULES['east'],
    landmarks=lm, animals_js=animals_js, extra_js=extra_js,
    stop_photos=stop_photos, flower_photos=flower_photos, animal_photos=animal_photos,
    overview=dict(h2='Harpers Ferry from both sides of the river',
                  p='Harpers Ferry sits where the Potomac and Shenandoah rivers meet and cut through the Blue Ridge, at the corner of West Virginia, Maryland and Virginia. Across the Potomac, Maryland Heights rises to about 1,450 feet, ringed with Civil War forts. A climbs from Lower Town to Jefferson Rock on the Appalachian Trail, B crosses the river to the Overlook Cliff, and C adds the Stone Fort Trail over the summit. Pick a trail to focus the model; click anything on it for a quick note.',
                  numbers='Plain numbers mark spots more than one trail passes: Lower Town, the footbridge and the lower Maryland Heights trail. Lettered stops belong to one trail: C2 is the second stop on Trail C.',
                  wild_h='Wildlife around Harpers Ferry',
                  note='Harpers Ferry National Historical Park, West Virginia and Maryland. Park at the main visitor center, 171 Shoreline Drive, Harpers Ferry, WV; entrance fee $20 per vehicle or $10 per person on foot or bike, good for three days, no cash. Park trails are open sunrise to sunset; the Appalachian Trail is always open. Status (November 2026): the Goodloe Byron Memorial Footbridge over the Potomac has been closed since July 27, 2026, for stairway construction, cutting the walking route from Lower Town to Maryland Heights. The Maryland Heights trails stay open; a shuttle runs from the visitor center to C&amp;O Canal Lock 34 about once an hour, 9 am to 5:30 pm (not in bad weather). Check nps.gov/hafe before you go. No water or restrooms on Maryland Heights. Terrain from USGS elevation data, stylized; not for navigation.'),
    links={'A': [('Camp Hill and Appalachian Trail · NPS', 'https://www.nps.gov/hafe/planyourvisit/camp-hill-and-appalachian-trail.htm'), ('Jefferson Rock · NPS', 'https://home.nps.gov/hafe/learn/historyculture/jefferson-rock.htm'), ('ATC Harpers Ferry visitor center', 'https://appalachiantrail.org/?p=858')],
           'B': [('Maryland Heights Trail · NPS', 'https://www.nps.gov/hafe/planyourvisit/maryland-heights-trail.htm'), ('Byron Bridge stairway project and shuttle · NPS', 'https://home.nps.gov/choh/planyourvisit/byron-bridge.htm'), ('Hikes at Harpers Ferry · NPS', 'https://www.nps.gov/hafe/planyourvisit/hikes.htm')],
           'C': [('Maryland Heights history · NPS', 'https://home.nps.gov/hafe/learn/historyculture/maryland-heights.htm'), ('Stone Fort Trail · Mid-Atlantic Day Trips', 'https://midatlanticdaytrips.com/2015/05/hiking-maryland-heights-part-2-stone-fort-trail/'), ('100-Pounder Battery · NPS', 'https://www.nps.gov/places/000/information-panel-100-pounder-battery-heaviest-and-highest.htm')]},
    viewaz={'all': 0.35, 'A': 0.35, 'B': 0.35, 'C': 0.35},
    zoomcap={'A': 3.8, 'B': 3.0, 'C': 2.4},
)
OUT = '/home/claude/site/out/harpers-ferry-maryland-heights/index.html'
json.dump({k: {'mi': R[k]['mi'], 'gain': R[k]['gain'], 'lo': R[k]['lo'], 'hi': R[k]['hi']} for k in R}, open('harpers/stats.json', 'w'))
os.makedirs(os.path.dirname(OUT), exist_ok=True)
print(build(cfg, OUT))
# post-process my own page: water functions, blue terrain under the rivers, no flowers in the water
h = open(OUT).read()
n0 = len(h)
h = h.replace('/* ================= landmarks + waterfall ================= */', WATER_FN + '/* ================= landmarks + waterfall ================= */', 1)
h = h.replace('if(mk<0.02)c=col(PAL.ground);else if(cd<140)c=col(PAL.riparian);', 'if(mk<0.02)c=col(PAL.ground);else if(inLake(mx,mn))c=col("#8FC6DA");else if(cd<140)c=col(PAL.riparian);', 1)
h = h.replace('if(!sp.rule(creekDist(x,n),e,g,s))continue;', 'if(inLake(x,n)||!sp.rule(creekDist(x,n),e,g,s))continue;')
print('post', len(h) - n0, h.count('function inLake'), h.count('inLake(mx,mn)'), h.count('inLake(x,n)||!sp.rule'))
open(OUT, 'w').write(h)
