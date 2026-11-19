from lib import *
from mk_sheet import build
import sys, json, math, os
import numpy as np

p = Park('deltalake', 43.713, -110.75)

TH = (4487, -7229)      # Taggart Lake Trailhead (start of OSM Taggart Lake Trail way 207798528; vault toilets node)
LTH = (2247, 7903)      # Lupine Meadows Trailhead (start of OSM Garnet Canyon Trail way 284022153; vault toilet node)
BRJ = (1573, -3954)     # Bradley / Taggart split (OSM way junction)
TGJ = (-390, -4432)     # Taggart Lake shore, Valley Trail junction (OSM)
NARROWS = (-640, -4858) # Valley Trail footbridge over the narrows of Taggart Lake (OSM Valley Trail, between the lake and its south lobe)
BCJ = (-1268, -7041)    # Valley Trail / Beaver Creek junction (OSM)
BRV = (-453, -244)      # OSM viewpoint "Bradley Lake"
TGV = (-45, -2863)      # OSM viewpoint above Taggart Lake on the moraine trail
VJ = (-1768, 4806)      # Garnet Canyon Trail / Valley Trail junction (OSM)
GCJ = (-3999, 4804)     # Garnet Canyon / Surprise-Amphitheater split (OSM)
DTO = (-4017, 5543)     # start of OSM "Delta Lake Trail" (unmarked turnoff)
DLK = (-5725, 7099)     # end of the Delta Lake Trail at the lake (OSM)


def mkroute(pts):
    E = [p.elev(*q) for q in pts]
    cum = [0.0]
    for i in range(1, len(pts)): cum.append(cum[-1] + math.dist(pts[i - 1], pts[i]))
    gain = sum(max(0, E[i] - E[i - 1]) for i in range(1, len(E)))
    return dict(pts=pts, E=E, cum=cum, segs=[], gain=gain, mi=cum[-1] / 5280, lo=min(E), hi=max(E))


def out_back(r):
    pts = r['pts'] + r['pts'][-2::-1]; r2 = mkroute(pts); r2['segs'] = r['segs']; return r2


AV = ('track', 'path', 'footway', 'Pathways', 'Horse', 'cycleway')
A = route_xy(p, TH, (2448, -4827), (-565, -4631), (-1029, -6322), (757, -8483), TH, avoid=AV)
B = route_xy(p, TH, (2448, -4827), (1043, -3020), BRV, (95, -2444), (623, -3762), TH, avoid=AV)
up_C = route_xy(p, LTH, (1364, 4061), (-3125, 4465), (-4910, 6519), DLK, avoid=AV)
R = {'A': A, 'B': B, 'C': out_back(up_C)}
UP = {'A': A, 'B': B, 'C': up_C}
for k in R: Park.smooth_E(R[k], 9); p.describe(R[k], k)
p.describe(up_C, 'C up')
OUTB = {'A': len(A['pts']), 'B': len(B['pts']), 'C': len(up_C['pts'])}


def M(k, mi): return tuple(p.at_mile(UP[k], mi)[0])


