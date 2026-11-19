from lib import *
from mk_sheet import build
import sys, json, os, math, re, glob
import numpy as np

os.chdir('/home/claude/parks')
p = Park('tunnels', 36.0117, -114.7939)
TH = (-86, -260)          # start of the OSM Historic Railroad Trail, at the Lakeshore Road trailhead below the visitor center
GARAGE = (15254, 1796)    # end of the trail at the top level of the Hoover Dam parking garage (OSM)
TUN = {i + 1: [tuple(round(v) for v in p.xy(q)) for q in p.WID[w]['p']] for i, w in
       enumerate(['195180379', '195180382', '195180381', '195180380', '195180383'])}   # OSM tunnel=yes ways, west to east
T1W, T5E = TUN[1][0], TUN[5][-1]


def outback(*pts):
    a = route_xy(p, *pts); b = route_xy(p, *pts[::-1])
    P = a['pts'] + b['pts'][1:]
    E = [p.elev(*q) for q in P]; cum = [0.0]
    for i in range(1, len(P)): cum.append(cum[-1] + math.dist(P[i - 1], P[i]))
    return dict(pts=P, E=E, cum=cum, segs=a['segs'], gain=0, mi=cum[-1] / 5280, lo=min(E), hi=max(E)), a


R, UP = {}, {}
R['A'], UP['A'] = outback(TH, T1W)
R['B'], UP['B'] = outback(TH, T5E)
R['C'], UP['C'] = outback(TH, GARAGE)
for k in R: Park.smooth_E(R[k], 9); p.describe(R[k], k)


def in_tunnel(x, n):
    for P in TUN.values():
        for a, b in zip(P, P[1:]):
            dx, dn = b[0] - a[0], b[1] - a[1]; L2 = dx * dx + dn * dn or 1
            t = max(0, min(1, ((x - a[0]) * dx + (n - a[1]) * dn) / L2))
            if math.hypot(x - a[0] - dx * t, n - a[1] - dn * t) < 45: return True
    return False


def railbed(r):
    """elevations with the tunnels bridged (the DEM follows the ridge above each tunnel)"""
    E = np.array([p.elev(*q) for q in r['pts']]); m = np.array([in_tunnel(*q) for q in r['pts']])
    idx = np.arange(len(E)); E[m] = np.interp(idx[m], idx[~m], E[~m])
    k = np.ones(9) / 9; E = np.convolve(np.pad(E, 4, mode='edge'), k, mode='valid')
    return E


STAT = {}
for k in R:
    E = railbed(R[k]); STAT[k] = dict(gain=int(round(sum(max(0, E[i] - E[i - 1]) for i in range(1, len(E))) / 10) * 10), hi=int(E.max()), lo=int(E.min()))
print('railbed stats', STAT)
# railbed is nearly level (NPS: 11 ft on the NPS section; Bird & Hike GPS 1,570-1,599 ft to Tunnel 5, 1,378 ft at the garage)
STAT = {'A': dict(gain=30, hi=1600, lo=1570), 'B': dict(gain=50, hi=1600, lo=1570), 'C': dict(gain=450, hi=1600, lo=1375)}


def M(mi): return tuple(p.at_mile(UP['C'], mi)[0])


ST = snap_stops(p, R, {
    'S1': (*TH, 'ABC'), 'S2': (3224, 724, 'ABC'), 'S3': (*M(1.15), 'ABC'), 'S4': (*T1W, 'ABC'),
    'S5': (*TUN[2][0], 'BC'), 'S6': (*TUN[3][0], 'BC'), 'S7': (*TUN[4][0], 'BC'), 'S8': (*T5E, 'BC'),
    'C1': (*M(2.75), 'C'), 'C2': (*GARAGE, 'C'),
})
for t in 'ABC': print(t, 'one way', round(UP[t]['mi'], 2), 'round trip', round(R[t]['mi'], 2))
print('tunnel miles', {i: round(p.mile_of(UP['C'], *P[0])[0], 2) for i, P in TUN.items()})

