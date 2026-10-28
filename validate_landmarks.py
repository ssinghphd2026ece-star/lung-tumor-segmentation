import argparse
from pathlib import Path
import pandas as pd
import numpy as np
import SimpleITK as sitk
from lunggtv.landmarks import tre

def main():
    p=argparse.ArgumentParser();p.add_argument('--target-landmarks',required=True,help='CSV columns x,y,z (mm)');p.add_argument('--source-landmarks',required=True);p.add_argument('--transform',required=True);p.add_argument('--out',default='outputs/tre.csv');a=p.parse_args()
    ta=pd.read_csv(a.target_landmarks)[['x','y','z']].to_numpy();so=pd.read_csv(a.source_landmarks)[['x','y','z']].to_numpy()
    tx=sitk.ReadTransform(a.transform);errors=tre(ta,so,tx)
    path=Path(a.out);path.parent.mkdir(parents=True,exist_ok=True);pd.DataFrame({'landmark_id':np.arange(len(errors)),'tre_mm':errors}).to_csv(path,index=False)
    print('TRE mean ± SD (mm):',float(errors.mean()),float(errors.std(ddof=1)) if len(errors)>1 else 0.)
if __name__=='__main__':main()
