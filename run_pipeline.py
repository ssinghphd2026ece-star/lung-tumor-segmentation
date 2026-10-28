import argparse,json,time
from pathlib import Path
import pandas as pd
import numpy as np
import yaml
import SimpleITK as sitk
from lunggtv.dataset import load_manifest
from lunggtv.io import read,write,resample,preprocess_ct,normalized_ct,to_array,from_array,ensure_geometry
from lunggtv.registration import register,warp,jacobian_qc
from lunggtv.prompts import prompt_data,prompt_volume,serializable_prompt
from lunggtv.metrics import segmentation_metrics,volume_cm3
from lunggtv.adapter import refine
from lunggtv.stats import volume_group,motion_group

def process(row,args,cfg):
    out=Path(args.out)/str(row.pair_id);out.mkdir(parents=True,exist_ok=True)
    t0=time.perf_counter();reference=read(row.reference_ct);target=read(row.target_ct);gtv=read(row.reference_gtv)
    ensure_geometry(reference,gtv)
    target_gt=read(row.target_gtv) if str(row.target_gtv) else None
    if target_gt is not None:ensure_geometry(target,target_gt)
    spacing=cfg['spacing_mm'];fixed=preprocess_ct(target,spacing);moving=preprocess_ct(reference,spacing)
    label=resample(gtv,spacing,True)
    # Resampling to own grid vs CT may introduce shape discrepancies if source masks have different geometry.
    ensure_geometry(moving,label)
    if target_gt is not None:
        truth=resample(target_gt,spacing,True);ensure_geometry(fixed,truth)
    else:truth=None
    preparation=time.perf_counter()-t0
    transforms,reg_info=register(fixed,moving,cfg['registration_iterations'],cfg['bspline_grid_mm'],cfg['seed'])
    (out/'registration.json').write_text(json.dumps(reg_info,indent=2))
    write(fixed,out/'target_ct_hu.nii.gz');write(normalized_ct(fixed),out/'target_ct_normalized.nii.gz')
    if truth is not None:write(truth,out/'target_gtv.nii.gz')
    rows=[];base_masks={}
    for stage,tx in transforms.items():
        sitk.WriteTransform(tx,str(out/f'{stage}.tfm'))
        predicted=warp(label,fixed,tx,True)>0
        write(sitk.Cast(predicted,sitk.sitkUInt8),out/f'{stage}_gtv.nii.gz')
        base_masks[stage]=predicted
        record={'pair_id':row.pair_id,'patient_id':row.patient_id,'pair_type':row.pair_type,'subset':row.subset,'method':stage,'motion_mm':float(row.motion_mm) if 'motion_mm' in row.index and str(row.motion_mm) else np.nan,'phase':str(row.respiratory_phase) if 'respiratory_phase' in row.index else '', 'volume_cm3':volume_cm3(to_array(truth) if truth is not None else to_array(predicted),fixed.GetSpacing())}
        record['volume_group']=volume_group(record['volume_cm3']);record['motion_group']=motion_group(record['motion_mm'])
        if truth is not None:record.update(segmentation_metrics(to_array(predicted),to_array(truth),fixed.GetSpacing(),cfg['surface_tolerance_mm']))
        rows.append(record)
    disp,jac,qa=jacobian_qc(fixed,transforms['bspline']);write(jac,out/'jacobian.nii.gz');write(disp,out/'displacement.nii.gz')
    (out/'jacobian_qc.json').write_text(json.dumps(qa,indent=2))
    for stage in ['rigid','affine','bspline'] if args.all_stages else ['bspline']:
        if not np.any(to_array(base_masks[stage])):continue
        prompts=prompt_data(to_array(base_masks[stage]),cfg['prompt_strategy'])
        write(from_array(prompt_volume(prompts),fixed,sitk.sitkUInt8),out/f'{stage}_prompt.nii.gz')
        (out/f'{stage}_prompt.json').write_text(json.dumps(serializable_prompt(prompts),indent=2))
        for model in args.models:
            result=refine(model,cfg['models'].get(model+'_command'),out/'target_ct_normalized.nii.gz',out/f'{stage}_prompt.nii.gz',out/f'{stage}_prompt.json',out/f'{stage}_{model}_gtv.nii.gz')
            rec=rows[['rigid','affine','bspline'].index(stage)].copy();rec['method']=stage+'+'+model
            if truth is not None:rec.update(segmentation_metrics(to_array(result),to_array(truth),fixed.GetSpacing(),cfg['surface_tolerance_mm']))
            rows.append(rec)
    return rows,{'pair_id':row.pair_id,'preprocess_seconds':preparation,'registration':reg_info,'jacobian':qa}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--manifest',required=True);ap.add_argument('--config',default='configs/default.yaml');ap.add_argument('--out',default='outputs');ap.add_argument('--models',nargs='*',choices=['nninteractive','medsam2'],default=[]);ap.add_argument('--all-stages',action='store_true');ap.add_argument('--subset',choices=['development','evaluation','all'],default='all');args=ap.parse_args()
    cfg=yaml.safe_load(Path(args.config).read_text());df=load_manifest(args.manifest)
    if args.subset!='all':df=df[df.subset==args.subset]
    records=[];qc=[]
    for _,row in df.iterrows():
        print('Processing',row.pair_id,flush=True)
        r,q=process(row,args,cfg);records+=r;qc.append(q)
        Path(args.out).mkdir(parents=True,exist_ok=True)
        pd.DataFrame(records).to_csv(Path(args.out)/'pair_metrics.csv',index=False)
        (Path(args.out)/'quality_control.json').write_text(json.dumps(qc,indent=2))
    print(f'Processed {len(df)} pairs. Results: {args.out}')
if __name__=='__main__':main()
