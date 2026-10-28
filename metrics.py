import numpy as np
from scipy.ndimage import binary_erosion,distance_transform_edt

def _surfaces(a,b,spacing_zyx):
    st=np.ones((3,3,3),dtype=bool)
    sa=a ^ binary_erosion(a,structure=st,border_value=0)
    sb=b ^ binary_erosion(b,structure=st,border_value=0)
    da=distance_transform_edt(~sa,sampling=spacing_zyx)[sb]
    db=distance_transform_edt(~sb,sampling=spacing_zyx)[sa]
    return da,db

def segmentation_metrics(pred,gt,spacing_xyz=(1.5,1.5,1.5),tolerance_mm=2.):
    a=np.asarray(pred)>0;b=np.asarray(gt)>0
    if a.shape!=b.shape:raise ValueError('Shapes differ')
    na=int(a.sum());nb=int(b.sum());tp=int(np.logical_and(a,b).sum())
    if na==0 and nb==0:
        return dict(dsc=1.,precision=1.,recall=1.,hd50_mm=0.,hd95_mm=0.,assd_mm=0.,surface_dice=1.)
    if na==0 or nb==0:
        return dict(dsc=0.,precision=0. if na else 1.,recall=0. if nb else 1.,hd50_mm=np.nan,hd95_mm=np.nan,assd_mm=np.nan,surface_dice=0.)
    d1,d2=_surfaces(a,b,tuple(reversed(spacing_xyz)))
    joined=np.concatenate((d1,d2)); sd=(np.count_nonzero(d1<=tolerance_mm)+np.count_nonzero(d2<=tolerance_mm))/(len(d1)+len(d2))
    return dict(dsc=2*tp/(na+nb),precision=tp/na,recall=tp/nb,hd50_mm=float(np.percentile(joined,50)),hd95_mm=float(np.percentile(joined,95)),assd_mm=float(joined.mean()),surface_dice=float(sd))

def volume_cm3(mask,spacing_xyz):return float(np.count_nonzero(mask)*np.prod(spacing_xyz)/1000.)
