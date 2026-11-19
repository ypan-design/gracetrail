# Indian Head & Rainbow Falls: shared routing (imported by the sheet and the plot run)
from lib import *
import numpy as np, math

def ih_park():
    p = Park('indianhead', 44.1495, -73.7682)   # origin: St. Huberts (AMR) parking area on Route 73
    # Lake Road and Ausable Club Road are the hiking route (private roads walked by all AMR hikers): no road penalty
    for u, v, dd in p.G.edges(data=True):
        if dd['nm'] in ('Lake Road', 'Ausable Club Road'): dd['w'] /= 3.0
    return p

def mk(p, pts):
    pts = [tuple(map(float, q)) for q in pts]
    out = [pts[0]]
    for q in pts[1:]:
        if math.dist(out[-1], q) > 1: out.append(q)
    E = [p.elev(*q) for q in out]; cum = [0.0]
    for i in range(1, len(out)): cum.append(cum[-1] + math.dist(out[i - 1], out[i]))
    gain = sum(max(0, E[i] - E[i - 1]) for i in range(1, len(E)))
    return dict(pts=out, E=E, cum=cum, segs=[], gain=gain, mi=cum[-1] / 5280, lo=min(E), hi=max(E))

def dens(a, b, step=60):
    n = max(1, int(math.dist(a, b) / step)); return [(a[0] + (b[0] - a[0]) * i / n, a[1] + (b[1] - a[1]) * i / n) for i in range(1, n + 1)]

def seq(p, parts):
    """parts: list of ('g', [waypoints]) routed over trails, or ('m', [points]) drawn straight (unmapped spur)."""
    pts = []
    for kind, wp in parts:
        if kind == 'g':
            r = route_xy(p, *wp); q = r['pts']; print('   seg', ' | '.join(f"{nm}@{m}" for nm, m in r['segs'] if nm != 'snap'))
        else:
            q = [wp[0]]
            for a, b in zip(wp, wp[1:]): q += dens(a, b)
        pts += q if not pts else q[1:] if math.dist(pts[-1], q[0]) < 5 else q
    return mk(p, pts)

PK = (0, 0)              # St. Huberts parking area (lakeplacid.com coordinates 44.14976, -73.7677)
LR0 = (-2858, 585)       # start of Lake Road (OSM), gate house and AMR gate
GBJ = (-10140, -6907)    # Gill Brook Trail leaves Lake Road (OSM way 268509364 end)
IHJ = (-14496, -11564)   # Indian Head Trail leaves Lake Road near the top of the last hill (OSM way 423932643)
LRE = (-14685, -11538)   # Lake Road end at the dam path
DAM = (-14806, -11320)   # Lower Ausable Lake Dam (OSM)
WRE = (-14991, -11257)   # West River Trail end, Cascade Brook footbridge
FALLS_SPUR = [(-14991, -11257), (-15138, -11345), (-15367, -11396), (-15485, -11327), (-15628, -11303), (-15777, -11307), (-15919, -11338)]   # past the Sawteeth Scenic Trail start, then the OSM Rainbow Falls Trail (way 234264679, not linked to the dam paths in OSM)
RF = (-15919, -11338)    # end of the Rainbow Falls Trail at the foot of the falls
RFC = (-16035, -11328)   # Rainbow Falls: Cascade Brook (OSM) crosses the OSM cliff line 489094266
RIDGE = (-14297, -13467) # ridge junction: Indian Head Trail / Fish Hawk Cliffs Trail / Indian Head Crossover Trail
IH = (-14502, -13615)    # Indian Head South Outlook (OSM viewpoint)
IHT = (-14571, -13722)   # Indian Head Trail end on the summit ledges
FH = (-14682, -14370)    # Fish Hawk Cliffs Lookout (OSM viewpoint)
FHS = (-14610, -14352)   # spur off the Fish Hawk Cliffs Trail
FHG = (-12801, -14540)   # Fish Hawk Cliffs Trail meets the Gill Brook Trail
XGB = (-11829, -12008)   # Indian Head Crossover Trail meets the Gill Brook Trail
NO = (-13268, -12597)    # North Outlook (OSM viewpoint)
NOS = (-13412, -12737)
GW = (-14440, -12486)    # Gothic Window (OSM viewpoint)
GWS = (-14314, -12346)

def ih_routes(p):
    R = {}
    out = seq(p, [('g', [PK, LR0, (-7745, -4015), IHJ, LRE, DAM, WRE]), ('m', FALLS_SPUR)])
    R['A'] = mk(p, out['pts'] + out['pts'][::-1][1:])
    R['B'] = seq(p, [('g', [PK, LR0, (-7745, -4015), IHJ, RIDGE, IH, IHT, IH, RIDGE, FHS, FH, FHS, FHG, XGB, GBJ, (-7745, -4015), LR0, PK])])
    up = seq(p, [('g', [PK, LR0, (-7745, -4015), GBJ, XGB, NOS, NO, NOS, RIDGE, IH, IHT, IH, RIDGE, GWS, GW, GWS, IHJ, LRE, DAM, WRE]), ('m', FALLS_SPUR)])
    back = seq(p, [('g', [WRE, DAM, LRE, IHJ, (-7745, -4015), LR0, PK])])
    R['C'] = mk(p, up['pts'] + back['pts'][1:])
    for k in R: Park.smooth_E(R[k], 9); p.describe(R[k], k)
    return R
