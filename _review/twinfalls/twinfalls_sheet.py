from lib import *
from mk_sheet import build
import mk_sheet, fauna
import sys, json, os
import numpy as np

os.chdir('/home/claude/parks')
sys.path.insert(0, '/home/claude/parks')

# --- extra animal models for this park, registered in memory only (fauna.py / mk_sheet.py untouched)
fauna.NEW['dipper'] = ("American dipper", "#6E7177", "A chunky gray songbird that bobs on rocks in fast streams and walks underwater to feed.", 1.6,
 '''dipper(){const g=new THREE.Group(),c="#6E7177",dk="#565A60";part(g,SPH,"#8C8A84",0,0.12,0,0.42,0.14,0.34);
   const b=part(g,SPH,c,0,0.5,0,0.36,0.27,0.25);rot(b,0,0,0.12);part(g,SPH,dk,0.3,0.68,0,0.17,0.16,0.15);
   part(g,SPH,"#111",0.4,0.72,0.09,0.03,0.03,0.03,0);part(g,SPH,"#111",0.4,0.72,-0.09,0.03,0.03,0.03,0);
   const bk=part(g,CONE,"#2A2A2A",0.5,0.67,0,0.035,0.12,0.035,0);rot(bk,0,0,-Math.PI/2);
   part(g,CYL,"#D9A6A0",0.05,0.3,0.08,0.025,0.18,0.025,0);part(g,CYL,"#D9A6A0",0.05,0.3,-0.08,0.025,0.18,0.025,0);
   const tail=new THREE.Group();tail.position.set(-0.32,0.55,0);g.add(tail);const t=part(tail,SPH,dk,-0.1,0.05,0,0.16,0.05,0.09);rot(t,0,0,0.5);g.userData.tail=tail;return g;}''')
fauna.NEW['newt'] = ("Rough-skinned newt", "#B4642C", "A brown newt with a bright orange belly. Its skin carries a strong toxin: look, but do not handle.", 1.8,
 '''newt(){const g=new THREE.Group(),c="#5A4636",o="#E8792A";part(g,SPH,c,0,0.14,0,0.42,0.1,0.13);part(g,SPH,o,0,0.08,0,0.4,0.06,0.11,0);
   part(g,SPH,c,0.44,0.15,0,0.15,0.09,0.11);part(g,SPH,"#111",0.5,0.22,0.07,0.025,0.025,0.025,0);part(g,SPH,"#111",0.5,0.22,-0.07,0.025,0.025,0.025,0);
   [[0.25,1],[0.25,-1],[-0.22,1],[-0.22,-1]].forEach(([x,sd])=>{const l=part(g,CYL,c,x,0.07,0.14*sd,0.03,0.16,0.03,0);rot(l,0.9*sd,0,0);});
   const tail=new THREE.Group();tail.position.set(-0.38,0.13,0);g.add(tail);part(tail,SPH,c,-0.3,0,0,0.36,0.07,0.04);g.userData.tail=tail;return g;}''')
fauna.BIRDS['owl'] = ("Barred owl", "#8A6F55", "A big round-headed owl with dark eyes and brown bars on its chest; its call sounds like 'who cooks for you'.", ["#8A6F55", "#E8E0D2", "#8A6F55"])
fauna.extend(mk_sheet)

