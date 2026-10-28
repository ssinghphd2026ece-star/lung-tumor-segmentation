import argparse,json
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from lunggtv.stats import compare_paired,holm

def main():
    p=argparse.ArgumentParser();p.add_argument('--metrics',required=True);p.add_argument('--out',default='outputs/analysis');p.add_argument('--baseline',default='bspline');p.add_argument('--refined',default='bspline+nninteractive');a=p.parse_args()
    df=pd.read_csv(a.metrics);out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
    fields=[x for x in ['dsc','hd50_mm','hd95_mm','assd_mm','surface_dice','precision','recall'] if x in df.columns]
    df.groupby('method')[fields].agg(['mean','std','count']).to_csv(out/'method_summary.csv')
    for group in ['volume_group','motion_group','phase']:
        if group in df.columns:df.groupby([group,'method'])[fields].agg(['mean','std','count']).to_csv(out/f'{group}_summary.csv')
    comparisons=[]
    for metric in fields:
        r=compare_paired(df,a.baseline,a.refined,metric);r['metric']=metric;comparisons.append(r)
    valid=[i for i,r in enumerate(comparisons) if r.get('p') is not None and np.isfinite(r['p'])]
    if valid:
        adjusted=holm([comparisons[i]['p'] for i in valid])
        for i,pval in zip(valid,adjusted):comparisons[i]['holm_p']=pval
    pd.DataFrame(comparisons).to_csv(out/'patient_level_tests.csv',index=False)
    if 'dsc' in df:
        pivot=df.pivot_table(index=['pair_id','patient_id'],columns='method',values='dsc').dropna(subset=[a.baseline,a.refined])
        pivot['delta_dsc']=pivot[a.refined]-pivot[a.baseline]
        pivot.to_csv(out/'dsc_gains.csv')
        print('Deteriorations:',sum(pivot.delta_dsc<0),'/',len(pivot))
    print('Analysis written:',out)
if __name__=='__main__':main()
