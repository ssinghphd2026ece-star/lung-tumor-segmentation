import numpy as np
import pandas as pd
from scipy.stats import wilcoxon,spearmanr,friedmanchisquare

def patient_level(data,metric='dsc'):
    df=pd.DataFrame(data)
    return df.groupby(['patient_id','method'],as_index=False)[metric].mean()

def compare_paired(data,method_a,method_b,metric='dsc'):
    pt=patient_level(data,metric).pivot(index='patient_id',columns='method',values=metric)
    pt=pt[[method_a,method_b]].dropna()
    if len(pt)<2:return {'n_patients':len(pt),'p':None}
    delta=pt[method_b]-pt[method_a]
    try:p=float(wilcoxon(delta).pvalue) if np.any(delta) else 1.
    except ValueError:p=np.nan
    return {'n_patients':len(pt),'mean_difference':float(delta.mean()),'p':p}

def holm(pvalues):
    p=np.array(pvalues,float);n=len(p);order=np.argsort(p);corrected=np.zeros(n);prior=0.
    for rank,i in enumerate(order):
        prior=max(prior,min(1.,(n-rank)*p[i]));corrected[i]=prior
    return corrected.tolist()

def motion_group(mm):
    if not np.isfinite(mm):return 'unknown'
    return 'low' if mm<5 else ('moderate' if mm<=10 else 'high')

def volume_group(v):return 'small' if v<10 else ('medium' if v<=50 else 'large')