TILE = (-5000, 20500, -8000, 10500)
GRID = (-5600, 21100, -8600, 11100)
STEP = 120
if 'plot' in sys.argv:
    from plot import plot
    plot(p, (-1000, 17500, -1500, 4500), 'tunnels/routes.png', routes=R, stops=ST, title='tunnels', grid=1000)
    sys.exit()

b64, NX, NN = p.dem_b64(*GRID, STEP=STEP)
Z = p.grid.astype(float)
RIDGE = int(np.percentile(Z[Z > 1215], 75))
print('grid', NX, NN, NX * NN, Z.min(), Z.max(), 'ridge', RIDGE)

# ---- water from the DEM: Lake Mead (flat surface in the elevation data) and the Colorado River below the dam
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from scipy import ndimage
xs = X0g = np.arange(GRID[0], GRID[0] + NX * STEP, STEP)[:NX]; ns = np.arange(GRID[2], GRID[2] + NN * STEP, STEP)[:NN]
vals, cnt = np.unique(np.round(Z), return_counts=True); LAKE_Z = float(vals[np.argmax(cnt)])
gy, gx = np.gradient(Z, STEP)
lake = (np.abs(Z - LAKE_Z) <= 2) & (np.hypot(gx, gy) < 0.01)
lake = ndimage.binary_opening(lake, iterations=1)
lab, nl = ndimage.label(lake); sz = ndimage.sum(lake, lab, range(1, nl + 1))
lake = np.isin(lab, [i + 1 for i, s in enumerate(sz) if s > 150])
lake = ndimage.binary_closing(lake, iterations=1)
river = Z < 700
lab, nl = ndimage.label(river); sz = ndimage.sum(river, lab, range(1, nl + 1))
river = np.isin(lab, [i + 1 for i, s in enumerate(sz) if s > 20])
RIV_Z = float(np.percentile(Z[river], 10)) + 8 if river.any() else 650
print('lake level in DEM', LAKE_Z, 'cells', int(lake.sum()), 'river', int(river.sum()), RIV_Z)
inset = (TILE[0] + 200, TILE[1] - 200, TILE[2] + 200, TILE[3] - 200)
XX, NNg = np.meshgrid(xs, ns)
inside = (XX > inset[0]) & (XX < inset[1]) & (NNg > inset[2]) & (NNg < inset[3])


def polys(mask, simplify=90, minlen=8):
    m = ndimage.gaussian_filter((mask & inside).astype(float), 0.8)
    cs = plt.contour(xs, ns, m, levels=[0.5]); out = []
    for seg in cs.allsegs[0]:
        if len(seg) < minlen: continue
        P = [seg[0]]
        for q in seg[1:]:
            if math.dist(q, P[-1]) >= simplify: P.append(q)
        if len(P) >= 4: out.append([[round(x), round(n)] for x, n in P])
    plt.close('all'); return out


LAKE = []
for a in range(TILE[0], TILE[1], 6000):   # pieces so each polygon triangulates cleanly
    band = (XX >= a) & (XX < a + 6000 + STEP)
    LAKE += polys(lake & band)
RIVER = []
for a in range(TILE[2], TILE[3], 4000):
    band = (NNg >= a) & (NNg < a + 4000 + STEP)
    RIVER += polys(river & band, 50, 5)
print('water polys', [len(r) for r in LAKE], [len(r) for r in RIVER])

# ---- landmarks
dam = [p.xy(q) for q in p.WID['49938932']['p']]
D = np.array(dam); c0 = D.mean(0); u, s_, vt = np.linalg.svd(D - c0); ax_ = vt[0]
proj = (D - c0) @ ax_; perp = (D - c0) @ vt[1]
DAMPTS = []
for t in np.linspace(proj.min() + 20, proj.max() - 20, 11):
    sel = np.abs(proj - t) < 60
    off = perp[sel].mean() if sel.any() else 0
    q = c0 + ax_ * t + vt[1] * off; DAMPTS.append([round(q[0]), round(q[1])])
print('dam crest pts', DAMPTS)
BR = []
for w in p.W:
    if 'Tillman Memorial Bridge Walkway' in (w['n'] or ''): BR += [p.xy(q) for q in w['p']]