p = Park('twinfalls', 47.4526, -121.7054)      # origin: Twin Falls Trailhead, end of SE 159th St
TH = (0, 0)              # Twin Falls Trailhead (OSM trail start, next to the toilet)
LVJ = (1848, -2363)      # top of the 104 steps to the Lower Twin Falls Viewpoint (OSM steps way 156017148)
LV = (1732, -2525)       # Lower Twin Falls Viewpoint platform (OSM viewpoint node)
BRa, BRb = (1962, -2681), (1929, -2745)   # Twin Falls Trail bridge (OSM way 163323654, bridge=yes)
BR = (1946, -2713)
UV = (2043, -2824)       # Upper Twin Falls Viewpoint (OSM viewpoint node)
UF = (2132, -2787)       # Twin Falls (Upper), OSM waterfall node
JW = (4939, -3762)       # Twin Falls Trail meets the Palouse to Cascades State Park Trail (OSM way end)
PIC = (12156, -6104)     # South Fork Picnic Area (OSM picnic site)
WT = (12581, -5963)      # west end of the Weeks Falls Interpretive Trail (OSM)
WV = (14140, -6999)      # Weeks Falls Viewpoint (OSM viewpoint node)
R = {}
R['A'] = route_xy(p, PIC, WT, (13700, -6660), WV)
R['B'] = route_xy(p, TH, LVJ, BR, UV)
R['C'] = route_xy(p, TH, LVJ, BR, UV, JW)
for k in R: Park.smooth_E(R[k], 9); p.describe(R[k], k)
ST = snap_stops(p, R, {
    'S1': (*TH, 'BC'), 'S2': (*LVJ, 'BC'), 'S3': (*BR, 'BC'), 'S4': (*UV, 'BC'),
    'C1': (*JW, 'C'),
    'A1': (*PIC, 'A'), 'A2': (*WV, 'A'),
})
TILE = (-3200, 17400, -10400, 3200)
GRID = (-3500, 17700, -10700, 3500)
if 'plot' in sys.argv:
    from plot import plot
    plot(p, (-500, 5500, -4500, 600), 'twinfalls/routesBC.png', routes=R, stops=ST, title='BC', grid=250)
    plot(p, (11800, 14800, -7600, -5500), 'twinfalls/routesA.png', routes=R, stops=ST, title='A', grid=250)
    sys.exit()

STEP = 90
b64, NX, NN = p.dem_b64(*GRID, STEP=STEP)
RIDGE = int(round(float(np.percentile(p.grid, 75)), -1))
print('grid', NX, NN, NX * NN, p.grid.min(), p.grid.max(), 'p75', RIDGE)

S = lambda i: ST[i]
stops = [
 dict(id='S1', trails=['B', 'C'], x=S('S1')[0], n=S('S1')[1], name='Twin Falls Trailhead',
      desc='The lot at the end of SE 159th Street, half a mile from I-90 exit 34, with a toilet. A Discover Pass is required (a day pass can be bought at the trailhead). The trail follows the South Fork Snoqualmie River for about half a mile through old-growth trees, then climbs. Kayaking is allowed only downstream of the falls.'),
 dict(id='S2', trails=['B', 'C'], x=S('S2')[0], n=S('S2')[1], name='Lower Twin Falls Viewpoint',
      desc='Here a side trail of 104 steps drops to a platform facing the lower falls, where the river cuts through a narrow rock canyon and plunges 135 feet. Closed since March 2026: a storm left the viewpoint structurally damaged. Stay on the main trail.'),
 dict(id='S3', trails=['B', 'C'], x=S('S3')[0], n=S('S3')[1], name='Twin Falls bridge',
      desc='More stairs lead down to a footbridge high over the gorge, just above the lower falls, with views down the valley and up to the stair-step upper falls.'),
 dict(id='S4', trails=['B', 'C'], x=S('S4')[0], n=S('S4')[1], name='Upper Twin Falls Viewpoint',
      desc='A few more stairs and a steep slope past the bridge lead to an overlook of the upper falls. Trail B turns back here: about 1.25 miles from the trailhead.'),
 dict(id='C1', trails=['C'], x=S('C1')[0], n=S('C1')[1], name='Palouse to Cascades Trail',
      desc='The trail climbs about another mile through second-growth forest, above the I-90 freeway (traffic is loud), to meet the Palouse to Cascades State Park Trail, the old Milwaukee Road rail line, also called the Iron Horse or John Wayne Pioneer Trail. Homestead Valley Trailhead is about a third of a mile east. Turn around here.'),
 dict(id='A1', trails=['A'], x=S('A1')[0], n=S('A1')[1], name='South Fork Picnic Area',
      desc='Riverside picnic tables, a play field, restrooms and a popular swimming hole at 51350 SE Homestead Valley Road. The Old Snoqualmie Wagon Road, finished in 1867 between Ellensburg and Seattle, ran through here. The interpretive trail heads upstream through old-growth trees.'),
 dict(id='A2', trails=['A'], x=S('A2')[0], n=S('A2')[1], name='Weeks Falls Viewpoint',
      desc='The 77-foot Weeks Falls, a run of cascades over rock ledges on the South Fork Snoqualmie River, about half a mile upstream from the picnic area. The viewpoint is wheelchair accessible from the small Weeks Falls Trailhead lot.'),
]
stops, order = renumber(p, R, stops)
print(order, [(s['id'], s['name']) for s in stops])
trails = [
 dict(id='A', name='Weeks Falls Interpretive Trail', short='Weeks Falls', official=1.0, unit='round trip', route='Out and back', time='30 min', level='Easy', color='--tA',
      desc='A short, nearly level walk upstream along the South Fork Snoqualmie River from the South Fork Picnic Area, past old-growth trees, to the viewpoint over Weeks Falls. Starts about 3 miles east of the Twin Falls Trailhead by road (I-90 exit 38).', anchors=p.anchors(R['A'])),
 dict(id='B', name='Twin Falls Trail', short='Twin Falls', official=2.5, unit='round trip', route='Out and back', time='1.5–2 hr', level='Easy/Moderate', color='--tB',
      desc='Follows the river, then climbs over two small hills with switchbacks: past The Benches, with a partial view of the lower falls, and the Big Tree, an ancient tree beside the path. Steps lead down to a bridge above the falls and on to the upper falls overlook. About 500 feet of climbing.', anchors=p.anchors(R['B'])),
 dict(id='C', name='Twin Falls to the Palouse to Cascades Trail', short='To the Iron Horse', official=4.0, unit='round trip', route='Out and back', time='2–3 hr', level='Moderate', color='--tC',
      desc='Continues past the upper falls overlook and climbs away from the river, above the freeway, to the old railroad grade of the Palouse to Cascades State Park Trail (Iron Horse Trail). It never returns to the river beyond the bridge. About 900 feet of climbing.', anchors=p.anchors(R['C'])),
]

