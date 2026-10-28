import argparse
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

def main():
    p=argparse.ArgumentParser();p.add_argument('--metrics',required=True);p.add_argument('--out',default='outputs/figures');a=p.parse_args();df=pd.read_csv(a.metrics);out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
    for metric in ('dsc','hd95_mm','surface_dice'):
        if metric not in df.columns:continue
        agg=df.groupby('method')[metric].agg(['mean','std']).sort_values('mean')
        fig,ax=plt.subplots(figsize=(9,5));ax.bar(agg.index,agg['mean'],yerr=agg['std'].fillna(0),capsize=3);ax.set_ylabel(metric);ax.tick_params(axis='x',rotation=30);fig.tight_layout();fig.savefig(out/f'{metric}_methods.png',dpi=220);plt.close(fig)
    for group in ('volume_group','motion_group','phase'):
        if group not in df.columns or 'dsc' not in df.columns:continue
        tab=df.pivot_table(index=group,columns='method',values='dsc',aggfunc='mean')
        ax=tab.plot.bar(figsize=(10,5));ax.set_ylabel('Mean DSC');ax.figure.tight_layout();ax.figure.savefig(out/f'dsc_{group}.png',dpi=220);plt.close(ax.figure)
if __name__=='__main__':main()
