import argparse,json
from pathlib import Path
import SimpleITK as sitk
from lunggtv.io import read,write,from_array,to_array
from lunggtv.prompts import prompt_data,prompt_volume,serializable_prompt

def main():
    p=argparse.ArgumentParser();p.add_argument('--mask',required=True);p.add_argument('--strategy',choices=['P1','P2','P3','P4','P5'],default='P5');p.add_argument('--out',required=True);a=p.parse_args()
    image=read(a.mask);data=prompt_data(to_array(image),a.strategy);path=Path(a.out);path.mkdir(parents=True,exist_ok=True)
    (path/'prompt.json').write_text(json.dumps(serializable_prompt(data),indent=2))
    write(from_array(prompt_volume(data),image,sitk.sitkUInt8),path/'prompt_mask.nii.gz')
if __name__=='__main__':main()
