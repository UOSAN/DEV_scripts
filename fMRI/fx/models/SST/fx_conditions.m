%-----------------------------------------------------------------------
% Job saved on 06-May-2019 21:13:12 by cfg_util (rev $Rev: 6942 $)
% spm SPM - SPM12 (7219)
% cfg_basicio BasicIO - Unknown
%-----------------------------------------------------------------------
matlabbatch{1}.cfg_basicio.file_dir.file_ops.file_fplist.dir = {'/projects/sanlab/shared/DEV/bids_data/derivatives/fmriprep_2022/sub-DEV004/ses-wave1/func/'};
matlabbatch{1}.cfg_basicio.file_dir.file_ops.file_fplist.filter = 's6_sub-DEV004_ses-wave1_task-SST_acq-1_space-MNI152NLin2009cAsym_preproc_bold.nii';
matlabbatch{1}.cfg_basicio.file_dir.file_ops.file_fplist.rec = 'FPList';
matlabbatch{5}.spm.util.exp_frames.files(1) = cfg_dep('File Selector (Batch Mode): Selected Files (s6_sub-DEV004_ses-wave1_task-SST_acq-1_space-MNI152NLin2009cAsym_preproc_bold.nii)', substruct('.','val', '{}',{1}, '.','val', '{}',{1}, '.','val', '{}',{1}, '.','val', '{}',{1}), substruct('.','files'));
matlabbatch{5}.spm.util.exp_frames.frames = Inf;
matlabbatch{9}.spm.stats.fmri_spec.dir = {'/projects/sanlab/shared/DEV/nonbids_data/fMRI/fx/models/SST/conditions/sub-DEV004'};
matlabbatch{9}.spm.stats.fmri_spec.timing.units = 'secs';
matlabbatch{9}.spm.stats.fmri_spec.timing.RT = 2;
matlabbatch{9}.spm.stats.fmri_spec.timing.fmri_t = 72;
matlabbatch{9}.spm.stats.fmri_spec.timing.fmri_t0 = 36;
matlabbatch{9}.spm.stats.fmri_spec.sess(1).scans(1) = cfg_dep('Expand image frames: Expanded filename list.', substruct('.','val', '{}',{5}, '.','val', '{}',{1}, '.','val', '{}',{1}), substruct('.','files'));
matlabbatch{9}.spm.stats.fmri_spec.sess(1).cond = struct('name', {}, 'onset', {}, 'duration', {}, 'tmod', {}, 'pmod', {}, 'orth', {});
matlabbatch{9}.spm.stats.fmri_spec.sess(1).multi = {'/projects/sanlab/shared/DEV/DEV_scripts/fMRI/fx/multiconds/SST/conditions/DEV004_1_SST1.mat'};
matlabbatch{9}.spm.stats.fmri_spec.sess(1).regress = struct('name', {}, 'val', {});
matlabbatch{9}.spm.stats.fmri_spec.sess(1).multi_reg = {'/projects/sanlab/shared/DEV/DEV_scripts/fMRI/fx/motion/auto-motion-fmriprep/rp_txt/rp_DEV004_1_SST_1.txt'};
matlabbatch{9}.spm.stats.fmri_spec.sess(1).hpf = 128;
matlabbatch{9}.spm.stats.fmri_spec.fact = struct('name', {}, 'levels', {});
matlabbatch{9}.spm.stats.fmri_spec.bases.hrf.derivs = [0 0];
matlabbatch{9}.spm.stats.fmri_spec.volt = 1;
matlabbatch{9}.spm.stats.fmri_spec.global = 'None';
matlabbatch{9}.spm.stats.fmri_spec.mthresh = -Inf;
matlabbatch{9}.spm.stats.fmri_spec.mask = {'/projects/sanlab/shared/spm12/canonical/MNI152_T1_1mm_brain_mask.nii,1'};
matlabbatch{9}.spm.stats.fmri_spec.cvi = 'FAST';
matlabbatch{10}.spm.stats.fmri_est.spmmat(1) = cfg_dep('fMRI model specification: SPM.mat File', substruct('.','val', '{}',{9}, '.','val', '{}',{1}, '.','val', '{}',{1}, '.','val', '{}',{1}), substruct('.','spmmat'));
matlabbatch{10}.spm.stats.fmri_est.write_residuals = 0;
matlabbatch{10}.spm.stats.fmri_est.method.Classical = 1;
