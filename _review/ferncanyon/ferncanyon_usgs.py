
import numpy as np, requests, io, json, math
from PIL import Image
d='/home/claude/parks/ferncanyon/'
M=np.load(d+'ferncanyon_dem.npy'); meta=json.load(open(d+'ferncanyon_meta.json'))
np.save(d+'terrarium_dem_backup.npy', M)
z=meta['z']; H,W=M.shape; R=6378137.0; C=2*math.pi*R
x0=meta['tx0']/2**z*C-C/2; x1=(meta['tx0']+W/256)/2**z*C-C/2
y0=C/2-meta['ty0']/2**z*C; y1=C/2-(meta['ty0']+H/256)/2**z*C
u='https://elevation.nationalmap.gov/arcgis/rest/services/3DEPElevation/ImageServer/exportImage'
r=requests.get(u,params=dict(bbox=f'{x0},{y1},{x1},{y0}',bboxSR=3857,imageSR=3857,size=f'{W},{H}',format='tiff',pixelType='F32',noData=-9999,interpolation='RSP_BilinearInterpolation',f='image'),timeout=170)
print(r.status_code, r.headers.get('content-type'), len(r.content))
im=Image.open(io.BytesIO(r.content)); A=np.array(im).astype(np.float32); print(A.shape, np.nanmin(A), np.nanmax(A))
land=(A>-100)&(A>0.5)
N=M.copy(); N[land]=A[land]
# sea: keep terrarium bathymetry but force <= -1 where USGS says no land
N[~land]=np.minimum(M[~land], -1.0)
np.save(d+'ferncanyon_dem.npy', N.astype(M.dtype)); print('replaced', land.sum(), (~land).sum())
