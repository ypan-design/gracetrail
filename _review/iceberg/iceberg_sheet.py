from lib import *
from mk_sheet import build
import sys, json, math, os
import numpy as np
sys.stdout.reconfigure(line_buffering=True)
os.chdir('/home/claude/parks')

p = Park('iceberg', 48.7990, -113.6800)
TH = (193, 385)          # Iceberg-Ptarmigan trailhead, behind the Swiftcurrent Motor Inn cabins (bottom of Ptarmigan Cutoff)
THA = (197, -361)        # Swiftcurrent Pass trailhead, west end of the Swiftcurrent parking lot
FISH = (-1250, -60)      # Fishercap Lake spur (north shore of the lake)
RLK = (-6200, -420)      # beside Redrock Lake
RF = (-7385, -1392)      # Redrock Falls viewpoint (OSM)
JN = (-7944, 8489)       # Iceberg Lake Trail leaves the Ptarmigan Trail
LK = (-14900, 6150)      # Iceberg Lake, northeast shore
TU = (-6594, 18508)      # Ptarmigan Tunnel, south portal (OSM tunnel way)
TUN = (-6540, 18588)     # north end of the tunnel way


def mkroute(pts):
    E = [p.elev(*q) for q in pts]; cum = [0.0]
    for i in range(1, len(pts)): cum.append(cum[-1] + math.dist(pts[i - 1], pts[i]))
    gain = sum(max(0, E[i] - E[i - 1]) for i in range(1, len(E)))
    return dict(pts=pts, E=E, cum=cum, segs=[], gain=gain, mi=cum[-1] / 5280, lo=min(E), hi=max(E))


def out_back(r):
    pts = r['pts'] + r['pts'][-2::-1]; r2 = mkroute(pts); r2['segs'] = r['segs']; return r2


UP = {'A': route_xy(p, THA, FISH, RLK, RF), 'B': route_xy(p, TH, JN, LK), 'C': route_xy(p, TH, JN, TU)}
R = {k: out_back(UP[k]) for k in UP}
for k in R: Park.smooth_E(R[k], 9); p.describe(R[k], k)
for k in UP: p.describe(UP[k], k + ' up')


def M(k, mi): return tuple(p.at_mile(UP[k], mi)[0])


W = json.load(open('iceberg/iceberg_ways.json'))
WB = {w['id']: w for w in W}


def wpts(i): return [p.xy(q) for q in WB[i]['p']]


# Ptarmigan Falls: steepest reach of Ptarmigan Creek within 700 ft of where the trail crosses it
creekP = wpts('82795079') + wpts('82800325')[1:]
cross = min(creekP, key=lambda q: min(math.dist(q, r) for r in UP['B']['pts']))
best = None
for a, b in zip(creekP, creekP[1:]):
    if math.dist(a, cross) > 700: continue
    s = abs(p.elev(*a) - p.elev(*b)) / (math.dist(a, b) or 1)
    if not best or s > best[0]: best = (s, a, b)
PF = ((best[1][0] + best[2][0]) / 2, (best[1][1] + best[2][1]) / 2)
PFD = (best[2][0] - best[1][0], best[2][1] - best[1][1]) if p.elev(*best[1]) > p.elev(*best[2]) else (best[1][0] - best[2][0], best[1][1] - best[2][1])
print('creek cross', [round(v) for v in cross], 'falls', [round(v) for v in PF], 'slope', round(best[0], 2), 'dir', [round(v) for v in PFD])
# Redrock Falls: steepest reach of Swiftcurrent Creek within 600 ft of the OSM viewpoint
scP = wpts('82801579')
best = None
for a, b in zip(scP, scP[1:]):
    if math.dist(a, RF) > 600: continue
    s = abs(p.elev(*a) - p.elev(*b)) / (math.dist(a, b) or 1)
    if not best or s > best[0]: best = (s, a, b)
RFX = ((best[1][0] + best[2][0]) / 2, (best[1][1] + best[2][1]) / 2) if best else RF
RFD = (best[2][0] - best[1][0], best[2][1] - best[1][1]) if best else (1, 0)
if best and p.elev(*best[1]) < p.elev(*best[2]): RFD = (-RFD[0], -RFD[1])
print('redrock falls', [round(v) for v in RFX], best and round(best[0], 2), [round(v) for v in RFD])
# Iceberg Creek footbridge: where B's outbound leg comes closest to Iceberg Creek
icP = wpts('82799721') + wpts('82799642')
IB = min(UP['B']['pts'], key=lambda q: min(math.dist(q, r) for r in icP))
print('iceberg bridge', [round(v) for v in IB], round(min(math.dist(IB, r) for r in icP)))
for nm in ('Swiftcurrent Motor Inn', 'Swiftcurrent'):
    for w in W:
        if nm in (w.get('n') or '') and (w['tags'].get('tourism') or w['tags'].get('building')):
            P = [p.xy(q) for q in w['p']]; print('bldg', w['n'], w['tags'], [round(sum(a for a, b in P) / len(P)), round(sum(b for a, b in P) / len(P))])

