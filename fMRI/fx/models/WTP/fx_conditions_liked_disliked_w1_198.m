%-----------------------------------------------------------------------
% Job saved on 06-May-2019 21:13:12 by cfg_util (rev $Rev: 6942 $)
% spm SPM - SPM12 (7219)
% cfg_basicio BasicIO - Unknown
%-----------------------------------------------------------------------

matlabbatch{1}.cfg_basicio.file_dir.file_ops.file_fplist.dir = {'/Users/benjaminsmith/Google Drive/oregon/data/DEV/bids_data/derivatives/fmriprep_2022/sub-DEV198/ses-wave1/func/'};
matlabbatch{1}.cfg_basicio.file_dir.file_ops.file_fplist.filter = 's6_sub-DEV198_ses-wave1_task-WTP_acq-1_space-MNI152NLin2009cAsym_desc-preproc_bold.nii';
matlabbatch{1}.cfg_basicio.file_dir.file_ops.file_fplist.rec = 'FPList';
matlabbatch{2}.cfg_basicio.file_dir.file_ops.file_fplist.dir = {'/Users/benjaminsmith/Google Drive/oregon/data/DEV/bids_data/derivatives/fmriprep_2022/sub-DEV198/ses-wave1/func/'};
matlabbatch{2}.cfg_basicio.file_dir.file_ops.file_fplist.filter = 's6_sub-DEV198_ses-wave1_task-WTP_acq-2_space-MNI152NLin2009cAsym_desc-preproc_bold.nii';
matlabbatch{2}.cfg_basicio.file_dir.file_ops.file_fplist.rec = 'FPList';
matlabbatch{3}.cfg_basicio.file_dir.file_ops.file_fplist.dir = {'/Users/benjaminsmith/Google Drive/oregon/data/DEV/bids_data/derivatives/fmriprep_2022/sub-DEV198/ses-wave1/func/'};
matlabbatch{3}.cfg_basicio.file_dir.file_ops.file_fplist.filter = 's6_sub-DEV198_ses-wave1_task-WTP_acq-3_space-MNI152NLin2009cAsym_desc-preproc_bold.nii';
matlabbatch{3}.cfg_basicio.file_dir.file_ops.file_fplist.rec = 'FPList';
matlabbatch{4}.cfg_basicio.file_dir.file_ops.file_fplist.dir = {'/Users/benjaminsmith/Google Drive/oregon/data/DEV/bids_data/derivatives/fmriprep_2022/sub-DEV198/ses-wave1/func/'};
matlabbatch{4}.cfg_basicio.file_dir.file_ops.file_fplist.filter = 's6_sub-DEV198_ses-wave1_task-WTP_acq-4_space-MNI152NLin2009cAsym_desc-preproc_bold.nii';
matlabbatch{4}.cfg_basicio.file_dir.file_ops.file_fplist.rec = 'FPList';
matlabbatch{5}.spm.util.exp_frames.files(1) = cfg_dep('File Selector (Batch Mode): Selected Files (s6_sub-DEV198_ses-wave1_task-WTP_acq-1_space-MNI152NLin2009cAsym_desc-preproc_bold.nii)', substruct('.','val', '{}',{1}, '.','val', '{}',{1}, '.','val', '{}',{1}, '.','val', '{}',{1}), substruct('.','files'));
matlabbatch{5}.spm.util.exp_frames.frames = Inf;
matlabbatch{6}.spm.util.exp_frames.files(1) = cfg_dep('File Selector (Batch Mode): Selected Files (s6_sub-DEV198_ses-wave1_task-WTP_acq-2_space-MNI152NLin2009cAsym_desc-preproc_bold.nii)', substruct('.','val', '{}',{2}, '.','val', '{}',{1}, '.','val', '{}',{1}, '.','val', '{}',{1}), substruct('.','files'));
matlabbatch{6}.spm.util.exp_frames.frames = Inf;
matlabbatch{7}.spm.util.exp_frames.files(1) = cfg_dep('File Selector (Batch Mode): Selected Files (s6_sub-DEV198_ses-wave1_task-WTP_acq-3_space-MNI152NLin2009cAsym_desc-preproc_bold.nii)', substruct('.','val', '{}',{3}, '.','val', '{}',{1}, '.','val', '{}',{1}, '.','val', '{}',{1}), substruct('.','files'));
matlabbatch{7}.spm.util.exp_frames.frames = Inf;
matlabbatch{8}.spm.util.exp_frames.files(1) = cfg_dep('File Selector (Batch Mode): Selected Files (s6_sub-DEV198_ses-wave1_task-WTP_acq-4_space-MNI152NLin2009cAsym_desc-preproc_bold.nii)', substruct('.','val', '{}',{4}, '.','val', '{}',{1}, '.','val', '{}',{1}, '.','val', '{}',{1}), substruct('.','files'));
matlabbatch{8}.spm.util.exp_frames.frames = Inf;
matlabbatch{9}.spm.stats.fmri_spec.dir = {'/Users/benjaminsmith/Google Drive/oregon/data/DEV/nonbids_data/fMRI/fx/models/WTP/wave1/conditions_liked_disliked/sub-DEV198'};
matlabbatch{9}.spm.stats.fmri_spec.timing.units = 'secs';
matlabbatch{9}.spm.stats.fmri_spec.timing.RT = 2;
matlabbatch{9}.spm.stats.fmri_spec.timing.fmri_t = 72;
matlabbatch{9}.spm.stats.fmri_spec.timing.fmri_t0 = 36;
matlabbatch{9}.spm.stats.fmri_spec.sess(1).scans(1) = cfg_dep('Expand image frames: Expanded filename list.', substruct('.','val', '{}',{5}, '.','val', '{}',{1}, '.','val', '{}',{1}), substruct('.','files'));
matlabbatch{9}.spm.stats.fmri_spec.sess(1).cond = struct('name', {}, 'onset', {}, 'duration', {}, 'tmod', {}, 'pmod', {}, 'orth', {});
matlabbatch{9}.spm.stats.fmri_spec.sess(1).multi = {'/Users/benjaminsmith/Google Drive/oregon/code/DEV_scripts/fMRI/fx/multiconds/WTP/conditions_liked_disliked/DEV198_1_WTP1.mat'};
matlabbatch{9}.spm.stats.fmri_spec.sess(1).regress = struct('name', {}, 'val', {});
matlabbatch{9}.spm.stats.fmri_spec.sess(1).multi_reg = {'/Users/benjaminsmith/Google Drive/oregon/data/DEV/bids_data/derivatives/auto-motion-fmriprep/sub-DEV198/sub-DEV198_task-WTP_acq-1_run-1_desc-motion_regressors.txt'};
matlabbatch{9}.spm.stats.fmri_spec.sess(1).hpf = 128;
matlabbatch{9}.spm.stats.fmri_spec.sess(2).scans(1) = cfg_dep('Expand image frames: Expanded filename list.', substruct('.','val', '{}',{6}, '.','val', '{}',{1}, '.','val', '{}',{1}), substruct('.','files'));
matlabbatch{9}.spm.stats.fmri_spec.sess(2).cond = struct('name', {}, 'onset', {}, 'duration', {}, 'tmod', {}, 'pmod', {}, 'orth', {});
matlabbatch{9}.spm.stats.fmri_spec.sess(2).multi = {'/Users/benjaminsmith/Google Drive/oregon/code/DEV_scripts/fMRI/fx/multiconds/WTP/conditions_liked_disliked/DEV198_1_WTP2.mat'};
matlabbatch{9}.spm.stats.fmri_spec.sess(2).regress = struct('name', {}, 'val', {});
matlabbatch{9}.spm.stats.fmri_spec.sess(2).multi_reg = {'/Users/benjaminsmith/Google Drive/oregon/data/DEV/bids_data/derivatives/auto-motion-fmriprep/sub-DEV198/sub-DEV198_task-WTP_acq-2_run-1_desc-motion_regressors.txt'};
matlabbatch{9}.spm.stats.fmri_spec.sess(2).hpf = 128;
matlabbatch{9}.spm.stats.fmri_spec.sess(3).scans(1) = cfg_dep('Expand image frames: Expanded filename list.', substruct('.','val', '{}',{7}, '.','val', '{}',{1}, '.','val', '{}',{1}), substruct('.','files'));
matlabbatch{9}.spm.stats.fmri_spec.sess(3).cond = struct('name', {}, 'onset', {}, 'duration', {}, 'tmod', {}, 'pmod', {}, 'orth', {});
matlabbatch{9}.spm.stats.fmri_spec.sess(3).multi = {'/Users/benjaminsmith/Google Drive/oregon/code/DEV_scripts/fMRI/fx/multiconds/WTP/conditions_liked_disliked/DEV198_1_WTP3.mat'};
matlabbatch{9}.spm.stats.fmri_spec.sess(3).regress = struct('name', {}, 'val', {});
matlabbatch{9}.spm.stats.fmri_spec.sess(3).multi_reg = {'/Users/benjaminsmith/Google Drive/oregon/data/DEV/bids_data/derivatives/auto-motion-fmriprep/sub-DEV198/sub-DEV198_task-WTP_acq-3_run-1_desc-motion_regressors.txt'};
matlabbatch{9}.spm.stats.fmri_spec.sess(3).hpf = 128;
matlabbatch{9}.spm.stats.fmri_spec.sess(4).scans(1) = cfg_dep('Expand image frames: Expanded filename list.', substruct('.','val', '{}',{8}, '.','val', '{}',{1}, '.','val', '{}',{1}), substruct('.','files'));
matlabbatch{9}.spm.stats.fmri_spec.sess(4).cond = struct('name', {}, 'onset', {}, 'duration', {}, 'tmod', {}, 'pmod', {}, 'orth', {});
matlabbatch{9}.spm.stats.fmri_spec.sess(4).multi = {'/Users/benjaminsmith/Google Drive/oregon/code/DEV_scripts/fMRI/fx/multiconds/WTP/conditions_liked_disliked/DEV198_1_WTP4.mat'};
matlabbatch{9}.spm.stats.fmri_spec.sess(4).regress = struct('name', {}, 'val', {});
matlabbatch{9}.spm.stats.fmri_spec.sess(4).multi_reg = {'/Users/benjaminsmith/Google Drive/oregon/data/DEV/bids_data/derivatives/auto-motion-fmriprep/sub-DEV198/sub-DEV198_task-WTP_acq-4_run-1_desc-motion_regressors.txt'};
matlabbatch{9}.spm.stats.fmri_spec.sess(4).hpf = 128;
matlabbatch{9}.spm.stats.fmri_spec.fact = struct('name', {}, 'levels', {});
matlabbatch{9}.spm.stats.fmri_spec.bases.hrf.derivs = [0 0];
matlabbatch{9}.spm.stats.fmri_spec.volt = 1;
matlabbatch{9}.spm.stats.fmri_spec.global = 'None';
matlabbatch{9}.spm.stats.fmri_spec.mthresh = -Inf;
matlabbatch{9}.spm.stats.fmri_spec.mask = {'/Users/benjaminsmith/Google Drive/oregon/data/MNI152_T1_1mm_brain_mask.nii,1'};
matlabbatch{9}.spm.stats.fmri_spec.cvi = 'FAST';
matlabbatch{10}.spm.stats.fmri_est.spmmat(1) = cfg_dep('fMRI model specification: SPM.mat File', substruct('.','val', '{}',{9}, '.','val', '{}',{1}, '.','val', '{}',{1}, '.','val', '{}',{1}), substruct('.','spmmat'));
matlabbatch{10}.spm.stats.fmri_est.write_residuals = 0;
matlabbatch{10}.spm.stats.fmri_est.method.Classical = 1;
