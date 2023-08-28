

import nibabel as nib
import nilearn as nil
from nilearn import plotting

from socket import gethostname
from yaml.loader import SafeLoader
import yaml

print(gethostname())
# Open the file and load the file
with open('config.yml') as f:
    all_yaml = yaml.load(f, Loader=SafeLoader)
    if gethostname() in all_yaml.keys():
        config = all_yaml[gethostname()]
    else:
        config = all_yaml['default']
        
print(config)
        
#dev_scripts_abs_path = config['l2_analysis_files']
l2_analysis_files = config['l2_analysis_files']
#posterror_folder = 'posterror_cues_no_rt_20230616'
posterror_folder = 'posterror_cues_no_rt_20230821'

cluster_folderpath = l2_analysis_files + '/SST/' + posterror_folder + '/CueFollowing(CS>FS)'
# roi file to open
roi_files = [cluster_folderpath + '/CueFollowing(CS>FS)striatal_cluster_1.nii',
cluster_folderpath + '/CueFollowing(CS>FS)striatal_cluster_2.nii']
# load each of the roi files
 
roi_data = []
for roi_file in roi_files:
    print(roi_file)
    ni_file = nib.load(roi_file)
    #binarize roi using nilearn
    ni_file = nil.image.math_img("img > 0", img=ni_file)
    roi_data = roi_data + [ni_file]
    #display the roi
    #plotting.plot_roi(ni_file, title=roi_file)
    print("displayed")
#combine the rois
#concatenate them
combined_roi_data = nil.image.concat_imgs(roi_data)
#then add them
combined_roi_data = nil.image.math_img("np.sum(imgs, axis=3)", imgs=combined_roi_data)

plotting.plot_roi(combined_roi_data, title="combined")
#save the combined roi
combined_roi_data.to_filename(
    cluster_folderpath + '/CueFollowing(CS>FS)striatal_cluster_combined.nii')

    