# boulder field: the point of the Delta Lake Trail that crosses OSM scree / bare rock, else 60 % along the spur
def boulder_pt():
    Pd = [p.xy(q) for q in p.WID['388158256']['p']]
    rocks = [w for w in p.W if w['k'] in ('scree', 'bare_rock')]
    def inside(P, x, n):
        c = False
        for i in range(len(P)):
            a, b = P[i], P[i - 1]
            if (a[1] > n) != (b[1] > n) and x < (b[0] - a[0]) * (n - a[1]) / (b[1] - a[1]) + a[0]: c = not c
        return c
    polys = [[p.xy(q) for q in w['p']] for w in rocks]
    hits = [q for q in Pd if any(inside(P, *q) for P in polys)]
    print('delta trail points in scree/bare rock:', len(hits), 'of', len(Pd))
    if hits: return hits[len(hits) // 2]
    return Pd[int(len(Pd) * 0.6)]
BLD = tuple(round(v) for v in boulder_pt())

ST = snap_stops(p, R, {
    'S1': (*TH, 'AB'), 'S2': (3670, -5875, 'AB'), 'S3': (*M('B', 0.9), 'AB'), 'S4': (*BRJ, 'AB'), 'S5': (*TGJ, 'AB'),
    'A1': (*NARROWS, 'A'), 'A2': (*BCJ, 'A'), 'A3': (*M('A', 3.0), 'A'),
    'B1': (*BRV, 'B'), 'B2': (*TGV, 'B'),
    'C1': (*LTH, 'C'), 'C2': (*M('C', 1.3), 'C'), 'C3': (*VJ, 'C'), 'C4': (*M('C', 2.4), 'C'), 'C5': (*GCJ, 'C'),
    'C6': (*DTO, 'C'), 'C7': (*BLD, 'C'), 'C8': (*DLK, 'C'),
})
TILE = (-11000, 9000, -12800, 12300)
GRID = (-11400, 9400, -13200, 12700)
STEP = 125
if 'plot' in sys.argv:
    from plot import plot
    plot(p, TILE, '/home/claude/parks/deltalake/routes.png', routes=R, stops=ST, title='deltalake', grid=1000)
    plot(p, (-7000, 3000, 3000, 9000), '/home/claude/parks/deltalake/routes_c.png', routes=R, stops=ST, title='deltalake C', grid=500)
    plot(p, (-3500, 5500, -9500, 2000), '/home/claude/parks/deltalake/routes_ab.png', routes=R, stops=ST, title='deltalake AB', grid=500)
    for k in R: print(k, 'mi', round(R[k]['mi'], 2), 'gain', round(R[k]['gain']), 'hi', round(R[k]['hi']))
    for k, v in ST.items(): print('stop', k, v)
    sys.exit()
b64, NX, NN = p.dem_b64(*GRID, STEP=STEP)
print('grid', NX, NN, NX * NN, p.grid.min(), p.grid.max(), 'p75', np.percentile(p.grid, 75))
band = 0.2 * min(TILE[1] - TILE[0], TILE[3] - TILE[2])
def clear(x, n): return min(x - TILE[0], TILE[1] - x, n - TILE[2], TILE[3] - n) - band
for kk in R: print('trail', kk, 'band clearance', round(min(clear(*q) for q in R[kk]['pts'])))

S = lambda i: ST[i]
def stop(key, trails, name, desc): return dict(id=key, trails=list(trails), x=S(key)[0], n=S(key)[1], name=name, desc=desc)
stops = [
 stop('S1', 'AB', 'Taggart Lake Trailhead', 'On Teton Park Road about 2.3 miles north of the Moose Entrance Station, at about 6,625 ft. The lot fills early in summer. The trailhead is being rebuilt with a larger lot, restrooms and a water station; it closes to all use from May 1, 2027 until the work is done.'),
 stop('S2', 'AB', 'Taggart Creek footbridge', 'About 0.4 mile in, a footbridge crosses Taggart Creek, with a small waterfall just upstream. The NPS horse corrals are nearby; from here the trail climbs through spruce, fir, lodgepole pine and aspen.'),
 stop('S3', 'AB', 'Beaver Creek Fire burn', 'About a mile in, the trail enters ground burned by the lightning-caused 1985 Beaver Creek Fire, which covered more than 1,000 acres. Young aspen and lodgepole now grow among the snags, and the open slopes give wide views of the range.'),
 stop('S4', 'AB', 'Bradley Lake split', 'A signed fork about 1.1 miles in on a glacial moraine. Left goes straight to Taggart Lake (Trail A); right climbs to Bradley Lake (Trail B).'),
 stop('S5', 'AB', 'Taggart Lake shore', 'The trail meets the Valley Trail at the lakeshore, about 6,900 ft. Across the water rise Middle Teton, the Grand Teton, Mount Owen and Teewinot, with Avalanche Canyon behind the lake. Taggart Lake covers about 305 acres and is named for William Rush Taggart of the 1872 Hayden Survey.'),
 stop('A1', 'A', 'Taggart Lake narrows bridge', 'The Valley Trail crosses a footbridge over a narrow neck of the lake, then climbs a short, fairly steep glacial moraine with views south over Jackson Hole.'),
 stop('A2', 'A', 'Beaver Creek junction', 'About 2.4 miles in, the loop leaves the Valley Trail and turns east down the Beaver Creek drainage.'),
 stop('A3', 'A', 'Beaver Creek', 'The return follows Beaver Creek through forest and willows. Watch for moose in the willows, and for elk, deer and black bears.'),
 stop('B1', 'B', 'Bradley Lake', 'Bradley Lake, about 225 acres, is the smallest of the chain of lakes at the foot of the range. Garnet Canyon creek feeds it from the glaciers on Middle Teton. It is named for Frank Bradley, chief geologist of the 1872 Hayden Survey; Nez Perce, Middle Teton and Teewinot rise above it.'),
 stop('B2', 'B', 'Moraine above Taggart Lake', 'The Valley Trail climbs over the moraine between the two lakes, through huckleberry patches, with views down onto Taggart Lake about 200 ft below.'),
 stop('C1', 'C', 'Lupine Meadows Trailhead', 'At the end of the 1.5-mile gravel Lupine Meadows Road, about 6,730 ft. Vault toilet and bear boxes; the lot fills around sunrise in summer. Teton Park Road is closed to cars here from November 1 to April 30.'),
 stop('C2', 'C', 'Ridge above Glacier Gulch', 'About 1.3 miles in the trail runs along a narrow moraine ridge, with Burned Wagon Gulch on the left and Glacier Gulch on the right.'),
 stop('C3', 'C', 'Valley Trail junction', 'Just over 1.7 miles in. Left goes down to Bradley and Taggart lakes; straight on starts the long switchbacks toward Garnet Canyon and Amphitheater Lake.'),
 stop('C4', 'C', 'Switchbacks over the lakes', 'The trail climbs about 1,100 ft in six long, sunny switchbacks. Bradley and Taggart lakes and Jackson Hole open up below.'),
 stop('C5', 'C', 'Garnet Canyon junction', 'About 3 miles in, the Garnet Canyon Trail branches left toward the Lower Saddle climbing route. Stay on the switchbacks toward Surprise and Amphitheater lakes.'),
 stop('C6', 'C', 'Unmarked Delta Lake turnoff', 'One switchback past the Garnet Canyon junction, an unmarked, steep dirt path leaves the maintained trail to the north. From here to the lake is an unofficial route that the park does not maintain as a trail.'),
 stop('C7', 'C', 'Boulder fields', 'The route climbs over and under downed trees, then crosses two large boulder fields marked by cairns. At the second, many hikers drift uphill onto a ridge; the route heads across toward the trees. Access Fund and park crews worked on wayfinding and erosion here in summer 2026.'),
 stop('C8', 'C', 'Delta Lake', 'A small glacial lake at 9,016 ft in Glacier Gulch, under the east face of the Grand Teton with Mount Owen and Teewinot alongside. Silt from the Teton Glacier turns the water turquoise. The last pitch below it is steep, loose dirt; the descent is often harder than the climb.'),
]
for st in stops:
    t = st['trails'][0]
    P = np.array(R[t]['pts'][:OUTB[t]]); j = int(np.argmin(np.hypot(P[:, 0] - st['x'], P[:, 1] - st['n'])))
    st['x'], st['n'] = round(P[j, 0]), round(P[j, 1])
stops, order = renumber(p, R, stops)
for s0 in stops: print(s0['id'], s0['name'], {t: p.mile_of(R[t], s0['x'], s0['n'])[:2] for t in s0['trails']})
SID = {s0['name']: s0['id'] for s0 in stops}
def SS(nm):
    s0 = next(s for s in stops if s['name'] == nm); return (s0['x'], s0['n'])

trails = [
 dict(id='A', name='Taggart Lake–Beaver Creek Loop', short='Taggart Lake', official=3.8, unit='loop', route='Loop', time='2–3 hr', level='Easy', color='--tA',
      desc='From the Taggart Lake Trailhead the trail crosses Taggart Creek and climbs an aspen-covered moraine through the 1985 Beaver Creek Fire burn to the shore of Taggart Lake. The loop turns south on the Valley Trail, crosses a footbridge over the lake, climbs over a moraine and returns along Beaver Creek. Rocks, roots and a few stairs.', anchors=p.anchors(R['A'])),
 dict(id='B', name='Taggart & Bradley Lakes Loop', short='Bradley Lake', official=5.6, unit='loop', route='Loop', time='2–3 hr', level='Moderate', color='--tB',
      desc='Up the same moraine, then right at the split to Bradley Lake. The Valley Trail climbs back over the moraine between the two lakes and drops to Taggart Lake before the walk out. The trail gains and loses height several times and is narrow and brushy in places.', anchors=p.anchors(R['B'])),
 dict(id='C', name='Delta Lake', short='Delta Lake', official=7.4, unit='round trip', route='Out and back', time='4–6 hr', level='Strenuous', color='--tC',
      desc='From Lupine Meadows the trail climbs a moraine to the Valley Trail junction, then switchbacks up the mountainside above Bradley and Taggart lakes. Past the Garnet Canyon junction an unmarked turnoff leaves the maintained trail: the last mile is an unofficial route over downed trees, two boulder fields and a steep, loose climb up Glacier Gulch to the turquoise lake under the Grand Teton. Route-finding needed; turn back in snow or storms.', anchors=p.anchors(R['C'])),
]
GAIN = {'A': 620, 'B': 860, 'C': 2300}

# --- water (OSM polygons, clipped to the tile)
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
inset = (TILE[0] + 300, TILE[1] - 300, TILE[2] + 300, TILE[3] - 300)
lakes, delta = [], []
for w in p.W:
    if w['k'] != 'water': continue
    P = [p.xy(q) for q in w['p']]
    if len(P) < 4 or P[0] != P[-1]: continue
    P = clip(P[:-1], inset)
    if len(P) < 3: continue
    poly = [[round(x), round(n)] for x, n in P]
    (delta if w['id'] == '284022148' else lakes).append(poly)
print('lakes', len(lakes), 'delta', len(delta))

extra_js = '''
TRAILS.forEach(T=>{const g=%s[T.id];if(g)T.gain=g;});
// stems walked twice (B, C): report the outbound mile for a stop
mileOf=(function(old){return function(T,x,n){let b=null;T.pts.forEach(p=>{const d=Math.hypot(p.x-x,p.n-n);if(!b||d<b.d)b={d,m:p.m,e:p.e};});if(!b||b.d>=260)return null;const f=T.pts.find(p=>Math.hypot(p.x-x,p.n-n)<b.d+60);return {d:b.d,m:f.m,e:f.e};};})(mileOf);
function lakeP(){return lakeP.c||(lakeP.c=%s);}
function deltaP(){return deltaP.c||(deltaP.c=%s);}
function inPoly(L,x,n){for(const P of L){let c=false;for(let i=0,j=P.length-1;i<P.length;j=i++){const a=P[i],b=P[j];if((a[1]>n)!==(b[1]>n)&&x<(b[0]-a[0])*(n-a[1])/(b[1]-a[1])+a[0])c=!c;}if(c)return true;}return false;}
function inLake(x,n){return inPoly(lakeP(),x,n)||inPoly(deltaP(),x,n);}
(function(){
  function draw(L,col,ed){const mat=new THREE.MeshLambertMaterial({color:col,side:THREE.DoubleSide});const edge=new THREE.LineBasicMaterial({color:ed});
  L.forEach(P=>{const sh=new THREE.Shape(P.map(([x,n])=>new THREE.Vector2(x,n)));const geo=new THREE.ShapeGeometry(sh);const pa=geo.attributes.position;
    for(let i=0;i<pa.count;i++){const x=pa.getX(i),n=pa.getY(i);const v=G(x,n,0.12);pa.setXYZ(i,v.x,v.y,v.z);}
    pa.needsUpdate=true;geo.computeVertexNormals();const m=new THREE.Mesh(geo,mat);m.renderOrder=1;world.add(m);
    const ring=P.concat([P[0]]).map(([x,n])=>G(x,n,0.14));world.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints(ring),edge));});}
  draw(lakeP(),"#8FC6DA","#5E9FB8");draw(deltaP(),"#3FC1C0","#1E9A9C");
})();
''' % (js(GAIN), js(lakes), js(delta))

s1, s2, s4, a1 = SS('Taggart Lake Trailhead'), SS('Taggart Creek footbridge'), SS('Bradley Lake split'), SS('Taggart Lake narrows bridge')
c1, c6, c7, c8 = SS('Lupine Meadows Trailhead'), SS('Unmarked Delta Lake turnoff'), SS('Boulder fields'), SS('Delta Lake')
DC = [round(sum(q[0] for q in delta[0]) / len(delta[0])), round(sum(q[1] for q in delta[0]) / len(delta[0]))] if delta else list(DLK)
lm = f'''  gate({s1[0] - 80},{s1[1] + 60},0.9);gate({c1[0] - 60},{c1[1] - 60},2.6);
  // trailhead signs (exaggerated, solid)
  [[{s1[0] - 260},{s1[1] + 120}],[{c1[0] - 200},{c1[1] - 160}]].forEach(([x,n])=>{{const q=G(x,n);part(world,cyl,"#6B4F3A",q.x-0.35,q.y+0.6,q.z,0.08,1.2,0.08);part(world,cyl,"#6B4F3A",q.x+0.35,q.y+0.6,q.z,0.08,1.2,0.08);part(world,box,"#7A5A3C",q.x,q.y+1.15,q.z,1.2,0.5,0.14,1.06);}});
  // footbridges: Taggart Creek and the narrows of Taggart Lake
  [[{s2[0]},{s2[1]},0.3],[{a1[0]},{a1[1]},1.45]].forEach(([x,n,r])=>{{const q=G(x,n,0.15);const g=new THREE.Group();g.position.copy(q);g.rotation.y=r;world.add(g);
    part(g,box,"#9C7653",0,0.12,0,1.8,0.14,0.5,1.06);part(g,box,"#7A5A3C",0,0.4,0.25,1.8,0.08,0.06,1.06);part(g,box,"#7A5A3C",0,0.4,-0.25,1.8,0.08,0.06,1.06);
    [-0.85,0,0.85].forEach(z=>{{part(g,box,"#6B4F3A",z,0.26,0.25,0.07,0.32,0.07);part(g,box,"#6B4F3A",z,0.26,-0.25,0.07,0.32,0.07);}});}});
  // signpost at the Bradley Lake split
  {{const q=G({s4[0] + 60},{s4[1] + 40});part(world,cyl,"#6B4F3A",q.x,q.y+0.6,q.z,0.08,1.2,0.08);part(world,box,"#8A6A4A",q.x+0.25,q.y+1.05,q.z,0.75,0.24,0.08,1.06);part(world,box,"#8A6A4A",q.x-0.2,q.y+0.78,q.z,0.7,0.22,0.08,1.06);}}
  // unmarked turnoff: a small cairn
  {{const q=G({c6[0] - 60},{c6[1] + 40});[[0.42,0.22],[0.33,0.2],[0.24,0.18],[0.15,0.16]].forEach(([r,h],i)=>part(world,ico,i%2?PAL.stone:PAL.stoneD,q.x,q.y+0.16+i*0.3,q.z,r*1.2,h*1.2,r*1.2));}}
  // boulder fields with cairns
  {{const q0=G({c7[0]},{c7[1]});[[-260,-120,1.0],[-120,180,0.8],[160,-60,1.1],[300,160,0.7],[40,320,0.9],[-380,140,0.75],[220,-260,0.85]].forEach(([dx,dn,s])=>rock({c7[0]}+dx,{c7[1]}+dn,s));
   [[60,40],[-180,260]].forEach(([dx,dn])=>{{const q=G({c7[0]}+dx,{c7[1]}+dn);[[0.4,0.22],[0.32,0.2],[0.24,0.18],[0.16,0.16]].forEach(([r,h],i)=>part(world,ico,i%2?PAL.stone:PAL.stoneD,q.x,q.y+0.16+i*0.3,q.z,r*1.2,h*1.2,r*1.2));}});}}
  // Delta Lake: a few big glacial boulders on the shore
  rock({DC[0] - 420},{DC[1] - 260},1.2);rock({DC[0] + 380},{DC[1] - 300},1.0);
'''

# --- wildlife
pa = place_along
def Aat(k, f, s=1, o=240):
    r = UP[k] if k == 'C' else R[k]
    return pa(p, r, [f], s, o)[0]
an = []
an += [f'{{k:"moose",path:{js(Aat("A",.80,-1,260)+Aat("A",.82,-1,260))},per:40}}', f'{{k:"moose",path:{js(Aat("B",.37,1,300)+Aat("B",.39,1,300))},per:44,ph:0.4}}']
an += [f'{{k:"bear",path:{js(Aat("B",.56,-1,260)+Aat("B",.58,-1,260))},per:30}}', f'{{k:"bear",path:{js(Aat("C",.52,1,260)+Aat("C",.54,1,260))},per:32,ph:0.5}}']
an += [f'{{k:"grizzly",path:{js(Aat("C",.10,1,320)+Aat("C",.13,1,320))},per:36}}']
an += [f'{{k:"elk",path:{js(Aat("A",.20,1,320)+Aat("A",.22,1,320))},per:38}}']
an += [f'{{k:"deer",path:{js(Aat("A",.93,1,300)+Aat("A",.95,1,300))},per:30}}', f'{{k:"deer",path:{js(Aat("C",.30,-1,260)+Aat("C",.32,-1,260))},per:28,ph:0.3}}']
an += [f'{{k:"beaver",at:{js(Aat("A",.47,-1,200))}}}']
an += [f'{{k:"fox",path:{js(Aat("B",.10,-1,260)+Aat("B",.12,-1,260))},per:26}}']
an += [f'{{k:"squirrel",at:{js(Aat("B",.40,1,160))}}}']
an += [f'{{k:"chipmunk",at:{js(Aat("C",.80,-1,150))},hop:true}}']
an += [f'{{k:"marmot",at:{js(Aat("C",.90,1,180))}}}', f'{{k:"marmot",at:{js(Aat("C",.48,-1,180))}}}']
an += [f'{{k:"pika",at:{js(Aat("C",.86,-1,140))},hop:true}}']
animals_js = '[\n ' + ',\n '.join(an) + '\n]'

species_extra = {
 'balsamroot_dl': 'balsamroot_dl:{name:"Arrowleaf balsamroot",latin:"Balsamorhiza sagittata",color:"#F2C230",shape:"dome",bloom:[6,7],sum:"Big yellow sunflower heads over silvery, arrow-shaped leaves. Covers the dry, rocky valley floor and sunny moraine slopes near the trailheads in June.",rule:(d,e,g,s)=>g>0.03&&g<0.7&&e<7300&&s>-0.2&&d>120}',
 'lupine_dl': 'lupine_dl:{name:"Silky lupine",latin:"Lupinus sericeus",color:"#7B6FD6",shape:"spike",bloom:[6,7],sum:"Purple-blue pea flowers over silvery, hand-shaped leaves, common in the valley in June and July and often mixed with balsamroot.",rule:(d,e,g,s)=>g>0.03&&g<0.6&&e<7400&&d>150}',
 'geranium_dl': 'geranium_dl:{name:"Sticky geranium",latin:"Geranium viscosissimum",color:"#D9659B",shape:"cup",bloom:[6,7,8],sum:"Five-petaled pink-magenta flowers with dark veins, along the trail edges and in aspen openings on the moraines.",rule:(d,e,g,s)=>g>0.03&&e<7800&&d>80}',
 'paintbrush_dl': 'paintbrush_dl:{name:"Indian paintbrush",latin:"Castilleja spp.",color:"#E0452E",shape:"spike",bloom:[6,7,8],sum:"Red to orange bracts on short stems, in the valley in June and July and higher in the canyons into August. Wyoming paintbrush is the state flower.",rule:(d,e,g,s)=>g>0.03&&g<0.9&&d>100}',
 'columbine_dl': 'columbine_dl:{name:"Colorado columbine",latin:"Aquilegia coerulea",color:"#C9D3F2",shape:"cup",bloom:[6,7,8],sum:"Large spurred flowers, mostly white here with a blue tinge, in moist, shady spots and rock gardens of the canyons from late June.",rule:(d,e,g,s)=>g>0.03&&e>7300&&s<0.1&&d<1200}',
 'huckleberry_dl': 'huckleberry_dl:{name:"Huckleberry",latin:"Vaccinium membranaceum",color:"#3E3A6E",shape:"berry",bloom:[6],fruit:[8,9],sum:"A knee-high shrub of the lodgepole forest. Patches line the moraine between Taggart and Bradley lakes; the purple berries ripen in August and draw bears.",rule:(d,e,g,s)=>g>0.03&&e<8800&&d>60}',
 'fireweed_dl': 'fireweed_dl:{name:"Fireweed",latin:"Chamaenerion angustifolium",color:"#D2449A",shape:"spike",bloom:[7,8],sum:"Tall magenta spikes from mid July, quick to move into burned and disturbed ground.",rule:(d,e,g,s)=>g>0.03&&e<9200&&d>100}',
}

PH = {}
if os.path.exists('/home/claude/parks/deltalake/photos_cfg.json'): PH = json.load(open('/home/claude/parks/deltalake/photos_cfg.json'))
stop_photos = {SID[k]: v for k, v in PH.get('stops', {}).items() if k in SID}
flower_photos = PH.get('flowers', {})
animal_photos = PH.get('animals', {})

from fauna import TREE_RULES
RARE_GRIZ = 'Rare here: grizzly bears are listed as threatened in the lower 48 states, and they are regularly active around Lupine Meadows and on the trail to Delta Lake. Hike in a group, make noise, especially on the off-trail stretch, and carry bear spray you know how to use.'
cfg = dict(
    title='Taggart Lake & Delta Lake', aria='Taggart Lake, Bradley Lake and Delta Lake in Grand Teton National Park', h1='Taggart Lake &amp; Delta Lake',
    canyons=None, trails=trails, stops=stops, order=order,
    species=list(species_extra), species_extra=species_extra,
    flora={'A': ['balsamroot_dl', 'lupine_dl', 'geranium_dl', 'fireweed_dl', 'paintbrush_dl'],
           'B': ['balsamroot_dl', 'lupine_dl', 'geranium_dl', 'huckleberry_dl', 'paintbrush_dl'],
           'C': ['balsamroot_dl', 'paintbrush_dl', 'columbine_dl', 'huckleberry_dl', 'fireweed_dl']},
    wild=['moose', 'bear', 'grizzly', 'elk', 'deer', 'beaver', 'fox', 'squirrel', 'chipmunk', 'marmot', 'pika',
          'nutcracker', 'steller', 'osprey', 'eagle', 'bluebird', 'woodpecker'],
    wild_sum={
     'moose': ('Moose', 'Browse the willows along Beaver Creek and the wet edges of Taggart and Bradley lakes, mostly early and late in the day. Give them at least 25 yards.'),
     'bear': ('Black bear', 'Common on all three trails, especially in the huckleberry patches on the moraine between the lakes in late summer. Black bears can be black, brown or cinnamon; stay at least 100 yards away.'),
     'grizzly': ('Grizzly bear', RARE_GRIZ),
     'elk': ('Elk', 'Graze the meadows and the regrowing Beaver Creek Fire burn, mostly at dawn and dusk; bulls bugle in September.'),
     'deer': ('Mule deer', 'Big-eared deer that browse the aspen and sagebrush edges near both trailheads and in the burn.'),
     'beaver': ('American beaver', 'Beavers build in the ponds and slow water around Taggart Lake and Beaver Creek. Look for chewed aspen stumps and lodges; they are out mostly at dusk.'),
     'fox': ('Red fox', 'Hunts voles in the sagebrush and meadows near the trailheads. In the Tetons it can be red, black or silver-gray, always with a white tail tip.'),
     'squirrel': ('American red squirrel', 'A small, noisy squirrel of the conifer forest. You often hear its chatter, or find piles of cone scales where it feeds.'),
     'chipmunk': ('Golden-mantled ground squirrel', 'Looks like a big chipmunk without face stripes. Common on the rocky slopes and around Delta Lake, where it raids unattended packs; do not feed it.'),
     'marmot': ('Yellow-bellied marmot', 'Suns on boulders in the rock fields below Delta Lake and along the switchbacks, and whistles when alarmed. Marmots chew into packs left on the ground.'),
     'pika': ('American pika', 'A small, round-eared relative of rabbits that lives in the boulder fields on the way to Delta Lake. You usually hear its sharp call before you see it.'),
     'nutcracker': ("Clark's nutcracker", 'A gray, black-winged bird of the high pines with a loud, grating call. It buries thousands of whitebark and limber pine seeds each fall.'),
     'steller': ("Steller's jay", 'A dark blue jay with a black crest, common in the conifer forest along both lake loops.'),
     'osprey': ('Osprey', 'A brown-and-white fish hawk that hovers over Taggart and Bradley lakes and dives feet first for fish.'),
     'eagle': ('Bald eagle', 'Seen over the lakes and along the valley; the white head and tail show from far away.'),
     'bluebird': ('Mountain bluebird', 'Sky-blue birds that nest in the snags of the Beaver Creek Fire burn and hunt insects over the open slopes.'),
     'woodpecker': ('Woodpeckers', 'Hairy and American three-toed woodpeckers, and northern flickers, work the dead trees of the burn for insects.'),
    },
    grid=GRID, step=STEP, dem_b64=b64, tile=TILE, ve=1.3, ridge_ft=None,
    palette='forest', tree_rule='if(inLake(x,n)){type=null;}else ' + TREE_RULES['conifer'], treeline_ft=10000, snow_ft=11200,
    landmarks=lm, animals_js=animals_js, extra_js=extra_js,
    stop_photos=stop_photos, flower_photos=flower_photos, animal_photos=animal_photos,
    overview=dict(h2='Taggart Lake, Bradley Lake and Delta Lake',
                  p='Taggart and Bradley lakes fill basins behind glacial moraines at the foot of the Grand Teton, and Delta Lake sits far above them in Glacier Gulch. A is the short loop to Taggart Lake and back along Beaver Creek, B adds Bradley Lake, and C climbs from Lupine Meadows to Delta Lake on an unofficial route. Pick a trail to focus the model; click anything on it for a quick note.',
                  numbers='Plain numbers mark spots that trails A and B share. Lettered stops belong to one trail: C6 is the sixth stop on Trail C. A and B start at the Taggart Lake Trailhead, C at Lupine Meadows.',
                  wild_h='Wildlife around Taggart and Delta lakes',
                  note='Grand Teton National Park, Wyoming. Taggart Lake Trailhead: Teton Park Road, about 2.3 miles north of the Moose Entrance Station. Lupine Meadows Trailhead: 1.5 miles up a gravel road off Teton Park Road, 1 mile south of South Jenny Lake Junction. Park entrance fee; no pets on trails. Both lots fill early in summer. Teton Park Road is closed to cars beyond the Taggart Lake Trailhead from November 1 to April 30. The Taggart Lake Trailhead and its trails close to all use from May 1, 2027 for reconstruction (through about November 2027). The Delta Lake route past the Amphitheater Lake trail is unofficial and unmaintained. Bears live here: carry bear spray and hike in groups. Terrain from USGS elevation data, stylized; not for navigation.'),
    links={'A': [('Taggart Lake–Beaver Creek Loop · NPS', 'https://www.nps.gov/thingstodo/taggartloop.htm'), ('Taggart Lake–Beaver Creek Loop · Teton Hiking Trails', 'https://tetonhikingtrails.com/taggart-lake-beaver-creek-loop.htm')],
           'B': [('Taggart Lake–Bradley Lake Loop · NPS', 'https://www.nps.gov/thingstodo/taggartbradley.htm'), ('Taggart Lake–Bradley Lake Loop · Teton Hiking Trails', 'https://tetonhikingtrails.com/bradley-lake.htm')],
           'C': [('Delta Lake route work, 2026 · NPS', 'https://www.nps.gov/grte/learn/news/trail-improvement-work-will-begin-in-late-june-on-delta-lake-route-in-grand-teton-national-park.htm'), ('Delta Lake · Hiking Project', 'https://www.hikingproject.com/trail/7116433/delta-lake'), ('Delta Lake hike guide · Go Wander Wild', 'https://gowanderwild.com/?p=7893')]},
    viewaz={'all': 1.0, 'A': 0.8, 'B': 1.0, 'C': 1.2},
    zoomcap={'A': 3.0, 'B': 2.8, 'C': 2.6},
)
cfg['ridge_ft'] = int(np.percentile(p.grid, 75))
creeks = []
GGC = [w['id'] for w in p.W if w['n'] == 'Glacier Gulch Creek']
TGC = [w['id'] for w in p.W if w['n'] == 'Taggart Creek' and w['k'] == 'stream']
print('glacier gulch creek ways', GGC, 'taggart creek ways', TGC)
for cid, ids, minor in (('garnet', ['921282566', '921282567'], False), ('glaciergulch', GGC[:1], True), ('taggart', ['207800986'] if '207800986' in p.WID else TGC[:1], True)):
    if not ids: continue
    if all(i in p.WID for i in ids):
        c = p.creek(ids, GRID, minor=minor)
        if c: creeks.append(dict(id=cid, **c))
cfg['canyons'] = creeks
json.dump({k: {'mi': R[k]['mi'], 'gain': R[k]['gain'], 'lo': R[k]['lo'], 'hi': R[k]['hi']} for k in R}, open('/home/claude/parks/deltalake/stats.json', 'w'))
print(build(cfg, '/home/claude/site/out/teton-delta-lake/index.html'))
