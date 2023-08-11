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



condition_filepaths = {
    matlabbatch{5}.spm.stats.fmri_spec.sess(1).multi{1} ,
    matlabbatch{5}.spm.stats.fmri_spec.sess(2).multi{1}
    };



motion_filepaths = {
    matlabbatch{5}.spm.stats.fmri_spec.sess(1).multi_reg{1},
    matlabbatch{5}.spm.stats.fmri_spec.sess(2).multi_reg{1}
    };


%CS>CG; include each wave iif we have BOTH of the two items within that wave
%CS>FS; include each wave iif we have BOTH of the two items within that wave
%CS2>CS1 % include only if we have both waves for the condition
%CG2>CS1 % include only if we have both waves for the condition
%FS2>FS1 % include only if we have both waves for the condition

%now we have appropriate contrast weight vectors
% we still need to check whether they have any values because 
% on the above code some will just be nothing

% 

CS_matrix =[];
CG_matrix = [];
FS_matrix = [];
CS_CG_matrix = [];
CS_FS_matrix = [];
wave_matrix = [];
for i = 1:numel(condition_filepaths)
    %get the multiconds
    multicond_mat = load(condition_filepaths{i});
    
    %count the number of motion regressors for this session
    dataTable = readtable(motion_filepaths{i}, 'Delimiter', '\t', 'ReadVariableNames', false);
    motion_colnum = width(dataTable);
    session_motion_regressor_count{i}=motion_colnum;

    
    % build concatenated matrices
    multicond_mat.CS_matrix = cellfun(@(x) strcmp(x,'CorrectStop'), multicond_mat.names, 'UniformOutput', 1);
    multicond_mat.CG_matrix = cellfun(@(x) strcmp(x,'CorrectGo'), multicond_mat.names, 'UniformOutput', 1);
    multicond_mat.FS_matrix = cellfun(@(x) strcmp(x,'FailedStop'), multicond_mat.names, 'UniformOutput', 1);
    has_CS = sum(multicond_mat.CS_matrix);
    has_CG = sum(multicond_mat.CG_matrix);
    has_FS = sum(multicond_mat.FS_matrix);
    
    

    %save to our multicond array
    multicond_array{i} = multicond_mat;

    motion_matrix = zeros(1,motion_colnum);
    motion_matrix
    %last of all, develop a continuously concatenated matrix for the three
    CS_matrix =[CS_matrix multicond_mat.CS_matrix motion_matrix];
    CG_matrix = [CG_matrix multicond_mat.CG_matrix motion_matrix];
    FS_matrix = [FS_matrix multicond_mat.FS_matrix motion_matrix];

    %only adds this session to the matrix if it has both of the relevant
    %items
    session_CS_CG = (multicond_mat.CS_matrix-multicond_mat.CG_matrix) * has_CS * has_CG; 
    CS_CG_matrix  = [CS_CG_matrix session_CS_CG motion_matrix];

    session_CS_FS = (multicond_mat.CS_matrix-multicond_mat.FS_matrix) * has_CS * has_FS; 
    CS_FS_matrix = [CS_FS_matrix session_CS_FS motion_matrix];

    %this just marks the waves
    wave_i_matrix = repmat(i,1,length(multicond_mat.names) + motion_colnum);
    wave_matrix = [wave_matrix wave_i_matrix];

end
%now do the wave contrasts
CS2_CS1 = CS_matrix.*(wave_matrix==2) - CS_matrix.*(wave_matrix==1);
CG2_CG1 = CG_matrix.*(wave_matrix==2) - CG_matrix.*(wave_matrix==1);
FS2_FS1 = FS_matrix.*(wave_matrix==2) - FS_matrix.*(wave_matrix==1);

%OK, now, if ANY of the contrasts are doable, we need to create the basic
%opening to contrast
% then we need to add the contrasts that can be added
contrasts = {
    %simple conditions (aggregated across multiple waves if available)
    struct(name = 'CS',weights = CS_matrix),
    struct(name = 'CG',weights = CG_matrix),
    struct(name = 'FS',weights = FS_matrix),
    %contrasts between conditions
    struct(name = 'CS>CG',weights = CS_CG_matrix),
    struct(name = 'CG>CS',weights = -CS_CG_matrix),
    struct(name = 'CS>FS',weights = CS_FS_matrix),
    struct(name = 'FS>CS',weights = -CS_FS_matrix),
    %contrasts between waves
    struct(name = 'CS(W2-W1)',weights = CS2_CS1),
    struct(name = 'CG(W2-W1)',weights = CG2_CG1),
    struct(name = 'FS(W2-W1)',weights = FS2_FS1),
    struct(name = 'CS(W1-W2)',weights = -CS2_CS1),
    struct(name = 'CG(W1-W2)',weights = -CG2_CG1),
    struct(name = 'FS(W1-W2)',weights = -FS2_FS1)
    };

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




function newArray = normalizePosAndNeg(inputArray)
    % Initialize the new array to the same values as the input array
    newArray = inputArray;

    % Get the sum of the positive values
    posSum = sum(inputArray(inputArray > 0));

    % Divide positive values by the sum of all the positives  
    newArray(inputArray > 0) = inputArray(inputArray > 0) / posSum; 

    % Get the sum of the negative values (it will be a negative number)
    negSum = sum(inputArray(inputArray < 0));

    % Divide negative values by the sum of all the negatives
    newArray(inputArray < 0) = inputArray(inputArray < 0) / abs(negSum); 

end