ST = snap_stops(p, R, {
    'A1': (*THA, 'A'), 'A2': (*FISH, 'A'), 'A3': (*RLK, 'A'), 'A4': (*RF, 'A'),
    's1': (*TH, 'BC'), 's2': (*M('B', 1.0), 'BC'), 's3': (*M('B', 2.48), 'BC'), 's4': (*JN, 'BC'),
    'B1': (*M('B', 3.15), 'B'), 'B2': (*IB, 'B'), 'B3': (*LK, 'B'),
    'C1': (*M('C', 4.3), 'C'), 'C2': (*TU, 'C'),
})
TILE = (-24500, 7200, -8500, 25700)
GRID = (-25000, 7700, -9000, 26200)
if 'plot' in sys.argv:
    from plot import plot
    plot(p, (-17000, 1000, -3000, 19500), 'iceberg/routes3.png', routes=R, stops=ST, title='iceberg', grid=1000)
    sys.exit()

STEP = 175
b64, NX, NN = p.dem_b64(*GRID, STEP=STEP)
RIDGE = int(round(float(np.percentile(p.grid, 75)), -1))
print('grid', NX, NN, NX * NN, p.grid.min(), p.grid.max(), 'p75', RIDGE)

S = lambda i: ST[i]
stops = [
 dict(id='A1', trails=['A'], x=S('A1')[0], n=S('A1')[1], name='Swiftcurrent Pass trailhead', desc='At the west end of the Swiftcurrent Motor Inn parking lot, at the end of Many Glacier Road. The trail crosses Wilbur Creek soon after leaving the lot.'),
 dict(id='A2', trails=['A'], x=S('A2')[0], n=S('A2')[1], name='Fishercap Lake', desc='About a third of a mile in, a short spur of less than 100 yards leads to the north shore. One of the best places in Many Glacier to see moose, especially in the morning and early evening.'),
 dict(id='A3', trails=['A'], x=S('A3')[0], n=S('A3')[1], name='Redrock Lake', desc='At about 1.7 miles the trail runs along Redrock Lake, with Mount Grinnell, Swiftcurrent Glacier and Swiftcurrent Mountain, topped by its fire lookout, ahead.'),
 dict(id='A4', trails=['A'], x=S('A4')[0], n=S('A4')[1], name='Redrock Falls', desc='Swiftcurrent Creek spills over red argillite in a series of cascades between Bullhead Lake and Redrock Lake. Side paths lead to views of the lower and upper falls; the rock is slick when wet.'),
 dict(id='s1', trails=['B', 'C'], x=S('s1')[0], n=S('s1')[1], name='Iceberg-Ptarmigan trailhead', desc='Behind the Swiftcurrent Motor Inn cabins, with a seasonal restroom and room for only a dozen or so cars; otherwise park at the motor inn. The first quarter mile climbs steeply to the Ptarmigan Trail.'),
 dict(id='s2', trails=['B', 'C'], x=S('s2')[0], n=S('s2')[1], name='Slopes below Mount Henkel', desc='The trail traverses open, brushy slopes with views of Mount Wilbur, Mount Grinnell and Swiftcurrent Mountain. This first stretch is prime grizzly habitat: make noise and carry bear spray.'),
 dict(id='s3', trails=['B', 'C'], x=S('s3')[0], n=S('s3')[1], name='Ptarmigan Falls', desc='About 2.5 miles in, a clearing looks down on Ptarmigan Creek falling through a narrow rock channel, and the rocks above the falls are a popular rest stop. A footbridge crosses the creek just beyond.'),
 dict(id='s4', trails=['B', 'C'], x=S('s4')[0], n=S('s4')[1], name='Iceberg Lake junction', desc='About 0.1 mile past the footbridge the trails split: the Iceberg Lake Trail goes left (west), the Ptarmigan Trail climbs right toward Ptarmigan Lake and the tunnel.'),
 dict(id='B1', trails=['B'], x=S('B1')[0], n=S('B1')[1], name='Under the Ptarmigan Wall', desc='The trail curves along the base of the Ptarmigan Wall, a serrated ridge rising more than 1,500 feet above the trail and separating the Many Glacier and Belly River valleys. Meadows here fill with wildflowers in early summer.'),
 dict(id='B2', trails=['B'], x=S('B2')[0], n=S('B2')[1], name='Iceberg Creek footbridge', desc='The trail crosses Iceberg Creek at about 4.4 miles and passes alpine meadows full of wildflowers, then climbs a short rise to the lake.'),
 dict(id='B3', trails=['B'], x=S('B3')[0], n=S('B3')[1], name='Iceberg Lake', desc='A turquoise lake at 6,094 ft in a cirque whose cliffs rise more than 2,000 ft above the water. Snow and ice often float on it well into summer; how much is left by late summer varies a lot from year to year. Turn around here.'),
 dict(id='C1', trails=['C'], x=S('C1')[0], n=S('C1')[1], name='Ptarmigan Lake', desc='At about 4.2 miles, just past a series of waterfalls and cascades, a small lake in a bowl under the Ptarmigan Wall. Bighorn sheep and mountain goats are often seen here. Switchbacks climb the scree above it.'),
 dict(id='C2', trails=['C'], x=S('C2')[0], n=S('C2')[1], name='Ptarmigan Tunnel', desc='A tunnel about 250 ft long blasted through the Ptarmigan Wall in 1930 for horse tours, at about 7,200 ft. Steel doors added in 1975 are closed from about October 1 until the trail is cleared, usually in mid-July. Through it you look north over Elizabeth Lake and the Belly River valley. Turn around here.'),
]
stops, order = renumber(p, R, stops)
sid = {s['name']: s['id'] for s in stops}
print(order, [(s['id'], s['name']) for s in stops])
trails = [
 dict(id='A', name='Redrock Falls', short='Redrock Falls', official=3.8, unit='round trip', route='Out and back', time='1.5–2.5 hr', level='Easy', color='--tA',
      desc='A nearly flat walk on the Swiftcurrent Pass Trail, mostly in forest with open views, past Fishercap Lake and Redrock Lake to a series of cascades on Swiftcurrent Creek. A good family hike and a good bet for moose. Return the same way.', anchors=p.anchors(R['A'])),
 dict(id='B', name='Iceberg Lake', short='Iceberg Lake', official=9.6, unit='round trip', route='Out and back', time='4.5–6 hr', level='Moderate', color='--tB',
      desc='One of the best-known hikes in Glacier. After a steep start the trail climbs gradually across open slopes to Ptarmigan Falls, then turns west under the Ptarmigan Wall through meadows to a cirque lake where ice and snow float into summer. Start early: the trail is busy in summer and often closed for bear activity.', anchors=p.anchors(R['B'])),
 dict(id='C', name='Ptarmigan Tunnel', short='Ptarmigan Tunnel', official=10.7, unit='round trip', route='Out and back', time='5–7 hr', level='Strenuous', color='--tC',
      desc='The same start as Iceberg Lake to Ptarmigan Falls, then the Ptarmigan Trail climbs past a thick huckleberry patch to Ptarmigan Lake and switchbacks up the scree to a 1930 tunnel through the Ptarmigan Wall, about 2,300 ft above the trailhead. The tunnel doors are closed from about October 1 to mid-July.', anchors=p.anchors(R['C'])),
]

