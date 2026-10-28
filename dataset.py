import json
from pathlib import Path
import pandas as pd

REQUIRED=['pair_id','patient_id','pair_type','reference_ct','reference_gtv','target_ct','target_gtv','subset']
def load_manifest(path):
    csv=Path(path);df=pd.read_csv(csv).fillna('')
    missing=set(REQUIRED)-set(df.columns)
    if missing:raise ValueError(f'Missing columns: {missing}')
    if df.pair_id.duplicated().any():raise ValueError('Duplicate pair_id')
    if not df.subset.isin(['development','evaluation']).all():raise ValueError('subset must be development or evaluation')
    if set(df[df.subset=='development'].patient_id)&set(df[df.subset=='evaluation'].patient_id):
        raise ValueError('Patient leakage between development and evaluation')
    for col in ('reference_ct','reference_gtv','target_ct','target_gtv'):
        for value in df[col]:
            if value and not Path(value).exists():raise FileNotFoundError(f'{col}: {value}')
    return df
