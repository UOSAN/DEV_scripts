addpath('../SST')
%list of runs we will include; not sure how we import but let's assume it's
%a numeric array of runs
runs_json = strrep(runs_json,"""","");
disp(runs_json);
included_runs_by_wave = jsondecode(runs_json);

if ismatrix(included_runs_by_wave)
    included_runs_by_wave = num2cell(included_runs_by_wave',1);
end

disp(included_runs_by_wave);

%-----------------------------------------------------------------------
% Job saved on 06-May-2019 21:13:12 by cfg_util (rev $Rev: 6942 $)
% spm SPM - SPM12 (7219)
% cfg_basicio BasicIO - Unknown
%-----------------------------------------------------------------------

for run_i = 1:length(included_runs_by_wave{1})
    run_name = included_runs_by_wave{1}(run_i);
    %just use the index because this is the first part of content in
    %matlabbatch
    matlabbatch{run_i}.cfg_basicio.file_dir.file_ops.file_fplist.dir = {'/projects/sanlab/shared/DEV/bids_data/derivatives/fmriprep_2022/sub-DEV001/ses-wave1/func/'};
    matlabbatch{run_i}.cfg_basicio.file_dir.file_ops.file_fplist.filter = sprintf('s6_sub-DEV001_ses-wave1_task-ROC_acq-%d_space-MNI152NLin2009cAsym_desc-preproc_bold.nii',run_name);
    matlabbatch{run_i}.cfg_basicio.file_dir.file_ops.file_fplist.rec = 'FPList';
end

wave_file_selector_first_mlb_index{1} = length(matlabbatch)+1;
for run_i = 1:length(included_runs_by_wave{1})
    run_name = included_runs_by_wave{1}(run_i);
    file_selector_string = sprintf('File Selector (Batch Mode): Selected Files (s6_sub-DEV001_ses-wave1_task-ROC_acq-%d_space-MNI152NLin2009cAsym_desc-preproc_bold.nii)',run_name);
    matlabbatch{length(matlabbatch)+1}.spm.util.exp_frames.files(1) = cfg_dep(file_selector_string, substruct('.','val', '{}',{run_i}, '.','val', '{}',{1}, '.','val', '{}',{1}, '.','val', '{}',{1}), substruct('.','files'));
    matlabbatch{length(matlabbatch)}.spm.util.exp_frames.frames = Inf;

end


for run_i = 1:length(included_runs_by_wave{2})
    run_name = included_runs_by_wave{2}(run_i);
    matlabbatch{length(matlabbatch)+1}.cfg_basicio.file_dir.file_ops.file_fplist.dir = {'/projects/sanlab/shared/DEV/bids_data/derivatives/fmriprep_2022/sub-DEV001/ses-wave2/func'};
    matlabbatch{length(matlabbatch)}.cfg_basicio.file_dir.file_ops.file_fplist.filter = sprintf('s6_sub-DEV001_ses-wave2_task-ROC_acq-%d_space-MNI152NLin2009cAsym_desc-preproc_bold.nii',run_name);
    matlabbatch{length(matlabbatch)}.cfg_basicio.file_dir.file_ops.file_fplist.rec = 'FPList';

end


wave_file_selector_first_mlb_index{2} = length(matlabbatch)+1;
for run_i = 1:length(included_runs_by_wave{2})
    run_name = included_runs_by_wave{2}(run_i);
    mlb_iterator = length(matlabbatch)+1;
    mlb_lookback = mlb_iterator - 4; %this is a reference back to the file filter.
    file_selector_string = sprintf('File Selector (Batch Mode): Selected Files (s6_sub-DEV001_ses-wave2_task-ROC_acq-%d_space-MNI152NLin2009cAsym_desc-preproc_bold.nii)',run_name);
    matlabbatch{mlb_iterator}.spm.util.exp_frames.files(1) = cfg_dep(file_selector_string, substruct('.','val', '{}',{mlb_lookback}, '.','val', '{}',{1}, '.','val', '{}',{1}, '.','val', '{}',{1}), substruct('.','files'));
    matlabbatch{mlb_iterator}.spm.util.exp_frames.frames = Inf;

end



matlabbatch{9}.spm.stats.fmri_spec.dir = {'/projects/sanlab/shared/DEV/nonbids_data/fMRI/fx/models/ROC/all_waves/conditions/sub-DEV001'};
matlabbatch{9}.spm.stats.fmri_spec.timing.units = 'secs';
matlabbatch{9}.spm.stats.fmri_spec.timing.RT = 2;
matlabbatch{9}.spm.stats.fmri_spec.timing.fmri_t = 72;
matlabbatch{9}.spm.stats.fmri_spec.timing.fmri_t0 = 36;
matlabbatch{9}.spm.stats.fmri_spec.sess(1).scans(1) = cfg_dep('Expand image frames: Expanded filename list.', substruct('.','val', '{}',{5}, '.','val', '{}',{1}, '.','val', '{}',{1}), substruct('.','files'));
matlabbatch{9}.spm.stats.fmri_spec.sess(1).cond = struct('name', {}, 'onset', {}, 'duration', {}, 'tmod', {}, 'pmod', {}, 'orth', {});
matlabbatch{9}.spm.stats.fmri_spec.sess(1).multi = {'/projects/sanlab/shared/DEV/DEV_scripts/fMRI/fx/multiconds/ROC/conditions/DEV001_1_ROC_run1.mat'};
matlabbatch{9}.spm.stats.fmri_spec.sess(1).regress = struct('name', {}, 'val', {});
matlabbatch{9}.spm.stats.fmri_spec.sess(1).multi_reg = {'/projects/sanlab/shared/DEV/bids_data/derivatives/auto-motion-fmriprep/sub-DEV001/sub-DEV001_ses-wave1_task-ROC_acq-1_run-1_desc-motion_regressors.txt'};
matlabbatch{9}.spm.stats.fmri_spec.sess(1).hpf = 128;
matlabbatch{9}.spm.stats.fmri_spec.sess(2).scans(1) = cfg_dep('Expand image frames: Expanded filename list.', substruct('.','val', '{}',{6}, '.','val', '{}',{1}, '.','val', '{}',{1}), substruct('.','files'));
matlabbatch{9}.spm.stats.fmri_spec.sess(2).cond = struct('name', {}, 'onset', {}, 'duration', {}, 'tmod', {}, 'pmod', {}, 'orth', {});
matlabbatch{9}.spm.stats.fmri_spec.sess(2).multi = {'/projects/sanlab/shared/DEV/DEV_scripts/fMRI/fx/multiconds/ROC/conditions/DEV001_1_ROC_run2.mat'};
matlabbatch{9}.spm.stats.fmri_spec.sess(2).regress = struct('name', {}, 'val', {});
matlabbatch{9}.spm.stats.fmri_spec.sess(2).multi_reg = {'/projects/sanlab/shared/DEV/bids_data/derivatives/auto-motion-fmriprep/sub-DEV001/sub-DEV001_ses-wave1_task-ROC_acq-2_run-1_desc-motion_regressors.txt'};
matlabbatch{9}.spm.stats.fmri_spec.sess(2).hpf = 128;
matlabbatch{9}.spm.stats.fmri_spec.sess(3).scans(1) = cfg_dep('Expand image frames: Expanded filename list.', substruct('.','val', '{}',{7}, '.','val', '{}',{1}, '.','val', '{}',{1}), substruct('.','files'));
matlabbatch{9}.spm.stats.fmri_spec.sess(3).cond = struct('name', {}, 'onset', {}, 'duration', {}, 'tmod', {}, 'pmod', {}, 'orth', {});
matlabbatch{9}.spm.stats.fmri_spec.sess(3).multi = {'/projects/sanlab/shared/DEV/DEV_scripts/fMRI/fx/multiconds/ROC/conditions/DEV001_1_ROC_run3.mat'};
matlabbatch{9}.spm.stats.fmri_spec.sess(3).regress = struct('name', {}, 'val', {});
matlabbatch{9}.spm.stats.fmri_spec.sess(3).multi_reg = {'/projects/sanlab/shared/DEV/bids_data/derivatives/auto-motion-fmriprep/sub-DEV001/sub-DEV001_ses-wave1_task-ROC_acq-3_run-1_desc-motion_regressors.txt'};
matlabbatch{9}.spm.stats.fmri_spec.sess(3).hpf = 128;
matlabbatch{9}.spm.stats.fmri_spec.sess(4).scans(1) = cfg_dep('Expand image frames: Expanded filename list.', substruct('.','val', '{}',{8}, '.','val', '{}',{1}, '.','val', '{}',{1}), substruct('.','files'));
matlabbatch{9}.spm.stats.fmri_spec.sess(4).cond = struct('name', {}, 'onset', {}, 'duration', {}, 'tmod', {}, 'pmod', {}, 'orth', {});
matlabbatch{9}.spm.stats.fmri_spec.sess(4).multi = {'/projects/sanlab/shared/DEV/DEV_scripts/fMRI/fx/multiconds/ROC/conditions/DEV001_1_ROC_run4.mat'};
matlabbatch{9}.spm.stats.fmri_spec.sess(4).regress = struct('name', {}, 'val', {});
matlabbatch{9}.spm.stats.fmri_spec.sess(4).multi_reg = {'/projects/sanlab/shared/DEV/bids_data/derivatives/auto-motion-fmriprep/sub-DEV001/sub-DEV001_ses-wave1_task-ROC_acq-4_run-1_desc-motion_regressors.txt'};
matlabbatch{9}.spm.stats.fmri_spec.sess(4).hpf = 128;
matlabbatch{9}.spm.stats.fmri_spec.fact = struct('name', {}, 'levels', {});
matlabbatch{9}.spm.stats.fmri_spec.bases.hrf.derivs = [0 0];
matlabbatch{9}.spm.stats.fmri_spec.volt = 1;
matlabbatch{9}.spm.stats.fmri_spec.global = 'None';
matlabbatch{9}.spm.stats.fmri_spec.mthresh = -Inf;
matlabbatch{9}.spm.stats.fmri_spec.mask = {'/projects/sanlab/shared/spm12/canonical/MNI152_T1_1mm_brain_mask.nii,1'};
matlabbatch{9}.spm.stats.fmri_spec.cvi = 'FAST';
matlabbatch{10}.spm.stats.fmri_est.spmmat(1) = cfg_dep('fMRI model specification: SPM.mat File', substruct('.','val', '{}',{9}, '.','val', '{}',{1}, '.','val', '{}',{1}, '.','val', '{}',{1}), substruct('.','spmmat'));
matlabbatch{10}.spm.stats.fmri_est.write_residuals = 0;
matlabbatch{10}.spm.stats.fmri_est.method.Classical = 1;