# ---------- lakes (OSM outlines) and glaciers, flat water surfaces
def clip(poly, box):
    X0, X1, N0, N1 = box
    def cut(P, inside, inter):
        out = []
        for i in range(len(P)):
            a, b = P[i - 1], P[i]
            if inside(b):
                if not inside(a): out.append(inter(a, b))
                out.append(b)
            elif inside(a): out.append(inter(a, b))
        return out
    def ix(v): return lambda a, b: (v, a[1] + (b[1] - a[1]) * (v - a[0]) / (b[0] - a[0]))
    def iy(v): return lambda a, b: (a[0] + (b[0] - a[0]) * (v - a[1]) / (b[1] - a[1]), v)
    P = poly
    for ins, it in [(lambda q: q[0] >= X0, ix(X0)), (lambda q: q[0] <= X1, ix(X1)), (lambda q: q[1] >= N0, iy(N0)), (lambda q: q[1] <= N1, iy(N1))]:
        if P: P = cut(P, ins, it)
    return P
inset = (TILE[0] + 400, TILE[1] - 400, TILE[2] + 400, TILE[3] - 400)
lakes, glac = [], []
for w in W:
    nat = w['tags'].get('natural')
    if nat not in ('water', 'glacier') or len(w['p']) < 6: continue
    P = [p.xy(q) for q in w['p']]
    if P[0] == P[-1]: P = P[:-1]
    P = clip(P, inset)
    if len(P) < 3: continue
    (lakes if nat == 'water' else glac).append([[round(x), round(n)] for x, n in P])
