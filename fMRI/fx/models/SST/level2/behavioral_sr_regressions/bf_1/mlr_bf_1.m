% List of open inputs
<<<<<<< HEAD:fMRI/fx/models/SST/level2/mlr_ssrt_job_and_script.m
nrun = 1; % enter the number of runs here
jobfile = {'/Users/benjaminsmith/Google Drive/oregon/preprocessing/DEV_scripts/fMRI/fx/models/SST/level2/mlr_ssrt_job_and_script_job.m'};
=======
nrun = X; % enter the number of runs here
jobfile = {'/Users/benjaminsmith/Google Drive/oregon/preprocessing/DEV_scripts/fMRI/fx/models/SST/level2/bf_1/mlr_bf_1_job.m'};
>>>>>>> f422704f1143fe46d01dc0d136b90ea53d3e473c:fMRI/fx/models/SST/level2/bf_1/mlr_bf_1.m
jobs = repmat(jobfile, 1, nrun);
inputs = cell(0, nrun);
for crun = 1:nrun
end
spm('defaults', 'FMRI');
spm_jobman('run', jobs, inputs{:});

