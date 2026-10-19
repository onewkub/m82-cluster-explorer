"""Reproject the six existing HST F435W reference images to the viewer's TAN plane.

These drizzled files retain stale SIP coefficients. Use the linear TAN WCS:
DRIZCORR=COMPLETE and catalogue X/Y->sky residuals independently verify it.
No star labels or research measurements are altered.
"""
from pathlib import Path
import argparse
import sys
import hashlib, json, warnings
import numpy as np
from astropy.io import fits
from astropy.wcs import WCS, FITSFixedWarning
from scipy.ndimage import map_coordinates
from PIL import Image

warnings.simplefilter('ignore', FITSFixedWarning)
sys.stdout.reconfigure(encoding='utf-8')
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'dist'/'data'
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--source', required=True, help='Folder containing pos1 through pos6 FITS subfolders')
args = parser.parse_args()
SOURCE = Path(args.source).expanduser().resolve()
meta=json.loads((OUT/'catalog.json').read_text(encoding='utf-8'))
a0,d0=np.deg2rad([meta['plane']['ra'],meta['plane']['dec']])
ARC=180/np.pi*3600

def project(ra,dec):
    a,d=np.deg2rad(ra),np.deg2rad(dec)
    den=np.sin(d0)*np.sin(d)+np.cos(d0)*np.cos(d)*np.cos(a-a0)
    return np.cos(d)*np.sin(a-a0)/den*ARC,(np.cos(d0)*np.sin(d)-np.sin(d0)*np.cos(d)*np.cos(a-a0))/den*ARC

def inverse(x,y):
    X,Y=x/ARC,y/ARC
    ra=a0+np.arctan2(X,np.cos(d0)-Y*np.sin(d0))
    dec=np.arctan2(np.sin(d0)+Y*np.cos(d0),np.sqrt((np.cos(d0)-Y*np.sin(d0))**2+X*X))
    return np.rad2deg(ra),np.rad2deg(dec)

def read_wcs(header):
    clean=header.copy()
    for key in list(clean):
        if any(key.startswith(prefix) for prefix in ('A_','B_','AP_','BP_')):
            del clean[key]
    return WCS(clean).celestial

files=sorted(SOURCE.glob('pos*/*_f435w_v1_ref.fits'))
assert len(files)==6
fields=[]
for path in files:
    with fits.open(path) as h:
        hdr=h[0].header
        assert hdr['DRIZCORR']=='COMPLETE' and hdr['FILTER2'].strip()=='F435W'
        w=read_wcs(hdr)
        height,width=h[0].data.shape
        world=w.wcs_pix2world([[-.5,-.5],[width-.5,-.5],[width-.5,height-.5],[-.5,height-.5]],0)
        x,y=project(world[:,0],world[:,1])
        table=fits.getdata(path.parent/f'hlsp_angst_hst_acs-wfc_10776-m82-{path.parent.name}_f555w-f814w_v1_gst.fits',1)[::100]
        ra,dec=w.wcs_pix2world(table['X'],table['Y'],1)
        residual=np.hypot((ra-table['RA'])*np.cos(np.deg2rad(table['DEC'])),dec-table['DEC'])*3600
        assert np.nanmax(residual)<.025, (path.name,float(np.nanmax(residual)))
        fields.append({'path':path,'wcs':w,'bounds':[x.min(),x.max(),y.min(),y.max()],
            'exposure':float(hdr['EXPTIME']),'medianResidual':float(np.nanmedian(residual)),
            'maxResidual':float(np.nanmax(residual))})