print('lakes', len(lakes), 'glaciers', len(glac))
ICE = [[round(x), round(n)] for x, n in [p.xy(q) for q in WB['82798328']['p']][:-1]]
ix0, ix1 = min(a for a, b in ICE), max(a for a, b in ICE); in0, in1 = min(b for a, b in ICE), max(b for a, b in ICE)


def inpoly(x, n, P):
    c = False
    for i in range(len(P)):
        a, b = P[i - 1], P[i]
        if (a[1] > n) != (b[1] > n) and x < (b[0] - a[0]) * (n - a[1]) / (b[1] - a[1]) + a[0]: c = not c
    return c


rng = np.random.default_rng(7)
FLOES = []
while len(FLOES) < 9:
    x, n = rng.uniform(ix0, ix1), rng.uniform(in0, in1)
    if inpoly(x, n, ICE) and all(math.dist((x, n), f[:2]) > 380 for f in FLOES) and min(math.dist((x, n), q) for q in ICE) > 180:
        FLOES.append([round(x), round(n), round(float(rng.uniform(0.5, 1.2)), 2), round(float(rng.uniform(0, 3.1)), 2)])

extra_js = '''
setTimeout(()=>{try{clouds.forEach(c=>{c.hx*=1.8;c.hz*=1.8;c.hy+=10;});}catch(e){}},0);
TRAILS.forEach(T=>{const g={A:267,B:1275,C:2300}[T.id];if(g)T.gain=g;});
mileOf=function(T,x,n){let b=null;T.pts.forEach(p=>{const d=Math.hypot(p.x-x,p.n-n);if(!b||d<b.d)b={d,m:p.m,e:p.e};});if(!b||b.d>=300)return null;const f=T.pts.find(p=>Math.hypot(p.x-x,p.n-n)<b.d+60);return {d:b.d,m:f.m,e:f.e};};
function lakeP(){return lakeP.c||(lakeP.c=%s);}
function glacP(){return glacP.c||(glacP.c=%s);}
function inPoly(x,n,P){let c=false;for(let i=0,j=P.length-1;i<P.length;j=i++){const a=P[i],b=P[j];if((a[1]>n)!==(b[1]>n)&&x<(b[0]-a[0])*(n-a[1])/(b[1]-a[1])+a[0])c=!c;}return c;}
function inLake(x,n){for(const P of lakeP()){if(inPoly(x,n,P))return true;}return false;}
(function(){const mat=new THREE.MeshLambertMaterial({color:"#7CC4D2",side:THREE.DoubleSide});const edge=new THREE.LineBasicMaterial({color:"#4E98B2"});
  lakeP().forEach(P=>{const sh=new THREE.Shape(P.map(([x,n])=>new THREE.Vector2(x,n)));const geo=new THREE.ShapeGeometry(sh);const pa=geo.attributes.position;
    let lo=1e9;P.forEach(([x,n])=>{lo=Math.min(lo,G(x,n,0).y);});
    for(let i=0;i<pa.count;i++){const x=pa.getX(i),n=pa.getY(i);const v=G(x,n,0.15);pa.setXYZ(i,v.x,Math.max(v.y,lo+0.15),v.z);}
    pa.needsUpdate=true;geo.computeVertexNormals();const m=new THREE.Mesh(geo,mat);m.renderOrder=1;world.add(m);
    const ring=P.concat([P[0]]).map(([x,n])=>{const v=G(x,n,0.17);v.y=lo+0.17;return v;});world.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints(ring),edge));});
  const gm=new THREE.MeshLambertMaterial({color:"#F4F8FA",side:THREE.DoubleSide});
  glacP().forEach(P=>{const sh=new THREE.Shape(P.map(([x,n])=>new THREE.Vector2(x,n)));const geo=new THREE.ShapeGeometry(sh);const pa=geo.attributes.position;
    for(let i=0;i<pa.count;i++){const x=pa.getX(i),n=pa.getY(i);const v=G(x,n,0.12);pa.setXYZ(i,v.x,v.y,v.z);}
    pa.needsUpdate=true;geo.computeVertexNormals();const m=new THREE.Mesh(geo,gm);world.add(m);});
})();
''' % (js(lakes), js(glac))

