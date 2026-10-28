import argparse
from pathlib import Path
import pandas as pd
import SimpleITK as sitk
from lunggtv.dataset import load_manifest
from lunggtv.io import read,ensure_geometry
from lunggtv.metrics import segmentation_metrics,volume_cm3

def main():
    p=argparse.ArgumentParser();p.add_argument('--manifest',required=True);p.add_argument('--pred-dir',required=True);p.add_argument('--method',required=True);p.add_argument('--out',default='outputs/scored.csv');a=p.parse_args()
    df=load_manifest(a.manifest);rows=[]
    for _,r in df.iterrows():
        if not str(r.target_gtv):continue
        gt=read(r.target_gtv);pred=read(Path(a.pred_dir)/str(r.pair_id)/(a.method+'_gtv.nii.gz'))
        # Evaluate on the ORIGINAL target grid, not on the resampled network grid.
        target=read(r.target_ct);ensure_geometry(target,gt)
        pred=sitk.Resample(pred,gt,sitk.Transform(),sitk.sitkNearestNeighbor,0,sitk.sitkUInt8)
        m=segmentation_metrics(sitk.GetArrayFromImage(pred),sitk.GetArrayFromImage(gt),gt.GetSpacing())
        rows.append({'pair_id':r.pair_id,'patient_id':r.patient_id,'method':a.method,'volume_cm3':volume_cm3(sitk.GetArrayFromImage(gt),gt.GetSpacing()),**m})
    out=Path(a.out);out.parent.mkdir(parents=True,exist_ok=True);pd.DataFrame(rows).to_csv(out,index=False)
    print(out)
if __name__=='__main__':main()
