%-----------------------------------------------------------------------
% Job saved on 24-May-2022 13:54:32 by cfg_util (rev $Rev: 7345 $)
% spm SPM - SPM12 (7771)
% cfg_basicio BasicIO - Unknown
%-----------------------------------------------------------------------
conditions_filepath = '/projects/sanlab/shared/DEV/DEV_scripts/fMRI/fx/multiconds/SST/full_duration/posterror_cues_no_rt/DEV004_1_SST1.mat';
matlabbatch{1}.cfg_basicio.file_dir.file_ops.file_fplist.dir = {'/projects/sanlab/shared/DEV/bids_data/derivatives/fmriprep/sub-DEV004/ses-wave1/func/'};
matlabbatch{1}.cfg_basicio.file_dir.file_ops.file_fplist.filter = 's6_sub-DEV004_ses-wave1_task-SST_acq-1_bold_space-MNI152NLin2009cAsym_preproc.nii';
matlabbatch{1}.cfg_basicio.file_dir.file_ops.file_fplist.rec = 'FPList';
matlabbatch{2}.spm.util.exp_frames.files(1) = cfg_dep('File Selector (Batch Mode): Selected Files (s6_sub-DEV004_ses-wave1_task-SST_acq-1_bold_space-MNI152NLin2009cAsym_preproc.nii)', substruct('.','val', '{}',{1}, '.','val', '{}',{1}, '.','val', '{}',{1}, '.','val', '{}',{1}), substruct('.','files'));
matlabbatch{2}.spm.util.exp_frames.frames = Inf;
matlabbatch{3}.spm.stats.fmri_spec.dir = {'/projects/sanlab/shared/DEV/nonbids_data/fMRI/fx/models/SST/wave1/posterror_cues_no_rt/sub-DEV004'};
matlabbatch{3}.spm.stats.fmri_spec.timing.units = 'secs';
matlabbatch{3}.spm.stats.fmri_spec.timing.RT = 2;
matlabbatch{3}.spm.stats.fmri_spec.timing.fmri_t = 72;
matlabbatch{3}.spm.stats.fmri_spec.timing.fmri_t0 = 36;
matlabbatch{3}.spm.stats.fmri_spec.sess.scans(1) = cfg_dep('Expand image frames: Expanded filename list.', substruct('.','val', '{}',{2}, '.','val', '{}',{1}, '.','val', '{}',{1}), substruct('.','files'));
matlabbatch{3}.spm.stats.fmri_spec.sess.cond = struct('name', {}, 'onset', {}, 'duration', {}, 'tmod', {}, 'pmod', {}, 'orth', {});
matlabbatch{3}.spm.stats.fmri_spec.sess.multi = {conditions_filepath};
matlabbatch{3}.spm.stats.fmri_spec.sess.regress = struct('name', {}, 'val', {});
matlabbatch{3}.spm.stats.fmri_spec.sess.multi_reg = {'/projects/sanlab/shared/DEV/DEV_scripts/fMRI/fx/motion/auto-motion-fmriprep/rp_txt/rp_DEV004_1_SST_1.txt'};
matlabbatch{3}.spm.stats.fmri_spec.sess.hpf = 128;
matlabbatch{3}.spm.stats.fmri_spec.fact = struct('name', {}, 'levels', {});
matlabbatch{3}.spm.stats.fmri_spec.bases.hrf.derivs = [0 0];
matlabbatch{3}.spm.stats.fmri_spec.volt = 1;
matlabbatch{3}.spm.stats.fmri_spec.global = 'None';
matlabbatch{3}.spm.stats.fmri_spec.mthresh = -Inf;
matlabbatch{3}.spm.stats.fmri_spec.mask = {'/projects/sanlab/shared/spm12/canonical/MNI152_T1_1mm_brain_mask.nii,1'};
matlabbatch{3}.spm.stats.fmri_spec.cvi = 'FAST';
matlabbatch{4}.spm.stats.fmri_est.spmmat(1) = cfg_dep('fMRI model specification: SPM.mat File', substruct('.','val', '{}',{3}, '.','val', '{}',{1}, '.','val', '{}',{1}), substruct('.','spmmat'));
matlabbatch{4}.spm.stats.fmri_est.write_residuals = 0;
matlabbatch{4}.spm.stats.fmri_est.method.Classical = 1;
matlabbatch{5}.spm.stats.con.spmmat(1) = cfg_dep('Model estimation: SPM.mat File', substruct('.','val', '{}',{4}, '.','val', '{}',{1}, '.','val', '{}',{1}), substruct('.','spmmat'));
%custom code--we have to decide on the fly which contrasts we want to add
conditions_mat = load(conditions_filepath);
contrast_iter = 1;
CueFCS_matrix = cellfun(@(x) strcmp(x,'CueFollowingCorrectStop'), conditions_mat.names, 'UniformOutput', 1);
CueFFS_matrix = cellfun(@(x) strcmp(x,'CueFollowingFailedStop'), conditions_mat.names, 'UniformOutput', 1);
CGFCS_matrix = cellfun(@(x) strcmp(x,'CorrectGoFollowingCorrectStop'), conditions_mat.names, 'UniformOutput', 1);
CGFFS_matrix = cellfun(@(x) strcmp(x,'CorrectGoFollowingFailedStop'), conditions_mat.names, 'UniformOutput', 1);
do_CueF_contrast = sum(CueFCS_matrix) && sum(CueFFS_matrix);
do_CGF_contrast = sum(CGFCS_matrix) && sum(CGFFS_matrix);
if do_CueF_contrast || do_CGF_contrast
    matlabbatch{5}.spm.stats.con.spmmat(1) = cfg_dep('Model estimation: SPM.mat File', substruct('.','val', '{}',{4}, '.','val', '{}',{1}, '.','val', '{}',{1}), substruct('.','spmmat'));
    matlabbatch{5}.spm.stats.con.delete = 0;
end
if do_CueF_contrast
	matlabbatch{5}.spm.stats.con.consess{contrast_iter}.tcon.name = 'CueFollowing(CS>FS)';
	matlabbatch{5}.spm.stats.con.consess{contrast_iter}.tcon.weights = CueFCS_matrix - CueFFS_matrix;
	matlabbatch{5}.spm.stats.con.consess{contrast_iter}.tcon.sessrep = 'none';
	matlabbatch{5}.spm.stats.con.consess{contrast_iter + 1}.tcon.name = 'CueFollowing(FS>CS)';
	matlabbatch{5}.spm.stats.con.consess{contrast_iter + 1}.tcon.weights = CueFFS_matrix - CueFCS_matrix;
	matlabbatch{5}.spm.stats.con.consess{contrast_iter + 1}.tcon.sessrep = 'none';
	contrast_iter = contrast_iter + 2;
end
if do_CGF_contrast
    matlabbatch{5}.spm.stats.con.consess{contrast_iter}.tcon.name = 'CorrectGoFollowing(CS>FS)';
    matlabbatch{5}.spm.stats.con.consess{contrast_iter}.tcon.weights = CGFCS_matrix - CGFFS_matrix;
    matlabbatch{5}.spm.stats.con.consess{contrast_iter}.tcon.sessrep = 'none';
    matlabbatch{5}.spm.stats.con.consess{contrast_iter + 1}.tcon.name = 'CorrectGoFollowing(FS>CS)';
    matlabbatch{5}.spm.stats.con.consess{contrast_iter + 1}.tcon.weights = CGFFS_matrix - CGFCS_matrix;
    matlabbatch{5}.spm.stats.con.consess{contrast_iter + 1}.tcon.sessrep = 'none';
end




