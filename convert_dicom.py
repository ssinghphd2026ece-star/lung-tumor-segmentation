import argparse
from pathlib import Path
import SimpleITK as sitk
from lunggtv.io import write

def main():
    p=argparse.ArgumentParser();p.add_argument('--dicom-dir',required=True);p.add_argument('--series-id',default=None);p.add_argument('--out',required=True);a=p.parse_args()
    ids=sitk.ImageSeriesReader.GetGDCMSeriesIDs(a.dicom_dir)
    if not ids:raise RuntimeError('No DICOM series found')
    if len(ids)>1 and a.series_id is None:raise RuntimeError('Multiple series: select --series-id from '+str(ids))
    sid=a.series_id or ids[0]
    files=sitk.ImageSeriesReader.GetGDCMSeriesFileNames(a.dicom_dir,sid)
    reader=sitk.ImageSeriesReader();reader.SetFileNames(files);reader.MetaDataDictionaryArrayUpdateOn();reader.LoadPrivateTagsOn()
    img=reader.Execute()
    write(img,a.out)
    print(f'Converted {len(files)} slices; verify HU rescale and orientation before analysis')
if __name__=='__main__':main()