extra_js = '''
TRAILS.forEach(T=>{const g={B:500,C:900}[T.id];if(g)T.gain=g;});
'''

creeks = []
c = p.creek(['32510073'], GRID, minor=False)
if c: creeks.append(dict(id='southfork', **c))
for wid, nm in (('164012598', 'change'), ('384287878', 'hall')):
    c = p.creek([wid], GRID, minor=True)
    if c: creeks.append(dict(id=nm, **c))
print('creeks', len(creeks))

pa = place_along
A_ = lambda k, f, s=1, o=200: pa(p, R[k], [f], s, o)[0]
def path(k, f, s=1, o=200, d=0.02): return js(A_(k, f, s, o) + A_(k, f + d, s, o))
an = []
an += [f'{{k:"elk",path:{js([12350, -5420, 12650, -5480])},per:40}}', f'{{k:"elk",path:{js([11050, -3780, 11350, -3860])},per:44,ph:0.4}}']
an += [f'{{k:"dipper",at:[369,-927],hop:true}}', f'{{k:"dipper",at:[13625,-6462],hop:true}}']
an += [f'{{k:"newt",path:{path("C",.84,-1,90,.01)},per:60}}', f'{{k:"newt",path:{path("B",.30,1,80,.01)},per:60,ph:0.5}}']
an += [f'{{k:"chipmunk",at:{js(A_("B",.15,1,110))},hop:true}}', f'{{k:"chipmunk",at:{js(A_("C",.70,1,140))},hop:true}}']
an += [f'{{k:"squirrel",at:{js(A_("C",.93,-1,160))},hop:true}}', f'{{k:"squirrel",at:{js(A_("B",.55,-1,150))},hop:true}}']
an += [f'{{k:"snake",path:{path("A",.5,1,120,.06)},per:30}}', f'{{k:"snake",path:{path("C",.60,-1,120,.01)},per:32,ph:0.5}}']
animals_js = '[\n ' + ',\n '.join(an) + '\n]'

