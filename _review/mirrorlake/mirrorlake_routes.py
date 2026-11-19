
from lib import *
import math
p = Park('mirrorlake', 37.7400, -119.5600)
TH = (-40, -120)       # Mirror Lake trailhead, shuttle stop 17, where the paved service road leaves Happy Isles Loop Road (approx)
PE = (2640, 2330)      # end of the paved road at Mirror Lake (approx, near interpretive exhibits)
NB = (2758, 3550)      # footbridge on the north-side trail (OSM bridge)
SCJ = (6073, 6977)     # Snow Creek Trail junction (OSM way end)
EB = (7373, 7080)      # east footbridge over Tenaya Creek (OSM bridge)
SJ = (5742, 11997)     # junction near Snow Creek (OSM way ends)
FB = (5975, 12281)     # Snow Creek footbridge (OSM bridge)
SS = (515, 602)        # south-side trail meets the valley trails
# PAVED: prefer the paved Mirror Lake service road (OSM way 292254779, closed to cars) over the parallel paths
for u, v, dd in p.G.edges(data=True):
    if dd.get('wid') == '292254779': dd['w'] = math.dist(p.xy(u), p.xy(v)) * 0.5
R = {}
VP0 = (2727, 3082)  # OSM viewpoint on the west shore of Mirror Lake
R['A'] = route_xy(p, TH, PE, VP0)
R['B'] = route_xy(p, TH, PE, NB, SCJ, EB, (4000, 4300), SS, TH)
R['C'] = route_xy(p, TH, PE, NB, SCJ, SJ, FB)
