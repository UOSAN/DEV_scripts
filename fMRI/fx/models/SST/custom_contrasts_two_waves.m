%TODO:
%open this up in MATLAB, open BOTH conditions files for an exemplar subject, and work out the right code to add to do the contrasts we need to do
%probably plan the contrasts first!
matlabbatch = {};


conditions_filepath_1 = '/Users/benjaminsmith/Google Drive/oregon/code/DEV_scripts/fMRI/fx/multiconds/SST/full_duration/conditions/DEV011_1_SST1.mat';
conditions_filepath_2 = '/Users/benjaminsmith/Google Drive/oregon/code/DEV_scripts/fMRI/fx/multiconds/SST/full_duration/conditions/DEV011_2_SST1.mat';

condition_filepaths = {conditions_filepath_1, 
    conditions_filepath_2};

motion_filepaths = {
    '/Users/benjaminsmith/Google Drive/oregon/data/DEV/bids_data/derivatives/auto-motion-fmriprep/sub-DEV011/sub-DEV011_ses-wave1_task-SST_acq-1_run-1_desc-motion_regressors.txt',
    '/Users/benjaminsmith/Google Drive/oregon/data/DEV/bids_data/derivatives/auto-motion-fmriprep/sub-DEV011/sub-DEV011_ses-wave2_task-SST_acq-1_run-1_desc-motion_regressors.txt'
    };

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

    subject_CS_CG = (multicond_mat.CS_matrix-multicond_mat.CG_matrix) * has_CS * has_CG; 
    CS_CG_matrix  = [CS_CG_matrix subject_CS_CG motion_matrix];

    subject_CS_FS = (multicond_mat.CS_matrix-multicond_mat.FS_matrix) * has_CS * has_FS; 
    CS_FS_matrix = [CS_FS_matrix subject_CS_FS motion_matrix];

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
    struct(name='CS',weights=CS_matrix),
    struct(name='CG',weights=CG_matrix),
    struct(name='FS',weights=FS_matrix),
    %contrasts between conditions
    struct(name='CS>CG',weights=CS_CG_matrix),
    struct(name='CG>CS',weights=-CS_CG_matrix),
    struct(name='CS>FS',weights=CS_FS_matrix),
    struct(name='FS>CS',weights=-CS_FS_matrix),
    %contrasts between waves
    struct(name='CS(W2-W1)',weights=CS2_CS1),
    struct(name='CG(W2-W1)',weights=CG2_CG1),
    struct(name='FS(W2-W1)',weights=FS2_FS1),
    struct(name='CS(W1-W2)',weights=-CS2_CS1),
    struct(name='CG(W1-W2)',weights=-CG2_CG1),
    struct(name='FS(W1-W2)',weights=-FS2_FS1)
    };

use_contrast = logical([]);
% for each set of contrast weights, normalize to zero
% and also mark whether we will use the contrasts
for i = 1:length(contrasts)
    % Normalize the weights
    contrasts{i}.weights = normalizePosAndNeg(contrasts{i}.weights);
    use_contrast = [use_contrast sum(abs(contrasts{i}.weights))>0];
end

%filter to only the contrasts we'll use
contrasts_filtered = contrasts(use_contrast);

%now add the contrasts
if any(use_contrast)
     matlabbatch{5}.spm.stats.con.spmmat(1) = cfg_dep('Model estimation: SPM.mat File', substruct('.','val', '{}',{4}, '.','val', '{}',{1}, '.','val', '{}',{1}), substruct('.','spmmat'));
     matlabbatch{5}.spm.stats.con.delete = 0;
end

for i = 1:length(contrasts_filtered)
    matlabbatch{5}.spm.stats.con.consess{i}.tcon.name = contrasts_filtered{i}.name;
    matlabbatch{5}.spm.stats.con.consess{i}.tcon.weights = contrasts_filtered{i}.weights;
    matlabbatch{5}.spm.stats.con.consess{i}.tcon.sessrep = 'none';
end


%CS>CG; include each wave iif we have BOTH of the two items within that wave
%CS>FS; include each wave iif we have BOTH of the two items within that wave
%CS2>CS1 % include only if we have both waves for the condition
%CG2>CS1 % include only if we have both waves for the condition
%FS2>FS1 % include only if we have both waves for the condition

%now we have appropriate contrast weight vectors
% we still need to check whether they have any values because 
% on the above code some will just be nothing

% 


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