bn = {s['name']: s for s in stops}
g = lambda nm: (bn[nm]['x'], bn[nm]['n'])
th, pic, jw = g('Twin Falls Trailhead'), g('South Fork Picnic Area'), g('Palouse to Cascades Trail')
lm = f'''  gate({th[0] - 60},{th[1] + 50},0.6);gate({pic[0] - 40},{pic[1] + 60},0.3);
  // falls: ribbons that follow the gorge, never dipping under the terrain (drawn wide so they read at this scale)
  const fallTex=stripeTex("#E4F6F6","#FFFFFF",64,128,22,9,14);fallTex.repeat.set(1,3);
  const fallMat=new THREE.MeshBasicMaterial({{map:fallTex,side:THREE.DoubleSide}});
  function fall(x0,n0,e0,x1,n1,e1,wd,lift){{const N=16,L=Math.hypot(x1-x0,n1-n0)||1,px=-(n1-n0)/L*wd/2,pn=(x1-x0)/L*wd/2;const pos=[],uv=[],idx=[];
    for(let i=0;i<=N;i++){{const t=i/N,x=x0+(x1-x0)*t,n=n0+(n1-n0)*t;const e=Math.max(e0+(e1-e0)*t,surf(x,n)+(lift||14));
      [-1,1].forEach(sd=>{{const v=Wv(x+px*sd,n+pn*sd,e);pos.push(v.x,v.y,v.z);uv.push(sd<0?0:1,1-t);}});
      if(i<N){{const a=i*2;idx.push(a,a+1,a+2,a+1,a+3,a+2);}}}}
    const geo=new THREE.BufferGeometry();geo.setAttribute("position",new THREE.Float32BufferAttribute(pos,3));geo.setAttribute("uv",new THREE.Float32BufferAttribute(uv,2));geo.setIndex(idx);
    const m=new THREE.Mesh(geo,fallMat);m.renderOrder=2;world.add(m);return m;}}
  function pool(x,n,e,r){{const v=Wv(x,n,Math.max(e,surf(x,n)+2));part(world,new THREE.CylinderGeometry(1,1,0.05,18),"#CFEFF2",v.x,v.y,v.z,r,1,r*0.8,1.03,false);}}
  // falls drawn as solid rock steps with a sheet of water over each face, exaggerated in height so they read at this scale
  function cascade(x,n,dx,dn,steps,w,h){{const g=new THREE.Group();g.position.copy(G(x,n));g.rotation.y=Math.atan2(dx,-dn);world.add(g);
    for(let i=0;i<steps;i++){{const z=-i*0.6,y0=i*h,H=(i+1)*h+0.4;
      part(g,box,i%2?"#8D8A82":"#7E7B74",0,H/2-0.4,z-0.3,w+0.7,H,0.6,1.05);
      const sh=new THREE.Mesh(new THREE.PlaneGeometry(w,h+0.06),fallMat);sh.position.set(0,y0+h/2,z+0.02);sh.renderOrder=2;g.add(sh);
      part(g,box,"#CFEFF2",0,y0+h+0.01,z-0.3,w,0.04,0.6,0);}}
    part(g,new THREE.CylinderGeometry(1,1,0.06,18),"#CFEFF2",0,0.03,0.55,w*0.75,1,0.6,1.03);return g;}}
  // Lower Twin Falls: one 135-ft plunge just below the bridge (river flows west-northwest)
  cascade(1840,-2630,-125,90,1,0.9,2.0);
  // upper falls: stair-step cascades above the bridge, up to the OSM waterfall node
  cascade(2045,-2752,-92,35,3,0.8,0.4);
  // Weeks Falls: 77 ft of cascades over ledges below the viewpoint
  cascade(13930,-6735,-270,255,3,1.0,0.4);
  const rings=[],mist=[];for(let i=0;i<6;i++){{const m=new THREE.Mesh(new THREE.SphereGeometry(0.3,8,6),new THREE.MeshBasicMaterial({{color:"#FFFFFF",transparent:true}}));
    const v=G(1840+(i%3-1)*40,-2630+(i>2?40:10),0.4);m.position.copy(v);world.add(m);mist.push({{m,ph:i/6,x:(i%3-1)*0.3}});}}
  anim.water={{fallTex,rings,mist}};
  // Twin Falls bridge (OSM way 163323654) high over the gorge, drawn large
  {{const a=G({BRa[0]},{BRa[1]}),b=G({BRb[0]},{BRb[1]});const y=Math.max(a.y,b.y,G(1840,-2630).y+2.1);const L=Math.hypot(b.x-a.x,b.z-a.z)*1.9;
   const g=new THREE.Group();g.position.set((a.x+b.x)/2,y,(a.z+b.z)/2);g.rotation.y=Math.atan2(-(b.z-a.z),b.x-a.x);world.add(g);
   part(g,box,"#8A6A4C",0,0,0,L,0.18,0.55,1.06);part(g,box,"#5E4632",0,0.32,0.27,L,0.08,0.06,0);part(g,box,"#5E4632",0,0.32,-0.27,L,0.08,0.06,0);
   for(let i=0;i<=6;i++){{const t=-L/2+L*i/6;part(g,box,"#5E4632",t,0.16,0.27,0.06,0.32,0.06,0);part(g,box,"#5E4632",t,0.16,-0.27,0.06,0.32,0.06,0);}}
   [[a,-1],[b,1]].forEach(([e,sd])=>{{const hh=y-e.y+0.2;part(g,box,"#6E5642",sd*(L/2-0.2),-hh/2,0,0.25,hh,0.5,1.05);}});}}
  // Lower Twin Falls Viewpoint: wooden platform on the canyon wall (closed), facing the falls to the east
  {{const q=G({LV[0]},{LV[1]});const g=new THREE.Group();g.position.copy(q);g.rotation.y=Math.atan2(-(-2660+2525),1880-1732);g.scale.setScalar(1.7);world.add(g);
   part(g,box,"#8A6A4C",0,0.25,0,1.1,0.14,0.8,1.06);[[-0.5,-0.36],[0.5,-0.36],[-0.5,0.36],[0.5,0.36]].forEach(([a,b])=>part(g,cyl,"#5E4632",a,0.0,b,0.06,0.6,0.06));
   part(g,box,"#5E4632",0.55,0.55,0,0.05,0.5,0.8,0);part(g,box,"#C8322C",-0.3,0.75,0.42,0.38,0.38,0.04,1.06);}}
  // Upper Twin Falls Viewpoint: railed overlook
  {{const q=G({UV[0]},{UV[1]});const g=new THREE.Group();g.position.copy(q);g.rotation.y=0.4;g.scale.setScalar(1.5);world.add(g);
   part(g,box,"#9A948A",0,0.12,0,1.2,0.24,0.8,1.06);part(g,box,"#5E4632",0,0.55,-0.38,1.2,0.06,0.06,0);[-0.55,0,0.55].forEach(a=>part(g,cyl,"#5E4632",a,0.4,-0.38,0.04,0.55,0.04));}}
  // junction signpost on the old rail grade
  {{const q=G({jw[0]},{jw[1]});const g=new THREE.Group();g.position.copy(q);g.scale.setScalar(1.8);world.add(g);
   part(g,cyl,"#6B4F3A",0,0.7,0,0.07,1.4,0.07);part(g,box,"#2D4A40",0.3,1.2,0,0.6,0.2,0.05,1.06);part(g,box,"#2D4A40",-0.25,0.95,0,0.5,0.18,0.05,1.06);}}
  // Weeks Falls Viewpoint: railed platform above the cascades
  {{const q=G({WV[0]},{WV[1]});const g=new THREE.Group();g.position.copy(q);g.rotation.y=-0.6;g.scale.setScalar(1.6);world.add(g);
   part(g,box,"#9A948A",0,0.12,0,1.3,0.24,0.8,1.06);part(g,box,"#5E4632",0,0.55,0.38,1.3,0.06,0.06,0);[-0.6,0,0.6].forEach(a=>part(g,cyl,"#5E4632",a,0.4,0.38,0.04,0.55,0.04));}}
  bench({pic[0] + 70},{pic[1] - 40},0.3);
'''