BR = np.array(BR); bc = BR.mean(0); _, _, bvt = np.linalg.svd(BR - bc); bpr = (BR - bc) @ bvt[0]
B0 = bc + bvt[0] * bpr.min(); B1 = bc + bvt[0] * bpr.max()
print('bridge', B0.round(), B1.round(), round(float(bpr.max() - bpr.min())))
side = 1 if p.elev(*(c0 + vt[1] * 350)) > p.elev(*(c0 - vt[1] * 350)) else -1
TOWERS = [[round(q[0] + vt[1][0] * 300 * side), round(q[1] + vt[1][1] * 300 * side)] for q in (DAMPTS[2], DAMPTS[4], DAMPTS[6], DAMPTS[8])]
DECK = int(max(p.elev(*B0), p.elev(*B1)))
print('towers', TOWERS, 'deck', DECK, 'side', side)
LV = next(t[2] for t in p.pois() if t[0] == 'Lakeview Overlook')
BONE = next(t[2] for t in p.pois() if t[0] == 'Boneyard of Hoover Dam')

S = lambda i: ST[i]
stops = [
 dict(id='S1', trails=['A', 'B', 'C'], x=S('S1')[0], n=S('S1')[1], name='Historic Railroad trailhead', desc='The paved lot on Lakeshore Road below the Lake Mead Visitor Center. Accessible pit toilets, a bike repair station and trash cans; drinking water is at the visitor center. The first 1.5 miles have no shade.'),
 dict(id='S2', trails=['A', 'B', 'C'], x=S('S2')[0], n=S('S2')[1], name='Hoover Dam Lodge spur', desc='A side trail climbs south to the Hoover Dam Lodge, a second place to start. The railroad bed runs on along the hillside with wide views over Boulder Basin of Lake Mead.'),
 dict(id='S3', trails=['A', 'B', 'C'], x=S('S3')[0], n=S('S3')[1], name='Concrete plugs', desc='Just before the first tunnel, a ravine on the right holds big concrete plugs. They were cut out of Hoover Dam to make room for turbines and dumped here.'),
 dict(id='S4', trails=['A', 'B', 'C'], x=S('S4')[0], n=S('S4')[1], name='Tunnel 1', desc='The first of five tunnels, each about 25 ft wide, 30 ft high and 300 ft long, blasted for the 1931 construction railroad. Eight sections of timber supports hold the rock, five of them with planks against falling stones. Turnaround for the short walk.'),
 dict(id='S5', trails=['B', 'C'], x=S('S5')[0], n=S('S5')[1], name='Tunnel 2', desc='Damaged by fire in 1990; shotcrete was sprayed where the original supports burned. One of two tunnels now lined with shipping containers that catch small rocks falling from the ceiling. Between this tunnel and the next, a rocky road below the railbed is thought to be the original construction road to the dam.'),
 dict(id='S6', trails=['B', 'C'], x=S('S6')[0], n=S('S6')[1], name='Tunnel 3', desc='The longest bend in the line. Rock pressure deformed its outer arch, which has been shored up. Bats sometimes roost in the tunnels.'),
 dict(id='S7', trails=['B', 'C'], x=S('S7')[0], n=S('S7')[1], name='Tunnel 4', desc='A short tunnel through a spur of the River Mountains. Lake Mead opens up to the north on the way to the last tunnel.'),
 dict(id='S8', trails=['B', 'C'], x=S('S8')[0], n=S('S8')[1], name='Tunnel 5', desc='Burned in 1978 and reopened in 2001. Just past it are a gate and a Bureau of Reclamation rest area with a vault toilet and picnic tables, about 2.2 miles from the trailhead. The Lakeview Overlook sits on the cliff above, but it is reached by road, not from the trail.'),
 dict(id='C1', trails=['C'], x=S('C1')[0], n=S('C1')[1], name='Reclamation section', desc='Past the gate the trail leaves the national park for Bureau of Reclamation land. It narrows to loose gravel and drops toward Black Canyon, the steepest part of the walk.'),
 dict(id='C2', trails=['C'], x=S('C2')[0], n=S('C2')[1], name='Hoover Dam parking garage', desc='The trail ends at the top level of the dam’s parking garage, about 3.7 miles from the trailhead. From here it is a short walk down to the dam and the visitor center. Climb back the way you came.'),
]
stops, order = renumber(p, R, stops)
print(order, [(s['id'], s['name']) for s in stops])
nm = {s['name']: s for s in stops}
trails = [
 dict(id='A', name='Historic Railroad Trail to Tunnel 1', short='Tunnel 1', official=2.5, unit='round trip', route='Out and back', time='1–1.5 hr', level='Easy', color='--tA',
      desc='The easy first stretch of the old Hoover Dam railroad: level, hard-packed gravel that suits wheelchairs, strollers and bikes. It follows the hillside above Lake Mead past the ravine of concrete plugs to the first tunnel. No shade.', anchors=p.anchors(R['A'])),
 dict(id='B', name='Historic Railroad Trail through the five tunnels', short='Five tunnels', official=4.4, unit='round trip', route='Out and back', time='2–2.5 hr', level='Easy', color='--tB',
      desc='The classic walk: on along the level railbed through all five tunnels, with Boulder Basin of Lake Mead below, to the gate and rest area just past Tunnel 5. This is the end of the National Park Service section; turn around here.', anchors=p.anchors(R['B'])),
 dict(id='C', name='Historic Railroad Trail to Hoover Dam', short='Hoover Dam', official=7.5, unit='round trip', route='Out and back', time='3–4 hr', level='Moderate', color='--tC',
      desc='The whole trail. Past Tunnel 5 the path narrows to loose gravel on Bureau of Reclamation land and winds down toward Black Canyon, ending at the top of the Hoover Dam parking garage. The walk back is uphill. Opened all the way to the dam in 2007.', anchors=p.anchors(R['C'])),
]

