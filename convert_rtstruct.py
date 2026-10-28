import argparse
from pathlib import Path
import numpy as np
import SimpleITK as sitk
from rt_utils import RTStructBuilder
from lunggtv.io import read,write

def main():
    p=argparse.ArgumentParser();p.add_argument('--dicom-dir',required=True);p.add_argument('--rtstruct',required=True);p.add_argument('--roi',required=True);p.add_argument('--reference-ct',required=True);p.add_argument('--out',required=True);a=p.parse_args()
    rt=RTStructBuilder.create_from(dicom_series_path=a.dicom_dir,rt_struct_path=a.rtstruct)
    print('Available ROI names:',rt.get_roi_names())
    mask=rt.get_roi_mask_by_name(a.roi) # rt-utils returns row,column,slice; verify geometry!
    reference=read(a.reference_ct)
    expected=(reference.GetSize()[1],reference.GetSize()[0],reference.GetSize()[2])
    if mask.shape!=expected:raise ValueError(f'RTSTRUCT {mask.shape} incompatible with reference CT {expected}')
    # rt-utils mask rows, columns, slices -> SITK z,y,x
    arr=np.transpose(mask,(2,0,1)).astype(np.uint8)
    img=sitk.GetImageFromArray(arr);img.CopyInformation(reference)
    write(img,a.out)
    print('IMPORTANT: visually verify RTSTRUCT orientation, contours and frame-of-reference UID before eligibility')
if __name__=='__main__':main()