species_extra = {
 'salmonberry_tf': 'salmonberry_tf:{name:"Salmonberry",latin:"Rubus spectabilis",color:"#D84A86",shape:"berry",bloom:[3,4,5,6,7],sum:"The berry the park is named for: Olallie is the Chinook Jargon word for salmonberry. Magenta flowers in spring, then orange-to-red berries in early summer along the river.",rule:(d,e,g,s)=>d<500&&g<0.9}',
 'trillium_tf': 'trillium_tf:{name:"Pacific trillium",latin:"Trillium ovatum",color:"#F7F3EA",shape:"cup",bloom:[3,4,5],sum:"Three white petals over three broad leaves, turning pink with age. Look on the river side of the trail in spring.",rule:(d,e,g,s)=>d<900&&g<0.8&&s<0.1}',
 'skunk_tf': 'skunk_tf:{name:"Western skunk cabbage",latin:"Lysichiton americanus",color:"#F2D23A",shape:"spike",bloom:[3,4],sum:"A bright yellow hood around a green spike, rising from the mud in early spring, with a musky smell. Grows in the swampy patch near the start of the Twin Falls Trail.",rule:(d,e,g,s)=>d<220&&g<0.35}',
 'bleeding_tf': 'bleeding_tf:{name:"Pacific bleeding heart",latin:"Dicentra formosa",color:"#E58FB4",shape:"tube",bloom:[3,4,5,6],sum:"Nodding pink heart-shaped flowers over lacy leaves in moist shade along the trails.",rule:(d,e,g,s)=>d<700&&g<0.9}',
 'corydalis_tf': 'corydalis_tf:{name:"Scouler’s corydalis",latin:"Corydalis scouleri",color:"#E6A3C2",shape:"spike",bloom:[4,5,6],sum:"Tall stems of spurred pink flowers over big ferny leaves, in moist forest beside the river. The flower most often photographed on these trails.",rule:(d,e,g,s)=>d<400&&g<0.7}',
 'maidenhair_tf': 'maidenhair_tf:{name:"Western maidenhair fern",latin:"Adiantum aleuticum",color:"#5E9E4A",shape:"fern",bloom:[],sum:"Delicate fan-shaped fronds on black stems, in walls along the wet, rocky banks of the Twin Falls Trail.",rule:(d,e,g,s)=>d<600&&g>0.3}',
}