pa = place_along
A_ = lambda k, f, s=1, o=240: pa(p, UP[k], f, s, o)
an = []
an += [f'{{k:"bighorn",at:{js(A_("C",[.42],1,420)[0])},flock:3}}', f'{{k:"bighorn",path:{js(A_("C",[.62],1,520)[0] + A_("C",[.66],1,520)[0])},per:30}}',
       f'{{k:"bighorn",path:{js(A_("C",[.86],-1,500)[0] + A_("C",[.89],-1,500)[0])},per:34,ph:0.4}}']
an += [f'{{k:"coyote",path:{js(A_("C",[.14],-1,500)[0] + A_("C",[.18],-1,500)[0])},per:24}}']
an += [f'{{k:"turtle",path:{js(A_("C",[.24],-1,300)[0] + A_("C",[.25],-1,300)[0])},per:60}}']
an += [f'{{k:"snake",path:{js(A_("C",[.52],-1,260)[0] + A_("C",[.535],-1,260)[0])},per:30}}', f'{{k:"snake",path:{js(A_("C",[.08],1,300)[0] + A_("C",[.095],1,300)[0])},per:32,ph:0.5}}']
animals_js = '[\n ' + ',\n '.join(an) + '\n]'


def heading(P):
    (x0, n0), (x1, n1) = P[0], P[-1]; return math.atan2(x1 - x0, -(n1 - n0))


portals = []
for i, P in TUN.items():
    portals.append([P[0][0], P[0][1], round(heading(P), 3)]); portals.append([P[-1][0], P[-1][1], round(heading(P), 3)])
