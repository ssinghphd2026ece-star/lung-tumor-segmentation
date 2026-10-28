import numpy as np
from lunggtv.prompts import prompt_data,prompt_volume
from lunggtv.metrics import segmentation_metrics,volume_cm3
from lunggtv.stats import holm,motion_group,volume_group

def test_prompts():
    a=np.zeros((20,20,20),bool);a[8:12,9:13,6:10]=1
    for strategy in ('P1','P2','P3','P4','P5'):
        p=prompt_data(a,strategy);assert p['strategy']==strategy
        assert prompt_volume(p).shape==a.shape
    assert prompt_volume(prompt_data(a,'P5')).sum()>=prompt_volume(prompt_data(a,'P4')).sum()

def test_metrics():
    a=np.zeros((8,8,8),bool);a[2:5,2:5,2:5]=1
    m=segmentation_metrics(a,a)
    assert m['dsc']==1 and m['hd95_mm']==0 and m['surface_dice']==1

def test_empty():
    z=np.zeros((5,5,5));assert segmentation_metrics(z,z)['dsc']==1

def test_volume():assert volume_cm3(np.ones((10,10,10)),(1,1,1))==1.

def test_groups():assert motion_group(5)=='moderate' and volume_group(51)=='large'

def test_holm():assert holm([0.01,0.04])[0]==0.02
