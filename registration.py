import time
import numpy as np
import SimpleITK as sitk
from .io import image_center

def registration_method(fixed,moving,initial,kind,iterations=150,bspline_grid_mm=45.,seed=42):
    r=sitk.ImageRegistrationMethod()
    r.SetMetricAsMattesMutualInformation(numberOfHistogramBins=50)
    r.SetMetricSamplingStrategy(r.RANDOM);r.SetMetricSamplingPercentage(0.15,seed)
    r.SetInterpolator(sitk.sitkLinear)
    r.SetOptimizerAsGradientDescent(learningRate=1.0,numberOfIterations=iterations,convergenceMinimumValue=1e-6,convergenceWindowSize=10)
    r.SetOptimizerScalesFromPhysicalShift()
    r.SetShrinkFactorsPerLevel([4,2,1]);r.SetSmoothingSigmasPerLevel([2,1,0]);r.SmoothingSigmasAreSpecifiedInPhysicalUnitsOn()
    r.SetInitialTransform(initial,inPlace=True)
    start=time.perf_counter(); tx=r.Execute(fixed,moving)
    return tx,{'seconds':time.perf_counter()-start,'metric':r.GetMetricValue(),'iterations':r.GetOptimizerIteration(),'stop':r.GetOptimizerStopConditionDescription()}

def register(fixed,moving,iterations=150,grid_mm=45.,seed=42):
    # SimpleITK resampling requires a fixed->moving transform. These are accumulated in that direction.
    rigid0=sitk.CenteredTransformInitializer(fixed,moving,sitk.Euler3DTransform(),sitk.CenteredTransformInitializerFilter.GEOMETRY)
    rigid,info_r=registration_method(fixed,moving,rigid0,'rigid',iterations,seed=seed)
    aff0=sitk.AffineTransform(3)
    # Encode rigid into affine; optimization begins from the rigid mapping.
    aff0.SetMatrix(rigid.GetMatrix());aff0.SetTranslation(rigid.GetTranslation());aff0.SetCenter(rigid.GetCenter())
    affine,info_a=registration_method(fixed,moving,aff0,'affine',iterations,seed=seed)
    # B-spline fitted against affine-warped moving image; residual maps fixed -> affinely-warped image.
    moving_affine=warp(moving,fixed,affine,False)
    physical=np.asarray(fixed.GetSize())*np.asarray(fixed.GetSpacing())
    mesh=[max(1,int(round(x/grid_mm))) for x in physical]
    bs0=sitk.BSplineTransformInitializer(fixed,mesh,order=3)
    residual,info_b=registration_method(fixed,moving_affine,bs0,'bspline',iterations,seed=seed)
    # Composite order in SimpleITK is back-to-front: residual first, then affine.
    composed=sitk.CompositeTransform(3);composed.AddTransform(affine);composed.AddTransform(residual)
    return {'rigid':rigid,'affine':affine,'bspline':composed},{'rigid':info_r,'affine':info_a,'bspline':info_b,'grid_mm':grid_mm}

def warp(moving,fixed,transform,mask=False):
    return sitk.Resample(moving,fixed,transform,sitk.sitkNearestNeighbor if mask else sitk.sitkLinear,0 if mask else -1000,moving.GetPixelID())

def jacobian_qc(fixed,transform):
    disp=sitk.TransformToDisplacementField(transform,sitk.sitkVectorFloat64,fixed.GetSize(),fixed.GetOrigin(),fixed.GetSpacing(),fixed.GetDirection())
    jac=sitk.DisplacementFieldJacobianDeterminant(disp)
    vals=sitk.GetArrayViewFromImage(jac)
    return disp,jac,{'folding_voxels':int(np.count_nonzero(vals<=0)),'folding_fraction':float(np.mean(vals<=0)),'jacobian_min':float(np.min(vals)),'jacobian_max':float(np.max(vals))}