s1, s3, c2 = nm['Historic Railroad trailhead'], nm['Concrete plugs'], nm['Hoover Dam parking garage']
lm = """  gate(%(gx)d,%(gn)d,0.3);
  // tunnel portals (OSM tunnel ends), drawn large and facing along the railbed
  %(portals)s.forEach(([x,n,h])=>{const g=new THREE.Group();g.position.copy(G(x,n));g.rotation.y=h;world.add(g);
    part(g,box,"#8A7461",-0.42,0.62,0,0.2,1.3,0.3,1.06);part(g,box,"#8A7461",0.42,0.62,0,0.2,1.3,0.3,1.06);part(g,box,"#8A7461",0,1.32,0,1.04,0.26,0.3,1.06);
    part(g,box,"#221D19",0,0.5,0,0.64,1.0,0.34,0);part(g,new THREE.CylinderGeometry(0.32,0.32,0.34,16),"#221D19",0,1.0,0,1,1,1,0).rotation.x=Math.PI/2;});
  // concrete plugs from Hoover Dam in the ravine before Tunnel 1
  [[0,0],[70,-50],[-60,-80],[30,-120]].forEach(([dx,dn],i)=>{const q=G(%(px)d+dx,%(pn)d-150+dn);part(world,cyl,"#CFC8BA",q.x,q.y+0.15,q.z,0.16,0.3,0.16,1.06);});
  // Lakeview Overlook (OSM) on the cliff above Tunnel 5: shade shelter
  {const q=G(%(lvx)d,%(lvn)d);[[-0.6,-0.6],[0.6,-0.6],[-0.6,0.6],[0.6,0.6]].forEach(([a,b])=>part(world,cyl,"#6B5A4A",q.x+a*0.5,q.y+0.35,q.z+b*0.5,0.04,0.7,0.04,0));part(world,box,"#B9AA92",q.x,q.y+0.72,q.z,0.8,0.1,0.8,1.06);}
  // Hoover Dam: curved concrete arch from the OSM outline, crest about 1,232 ft
  {const P=%(dam)s;let TOPD=1232;P.forEach(q=>{TOPD=Math.max(TOPD,surf(q[0],q[1])+70);});for(let i=0;i<P.length-1;i++){const a=P[i],b=P[i+1];const mx=(a[0]+b[0])/2,mn=(a[1]+b[1])/2;const top=Wv(mx,mn,TOPD),bot=Wv(mx,mn,Math.min(810,surf(mx,mn)-300));const L=Math.hypot(b[0]-a[0],b[1]-a[1])*S;
    const m=part(world,box,"#E3DDD0",top.x,(top.y+bot.y)/2,top.z,L+0.14,top.y-bot.y,0.26,1.04);rot(m,0,Math.atan2(b[1]-a[1],b[0]-a[0]),0);}
    }
  // four intake towers on the lake side (positions from the dam outline)
  %(towers)s.forEach(([x,n])=>{const v=Wv(x,n,Math.min(1206,surf(x,n)));part(world,cyl,"#EDE7DA",v.x,v.y+0.7,v.z,0.22,1.6,0.22,1.06);part(world,cyl,"#C9C1B2",v.x,v.y+1.55,v.z,0.27,0.16,0.27,1.06);});
  // Mike O'Callaghan–Pat Tillman Memorial Bridge (OSM walkway): deck and arch over Black Canyon
  {const a=[%(b0x)d,%(b0n)d],b=[%(b1x)d,%(b1n)d];let DK=%(deck)d;for(let i=0;i<=24;i++){const t=i/24;DK=Math.max(DK,surf(a[0]+(b[0]-a[0])*t,a[1]+(b[1]-a[1])*t)+60);}const A=Wv(a[0],a[1],DK),B=Wv(b[0],b[1],DK);const L=A.distanceTo(B),ang=Math.atan2(b[1]-a[1],b[0]-a[0]);
    const d=part(world,box,"#D8D3CA",(A.x+B.x)/2,A.y,(A.z+B.z)/2,L,0.35,1.0,1.04);rot(d,0,ang,0);
    const N=16;for(let i=0;i<=N;i++){const t=i/N,x=a[0]+(b[0]-a[0])*(0.1+0.8*t),n=a[1]+(b[1]-a[1])*(0.1+0.8*t);const y=DK-330+290*(1-Math.pow(2*t-1,2));if(y<surf(x,n))continue;const v=Wv(x,n,y);rot(part(world,box,"#C9C3B8",v.x,v.y,v.z,0.8,0.55,0.9,1.04),0,ang,0);}}
""" % dict(gx=s1['x'] + 60, gn=s1['n'] - 60, portals=js(portals), px=s3['x'], pn=s3['n'], lvx=LV[0], lvn=LV[1], dam=js(DAMPTS), rz=int(RIV_Z),
           towers=js(TOWERS), deck=DECK, b0x=B0[0], b0n=B0[1], b1x=B1[0], b1n=B1[1])