# ---------- landmarks
tdx, tdn = TUN[0] - TU[0], TUN[1] - TU[1]
lm = f'''  gate({S('A1')[0]},{S('A1')[1]},1.6);gate({S('s1')[0]},{S('s1')[1]},2.0);
  // trail sign at the Iceberg Lake / Ptarmigan junction
  {{const q=G({S('s4')[0] + 60},{S('s4')[1] - 50});part(world,cyl,"#6B4F3A",q.x,q.y+0.9,q.z,0.1,1.8,0.1);const b=part(world,box,"#8A6A4A",q.x,q.y+1.6,q.z,1.5,0.45,0.12,1.06);rot(b,0,0.6,0);}}
  // waterfalls: Ptarmigan Falls and Redrock Falls (sheets, splash rings and mist)
  const fallTex=stripeTex("#E4F6F6","#FFFFFF",64,128,22,9,14);fallTex.repeat.set(1,1.5);
  const fallMat=new THREE.MeshBasicMaterial({{map:fallTex,side:THREE.DoubleSide}});
  const rings=[],mist=[];
  function mkFall(x,n,dx,dn,sc){{const F=G(x,n);const d=new THREE.Vector3(dx,0,-dn).normalize();const ry=Math.atan2(d.x,d.z);
    const wf=new THREE.Group();wf.position.copy(F);wf.rotation.y=ry;wf.scale.setScalar(sc);world.add(wf);
    [[1.3,3.0,-0.9,4.6],[1.7,2.0,-0.35,2.2],[2.0,1.3,0.15,0.7]].forEach(([wd,ht,z,yc])=>{{const pl=new THREE.Mesh(new THREE.PlaneGeometry(wd,ht),fallMat);pl.position.set(0,yc,z);wf.add(pl);
      part(wf,ico,PAL.stone,-wd/2-0.45,yc+ht/2-0.25,z-0.1,0.55,0.45,0.5);part(wf,ico,PAL.stoneD,wd/2+0.45,yc+ht/2-0.35,z-0.1,0.5,0.42,0.5);}});
    part(wf,ico,PAL.stoneD,-1.5,2.2,-1.3,0.55,0.9,0.5);part(wf,ico,PAL.stone,1.5,2.0,-1.2,0.5,0.85,0.5);
    part(wf,new THREE.CylinderGeometry(1,1,0.06,18),"#DDF3F3",0,0.05,1.3,1.7,1,1.2,1.04,false);
    for(let i=0;i<3;i++){{const rg=new THREE.Mesh(new THREE.RingGeometry(0.75,0.88,24),new THREE.MeshBasicMaterial({{color:"#FFFFFF",transparent:true,side:THREE.DoubleSide}}));rg.rotation.x=-Math.PI/2;rg.position.set(0,0.1,0.95);wf.add(rg);rings.push(rg);}}
    for(let i=0;i<6;i++){{const m=new THREE.Mesh(new THREE.SphereGeometry(0.22,8,6),new THREE.MeshBasicMaterial({{color:"#FFFFFF",transparent:true}}));wf.add(m);mist.push({{m,ph:i/6,x:(i%3-1)*0.45}});}}}}
  mkFall({PF[0]:.0f},{PF[1]:.0f},{PFD[0]:.0f},{PFD[1]:.0f},1.4);
  mkFall({RFX[0]:.0f},{RFX[1]:.0f},{RFD[0]:.0f},{RFD[1]:.0f},1.2);
  anim.water={{fallTex,rings,mist}};
  // Ptarmigan Tunnel: stone portal block with a dark arched opening and open steel doors, facing along the tunnel
  {{const q=G({TU[0]},{TU[1]});const g=new THREE.Group();g.position.copy(q);g.rotation.y=Math.atan2({tdx},{-tdn});world.add(g);
    part(g,box,"#8E7F70",0,0.9,0,3.6,2.6,2.4,1.04);
    [1,-1].forEach(sd=>{{part(g,box,"#1E1A18",0,0.85,1.22*sd,1.3,1.7,0.06,0);const a=part(g,new THREE.CylinderGeometry(0.65,0.65,0.06,16,1,false,-Math.PI/2,Math.PI),"#1E1A18",0,1.7,1.22*sd,1,1,1,0);rot(a,-Math.PI/2,0,0);}});
    part(g,box,"#6E7378",-0.95,0.85,1.6,0.08,1.7,0.75,1.04);part(g,box,"#6E7378",0.95,0.85,1.6,0.08,1.7,0.75,1.04);
    part(g,box,"#A89A8A",0,2.3,0,3.9,0.25,2.6,1.04);}}
  // ice floes on Iceberg Lake
  {{let lo=1e9;lakeP().forEach(P=>{{if(inPoly({LK[0]},{LK[1]},P)||P.some(([x,n])=>Math.hypot(x-({ix0}+{ix1})/2,n-({in0}+{in1})/2)<1600))P.forEach(([x,n])=>{{lo=Math.min(lo,G(x,n,0).y);}});}});
    {js(FLOES)}.forEach(([x,n,s,r])=>{{const q=G(x,n);const y=Math.max(q.y,lo);const m=part(world,box,"#FFFFFF",q.x,y+0.32,q.z,1.6*s,0.35,1.0*s,1.04);rot(m,0,r,0);const t=part(world,box,"#E6F4F8",q.x+0.2*s,y+0.6,q.z,0.8*s,0.3,0.6*s,1.04);rot(t,0,r+0.4,0);}});}}
  // Swiftcurrent Motor Inn cabins by the trailheads
  house({S('s1')[0] + 320},{S('s1')[1] - 360},0.7,0.3);house({S('s1')[0] + 520},{S('s1')[1] - 260},0.7,0.3);house({S('s1')[0] + 140},{S('s1')[1] - 520},0.9,1.8);
  bench({S('s3')[0] + 70},{S('s3')[1] - 40},0.8);bench({S('B3')[0] + 60},{S('B3')[1] + 80},2.3);
'''

