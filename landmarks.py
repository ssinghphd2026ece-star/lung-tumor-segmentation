import numpy as np
import SimpleITK as sitk

def tre(target_xyz,source_xyz,fixed_to_moving_transform):
    """Points in physical mm (xyz). SITK transform maps target/fixed -> source/moving."""
    a=np.asarray(target_xyz,float);b=np.asarray(source_xyz,float)
    if a.shape!=b.shape or a.ndim!=2 or a.shape[1]!=3: raise ValueError('Expected matching Nx3 physical coordinates')
    transformed=np.asarray([fixed_to_moving_transform.TransformPoint(tuple(x)) for x in a])
    return np.linalg.norm(transformed-b,axis=1)
