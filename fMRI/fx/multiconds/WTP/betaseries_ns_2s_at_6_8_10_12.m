% This script pulls onsets and durations from the subject output files for
% WTP to create FX multicond files
%
% D.Cos 10/2018

writeDir = '~/Google Drive/oregon/preprocessing/DEV_scripts/fMRI/fx/multiconds/WTP/betaseries_ns_6s_split_series';

onset_offsets =[6, 8, 10, 12];

%% Loop through subjects and runs and save names, onsets, and durations as .mat files
gen_betaseries_with_offsets(writeDir,onset_offsets)