RBP = {}
for k in R:
    E = railbed(R[k]); kk = np.ones(31) / 31; E = np.convolve(np.pad(E, 15, mode='edge'), kk, mode='valid'); E = np.minimum(E, 1600); c = R[k]['cum']; out = []; last = -1e9
    for i in range(len(E)):
        if c[i] - last >= 150 or i == len(E) - 1: out.append([round(c[i] / 5280, 3), round(float(E[i]))]); last = c[i]
    RBP[k] = out
extra_js = '''
TRAILS.forEach(T=>{const s=%s[T.id];if(s){T.gain=s.gain;T.hi=s.hi;T.lo=s.lo;}});
// elevation profile: the railbed through the tunnels, not the ridge above them
(function(){const RB=%s;TRAILS.forEach(T=>{const L=RB[T.id];if(!L)return;T.pts.forEach(p=>{let k=1;while(k<L.length-1&&L[k][0]<p.m)k++;const a=L[k-1],b=L[k];const t=Math.max(0,Math.min(1,(p.m-a[0])/((b[0]-a[0])||1)));p.e=a[1]+(b[1]-a[1])*t;});});})();
// out-and-back: report the outbound mile for a stop
mileOf=function(T,x,n){let b=null;T.pts.forEach(p=>{const d=Math.hypot(p.x-x,p.n-n);if(!b||d<b.d)b={d,m:p.m,e:p.e};});if(!b||b.d>=260)return null;const f=T.pts.find(p=>Math.hypot(p.x-x,p.n-n)<b.d+60);return {d:b.d,m:f.m,e:f.e};};
function lakeP(){return lakeP.c||(lakeP.c=%s);}
function riverP(){return riverP.c||(riverP.c=%s);}
function inPoly(P,x,n){let c=false;for(let i=0,j=P.length-1;i<P.length;j=i++){const a=P[i],b=P[j];if((a[1]>n)!==(b[1]>n)&&x<(b[0]-a[0])*(n-a[1])/(b[1]-a[1])+a[0])c=!c;}return c;}
function inLake(x,n){return lakeP().some(P=>inPoly(P,x,n))||riverP().some(P=>inPoly(P,x,n));}
(function(){const mat=new THREE.MeshLambertMaterial({color:"#5FA9C4",side:THREE.DoubleSide});const edge=new THREE.LineBasicMaterial({color:"#3F8AA6"});
  const v2=P=>P.map(([x,n])=>new THREE.Vector2(x,n));
  [[lakeP(),%d],[riverP(),%d]].forEach(([L,w0])=>L.forEach(P=>{const geo=new THREE.ShapeGeometry(new THREE.Shape(v2(P)));const pa=geo.attributes.position;
    for(let i=0;i<pa.count;i++){const x=pa.getX(i),n=pa.getY(i);const v=Wv(x,n,Math.min(w0,surf(x,n)+2));pa.setXYZ(i,v.x,v.y,v.z);}
    pa.needsUpdate=true;geo.computeVertexNormals();const m=new THREE.Mesh(geo,mat);m.renderOrder=1;world.add(m);}));
})();
''' % (js(STAT), js(RBP), js(LAKE), js(RIVER), int(LAKE_Z) + 3, int(RIV_Z))