PM = json.load(open('/mnt/files/gtb/photos/twinfalls/photos_meta.json'))
def keep(key, nums):
    out = []
    for i in nums:
        for x in PM.get(key, []):
            if x['f'].endswith(f'_{i}.jpg'): out.append(dict(x))
    return out
EX = lambda f, by, lic, src, t: {'f': '../photos/' + f, 'by': by, 'lic': lic, 'src': src, 't': t}
by_name = {
 'Lower Twin Falls Viewpoint': keep('twin', [0]),
 'Twin Falls bridge': keep('twin', [2]),
 'Upper Twin Falls Viewpoint': keep('twin', [3]),
 'Weeks Falls Viewpoint': keep('weeks', [0, 1]),
}
stop_photos = {s['id']: by_name[s['name']] for s in stops if by_name.get(s['name'])}
flower_photos = {
 'salmonberry_tf': [EX('sp_salmonberry_0.jpg', 'pfly', 'BY-SA 2.0', 'https://www.flickr.com/photos/24934185@N00/127232176', 'Salmonberry, Rubus spectabilis')],
 'trillium_tf': [EX('sp_trillium_1.jpg', 'brewbooks', 'BY-SA 2.0', 'https://www.flickr.com/photos/93452909@N00/4612517290', 'Trillium ovatum with Pollinator')],
 'skunk_tf': [EX('sp_l22_skunkcabbage_1.jpg', 'The Cosmonaut', 'CC BY-SA 2.5 ca', 'https://commons.wikimedia.org/wiki/File:Lysichiton_americanus_-_Aldergrove_Regional_Park.jpg', 'Lysichiton americanus - Aldergrove Regional Park')],
 'bleeding_tf': [EX('sp_bleedingheart_0.jpg', 'John Rusk', 'BY 2.0', 'https://www.flickr.com/photos/12303842@N00/18399408850', 'J20150605-0050—Dicentra formosa—RPBG')],
 'corydalis_tf': [EX('sp_corydalis_0.jpg', 'Flickr-User pfly', 'CC BY-SA 2.0', 'https://commons.wikimedia.org/wiki/File:Corydalis_scouleri.jpg', 'Corydalis scouleri')],
 'maidenhair_tf': [EX('sp_hl_maidenhair_0.jpg', 'brewbooks', 'BY-SA 2.0', 'https://www.flickr.com/photos/93452909@N00/196482520', 'Adiantum pedatum Maidenhair fern on serpentine rock')],
}
animal_photos = {
 'elk': [EX('sp_elk_0.jpg', 'Bryce Bradford', 'BY-NC-ND 2.0', 'https://www.flickr.com/photos/28508197@N07/5922322660', 'The Elk & I')],
 'chipmunk': [EX('sp_townsendchipmunk_0.jpg', 'Michael W Klotz - The Bird Blogger.com', 'BY-NC 2.0', 'https://www.flickr.com/photos/23020855@N03/34260697942', "Townsend's Chipmunk - Langley, BC")],
 'squirrel': [EX('sp_douglassquirrel_0.jpg', 'Franco Folini', 'BY-SA 2.0', 'https://www.flickr.com/photos/78425154@N00/424678972', "Douglas' Squirrel, Oregon")],
 'snake': [EX('sp_gartersnake_0.jpg', 'GlacierNPS', 'PDM 1.0', 'https://www.flickr.com/photos/43288043@N04/27953016766', 'Common Garter Snakes - Thamnophis sirtalis')],
 'steller': [EX('sp_mr_steller_0.jpg', 'jimculp@live.com', 'BY-NC-ND 2.0', 'https://www.flickr.com/photos/93815673@N00/22209778395', "Steller's Jay")],
 'raven': [EX('sp_raven_1.jpg', 'Frank.Vassen', 'BY 2.0', 'https://www.flickr.com/photos/42244964@N03/5357074718', 'Common Raven (Corvus corax), Tefia, Fuerteventura')],
 'vulture': [EX('sp_tvulture_0.jpg', 'Charles J. Sharp', 'CC BY-SA 4.0', 'https://commons.wikimedia.org/wiki/File:Turkey_vulture_(Cathartes_aura)_in_flight.JPG', 'Turkey vulture (Cathartes aura) in flight')],
 'dipper': keep('sp:dipper', [0, 2, 3]),
 'owl': keep('sp:barredowl', [0, 2]),
 'newt': keep('sp:roughnewt', [0, 1, 3]),
 'woodpecker': keep('sp:hairywoodpecker', [1, 2, 3]),
}

