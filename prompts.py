import numpy as np
from scipy.ndimage import binary_dilation

def prompt_data(mask,strategy='P5'):
    """Array ordering z,y,x. Returns masks and coordinates for external model adapters."""
    mask=np.asarray(mask)>0
    if not mask.any(): raise ValueError('Empty propagated GTV; cannot derive valid prompts')
    points=np.argwhere(mask);center=np.rint(points.mean(axis=0)).astype(int)
    z,y,x=map(int,center)
    use=binary_dilation(mask,iterations=1) if strategy=='P5' else mask
    bounds=np.stack((points.min(axis=0),points.max(axis=0)),axis=0).tolist()
    data={'strategy':strategy,'center_zyx':[z,y,x],'box_zyx':bounds,'shape_zyx':list(mask.shape)}
    if strategy=='P1': data['point_zyx']=[z,y,x]
    elif strategy=='P2': pass
    elif strategy in ('P3','P4','P5'):
        data['axial_index']=z;data['axial_mask']=use[z,:,:].astype(np.uint8)
        if strategy in ('P4','P5'):
            data['coronal_index']=y;data['coronal_mask']=use[:,y,:].astype(np.uint8)
            data['sagittal_index']=x;data['sagittal_mask']=use[:,:,x].astype(np.uint8)
    else:raise ValueError('strategy must be P1..P5')
    return data

def prompt_volume(prompt):
    """Sparse 3D prompt-mask image; P1/P2 are encoded separately by JSON."""
    out=np.zeros(prompt['shape_zyx'],np.uint8)
    if 'axial_mask' in prompt:out[prompt['axial_index'],:,:]=np.maximum(out[prompt['axial_index'],:,:],prompt['axial_mask'])
    if 'coronal_mask' in prompt:out[:,prompt['coronal_index'],:]=np.maximum(out[:,prompt['coronal_index'],:],prompt['coronal_mask'])
    if 'sagittal_mask' in prompt:out[:,:,prompt['sagittal_index']]=np.maximum(out[:,:,prompt['sagittal_index']],prompt['sagittal_mask'])
    return out

def serializable_prompt(prompt):
    return {k:(v.tolist() if isinstance(v,np.ndarray) else v) for k,v in prompt.items() if not k.endswith('_mask')}
