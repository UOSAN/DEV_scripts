%-----------------------------------------------------------------------
% Job saved on 24-May-2022 13:54:32 by cfg_util (rev $Rev: 7345 $)
% spm SPM - SPM12 (7771):
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
matlabbatch{5}.spm.stats.fmri_spec.sess(1).scans(1) = cfg_dep('Expand image frames: Expanded filename list.', substruct('.','val', '{}',{3}, '.','val', '{}',{1}, '.','val', '{}',{1}), substruct('.','files'));
matlabbatch{5}.spm.stats.fmri_spec.sess(1).cond = struct('name', {}, 'onset', {}, 'duration', {}, 'tmod', {}, 'pmod', {}, 'orth', {});
matlabbatch{5}.spm.stats.fmri_spec.sess(1).multi = {'/projects/sanlab/shared/DEV/DEV_scripts/fMRI/fx/multiconds/SST/full_duration/posterror_cues_no_rt/DEV004_1_SST1.mat'};
matlabbatch{5}.spm.stats.fmri_spec.sess(1).regress = struct('name', {}, 'val', {});
matlabbatch{5}.spm.stats.fmri_spec.sess(1).multi_reg = {'/projects/sanlab/shared/DEV/bids_data/derivatives/auto-motion-fmriprep/sub-DEV004/sub-DEV004_ses-wave1_task-SST_acq-1_run-1_desc-motion_regressors.txt'};
matlabbatch{5}.spm.stats.fmri_spec.sess(1).hpf = 128;
matlabbatch{5}.spm.stats.fmri_spec.sess(2).scans(1) = cfg_dep('Expand image frames: Expanded filename list.', substruct('.','val', '{}',{4}, '.','val', '{}',{1}, '.','val', '{}',{1}), substruct('.','files'));
matlabbatch{5}.spm.stats.fmri_spec.sess(2).cond = struct('name', {}, 'onset', {}, 'duration', {}, 'tmod', {}, 'pmod', {}, 'orth', {});
matlabbatch{5}.spm.stats.fmri_spec.sess(2).multi = {'/projects/sanlab/shared/DEV/DEV_scripts/fMRI/fx/multiconds/SST/full_duration/posterror_cues_no_rt/DEV004_2_SST1.mat'};
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

condition_filepaths = {
    matlabbatch{5}.spm.stats.fmri_spec.sess(1).multi{1} ,
    matlabbatch{5}.spm.stats.fmri_spec.sess(2).multi{1}
    };

motion_filepaths = {
    matlabbatch{5}.spm.stats.fmri_spec.sess(1).multi_reg{1},
    matlabbatch{5}.spm.stats.fmri_spec.sess(2).multi_reg{1}
    };

main_betas = {
'CueFollowingCorrectStop',
'CueFollowingFailedStop',
'CorrectGoFollowingCorrectStop',
'CorrectGoFollowingFailedStop',
'CorrectStopPrecedingCorrectGo',
'FailedStopPrecedingCorrectGo',
'OtherCue',
'OtherCorrectGo',
'OtherCorrectStop',
'OtherFailedStop',
'OtherFailedGo'};

beta_matrix = struct;
for mb_i = 1:length(main_betas)
    mb = main_betas{mb_i};
    beta_matrix.(mb) = [];
end
wave_matrix = [];

CueFollowingCSmFS_matrix=[];
CueFollowingFSmCS_matrix = [];
CGFollowingCSmFS_matrix = [];
CGFollowingFSmCS_matrix = [];