species_extra = {
 'creosote': 'creosote:{name:"Creosote bush",latin:"Larrea tridentata",color:"#F0D23A",shape:"dome",bloom:[3,4,5],sum:"The most common shrub along the trail: small, waxy dark-green leaves and little yellow flowers in spring, then fuzzy white seed balls. After rain the desert smells of it.",rule:(d,e,g,s)=>e>1215&&g<0.8}',
 'brittlebush': 'brittlebush:{name:"Brittlebush",latin:"Encelia farinosa",color:"#F2C230",shape:"dome",bloom:[2,3,4],sum:"A rounded, silver-leaved shrub that turns the hills along Lakeshore Road yellow with daisies in early spring.",rule:(d,e,g,s)=>e>1215&&s>-0.2&&g<0.7}',
 'globemallow': 'globemallow:{name:"Desert globemallow",latin:"Sphaeralcea ambigua",color:"#E8743B",shape:"cup",bloom:[3,4,5],sum:"A gray-green shrub with cups of apricot-orange flowers in spring, along washes and trail edges across the park.",rule:(d,e,g,s)=>e>1215&&g<0.5}',
 'beavertail': 'beavertail:{name:"Beavertail cactus",latin:"Opuntia basilaris",color:"#D9418C",shape:"pad",bloom:[3,4,5],sum:"Flat blue-gray pads without big spines (the tiny bristles still hurt) and bright magenta flowers in spring, common along Lakeshore Road.",rule:(d,e,g,s)=>e>1215&&g<0.8}',
 'azlupine': 'azlupine:{name:"Arizona lupine",latin:"Lupinus arizonicus",color:"#B05FC2",shape:"spike",bloom:[2,3,4],sum:"Spikes of pink-purple pea flowers on sandy ground and road edges after wet winters, around the Boulder City entrance of the park.",rule:(d,e,g,s)=>e>1215&&d>100&&g<0.4}',
}
tree_rule = 'if(inLake(x,n)||mk<0.25||g>0.9||e<1215){type=null;}else{type="shrub";p=0.02+cl*.02;}'

# ---- photos: this park's, plus species photos already on the site (meta read from their pages)
MD = json.load(open('/mnt/files/gtb/photos/tunnels/photos_meta.json')) if os.path.exists('/mnt/files/gtb/photos/tunnels/photos_meta.json') else {}
MM = {m['f'].split('/')[-1][:-4]: m for v in MD.values() for m in v}
SPM = {}
for f in glob.glob('/home/claude/site/out/*/index.html'):
    for m in re.findall(r'\{"f":"\.\./photos/sp_[^}]*\}', open(f, errors='ignore').read()):
        try:
            d = json.loads(m); SPM.setdefault(d['f'].split('/')[-1][:-4], d)
        except Exception: pass
KEEP = json.load(open('tunnels/keep.json')) if os.path.exists('tunnels/keep.json') else {}
def ph(fs): return [dict(MM[f]) for f in fs if f in MM]
def sp(fs): return [dict(MM.get(f) or SPM[f]) for f in fs if f in MM or f in SPM]
stop_photos = {nm[k]['id']: ph(v) for k, v in KEEP.get('stops', {}).items() if k in nm and ph(v)}
flower_photos = {k: sp(v) for k, v in KEEP.get('flowers', {}).items() if sp(v)}
animal_photos = {k: sp(v) for k, v in KEEP.get('animals', {}).items() if sp(v)}
print('photos', {k: len(v) for k, v in stop_photos.items()}, {k: len(v) for k, v in {**flower_photos, **animal_photos}.items()})

