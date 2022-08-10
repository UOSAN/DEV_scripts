ROI = spm_read_vols(spm_vol('/Users/benjaminsmith/Google Drive/oregon/code/DEV_scripts/fMRI/fx/models/SST/level2/sphere_3-38_-70_-18.nii'));
indx = find(ROI>0);
[x,y,z] = ind2sub(size(ROI),indx);
ROI_XYZ = [x y z]';
FS_minus_CS_contrasts = mean(spm_get_data(SPM.xY.P, ROI_XYZ),2);
[h, p, ci, stats] = ttest(FS_minus_CS_contrasts)

%https://docs.google.com/spreadsheets/d/17cOExcbFp6K9AyGuHOwywQv8NWiwWcKkAo5qlYLfFP8/edit#gid=0

FS_minus_CS_contrasts_exclude_bad=[
    FS_minus_CS_contrasts(1:2);
    FS_minus_CS_contrasts(4:5);
    FS_minus_CS_contrasts(7:18);
    FS_minus_CS_contrasts(20:83);
    ];

[h, p, ci, stats] = ttest(FS_minus_CS_contrasts_exclude_bad)
