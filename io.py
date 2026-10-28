from pathlib import Path
import numpy as np
import SimpleITK as sitk

def read(path):
    path = Path(path)
    if not path.exists(): raise FileNotFoundError(path)
    img = sitk.ReadImage(str(path))
    if img.GetDimension()!=3: raise ValueError(f'Expected 3D: {path}')
    return img

def write(img,path):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    sitk.WriteImage(img,str(path),True)

def to_array(img): return sitk.GetArrayFromImage(img)

def from_array(arr,reference,pixel=None):
    img=sitk.GetImageFromArray(arr)
    img.CopyInformation(reference)
    return sitk.Cast(img,pixel) if pixel is not None else img

def resample(img,spacing=(1.5,1.5,1.5),mask=False):
    old=np.asarray(img.GetSpacing(),float); new=np.asarray(spacing,float)
    size=np.maximum(1,np.rint(np.asarray(img.GetSize())*old/new).astype(int))
    f=sitk.ResampleImageFilter(); f.SetSize([int(x) for x in size]);f.SetOutputSpacing(tuple(map(float,new)))
    f.SetOutputOrigin(img.GetOrigin());f.SetOutputDirection(img.GetDirection());f.SetTransform(sitk.Transform())
    f.SetInterpolator(sitk.sitkNearestNeighbor if mask else sitk.sitkLinear)
    f.SetDefaultPixelValue(0 if mask else -1000)
    return f.Execute(img)

def preprocess_ct(img,spacing=(1.5,1.5,1.5)):
    # Inputs MUST already be in HU (DICOM conversion applies rescale slope/intercept).
    img=sitk.Clamp(sitk.Cast(img,sitk.sitkFloat32),sitk.sitkFloat32,-1000,1000)
    return resample(img,spacing,False)

def normalized_ct(img):
    return sitk.ShiftScale(img,shift=1000.,scale=1/2000.)

def ensure_geometry(image,mask,atol=1e-4):
    if image.GetSize()!=mask.GetSize() or not np.allclose(image.GetSpacing(),mask.GetSpacing(),atol=atol) or not np.allclose(image.GetOrigin(),mask.GetOrigin(),atol=atol) or not np.allclose(image.GetDirection(),mask.GetDirection(),atol=atol):
        raise ValueError('CT and mask geometry mismatch; resample mask into image geometry with an authenticated transform before use')

def image_center(img):
    return img.TransformContinuousIndexToPhysicalPoint([(s-1)/2 for s in img.GetSize()])
