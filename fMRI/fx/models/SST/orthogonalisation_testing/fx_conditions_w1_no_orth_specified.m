%-----------------------------------------------------------------------
% Job saved on 11-Sep-2021 12:22:38 by cfg_util (rev $Rev: 7345 $)
% spm SPM - SPM12 (7771)
% cfg_basicio BasicIO - Unknown
%-----------------------------------------------------------------------
%s6_sub-DEV004_ses-wave1_task-SST_acq-1_bold_space-MNI152NLin2009cAsym_preproc.nii
%s6_sub-DEV004_ses-wave1_task-SST_acq-1_bold_space-MNI152NLin2009cAsym_preproc.nii
DEV_path = '/Users/benjaminsmith/Google Drive/oregon/data/DEV'
DEV_scripts_path = '/Users/benjaminsmith/Google Drive/oregon/code/DEV_scripts'
disp([DEV_path '/bids_data/derivatives/fmriprep/sub-DEV004/ses-wave1/func/']);
matlabbatch{1}.cfg_basicio.file_dir.file_ops.file_fplist.dir = {[DEV_path '/bids_data/derivatives/fmriprep/sub-DEV004/ses-wave1/func/']};
matlabbatch{1}.cfg_basicio.file_dir.file_ops.file_fplist.filter = 's6_sub-DEV004_ses-wave1_task-SST_acq-1_bold_space-MNI152NLin2009cAsym_preproc.nii';
matlabbatch{1}.cfg_basicio.file_dir.file_ops.file_fplist.rec = 'FPList';
matlabbatch{2}.spm.util.exp_frames.files = cfg_dep('File Selector (Batch Mode): Selected Files (s6_sub-DEV004_ses-wave1_task-SST_acq-1_bold_space-MNI152NLin2009cAsym_preproc.nii)', substruct('.','val', '{}',{1}, '.','val', '{}',{1}, '.','val', '{}',{1}, '.','val', '{}',{1}), substruct('.','files'));
matlabbatch{2}.spm.util.exp_frames.frames = Inf;
matlabbatch{3}.spm.stats.fmri_spec.dir = {[DEV_path '/nonbids_data/fMRI/fx/models/SST/wave1/conditions/sub-DEV004/orth_testing/no_orth_specified']};
matlabbatch{3}.spm.stats.fmri_spec.timing.units = 'secs';
matlabbatch{3}.spm.stats.fmri_spec.timing.RT = 2;
matlabbatch{3}.spm.stats.fmri_spec.timing.fmri_t = 72;
matlabbatch{3}.spm.stats.fmri_spec.timing.fmri_t0 = 36;
matlabbatch{3}.spm.stats.fmri_spec.sess.scans(1) = cfg_dep('Expand image frames: Expanded filename list.', substruct('.','val', '{}',{2}, '.','val', '{}',{1}, '.','val', '{}',{1}), substruct('.','files'));
matlabbatch{3}.spm.stats.fmri_spec.sess.cond = struct('name', {}, 'onset', {}, 'duration', {}, 'tmod', {}, 'pmod', {}, 'orth', {});
matlabbatch{3}.spm.stats.fmri_spec.sess.multi = {[DEV_scripts_path '/fMRI/fx/models/SST/orthogonalisation_testing/DEV004_1_SST1_no_orth_specified.mat']};
matlabbatch{3}.spm.stats.fmri_spec.sess.regress = struct('name', {}, 'val', {});
matlabbatch{3}.spm.stats.fmri_spec.sess.multi_reg = {[DEV_scripts_path '/fMRI/fx/motion/auto-motion-fmriprep/rp_txt/rp_DEV004_1_SST_1.txt']};
matlabbatch{3}.spm.stats.fmri_spec.sess.hpf = 128;
matlabbatch{3}.spm.stats.fmri_spec.fact = struct('name', {}, 'levels', {});
matlabbatch{3}.spm.stats.fmri_spec.bases.hrf.derivs = [0 0];
matlabbatch{3}.spm.stats.fmri_spec.volt = 1;
matlabbatch{3}.spm.stats.fmri_spec.global = 'None';
matlabbatch{3}.spm.stats.fmri_spec.mthresh = -Inf;
matlabbatch{3}.spm.stats.fmri_spec.mask = {'/Users/benjaminsmith/Google Drive/oregon/data/MNI152_T1_1mm_brain_mask.nii,1'};
matlabbatch{3}.spm.stats.fmri_spec.cvi = 'FAST';
matlabbatch{4}.spm.stats.fmri_est.spmmat(1) = cfg_dep('fMRI model specification: SPM.mat File', substruct('.','val', '{}',{3}, '.','val', '{}',{1}, '.','val', '{}',{1}), substruct('.','spmmat'));
matlabbatch{4}.spm.stats.fmri_est.write_residuals = 0;
matlabbatch{4}.spm.stats.fmri_est.method.Classical = 1;