# ---------- wildlife
pa = place_along
A_ = lambda k, f, s=1, o=240: pa(p, UP[k], [f], s, o)[0]
def path2(k, f, s=1, o=240, d=0.02): return js(A_(k, f, s, o) + A_(k, f + d, s, o))
an = []
an += [f'{{k:"grizzly",path:{path2("B", .13, -1, 900, .02)},per:40}}', f'{{k:"grizzly",path:{path2("B", .78, -1, 650, .02)},per:44,ph:0.4}}']
an += [f'{{k:"moose",path:{js([-1450, -350, -1150, -500])},per:40}}', f'{{k:"moose",path:{path2("A", .8, -1, 260, .03)},per:44,ph:0.5}}']
an += [f'{{k:"bighorn",path:{path2("B", .66, 1, 650, .02)},per:32}}', f'{{k:"bighorn",path:{path2("C", .72, -1, 600, .015)},per:30,ph:0.3}}']
an += [f'{{k:"goat",path:{js([-16600, 7400, -16450, 7600])},per:34}}', f'{{k:"goat",path:{path2("C", .93, -1, 650, .01)},per:36,ph:0.5}}']
an += [f'{{k:"chipmunk",at:{js(A_("B", .565, 1, 140))},hop:true}}', f'{{k:"chipmunk",at:{js(A_("B", .985, -1, 160))},hop:true}}']
animals_js = '[\n ' + ',\n '.join(an) + '\n]'

sp_extra = {
 'glacierlily': 'glacierlily:{name:"Glacier lily",latin:"Erythronium grandiflorum",color:"#F4CE2A",shape:"cup",bloom:[6,7],sum:"Nodding yellow lilies with swept-back petals that bloom right behind the melting snow. With fleabane they make a showy display near Iceberg Lake in early summer.",rule:(d,e,g,s)=>e>5600&&g<0.7}',
 'beargrass': 'beargrass:{name:"Beargrass",latin:"Xerophyllum tenax",color:"#F6F0D8",shape:"yucca",bloom:[6,7,8],sum:"A grassy clump that sends up a tall stalk topped with a club of tiny cream flowers. Each plant blooms only every several years, so some summers are much showier than others.",rule:(d,e,g,s)=>e>5000&&e<7000&&g<0.9}',
 'daisy': 'daisy:{name:"Subalpine fleabane",latin:"Erigeron peregrinus",color:"#B8A6E8",shape:"dome",bloom:[7,8],sum:"A lavender daisy with a yellow center that fills moist alpine meadows in midsummer, including the basin around Iceberg Lake.",rule:(d,e,g,s)=>e>5700&&g<0.6}',
 'huckleberry': 'huckleberry:{name:"Huckleberry",latin:"Vaccinium membranaceum",color:"#3E3A6E",shape:"berry",bloom:[6],fruit:[8,9],sum:"A knee-high shrub with dark purple berries in late summer, a key food for grizzlies. Thick patches grow along the Ptarmigan Trail above the Iceberg Lake junction and beside the Redrock Falls trail.",rule:(d,e,g,s)=>e<6600&&g<0.8&&d>60}',
 'thimbleberry': 'thimbleberry:{name:"Thimbleberry",latin:"Rubus parviflorus",color:"#FBF7EE",shape:"cup",bloom:[6,7],fruit:[8],sum:"A thornless shrub with big soft maple-like leaves, white crinkled flowers and soft red berries, common along the trail to Redrock Falls.",rule:(d,e,g,s)=>e<5600&&g<0.7}',
}

# ---------- photos
PHM = json.load(open('/mnt/files/gtb/photos/iceberg/photos_meta.json'))
REUSE = json.load(open('iceberg_reuse.json'))
def pick(key, idx):
    out = []
    for i in idx:
        m = next((m for m in PHM.get(key, []) if m['f'].endswith(f'_{i}.jpg')), None)
        if m: out.append(m)
    return out
