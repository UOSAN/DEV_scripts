addpath('../SST')
%list of runs we will include; not sure how we import but let's assume it's
%a numeric array of runs
runs_json = strrep(runs_json,"""","");
disp(runs_json);
included_runs_for_wave = jsondecode(runs_json);

% if ismatrix(included_runs_by_wave)
%     included_runs_by_wave = num2cell(included_runs_by_wave',1);
% end

% disp(included_runs_by_wave);

%-----------------------------------------------------------------------
% Job saved on 06-May-2019 21:13:12 by cfg_util (rev $Rev: 6942 $)
% spm SPM - SPM12 (7219)
% cfg_basicio BasicIO - Unknown
%-----------------------------------------------------------------------

for run_i = 1:length(included_runs_for_wave)
    run_name = included_runs_for_wave(run_i);
    %just use the index because this is the first part of content in
    %matlabbatch
    matlabbatch{run_i}.cfg_basicio.file_dir.file_ops.file_fplist.dir = {'/projects/sanlab/shared/DEV/bids_data/derivatives/fmriprep_2022/sub-DEV001/ses-wave1/func/'};
    matlabbatch{run_i}.cfg_basicio.file_dir.file_ops.file_fplist.filter = sprintf('s6_sub-DEV001_ses-wave%d_task-ROC_acq-%d_space-MNI152NLin2009cAsym_desc-preproc_bold.nii',wave, run_name);
    matlabbatch{run_i}.cfg_basicio.file_dir.file_ops.file_fplist.rec = 'FPList';
    %     matlabbatch{1}.cfg_basicio.file_dir.file_ops.file_fplist.dir = {'/projects/sanlab/shared/DEV/bids_data/derivatives/fmriprep/sub-DEV001/ses-wave1/func/'};
    % matlabbatch{1}.cfg_basicio.file_dir.file_ops.file_fplist.filter = 's6_sub-DEV001_ses-wave1_task-ROC_acq-1_bold_space-MNI152NLin2009cAsym_preproc.nii';
    % matlabbatch{1}.cfg_basicio.file_dir.file_ops.file_fplist.rec = 'FPList';
end

%wave_file_selector_first_mlb_index{1} = length(matlabbatch)+1;

for run_i = 1:length(included_runs_for_wave)
    run_name = included_runs_for_wave(run_i);
    file_selector_string = sprintf('File Selector (Batch Mode): Selected Files (s6_sub-DEV001_ses-wave%d_task-ROC_acq-%d_space-MNI152NLin2009cAsym_desc-preproc_bold.nii)',wave, run_name);
    matlabbatch{length(matlabbatch)+1}.spm.util.exp_frames.files(1) = cfg_dep(file_selector_string, substruct('.','val', '{}',{run_i}, '.','val', '{}',{1}, '.','val', '{}',{1}, '.','val', '{}',{1}), substruct('.','files'));
    matlabbatch{length(matlabbatch)}.spm.util.exp_frames.frames = Inf;
% matlabbatch{5}.spm.util.exp_frames.files(1) = cfg_dep('File Selector (Batch Mode): Selected Files (s6_sub-DEV001_ses-wave1_task-ROC_acq-1_bold_space-MNI152NLin2009cAsym_preproc.nii)', substruct('.','val', '{}',{1}, '.','val', '{}',{1}, '.','val', '{}',{1}, '.','val', '{}',{1}), substruct('.','files'));
% matlabbatch{5}.spm.util.exp_frames.frames = Inf;

end

matlabbatch{length(matlabbatch)+1}.spm.stats.fmri_spec.dir = {sprintf('/projects/sanlab/shared/DEV/nonbids_data/fMRI/fx/models/ROC/wave%d/betaseries/sub-DEV001',wave)};
matlabbatch{length(matlabbatch)}.spm.stats.fmri_spec.timing.units = 'secs';
matlabbatch{length(matlabbatch)}.spm.stats.fmri_spec.timing.RT = 2;
matlabbatch{length(matlabbatch)}.spm.stats.fmri_spec.timing.fmri_t = 72;
matlabbatch{length(matlabbatch)}.spm.stats.fmri_spec.timing.fmri_t0 = 36;


spec_i = 0;
for run_i = 1:length(included_runs_for_wave)
    run_name = included_runs_for_wave(run_i);
    %we don't need to specify wave names because for this analysis
    %there are always exactly 2 waves
    spec_i = spec_i + 1; %going through all of the runs. don't assume presence of any
    %file_selector_mlb_index = wave_file_selector_first_mlb_index{wave_i} + (run_i-1);
    matlabbatch{length(matlabbatch)}.spm.stats.fmri_spec.sess(spec_i).scans(1) = cfg_dep('Expand image frames: Expanded filename list.', substruct('.','val', '{}',{file_selector_mlb_index}, '.','val', '{}',{1}, '.','val', '{}',{1}), substruct('.','files'));
    matlabbatch{length(matlabbatch)}.spm.stats.fmri_spec.sess(spec_i).cond = struct('name', {}, 'onset', {}, 'duration', {}, 'tmod', {}, 'pmod', {}, 'orth', {});
    matlabbatch{length(matlabbatch)}.spm.stats.fmri_spec.sess(spec_i).multi = {sprintf('/projects/sanlab/shared/DEV/DEV_scripts/fMRI/fx/multiconds/ROC/betaseries/DEV001_%d_ROC%d.mat',wave_i,run_name)};
    matlabbatch{length(matlabbatch)}.spm.stats.fmri_spec.sess(spec_i).regress = struct('name', {}, 'val', {});
    matlabbatch{length(matlabbatch)}.spm.stats.fmri_spec.sess(spec_i).multi_reg = {sprintf('/projects/sanlab/shared/DEV/bids_data/derivatives/auto-motion-fmriprep/sub-DEV001/sub-DEV001_ses-wave%d_task-ROC_acq-%d_run-1_desc-motion_regressors.txt',wave,run_name)};
    matlabbatch{length(matlabbatch)}.spm.stats.fmri_spec.sess(spec_i).hpf = 128;
end



matlabbatch{length(matlabbatch)}.spm.stats.fmri_spec.fact = struct('name', {}, 'levels', {});
matlabbatch{length(matlabbatch)}.spm.stats.fmri_spec.bases.hrf.derivs = [0 0];
matlabbatch{length(matlabbatch)}.spm.stats.fmri_spec.volt = 1;
matlabbatch{length(matlabbatch)}.spm.stats.fmri_spec.global = 'None';
matlabbatch{length(matlabbatch)}.spm.stats.fmri_spec.mthresh = -Inf;
matlabbatch{length(matlabbatch)}.spm.stats.fmri_spec.mask = {'/projects/sanlab/shared/spm12/canonical/MNI152_T1_1mm_brain_mask.nii,1'};
matlabbatch{length(matlabbatch)}.spm.stats.fmri_spec.cvi = 'FAST';


mlb_spec_index = length(matlabbatch);
matlabbatch{length(matlabbatch)+1}.spm.stats.fmri_est.spmmat(1) = cfg_dep('fMRI model specification: SPM.mat File', substruct('.','val', '{}',{mlb_spec_index}, '.','val', '{}',{1}, '.','val', '{}',{1}), substruct('.','spmmat'));
matlabbatch{length(matlabbatch)}.spm.stats.fmri_est.write_residuals = 0;
matlabbatch{length(matlabbatch)}.spm.stats.fmri_est.method.Classical = 1;
mlb_est_index = length(matlabbatch);
mlb_contrasts_index = length(matlabbatch)+1;