from fauna import TREE_RULES
cfg = dict(
    title='Twin Falls, Olallie State Park', aria='Twin Falls and Weeks Falls in Olallie State Park, Washington', h1='Twin Falls &amp; Olallie State Park',
    canyons=creeks, trails=trails, stops=stops, order=order,
    species=list(species_extra), species_extra=species_extra,
    flora={'A': ['salmonberry_tf', 'skunk_tf', 'corydalis_tf', 'bleeding_tf'], 'B': ['trillium_tf', 'maidenhair_tf', 'skunk_tf', 'salmonberry_tf', 'bleeding_tf'],
           'C': ['trillium_tf', 'maidenhair_tf', 'corydalis_tf', 'salmonberry_tf']},
    wild=['elk', 'chipmunk', 'squirrel', 'snake', 'newt', 'dipper', 'steller', 'owl', 'woodpecker', 'raven', 'vulture'],
    wild_sum={
     'elk': ('Elk', 'A herd of elk lives in the valley. They are seen in the open ground near the South Fork Picnic Area and along Homestead Valley Road, mostly early and late in the day. Give them plenty of room.'),
     'chipmunk': ("Townsend's chipmunk", 'A dark, striped chipmunk of wet Northwest forests and the mammal most often photographed on these trails. Look on logs and mossy rocks beside the path.'),
     'squirrel': ('Douglas squirrel', 'A small tree squirrel with a rusty-orange belly that lives in the hemlocks and Douglas-firs. You usually hear its loud, chattering scold before you see it.'),
     'snake': ('Garter snake', 'Common and northwestern garter snakes, both harmless, sun themselves on warm trail edges in summer and hunt slugs and frogs near the river.'),
     'newt': ('Rough-skinned newt', 'A brown newt with a bright orange belly that walks across the trail on wet days, mostly in fall and spring. Its skin is toxic: look, but don’t pick it up.'),
     'dipper': ('American dipper', 'A plump gray songbird that bobs on rocks in the fast water and walks underwater to feed. Watch the river near the trailhead, below the falls and at Weeks Falls.'),
     'steller': ("Steller's jay", 'A dark blue jay with a black crest, loud and bold in the conifers and around the picnic area.'),
     'owl': ('Barred owl', 'A big, round-headed brown-and-white owl, seen by day on the Twin Falls Trail in spring. Its call sounds like “who cooks for you, who cooks for you-all.”'),
     'woodpecker': ('Hairy woodpecker', 'A black-and-white woodpecker of the old-growth forest; males have a red patch on the head. Northern flickers and red-breasted sapsuckers are here too.'),
     'raven': ('Common raven', 'Big black birds with a croaking call that ride the wind over the valley and the cliffs of Mount Washington.'),
     'vulture': ('Turkey vulture', 'Rocks side to side on wings held in a shallow V, riding warm air over the valley from spring to fall.'),
    },
    grid=GRID, step=STEP, dem_b64=b64, tile=TILE, ve=1.4, ridge_ft=RIDGE,
    palette={"ground": "#B9E0C9", "groundN": "#A1CFB5", "conifer": "#2E5A3C", "oak": "#4C7A36", "rock": "#9A978C", "rockDeep": "#7C7A72", "ridge": "#C8D8C0"},
    tree_rule=TREE_RULES['conifer'], rock_all_aspects=True,
    landmarks=lm, animals_js=animals_js, extra_js=extra_js, zoomcap={'A': 7.0, 'B': 7.0, 'C': 4.8},
    stop_photos=stop_photos, flower_photos=flower_photos, animal_photos=animal_photos,
    overview=dict(h2='Waterfalls on the South Fork Snoqualmie',
                  p='In Olallie State Park, east of North Bend, the South Fork Snoqualmie River drops through a rock canyon at Twin Falls and over the ledges of Weeks Falls. A is a short riverside walk to Weeks Falls, B climbs through old-growth forest to the bridge and the upper falls overlook, and C keeps going up to the old Milwaukee Road rail line, now the Palouse to Cascades Trail. Pick a trail to focus the model; click anything on it for a quick note.',
                  numbers='Plain numbers mark spots that more than one trail passes: B and C share the Twin Falls Trail as far as the upper falls overlook. Lettered stops belong to one trail: C1 is the first stop on Trail C. All three are out and back, so the miles count the way out.',
                  wild_h='Wildlife around Twin Falls',
                  note='Olallie State Park, North Bend, Washington. Twin Falls Trailhead: 47600 SE 159th Street, I-90 exit 34. South Fork Picnic Area (Weeks Falls): 51350 SE Homestead Valley Road, I-90 exit 38. Open 6:30 am to dusk, day use only. A Discover Pass is required ($10 a day, $45 a year). Hiking only on the Twin Falls and Weeks Falls trails; dogs on leash. Status (November 2026): the Lower Twin Falls Viewpoint (the 104 steps and platform) has been closed since March 16, 2026, after storm damage; the rest of the Twin Falls Trail is open. On the Palouse to Cascades Trail a 350-foot bypass goes around a storm-damaged section near Mount Washington Trailhead (reopened June 2026). Check parks.wa.gov before you go. Terrain from USGS elevation data, stylized; not for navigation.'),
    links={'A': [('Olallie State Park · Washington State Parks', 'https://parks.wa.gov/find-parks/state-parks/olallie-state-park'), ('Olallie State Park brochure (PDF)', 'https://parks.wa.gov/sites/default/files/2023-05/Olallie%20State%20Park%20Brochure.pdf')],
           'B': [('Twin Falls · Washington Trails Association', 'https://www.wta.org/go-hiking/hikes/twin-falls-state-park'), ('Twin Falls · The Mountaineers', 'https://www.mountaineers.org/activities/routes-places/twin-falls'), ('Olallie State Park alerts · Washington State Parks', 'https://parks.wa.gov/find-parks/state-parks/olallie-state-park')],
           'C': [('Twin Falls Trail · Hiking Project', 'https://www.hikingproject.com/trail/7079657/twin-falls-trail'), ('Palouse to Cascades State Park Trail', 'https://parks.wa.gov/find-parks/state-parks/palouse-cascades-state-park-trail')]},
    viewaz={'all': 2.75, 'A': 2.75, 'B': 2.75, 'C': 2.75},
)
json.dump({k: {'mi': R[k]['mi'], 'gain': R[k]['gain'], 'lo': R[k]['lo'], 'hi': R[k]['hi']} for k in R}, open('twinfalls/stats.json', 'w'))
os.makedirs('/home/claude/site/out/twin-falls-wa', exist_ok=True)
print(build(cfg, '/home/claude/site/out/twin-falls-wa/index.html'))