def ru(*names): return [REUSE[n] for n in names if n in REUSE]
stop_photos = {sid['Iceberg Lake']: pick('lake', [0, 1, 2]), sid['Ptarmigan Tunnel']: pick('tunnel', [0, 1]),
               sid['Ptarmigan Lake']: pick('ptlake', [0, 1, 2]), sid['Fishercap Lake']: pick('fisher', [0, 1, 2]),
               sid['Redrock Lake']: pick('redlake', [2, 1])}
flower_photos = {'glacierlily': ru('sp_gl_glacierlily_1.jpg', 'sp_gl_glacierlily_2.jpg', 'sp_gl_glacierlily_3.jpg'),
                 'beargrass': ru('sp_gl_beargrass_2.jpg', 'sp_gl_beargrass_1.jpg', 'sp_gl_beargrass_3.jpg'),
                 'daisy': ru('sp_gl_daisy_0.jpg', 'sp_gl_daisy_2.jpg', 'sp_gl_daisy_3.jpg'),
                 'thimbleberry': ru('sp_av_thimbleberry_0.jpg', 'sp_av_thimbleberry_3.jpg'),
                 'huckleberry': pick('sp:ic_huckleberry', [0, 3, 1])}
animal_photos = {'grizzly': ru('sp_gl_grizzly_0.jpg', 'sp_grizzly_gt_1.jpg'), 'moose': pick('fisher', [0]) + ru('sp_moose_gt_0.jpg', 'sp_moose_gt_3.jpg'),
                 'bighorn': ru('sp_gl_bighorn_2.jpg', 'sp_gl_bighorn_3.jpg'), 'goat': ru('sp_gl_goat_1.jpg', 'sp_gl_goat_2.jpg', 'sp_gl_goat_3.jpg'),
                 'chipmunk': ru('sp_av_chipmunk_1.jpg', 'sp_av_chipmunk_2.jpg'), 'ptarmigan': ru('sp_gl_ptarmigan_0.jpg', 'sp_gl_ptarmigan_1.jpg', 'sp_gl_ptarmigan_2.jpg')}

creeks = []
named = {'Swiftcurrent Creek', 'Wilbur Creek', 'Iceberg Creek', 'Ptarmigan Creek', 'Kennedy Creek', 'Apikuni Creek', 'Belly River', 'Allen Creek', 'Cataract Creek'}
for w in W:
    if w['tags'].get('waterway') in ('stream', 'river') and w.get('n') in named and len(w['p']) >= 3:
        c = p.creek([w['id']], GRID, minor=w['n'] != 'Swiftcurrent Creek', every=200)
        if c and len(c['pts']) >= 2: creeks.append(dict(id='c' + w['id'], **c))
print('creeks', len(creeks))

