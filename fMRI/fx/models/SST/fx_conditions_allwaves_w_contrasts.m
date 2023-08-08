%-----------------------------------------------------------------------
% Job saved on 08-Aug-2023 09:25:20 by cfg_util (rev $Rev: 7345 $)
% spm SPM - SPM12 (7771)
% cfg_basicio BasicIO - Unknown
%-----------------------------------------------------------------------
matlabbatch{1}.cfg_basicio.file_dir.file_ops.file_fplist.dir = {'/projects/sanlab/shared/DEV/bids_data/derivatives/fmriprep_2022/sub-DEV004/ses-wave1/func/'};
matlabbatch{1}.cfg_basicio.file_dir.file_ops.file_fplist.filter = 's6_sub-DEV004_ses-wave1_task-SST_acq-1_space-MNI152NLin2009cAsym_desc-preproc_bold.nii';
matlabbatch{1}.cfg_basicio.file_dir.file_ops.file_fplist.rec = 'FPList';
matlabbatch{2}.cfg_basicio.file_dir.file_ops.file_fplist.dir = {'/projects/sanlab/shared/DEV/bids_data/derivatives/fmriprep_2022/sub-DEV004/ses-wave2/func/'};
matlabbatch{2}.cfg_basicio.file_dir.file_ops.file_fplist.filter = 's6_sub-DEV004_ses-wave2_task-SST_acq-1_space-MNI152NLin2009cAsym_desc-preproc_bold.nii';
matlabbatch{2}.cfg_basicio.file_dir.file_ops.file_fplist.rec = 'FPList';
matlabbatch{3}.spm.util.exp_frames.files(1) = cfg_dep('File Selector (Batch Mode): Selected Files (s6_sub-DEV004_ses-wave1_task-SST_acq-1_space-MNI152NLin2009cAsym_desc-preproc_bold.nii)', substruct('.','val', '{}',{1}, '.','val', '{}',{1}, '.','val', '{}',{1}, '.','val', '{}',{1}), substruct('.','files'));
matlabbatch{3}.spm.util.exp_frames.frames = Inf;
matlabbatch{4}.spm.util.exp_frames.files(1) = cfg_dep('File Selector (Batch Mode): Selected Files (s6_sub-DEV004_ses-wave2_task-SST_acq-1_space-MNI152NLin2009cAsym_desc-preproc_bold.nii)', substruct('.','val', '{}',{2}, '.','val', '{}',{1}, '.','val', '{}',{1}, '.','val', '{}',{1}), substruct('.','files'));
matlabbatch{4}.spm.util.exp_frames.frames = Inf;
matlabbatch{5}.spm.stats.fmri_spec.dir = {'/projects/sanlab/shared/DEV/nonbids_data/fMRI/fx/models/SST/all_waves/conditions/sub-DEV004'};
matlabbatch{5}.spm.stats.fmri_spec.timing.units = 'secs';
matlabbatch{5}.spm.stats.fmri_spec.timing.RT = 2;
matlabbatch{5}.spm.stats.fmri_spec.timing.fmri_t = 72;
matlabbatch{5}.spm.stats.fmri_spec.timing.fmri_t0 = 36;
matlabbatch{5}.spm.stats.fmri_spec.sess(1).scans(1) = cfg_dep('Expand image frames: Expanded filename list.', substruct('.','val', '{}',{3}, '.','val', '{}',{1}, '.','val', '{}',{1}), substruct('.','files'));
matlabbatch{5}.spm.stats.fmri_spec.sess(1).cond = struct('name', {}, 'onset', {}, 'duration', {}, 'tmod', {}, 'pmod', {}, 'orth', {});
matlabbatch{5}.spm.stats.fmri_spec.sess(1).multi = {'/projects/sanlab/shared/DEV/DEV_scripts/fMRI/fx/multiconds/SST/full_duration/conditions/DEV004_1_SST1.mat'};
matlabbatch{5}.spm.stats.fmri_spec.sess(1).regress = struct('name', {}, 'val', {});
matlabbatch{5}.spm.stats.fmri_spec.sess(1).multi_reg = {'/projects/sanlab/shared/DEV/bids_data/derivatives/auto-motion-fmriprep/sub-DEV004/sub-DEV004_ses-wave1_task-SST_acq-1_run-1_desc-motion_regressors.txt'};
matlabbatch{5}.spm.stats.fmri_spec.sess(1).hpf = 128;
matlabbatch{5}.spm.stats.fmri_spec.sess(2).scans(1) = cfg_dep('Expand image frames: Expanded filename list.', substruct('.','val', '{}',{4}, '.','val', '{}',{1}, '.','val', '{}',{1}), substruct('.','files'));
matlabbatch{5}.spm.stats.fmri_spec.sess(2).cond = struct('name', {}, 'onset', {}, 'duration', {}, 'tmod', {}, 'pmod', {}, 'orth', {});
matlabbatch{5}.spm.stats.fmri_spec.sess(2).multi = {'/projects/sanlab/shared/DEV/DEV_scripts/fMRI/fx/multiconds/SST/full_duration/conditions/DEV004_2_SST1.mat'};
matlabbatch{5}.spm.stats.fmri_spec.sess(2).regress = struct('name', {}, 'val', {});
matlabbatch{5}.spm.stats.fmri_spec.sess(2).multi_reg = {'/projects/sanlab/shared/DEV/bids_data/derivatives/auto-motion-fmriprep/sub-DEV004/sub-DEV004_ses-wave2_task-SST_acq-1_run-1_desc-motion_regressors.txt'};
matlabbatch{5}.spm.stats.fmri_spec.sess(2).hpf = 128;
matlabbatch{5}.spm.stats.fmri_spec.fact = struct('name', {}, 'levels', {});
matlabbatch{5}.spm.stats.fmri_spec.bases.hrf.derivs = [0 0];
matlabbatch{5}.spm.stats.fmri_spec.volt = 1;
matlabbatch{5}.spm.stats.fmri_spec.global = 'None';
matlabbatch{5}.spm.stats.fmri_spec.mthresh = -Inf;
matlabbatch{5}.spm.stats.fmri_spec.mask = {'/projects/sanlab/shared/spm12/canonical/MNI152_T1_1mm_brain_mask.nii,1'};
matlabbatch{5}.spm.stats.fmri_spec.cvi = 'FAST';
matlabbatch{6}.spm.stats.fmri_est.spmmat(1) = cfg_dep('fMRI model specification: SPM.mat File', substruct('.','val', '{}',{5}, '.','val', '{}',{1}, '.','val', '{}',{1}), substruct('.','spmmat'));
matlabbatch{6}.spm.stats.fmri_est.write_residuals = 0;
matlabbatch{6}.spm.stats.fmri_est.method.Classical = 1;
