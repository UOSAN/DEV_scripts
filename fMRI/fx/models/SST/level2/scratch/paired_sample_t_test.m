% List of open inputs
nrun = X; % enter the number of runs here
jobfile = {'/Users/benjaminsmith/Google Drive/oregon/preprocessing/DEV_scripts/fMRI/fx/models/SST/level2/scratch/paired_sample_t_test_job.m'};
jobs = repmat(jobfile, 1, nrun);
inputs = cell(0, nrun);
for crun = 1:nrun
end
spm('defaults', 'FMRI');
spm_jobman('run', jobs, inputs{:});