cfg = dict(
    title='Historic Railroad Trail', aria='the Historic Railroad Trail and its five tunnels between Lake Mead and Hoover Dam', h1='Historic Railroad Trail · Lake Mead',
    canyons=[], trails=trails, stops=stops, order=order,
    species=['creosote', 'brittlebush', 'globemallow', 'beavertail', 'azlupine'], species_extra=species_extra,
    flora={'A': ['creosote', 'brittlebush', 'beavertail', 'azlupine'], 'B': ['creosote', 'brittlebush', 'globemallow', 'beavertail'], 'C': ['creosote', 'globemallow', 'brittlebush', 'beavertail']},
    wild=['bighorn', 'coyote', 'turtle', 'snake', 'raven', 'peregrine', 'eagle'],
    wild_sum={'bighorn': ('Desert bighorn sheep', 'The animal most people hope to see here. Bands of bighorn live in the River Mountains and are often spotted on the slopes and ledges above the tunnels. Keep your distance and keep dogs leashed.'),
              'coyote': ('Coyote', 'A lean gray-tan wild dog that hunts the desert flats and washes, most active at dawn and dusk.'),
              'turtle': ('Desert tortoise', 'Nevada’s state reptile and a threatened species, living up to 50 years in burrows on the desert flats. Mostly out after spring rains. Never pick one up: a frightened tortoise can lose the water it stores.'),
              'snake': ('Rattlesnake', 'Four species of rattlesnake live in the park, all dangerously venomous. They are most active on warm spring and fall days and summer nights; watch where you step off the railbed.'),
              'raven': ('Common raven', 'Big black birds that ride the updrafts along the cliffs and patrol the parking lots. They also prey on young desert tortoises.'),
              'peregrine': ('Peregrine falcon', 'Nests on the cliffs of Black Canyon and dives at great speed after swifts and pigeons around Hoover Dam.'),
              'eagle': ('Bald eagle', 'A winter visitor to Lake Mead, fishing the open water of the lake from November to March.')},
    grid=GRID, step=STEP, dem_b64=b64, tile=TILE, ve=1.6, ridge_ft=RIDGE,
    palette={"ground": "#EDE0C6", "groundN": "#E2D3B6", "rock": "#A88E78", "rockDeep": "#8C735F", "ridge": "#E9DCC4", "oak": "#6F8A55", "shrub": "#9FA06E"},
    tree_rule=tree_rule, rock_all_aspects=True,
    landmarks=lm, animals_js=animals_js, extra_js=extra_js,
    zoomcap={'A': 4.2, 'B': 3.4, 'C': 2.6},
    overview=dict(h2='Five tunnels from Lake Mead to Hoover Dam',
                  p='In 1931 the government and Six Companies built a railroad to carry cement, gravel and machinery to Hoover Dam. The tracks came up in 1962; the railbed is now a wide gravel trail along the River Mountains above Boulder Basin of Lake Mead, through five tunnels, each 25 ft wide. A walks to the first tunnel, B goes through all five, and C continues down to Hoover Dam. Pick a trail to focus the model; click anything on it for a quick note.',
                  numbers='All three trails start from the same lot and follow the same railbed, so shared stops carry plain numbers (1 to 8, in the order you reach them). Lettered stops are on Trail C only.',
                  wild_h='Wildlife along the railbed',
                  note='Historic Railroad Trail, Lakeshore Road near the Lake Mead Visitor Center, Boulder City, Nevada (Lake Mead National Recreation Area). Open; the trail is in a fee area: $25 per private vehicle for 7 days, or an annual pass; keep proof of payment in the car. Leashed pets allowed (6 ft leash max); the gravel can reach about 135°F when the air is 85°F. Summer highs of 100–115°F: not recommended in summer; go early. Pit toilets at the trailhead, water at the visitor center; the last 1.5 miles to the dam are Bureau of Reclamation land. Lake levels change and the water on the model follows older elevation data. Terrain from USGS elevation data, stylized; not for navigation.'),
    links={'A': [('Historic Railroad Trail · NPS', 'https://www.nps.gov/thingstodo/hike-the-historic-railroad-trail.htm'), ('Historic Railroad Tunnel · NPS', 'https://www.nps.gov/lake/learn/historic-railroad-tunnel.htm')],
           'B': [('Railroad Tunnels Trail · Bird & Hike', 'https://birdandhike.com/Hike/LAME/Railroad/_Railroad.htm'), ('Historic Railroad Trail · TrailLink', 'https://www.traillink.com/trail/historic-railroad-trail/')],
           'C': [('Historic RR Tunnels, Hoover Dam & Bridge · Hiking Project', 'https://www.hikingproject.com/trail/7010999/historic-rr-tunnels-hoover-dam-bridge'), ('Lake Mead hikes · NPS (PDF)', 'https://www.nps.gov/lake/planyourvisit/upload/Lake-Mead-Hikes-3_22_2018.pdf')]},
    viewaz={'all': 0.35, 'A': 0.35, 'B': 0.35, 'C': 0.35},
    stop_photos=stop_photos, flower_photos=flower_photos, animal_photos=animal_photos,
)
json.dump({k: {'mi': R[k]['mi'], **STAT[k]} for k in R}, open('tunnels/stats.json', 'w'))
os.makedirs('/home/claude/site/out/lake-mead-railroad-tunnels', exist_ok=True)
print(build(cfg, '/home/claude/site/out/lake-mead-railroad-tunnels/index.html'))
