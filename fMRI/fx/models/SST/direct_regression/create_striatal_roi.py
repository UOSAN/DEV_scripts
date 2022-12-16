

import nibabel as nib
import nilearn as nil
from nilearn import plotting

# roi file to open
roi_files = ['/Users/benjaminsmith/Google Drive/oregon/code/DEV_scripts/fMRI/fx/models/SST/level2/posterror_cues_no_rt_20221207/CueFollowing(CS>FS)/CueFollowing(CS>FS)striatal_cluster_1.nii',
'/Users/benjaminsmith/Google Drive/oregon/code/DEV_scripts/fMRI/fx/models/SST/level2/posterror_cues_no_rt_20221207/CueFollowing(CS>FS)/CueFollowing(CS>FS)striatal_cluster_2.nii']
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
    '/Users/benjaminsmith/Google Drive/oregon/code/DEV_scripts/fMRI/fx/models/SST/level2/posterror_cues_no_rt_20221207/CueFollowing(CS>FS)/CueFollowing(CS>FS)striatal_cluster_combined.nii')

    


