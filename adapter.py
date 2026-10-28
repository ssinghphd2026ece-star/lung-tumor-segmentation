"""Safe external executable adapter: runs actual installed nnInteractive / MedSAM2 wrapper supplied by user.

No fake/refinement heuristic is used. Wrapper must write a binary prediction aligned with target CT.
"""
from pathlib import Path
import subprocess,shlex
import SimpleITK as sitk
from .io import read,ensure_geometry

def refine(model,command_template,ct_path,prompt_mask_path,prompt_json_path,output_path,timeout=3600):
    if model=='none':return None
    if not command_template:
        raise RuntimeError(f'{model} selected but no model adapter command supplied. See adapters/README.md; actual model checkpoints are required.')
    allowed={'ct':str(Path(ct_path).resolve()),'prompt_mask':str(Path(prompt_mask_path).resolve()),'prompt_json':str(Path(prompt_json_path).resolve()),'output':str(Path(output_path).resolve()),'model':model}
    command=command_template.format(**allowed)
    subprocess.run(shlex.split(command),check=True,timeout=timeout)
    if not Path(output_path).exists(): raise RuntimeError(f'{model} adapter did not create {output_path}')
    out=read(output_path);ensure_geometry(read(ct_path),out)
    return out
