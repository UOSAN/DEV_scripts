% List of open inputs
nrun = 1; % enter the number of runs here
jobfile = {'/Users/benjaminsmith/Google Drive/oregon/preprocessing/DEV_scripts/fMRI/fx/models/SST/level2/mlr_ssrt_job_and_script_job.m'};
jobs = repmat(jobfile, 1, nrun);
inputs = cell(0, nrun);
for crun = 1:nrun
end
spm('defaults', 'FMRI');
spm_jobman('run', jobs, inputs{:});

