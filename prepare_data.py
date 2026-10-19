"""Export saved labels on a common tangent plane; do not rerun clustering."""
from pathlib import Path
import argparse
import json, hashlib
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--source', required=True, help='Folder containing the saved clustering CSV files')
args = parser.parse_args()
SOURCE = Path(args.source).expanduser().resolve()
OUT = ROOT / 'dist' / 'data'
OUT.mkdir(parents=True, exist_ok=True)
FILES = {'2d': 'm82_dwarf_galaxy_candidates_2d.csv',
         '3d': 'm82_clusters_3d_live.csv',
         'hdb': 'm82_dwarf_galaxy_candidates_2d_hdbscan.csv'}
frames = {key: pd.read_csv(SOURCE / name) for key, name in FILES.items()}
base = frames['2d']
for frame in frames.values():
    assert np.array_equal(base[['RA','DEC','MAG1_ACS','MAG2_ACS']].values,
                          frame[['RA','DEC','MAG1_ACS','MAG2_ACS']].values)
    assert np.array_equal(base.pop_type, frame.pop_type)
ra0, dec0 = 148.9721537674264, 69.68166574647661
ref = [149.1341, 69.7126]
def project(ra, dec):
    a,d = np.deg2rad(ra),np.deg2rad(dec)
    a0,d0 = np.deg2rad([ra0,dec0])
    c = np.sin(d0)*np.sin(d)+np.cos(d0)*np.cos(d)*np.cos(a-a0)
    return np.cos(d)*np.sin(a-a0)/c*206264.806247, (np.cos(d0)*np.sin(d)-np.sin(d0)*np.cos(d)*np.cos(a-a0))/c*206264.806247
def angular(ra,dec,rc,dc):
    a,d,r,t = (np.deg2rad(v) for v in (ra,dec,rc,dc))
    h = np.sin((d-t)/2)**2+np.cos(d)*np.cos(t)*np.sin((a-r)/2)**2
    return 2*np.arcsin(np.sqrt(np.clip(h,0,1)))*206264.806247
x,y=project(base.RA.values,base.DEC.values)
points=np.column_stack([x,y,base.RA,base.DEC,base.MAG1_ACS,base.MAG2_ACS]).astype('<f4')
points.tofile(OUT/'points.bin')
base[['RA','DEC']].to_numpy(dtype='<f8').tofile(OUT/'radec.bin')
(base.pop_type=='young').to_numpy(dtype=np.uint8).tofile(OUT/'population.bin')
quality=set(pd.read_csv(SOURCE/'candidates_quality_screening.csv').cluster.astype(int))
meta={'count':len(base),'plane':{'ra':ra0,'dec':dec0},'reference':{'ra':ref[0],'dec':ref[1],'xy':list(project(*ref))},
      'pcPerArcsec':17,'bounds':[float(x.min()),float(x.max()),float(y.min()),float(y.max())],
      'sources':{},'methods':{},'schema':['east_arcsec','north_arcsec','ra_deg','dec_deg','F555W_ACS','F814W_ACS']}
for key,frame in frames.items():
    labels=frame.cluster.to_numpy(dtype='<i2')
    labels.tofile(OUT/f'{key}.bin')
    clusters=[]
    for label,g in frame[frame.cluster>=0].groupby('cluster',sort=True):
        rc,dc=g.RA.mean(),g.DEC.mean()
        r=angular(g.RA.to_numpy(),g.DEC.to_numpy(),rc,dc)
        color=g.MAG1_ACS-g.MAG2_ACS
        pop=str(g.pop_type.iloc[0])
        clusters.append({'id':int(label),'name':f'{"Y" if pop=="young" else "O"}-{label}',
            'pop':pop,'n':len(g),'ra':rc,'dec':dc,'xy':list(project(rc,dc)),
            'rms':float(np.sqrt(np.mean(r*r))*17),'rmax':float(r.max()*17),
            'iqr':float(color.quantile(.75)-color.quantile(.25)),
            'offset':float(angular(np.array([rc]),np.array([dc]),*ref)[0]),
            'candidate':bool(key=='2d' and label in quality)})
    meta['methods'][key]={'clusters':clusters,'noise':int((labels<0).sum()),
        'young':sum(c['pop']=='young' for c in clusters),'old':sum(c['pop']=='old' for c in clusters)}
    path=SOURCE/FILES[key]
    meta['sources'][key]={'file':path.name,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
meta['sources']['quality']={'file':'candidates_quality_screening.csv','count':len(quality)}
(OUT/'catalog.json').write_text(json.dumps(meta,ensure_ascii=False,allow_nan=False,separators=(',',':')),encoding='utf-8')
assert [len(meta['methods'][k]['clusters']) for k in FILES]==[510,49,318]
c=next(c for c in meta['methods']['2d']['clusters'] if c['id']==1075)
assert c['n']==13 and abs(c['rms']-24.5873)<.01
print(json.dumps({'stars':len(base),'clusters':{k:len(v['clusters']) for k,v in meta['methods'].items()},'Y-1075':c},indent=2))