pixel=.15
xmin=np.floor(min(f['bounds'][0] for f in fields)/pixel)*pixel
xmax=np.ceil(max(f['bounds'][1] for f in fields)/pixel)*pixel
ymin=np.floor(min(f['bounds'][2] for f in fields)/pixel)*pixel
ymax=np.ceil(max(f['bounds'][3] for f in fields)/pixel)*pixel
width=int(round((xmax-xmin)/pixel));height=int(round((ymax-ymin)/pixel))
print('Mosaic pixels:',width,height,flush=True)
total=np.zeros((height,width),dtype=np.float32)
count=np.zeros((height,width),dtype=np.uint8)
for field in fields:
    with fits.open(field['path'],memmap=False) as hdus:
        raw=hdus[0].data.astype(np.float32)
    padding=float(np.nanmin(raw))
    valid=np.isfinite(raw)&(raw>padding+.01)
    assert padding < -1000
    # Exposure-normalized intensities, with one global display stretch later.
    data=np.where(valid,raw/field['exposure'],0).astype(np.float32)
    weight=valid.astype(np.float32)
    b=field['bounds']
    c0=max(0,int((xmax-b[1])/pixel)-2);c1=min(width,int((xmax-b[0])/pixel)+3)
    r0=max(0,int((ymax-b[3])/pixel)-2);r1=min(height,int((ymax-b[2])/pixel)+3)
    xs=xmax-(np.arange(c0,c1)+.5)*pixel
    for row in range(r0,r1,128):
        end=min(row+128,r1)
        ys=ymax-(np.arange(row,end)+.5)*pixel
        xx,yy=np.meshgrid(xs,ys)
        ra,dec=inverse(xx,yy)
        px,py=field['wcs'].wcs_world2pix(ra,dec,0)
        sampled=map_coordinates(data,[py,px],order=1,mode='constant',cval=0,prefilter=False)
        ws=map_coordinates(weight,[py,px],order=1,mode='constant',cval=0,prefilter=False)
        mask=ws>.99
        total[row:end,c0:c1]+=np.where(mask,sampled/np.maximum(ws,1e-6),0)
        count[row:end,c0:c1]+=mask
    print(field['path'].parent.name,'projected; astrometric residual median',field['medianResidual'],flush=True)
covered=count>0
np.divide(total,count,out=total,where=covered)
sample=total[::5,::5][covered[::5,::5]]
low,high=np.percentile(sample,[1,99.8])
soft=.035*(high-low)
image=np.arcsinh(np.maximum(total-low,0)/soft)/np.arcsinh((high-low)/soft)
gray=np.uint8(np.clip(image,0,1)*255)
rgba=np.stack([gray,gray,gray,np.uint8(covered)*255],axis=-1)
Image.fromarray(rgba).save(OUT/'hst-f435w.png',optimize=True)
metadata={'image':'hst-f435w.png','width':width,'height':height,'bounds':[xmin,xmax,ymin,ymax],
 'pixelArcsec':pixel,'filter':'F435W','label':'Hubble / ACS F435W',
 'credit':'HST ACS / ANGST reference images, program 10776; six fields from local FITS',
 'description':'Single-band monochrome mosaic; not an RGB NASA publicity image.',
 'stretch':{'type':'asinh','lowCountsPerSecond':float(low),'highCountsPerSecond':float(high),'softening':float(soft)},
 'registration':'Shared TAN plane; linear WCS of drizzled image; stale SIP removed.',
 'validation':{'cataloguePixelOrigin':1,'maxResidualArcsec':max(f['maxResidual'] for f in fields)},
 'sources':[{'file':f['path'].name,'sha256':hashlib.sha256(f['path'].read_bytes()).hexdigest(),
  'medianResidualArcsec':f['medianResidual'],'maxResidualArcsec':f['maxResidual']} for f in fields]}
(OUT/'background.json').write_text(json.dumps(metadata,indent=2),encoding='utf-8')
# A portable preview for image QA; original mosaic retains its full resolution.
preview=Image.fromarray(rgba);preview.thumbnail((1400,1400));preview.save(ROOT.parent/'m82-fits-mosaic-preview.png')
print('Saved',OUT/'hst-f435w.png','bytes',(OUT/'hst-f435w.png').stat().st_size,flush=True)
