import argparse,subprocess,sys
from pathlib import Path
import yaml

def main():
    p=argparse.ArgumentParser();p.add_argument('--manifest',required=True);p.add_argument('--config',default='configs/default.yaml');p.add_argument('--model',default='nninteractive',choices=['nninteractive','medsam2']);p.add_argument('--out',default='outputs/ablation');a=p.parse_args()
    for strategy in ['P1','P2','P3','P4','P5']:
        cfg=yaml.safe_load(Path(a.config).read_text());cfg['prompt_strategy']=strategy
        out=Path(a.out)/strategy;out.mkdir(parents=True,exist_ok=True);config_path=out/'config.yaml';config_path.write_text(yaml.safe_dump(cfg))
        subprocess.run([sys.executable,'-m','scripts.run_pipeline','--manifest',a.manifest,'--config',str(config_path),'--out',str(out),'--models',a.model,'--subset','development'],check=True)
if __name__=='__main__':main()