from fauna import TREE_RULES
cfg = dict(
    title='Iceberg Lake, Glacier National Park', aria='Iceberg Lake, Ptarmigan Tunnel and Redrock Falls in Many Glacier, Glacier National Park', h1='Iceberg Lake &amp; Ptarmigan Tunnel',
    canyons=creeks, trails=trails, stops=stops, order=order,
    species=list(sp_extra), species_extra=sp_extra,
    flora={'A': ['thimbleberry', 'huckleberry', 'beargrass'], 'B': ['glacierlily', 'daisy', 'beargrass', 'huckleberry'], 'C': ['huckleberry', 'beargrass', 'glacierlily', 'daisy']},
    wild=['grizzly', 'moose', 'bighorn', 'goat', 'chipmunk', 'ptarmigan'],
    wild_sum={
     'grizzly': ('Grizzly bear', 'Many Glacier is prime grizzly country. Bears feed on the berry slopes along the first miles of the Iceberg and Ptarmigan trails and graze the meadows below the Ptarmigan Wall, and these trails are often closed for bear activity. Carry bear spray, hike in groups and make noise.'),
     'moose': ('Moose', 'Moose feed in the willows and shallows of Fishercap Lake and Redrock Lake, best seen in the morning and early evening. They also browse the willow drainages below the Iceberg Lake Trail. Give them plenty of room.'),
     'bighorn': ('Bighorn sheep', 'Bighorn sheep graze the meadows along the Iceberg Lake Trail and are often seen near Ptarmigan Lake, usually in small groups of rams or ewes with lambs.'),
     'goat': ('Mountain goat', 'Look for white dots on the cliffs and ledges above Iceberg Lake and around Ptarmigan Lake and the tunnel. Binoculars help.'),
     'chipmunk': ('Chipmunk', 'Bold chipmunks work the rest stops at Ptarmigan Falls and the shore of Iceberg Lake. Do not feed them.'),
     'ptarmigan': ('White-tailed ptarmigan', 'The small alpine grouse that gives Ptarmigan Falls, Lake, Wall and Tunnel their names: mottled brown in summer and white in winter, it sits still among the rocks above treeline and is easy to miss.'),
    },
    grid=GRID, step=STEP, dem_b64=b64, tile=TILE, ve=1.6, ridge_ft=RIDGE,
    palette={"ground": "#C9E2C4", "groundN": "#B3D5B3", "rock": "#C9A898", "rockDeep": "#B08A7C", "ridge": "#DDD5CC", "conifer": "#2F5A3E", "shrub": "#8FA878", "riparian": "#BFE0CF"},
    tree_rule='if(inLake(x,n)){type=null;}else ' + TREE_RULES['conifer'].replace('type=tr()<.3?"gold":"conifer"', 'type=tr()<.15?"gold":"conifer"').replace('r0<.72?"conifer":r0<.86?"shrub":"gold"', 'r0<.8?"conifer":r0<.95?"shrub":"gold"'), treeline_ft=6900,
    rock_all_aspects=True,
    landmarks=lm, animals_js=animals_js, extra_js=extra_js,
    stop_photos=stop_photos, animal_photos=animal_photos, flower_photos=flower_photos,
    overview=dict(h2='Many Glacier: ice, falls and a tunnel',
                  p='Many Glacier, on the east side of Glacier National Park, is where four valleys meet below steep walls of red and gray rock. All three hikes start at the Swiftcurrent Motor Inn at the end of Many Glacier Road. A is the easy walk past Fishercap and Redrock Lakes to Redrock Falls, B climbs past Ptarmigan Falls to Iceberg Lake, and C leaves the Iceberg trail at the junction for Ptarmigan Lake and the Ptarmigan Tunnel. Pick a trail to focus the model; click anything on it for a quick note.',
                  numbers='B and C share their first 2.6 miles, so stops on that stretch carry plain numbers (1–4). Stops on one trail only carry its letter: B3 is the third stop on Trail B after the shared part. All three are out and back; their miles count the way in. Lakes are drawn from OpenStreetMap outlines.',
                  wild_h='Wildlife in Many Glacier',
                  note='Swiftcurrent Motor Inn, end of Many Glacier Road, Glacier National Park, Montana (near Babb). Park entrance pass required; no vehicle reservations in 2026. Many Glacier Road closes for winter the third weekend of November, weather permitting, and services are closed until late spring. Ptarmigan Tunnel doors are closed from about October 1 to mid-July, and snow often lingers on the upper trails into July. Trails here are often closed for bear activity: check with a ranger, carry bear spray, no dogs on trails. Terrain from USGS elevation data, stylized; not for navigation.'),
    links={'A': [('Redrock Falls Trail · NPS', 'https://www.nps.gov/places/redrock-falls-trail.htm'), ('Redrock Falls · Hiking in Glacier', 'https://hikinginglacier.com/redrock-falls.htm')],
           'B': [('Iceberg Lake Trailhead · NPS', 'https://www.nps.gov/places/iceberg-lake-trailhead.htm'), ('Iceberg Lake · Hiking in Glacier', 'https://hikinginglacier.com/iceberg-lake.htm'), ('Iceberg Lake · Hiking Project', 'https://www.hikingproject.com/trail/7018720/iceberg-lake')],
           'C': [('Ptarmigan Tunnel · Hiking in Glacier', 'https://hikinginglacier.com/ptarmigan-tunnel.htm'), ('Ptarmigan Tunnel · Wikipedia', 'https://en.wikipedia.org/wiki/Ptarmigan_Tunnel')]},
    viewaz={'all': 1.6, 'A': 1.6, 'B': 1.6, 'C': 2.4},
    zoomcap={'A': 3.6, 'B': 2.2, 'C': 2.6},
)
OUT = '/home/claude/site/out/glacier-iceberg-lake/index.html'
os.makedirs(os.path.dirname(OUT), exist_ok=True)
json.dump({k: {'mi': R[k]['mi'], 'gain': R[k]['gain'], 'lo': R[k]['lo'], 'hi': R[k]['hi']} for k in R}, open('iceberg/stats.json', 'w'))
print(build(cfg, OUT))
src = open(OUT).read()
def rp(a, b):
    global src
    assert src.count(a) == 1, (a, src.count(a)); src = src.replace(a, b)
rp('if(!sp.rule(creekDist(x,n),e,g,s))continue;', 'if(inLake(x,n)||!sp.rule(creekDist(x,n),e,g,s))continue;')
open(OUT, 'w').write(src)
print('patched')