for i = 1:numel(condition_filepaths) %iterate through the two sessiosn
    % for this session
    %get the multiconds
    multicond_mat = load(condition_filepaths{i});
    
    %count the number of motion regressors for this session
    dataTable = readtable(motion_filepaths{i}, 'Delimiter', '\t', 'ReadVariableNames', false);
    motion_colnum = width(dataTable);
    session_motion_regressor_count{i}=motion_colnum;

    
    % build concatenated matrices
    for mb_i = 1:length(main_betas)
        mb = main_betas{mb_i};
        multicond_mat.(mb) = cellfun(@(x) strcmp(x,mb), multicond_mat.names, 'UniformOutput', 1);
        has_mb.(mb)=sum(multicond_mat.(mb));
    end

    %save to our multicond array
    multicond_array{i} = multicond_mat;

    motion_matrix = zeros(1,motion_colnum);
    
    %last of all, develop a continuously concatenated matrix for the three
    for mb_i = 1:length(main_betas)
        mb = main_betas{mb_i};
        beta_matrix.(mb) = [beta_matrix.(mb) multicond_mat.(mb) motion_matrix];
    end

    %only adds this session to the matrix if it has both of the relevant
    %items
    %'CueFollowing(CS>FS)'
    session_CueFollowingCSmFS = (multicond_mat.CueFollowingCorrectStop-multicond_mat.CueFollowingFailedStop) * has_mb.('CueFollowingCorrectStop') * has_mb.('CueFollowingFailedStop'); 
    CueFollowingCSmFS_matrix  = [CueFollowingCSmFS_matrix session_CueFollowingCSmFS motion_matrix];

    %'CorrectGoFollowing(CS>FS)'
    session_CGFollowingCSmFS = (multicond_mat.CorrectGoFollowingCorrectStop-multicond_mat.CorrectGoFollowingFailedStop) * has_mb.('CorrectGoFollowingCorrectStop') * has_mb.('CorrectGoFollowingFailedStop'); 
    CGFollowingCSmFS_matrix  = [CGFollowingCSmFS_matrix session_CGFollowingCSmFS motion_matrix];

    %this just marks the waves
    wave_i_matrix = repmat(i,1,length(multicond_mat.names) + motion_colnum);
    wave_matrix = [wave_matrix wave_i_matrix];

end
%now do the wave contrasts
for mb_i = 1:length(main_betas)
    mb = main_betas{mb_i};
    %beta_matrix.(mb) = [beta_matrix.(mb) multicond_mat[mb] motion_matrix];
    main_betas_2_1.(mb) = beta_matrix.(mb).*(wave_matrix==2) - beta_matrix.(mb).*(wave_matrix==1);
end

%simple conditions (aggregated across multiple waves if available)
simple_condition_aggregates= {};
for mb_i = 1:length(main_betas)
    mb = main_betas{mb_i};
    simple_condition_aggregates = [simple_condition_aggregates; struct('name', mb, 'weights', beta_matrix.(mb))];
end
% contrasts between conditions
condition_contrasts = {
    struct('name', 'CueFollowing(CS>FS)', 'weights', CueFollowingCSmFS_matrix),
    struct('name', 'CueFollowing(FS>CS)', 'weights', -CueFollowingCSmFS_matrix),
    struct('name', 'CorrectGoFollowing(CS>FS)', 'weights', CGFollowingCSmFS_matrix),
    struct('name', 'CorrectGoFollowing(FS>CS)', 'weights', -CGFollowingCSmFS_matrix),
    };

%wave contrasts for each of the betas
wave_contrasts = {};
for mb_i = 1:length(main_betas)
    mb = main_betas{mb_i};
    name_2_1 = [mb '(W2-W1)'];
    wave_contrasts = [wave_contrasts; {struct('name', name_2_1, 'weights', main_betas_2_1.(mb))}];
    name_1_2 = [mb '(W1-W2)'];
    wave_contrasts = [wave_contrasts; {struct('name', name_1_2, 'weights', -main_betas_2_1.(mb))}];
end

contrasts = [
    simple_condition_aggregates, %simple conditions (aggregated across multiple waves if available)
    condition_contrasts, %contrasts between conditions
    wave_contrasts %contrasts between waves
    ];


use_contrast = logical([]);
% for each set of contrast weights, normalize to zero
% and also mark whether we will use the contrasts
%some of the contrasts might e completely zero (because there wasn't data
%avilable) and in that case, we'd exclude them
for i = 1:length(contrasts)
    % Normalize the weights so that the positive weights and negative
    % weights each sum to 1
    contrasts{i}.weights = normalizePosAndNeg(contrasts{i}.weights);
    use_contrast = [use_contrast sum(abs(contrasts{i}.weights))>0];
end

%filter to only the contrasts we'll use
contrasts_filtered = contrasts(use_contrast);

%now add the contrasts

%first the preamble apply to all of the 
if any(use_contrast)
     matlabbatch{7}.spm.stats.con.spmmat(1) = cfg_dep('Model estimation: SPM.mat File', substruct('.','val', '{}',{6}, '.','val', '{}',{1}, '.','val', '{}',{1}), substruct('.','spmmat'));
     matlabbatch{7}.spm.stats.con.delete = 0;
end

for i = 1:length(contrasts_filtered)
    matlabbatch{7}.spm.stats.con.consess{i}.tcon.name = contrasts_filtered{i}.name;
    matlabbatch{7}.spm.stats.con.consess{i}.tcon.weights = contrasts_filtered{i}.weights;
    matlabbatch{7}.spm.stats.con.consess{i}.tcon.sessrep = 'none';
end

