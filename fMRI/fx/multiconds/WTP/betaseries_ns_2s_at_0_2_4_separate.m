
% This script pulls onsets and durations from the subject output files for
% WTP to create FX multicond files
%
% D.Cos 10/2018


%%%%%%%%%%%
%% Offset of 0 %%%%%%%%%
%% Load data and intialize variables
writeDir = '~/Google Drive/oregon/preprocessing/DEV_scripts/fMRI/fx/multiconds/WTP/betaseries_ns_2s_split_0';

onset_offsets =[0];

%% Loop through subjects and runs and save names, onsets, and durations as .mat files
gen_betaseries_with_offsets(writeDir,onset_offsets)

%%%%%%%%%%%%%%%%%%%%%%%%
%% Offset of 2 %%%%%%%%%


% This script pulls onsets and durations from the subject output files for
% WTP to create FX multicond files
%
% D.Cos 10/2018

%% Load data and intialize variables
writeDir = '~/Google Drive/oregon/preprocessing/DEV_scripts/fMRI/fx/multiconds/WTP/betaseries_ns_2s_split_2';

onset_offsets =[2];


%% Loop through subjects and runs and save names, onsets, and durations as .mat files
gen_betaseries_with_offsets(writeDir,onset_offsets)

%%%%%%%%%%%%%%%%%%%%%%%%
%% Offset of 4 %%%%%%%%%


%% Load data and intialize variables
writeDir = '~/Google Drive/oregon/preprocessing/DEV_scripts/fMRI/fx/multiconds/WTP/betaseries_ns_2s_split_4';

onset_offsets =[4];

%% Loop through subjects and runs and save names, onsets, and durations as .mat files
gen_betaseries_with_offsets(writeDir,onset_offsets)