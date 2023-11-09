addpath('../SST')
%list of runs we will include; not sure how we import but let's assume it's
%a numeric array of runs
%included_runs_w1=[2,4];
%included_runs_w2=[2,4];
%included_runs_by_wave = {included_runs_w1,included_runs_w2};
included_runs_by_wave = jsondecode(runs_json);

if ismatrix(included_runs_by_wave)
    included_runs_by_wave = num2cell(included_runs_by_wave',1);
end

%can get the number of runs with numel(included_runs)
%-----------------------------------------------------------------------
% Job saved on 01-Aug-2023 14:12:41 by cfg_util (rev $Rev: 7345 $)
% spm SPM - SPM12 (7771)
% cfg_basicio BasicIO - Unknown
%-----------------------------------------------------------------------
for run_i = 1:length(included_runs_w1)
    run_name = included_runs_w1(run_i);
    %just use the index because this is the first part of content in
    %matlabbatch
    matlabbatch{run_i}.cfg_basicio.file_dir.file_ops.file_fplist.dir = {'/Users/benjaminsmith/Google Drive/oregon/data/DEV/bids_data/derivatives/fmriprep_2022/sub-DEV023/ses-wave1/func/'};
    matlabbatch{run_i}.cfg_basicio.file_dir.file_ops.file_fplist.filter = sprintf('s6_sub-DEV023_ses-wave1_task-WTP_acq-%d_space-MNI152NLin2009cAsym_desc-preproc_bold.nii',run_name);
    matlabbatch{run_i}.cfg_basicio.file_dir.file_ops.file_fplist.rec = 'FPList';
% matlabbatch{2}.cfg_basicio.file_dir.file_ops.file_fplist.dir = {'/Users/benjaminsmith/Google Drive/oregon/data/DEV/bids_data/derivatives/fmriprep_2022/sub-DEV023/ses-wave1/func/'};
% matlabbatch{2}.cfg_basicio.file_dir.file_ops.file_fplist.filter = 's6_sub-DEV023_ses-wave1_task-WTP_acq-2_space-MNI152NLin2009cAsym_desc-preproc_bold.nii';
% matlabbatch{2}.cfg_basicio.file_dir.file_ops.file_fplist.rec = 'FPList';
% matlabbatch{3}.cfg_basicio.file_dir.file_ops.file_fplist.dir = {'/Users/benjaminsmith/Google Drive/oregon/data/DEV/bids_data/derivatives/fmriprep_2022/sub-DEV023/ses-wave1/func/'};
% matlabbatch{3}.cfg_basicio.file_dir.file_ops.file_fplist.filter = 's6_sub-DEV023_ses-wave1_task-WTP_acq-3_space-MNI152NLin2009cAsym_desc-preproc_bold.nii';
% matlabbatch{3}.cfg_basicio.file_dir.file_ops.file_fplist.rec = 'FPList';
% matlabbatch{4}.cfg_basicio.file_dir.file_ops.file_fplist.dir = {'/Users/benjaminsmith/Google Drive/oregon/data/DEV/bids_data/derivatives/fmriprep_2022/sub-DEV023/ses-wave1/func/'};
% matlabbatch{4}.cfg_basicio.file_dir.file_ops.file_fplist.filter = 's6_sub-DEV023_ses-wave1_task-WTP_acq-4_space-MNI152NLin2009cAsym_desc-preproc_bold.nii';
% matlabbatch{4}.cfg_basicio.file_dir.file_ops.file_fplist.rec = 'FPList';
end

wave_file_selector_first_mlb_index{1} = length(matlabbatch)+1;
for run_i = 1:length(included_runs_w1)
    run_name = included_runs_w1(run_i);
    file_selector_string = sprintf('File Selector (Batch Mode): Selected Files (s6_sub-DEV023_ses-wave1_task-WTP_acq-%d_space-MNI152NLin2009cAsym_desc-preproc_bold.nii)',run_name);
    matlabbatch{length(matlabbatch)+1}.spm.util.exp_frames.files(1) = cfg_dep(file_selector_string, substruct('.','val', '{}',{run_i}, '.','val', '{}',{1}, '.','val', '{}',{1}, '.','val', '{}',{1}), substruct('.','files'));
    matlabbatch{length(matlabbatch)}.spm.util.exp_frames.frames = Inf;
%     matlabbatch{6}.spm.util.exp_frames.files(1) = cfg_dep('File Selector (Batch Mode): Selected Files (s6_sub-DEV023_ses-wave1_task-WTP_acq-2_space-MNI152NLin2009cAsym_desc-preproc_bold.nii)', substruct('.','val', '{}',{2}, '.','val', '{}',{1}, '.','val', '{}',{1}, '.','val', '{}',{1}), substruct('.','files'));
%     matlabbatch{6}.spm.util.exp_frames.frames = Inf;
%     matlabbatch{7}.spm.util.exp_frames.files(1) = cfg_dep('File Selector (Batch Mode): Selected Files (s6_sub-DEV023_ses-wave1_task-WTP_acq-3_space-MNI152NLin2009cAsym_desc-preproc_bold.nii)', substruct('.','val', '{}',{3}, '.','val', '{}',{1}, '.','val', '{}',{1}, '.','val', '{}',{1}), substruct('.','files'));
%     matlabbatch{7}.spm.util.exp_frames.frames = Inf;
%     matlabbatch{8}.spm.util.exp_frames.files(1) = cfg_dep('File Selector (Batch Mode): Selected Files (s6_sub-DEV023_ses-wave1_task-WTP_acq-4_space-MNI152NLin2009cAsym_desc-preproc_bold.nii)', substruct('.','val', '{}',{4}, '.','val', '{}',{1}, '.','val', '{}',{1}, '.','val', '{}',{1}), substruct('.','files'));
%     matlabbatch{8}.spm.util.exp_frames.frames = Inf;
end

for run_i = 1:length(included_runs_w2)
    run_name = included_runs_w2(run_i);
    matlabbatch{length(matlabbatch)+1}.cfg_basicio.file_dir.file_ops.file_fplist.dir = {'/Users/benjaminsmith/Google Drive/oregon/data/DEV/bids_data/derivatives/fmriprep_2022/sub-DEV023/ses-wave2/func'};
    matlabbatch{length(matlabbatch)}.cfg_basicio.file_dir.file_ops.file_fplist.filter = sprintf('s6_sub-DEV023_ses-wave2_task-WTP_acq-%d_space-MNI152NLin2009cAsym_desc-preproc_bold.nii',run_name);
    matlabbatch{length(matlabbatch)}.cfg_basicio.file_dir.file_ops.file_fplist.rec = 'FPList';
% matlabbatch{10}.cfg_basicio.file_dir.file_ops.file_fplist.dir = {'/Users/benjaminsmith/Google Drive/oregon/data/DEV/bids_data/derivatives/fmriprep_2022/sub-DEV023/ses-wave2/func'};
% matlabbatch{10}.cfg_basicio.file_dir.file_ops.file_fplist.filter = 's6_sub-DEV023_ses-wave2_task-WTP_acq-2_space-MNI152NLin2009cAsym_desc-preproc_bold.nii';
% matlabbatch{10}.cfg_basicio.file_dir.file_ops.file_fplist.rec = 'FPList';
% matlabbatch{11}.cfg_basicio.file_dir.file_ops.file_fplist.dir = {'/Users/benjaminsmith/Google Drive/oregon/data/DEV/bids_data/derivatives/fmriprep_2022/sub-DEV023/ses-wave2/func'};
% matlabbatch{11}.cfg_basicio.file_dir.file_ops.file_fplist.filter = 's6_sub-DEV023_ses-wave2_task-WTP_acq-3_space-MNI152NLin2009cAsym_desc-preproc_bold.nii';
% matlabbatch{11}.cfg_basicio.file_dir.file_ops.file_fplist.rec = 'FPList';
% matlabbatch{12}.cfg_basicio.file_dir.file_ops.file_fplist.dir = {'/Users/benjaminsmith/Google Drive/oregon/data/DEV/bids_data/derivatives/fmriprep_2022/sub-DEV023/ses-wave2/func'};
% matlabbatch{12}.cfg_basicio.file_dir.file_ops.file_fplist.filter = 's6_sub-DEV023_ses-wave2_task-WTP_acq-4_space-MNI152NLin2009cAsym_desc-preproc_bold.nii';
% matlabbatch{12}.cfg_basicio.file_dir.file_ops.file_fplist.rec = 'FPList';
end

wave_file_selector_first_mlb_index{2} = length(matlabbatch)+1;
for run_i = 1:length(included_runs_w2)
    run_name = included_runs_w2(run_i);
    mlb_iterator = length(matlabbatch)+1;
    mlb_lookback = mlb_iterator - 4; %this is a reference back to the file filter.
    file_selector_string = sprintf('File Selector (Batch Mode): Selected Files (s6_sub-DEV023_ses-wave2_task-WTP_acq-%d_space-MNI152NLin2009cAsym_desc-preproc_bold.nii)',run_name);
    matlabbatch{mlb_iterator}.spm.util.exp_frames.files(1) = cfg_dep(file_selector_string, substruct('.','val', '{}',{mlb_lookback}, '.','val', '{}',{1}, '.','val', '{}',{1}, '.','val', '{}',{1}), substruct('.','files'));
    matlabbatch{mlb_iterator}.spm.util.exp_frames.frames = Inf;
% matlabbatch{14}.spm.util.exp_frames.files(1) = cfg_dep('File Selector (Batch Mode): Selected Files (s6_sub-DEV023_ses-wave2_task-WTP_acq-2_space-MNI152NLin2009cAsym_desc-preproc_bold.nii)', substruct('.','val', '{}',{10}, '.','val', '{}',{1}, '.','val', '{}',{1}, '.','val', '{}',{1}), substruct('.','files'));
% matlabbatch{14}.spm.util.exp_frames.frames = Inf;
% matlabbatch{15}.spm.util.exp_frames.files(1) = cfg_dep('File Selector (Batch Mode): Selected Files (s6_sub-DEV023_ses-wave2_task-WTP_acq-3_space-MNI152NLin2009cAsym_desc-preproc_bold.nii)', substruct('.','val', '{}',{11}, '.','val', '{}',{1}, '.','val', '{}',{1}, '.','val', '{}',{1}), substruct('.','files'));
% matlabbatch{15}.spm.util.exp_frames.frames = Inf;
% matlabbatch{16}.spm.util.exp_frames.files(1) = cfg_dep('File Selector (Batch Mode): Selected Files (s6_sub-DEV023_ses-wave2_task-WTP_acq-4_space-MNI152NLin2009cAsym_desc-preproc_bold.nii)', substruct('.','val', '{}',{12}, '.','val', '{}',{1}, '.','val', '{}',{1}, '.','val', '{}',{1}), substruct('.','files'));
% matlabbatch{16}.spm.util.exp_frames.frames = Inf;
end

matlabbatch{length(matlabbatch)+1}.spm.stats.fmri_spec.dir = {'/Users/benjaminsmith/Google Drive/oregon/data/DEV/nonbids_data/fMRI/fx/models/WTP/all_waves/conditions/sub-DEV023'};
matlabbatch{length(matlabbatch)}.spm.stats.fmri_spec.timing.units = 'secs';
matlabbatch{length(matlabbatch)}.spm.stats.fmri_spec.timing.RT = 2;
matlabbatch{length(matlabbatch)}.spm.stats.fmri_spec.timing.fmri_t = 72;
matlabbatch{length(matlabbatch)}.spm.stats.fmri_spec.timing.fmri_t0 = 36;
for wave_i = 1:length(included_runs_by_wave)
    for run_i = 1:length(included_runs_by_wave{wave_i})
        run_name = included_runs_by_wave{wave_i}(run_i);
        %we don't need to specify wave names because for this analysis
        %there are always exactly 2 waves
        spec_i = (wave_i - 1) + run_i; %going from 1 to 8 assuming all runs present
        file_selector_mlb_index = wave_file_selector_first_mlb_index{wave_i} + (run_i-1);
        matlabbatch{length(matlabbatch)}.spm.stats.fmri_spec.sess(spec_i).scans(1) = cfg_dep('Expand image frames: Expanded filename list.', substruct('.','val', '{}',{file_selector_mlb_index}, '.','val', '{}',{1}, '.','val', '{}',{1}), substruct('.','files'));
        matlabbatch{length(matlabbatch)}.spm.stats.fmri_spec.sess(spec_i).cond = struct('name', {}, 'onset', {}, 'duration', {}, 'tmod', {}, 'pmod', {}, 'orth', {});
        matlabbatch{length(matlabbatch)}.spm.stats.fmri_spec.sess(spec_i).multi = {sprintf('/Users/benjaminsmith/Google Drive/oregon/code/DEV_scripts/fMRI/fx/multiconds/WTP/conditions/DEV023_%d_WTP%d.mat',wave_i,run_name)};
        matlabbatch{length(matlabbatch)}.spm.stats.fmri_spec.sess(spec_i).regress = struct('name', {}, 'val', {});
        matlabbatch{length(matlabbatch)}.spm.stats.fmri_spec.sess(spec_i).multi_reg = {sprintf('/Users/benjaminsmith/Google Drive/oregon/data/DEV/bids_data/derivatives/auto-motion-fmriprep/sub-DEV023/sub-DEV023_ses-wave%d_task-WTP_acq-%d_run-1_desc-motion_regressors.txt',wave_i,run_name)};
        matlabbatch{length(matlabbatch)}.spm.stats.fmri_spec.sess(spec_i).hpf = 128;
%         matlabbatch{17}.spm.stats.fmri_spec.sess(2).scans(1) = cfg_dep('Expand image frames: Expanded filename list.', substruct('.','val', '{}',{6}, '.','val', '{}',{1}, '.','val', '{}',{1}), substruct('.','files'));
%         matlabbatch{17}.spm.stats.fmri_spec.sess(2).cond = struct('name', {}, 'onset', {}, 'duration', {}, 'tmod', {}, 'pmod', {}, 'orth', {});
%         matlabbatch{17}.spm.stats.fmri_spec.sess(2).multi = {'/Users/benjaminsmith/Google Drive/oregon/code/DEV_scripts/fMRI/fx/multiconds/WTP/conditions/DEV023_1_WTP2.mat'};
%         matlabbatch{17}.spm.stats.fmri_spec.sess(2).regress = struct('name', {}, 'val', {});
%         matlabbatch{17}.spm.stats.fmri_spec.sess(2).multi_reg = {'/Users/benjaminsmith/Google Drive/oregon/data/DEV/bids_data/derivatives/auto-motion-fmriprep/sub-DEV023/sub-DEV023_ses-wave1_task-WTP_acq-2_run-1_desc-motion_regressors.txt'};
%         matlabbatch{17}.spm.stats.fmri_spec.sess(2).hpf = 128;
%         matlabbatch{17}.spm.stats.fmri_spec.sess(3).scans(1) = cfg_dep('Expand image frames: Expanded filename list.', substruct('.','val', '{}',{7}, '.','val', '{}',{1}, '.','val', '{}',{1}), substruct('.','files'));
%         matlabbatch{17}.spm.stats.fmri_spec.sess(3).cond = struct('name', {}, 'onset', {}, 'duration', {}, 'tmod', {}, 'pmod', {}, 'orth', {});
%         matlabbatch{17}.spm.stats.fmri_spec.sess(3).multi = {'/Users/benjaminsmith/Google Drive/oregon/code/DEV_scripts/fMRI/fx/multiconds/WTP/conditions/DEV023_1_WTP3.mat'};
%         matlabbatch{17}.spm.stats.fmri_spec.sess(3).regress = struct('name', {}, 'val', {});
%         matlabbatch{17}.spm.stats.fmri_spec.sess(3).multi_reg = {'/Users/benjaminsmith/Google Drive/oregon/data/DEV/bids_data/derivatives/auto-motion-fmriprep/sub-DEV023/sub-DEV023_ses-wave1_task-WTP_acq-3_run-1_desc-motion_regressors.txt'};
%         matlabbatch{17}.spm.stats.fmri_spec.sess(3).hpf = 128;
%         matlabbatch{17}.spm.stats.fmri_spec.sess(4).scans(1) = cfg_dep('Expand image frames: Expanded filename list.', substruct('.','val', '{}',{8}, '.','val', '{}',{1}, '.','val', '{}',{1}), substruct('.','files'));
%         matlabbatch{17}.spm.stats.fmri_spec.sess(4).cond = struct('name', {}, 'onset', {}, 'duration', {}, 'tmod', {}, 'pmod', {}, 'orth', {});
%         matlabbatch{17}.spm.stats.fmri_spec.sess(4).multi = {'/Users/benjaminsmith/Google Drive/oregon/code/DEV_scripts/fMRI/fx/multiconds/WTP/conditions/DEV023_1_WTP4.mat'};
%         matlabbatch{17}.spm.stats.fmri_spec.sess(4).regress = struct('name', {}, 'val', {});
%         matlabbatch{17}.spm.stats.fmri_spec.sess(4).multi_reg = {'/Users/benjaminsmith/Google Drive/oregon/data/DEV/bids_data/derivatives/auto-motion-fmriprep/sub-DEV023/sub-DEV023_ses-wave1_task-WTP_acq-4_run-1_desc-motion_regressors.txt'};
%         matlabbatch{17}.spm.stats.fmri_spec.sess(4).hpf = 128;
%         matlabbatch{17}.spm.stats.fmri_spec.sess(5).scans(1) = cfg_dep('Expand image frames: Expanded filename list.', substruct('.','val', '{}',{13}, '.','val', '{}',{1}, '.','val', '{}',{1}), substruct('.','files'));
%         matlabbatch{17}.spm.stats.fmri_spec.sess(5).cond = struct('name', {}, 'onset', {}, 'duration', {}, 'tmod', {}, 'pmod', {}, 'orth', {});
%         matlabbatch{17}.spm.stats.fmri_spec.sess(5).multi = {'/Users/benjaminsmith/Google Drive/oregon/code/DEV_scripts/fMRI/fx/multiconds/WTP/conditions/DEV023_2_WTP1.mat'};
%         matlabbatch{17}.spm.stats.fmri_spec.sess(5).regress = struct('name', {}, 'val', {});
%         matlabbatch{17}.spm.stats.fmri_spec.sess(5).multi_reg = {'/Users/benjaminsmith/Google Drive/oregon/data/DEV/bids_data/derivatives/auto-motion-fmriprep/sub-DEV023/sub-DEV023_ses-wave2_task-WTP_acq-1_run-1_desc-motion_regressors.txt'};
%         matlabbatch{17}.spm.stats.fmri_spec.sess(5).hpf = 128;
%         matlabbatch{17}.spm.stats.fmri_spec.sess(6).scans(1) = cfg_dep('Expand image frames: Expanded filename list.', substruct('.','val', '{}',{14}, '.','val', '{}',{1}, '.','val', '{}',{1}), substruct('.','files'));
%         matlabbatch{17}.spm.stats.fmri_spec.sess(6).cond = struct('name', {}, 'onset', {}, 'duration', {}, 'tmod', {}, 'pmod', {}, 'orth', {});
%         matlabbatch{17}.spm.stats.fmri_spec.sess(6).multi = {'/Users/benjaminsmith/Google Drive/oregon/code/DEV_scripts/fMRI/fx/multiconds/WTP/conditions/DEV023_2_WTP2.mat'};
%         matlabbatch{17}.spm.stats.fmri_spec.sess(6).regress = struct('name', {}, 'val', {});
%         matlabbatch{17}.spm.stats.fmri_spec.sess(6).multi_reg = {'/Users/benjaminsmith/Google Drive/oregon/data/DEV/bids_data/derivatives/auto-motion-fmriprep/sub-DEV023/sub-DEV023_ses-wave2_task-WTP_acq-2_run-1_desc-motion_regressors.txt'};
%         matlabbatch{17}.spm.stats.fmri_spec.sess(6).hpf = 128;
%         matlabbatch{17}.spm.stats.fmri_spec.sess(7).scans(1) = cfg_dep('Expand image frames: Expanded filename list.', substruct('.','val', '{}',{15}, '.','val', '{}',{1}, '.','val', '{}',{1}), substruct('.','files'));
%         matlabbatch{17}.spm.stats.fmri_spec.sess(7).cond = struct('name', {}, 'onset', {}, 'duration', {}, 'tmod', {}, 'pmod', {}, 'orth', {});
%         matlabbatch{17}.spm.stats.fmri_spec.sess(7).multi = {'/Users/benjaminsmith/Google Drive/oregon/code/DEV_scripts/fMRI/fx/multiconds/WTP/conditions/DEV023_2_WTP3.mat'};
%         matlabbatch{17}.spm.stats.fmri_spec.sess(7).regress = struct('name', {}, 'val', {});
%         matlabbatch{17}.spm.stats.fmri_spec.sess(7).multi_reg = {'/Users/benjaminsmith/Google Drive/oregon/data/DEV/bids_data/derivatives/auto-motion-fmriprep/sub-DEV023/sub-DEV023_ses-wave2_task-WTP_acq-3_run-1_desc-motion_regressors.txt'};
%         matlabbatch{17}.spm.stats.fmri_spec.sess(7).hpf = 128;
%         matlabbatch{17}.spm.stats.fmri_spec.sess(8).scans(1) = cfg_dep('Expand image frames: Expanded filename list.', substruct('.','val', '{}',{16}, '.','val', '{}',{1}, '.','val', '{}',{1}), substruct('.','files'));
%         matlabbatch{17}.spm.stats.fmri_spec.sess(8).cond = struct('name', {}, 'onset', {}, 'duration', {}, 'tmod', {}, 'pmod', {}, 'orth', {});
%         matlabbatch{17}.spm.stats.fmri_spec.sess(8).multi = {'/Users/benjaminsmith/Google Drive/oregon/code/DEV_scripts/fMRI/fx/multiconds/WTP/conditions/DEV023_2_WTP4.mat'};
%         matlabbatch{17}.spm.stats.fmri_spec.sess(8).regress = struct('name', {}, 'val', {});
%         matlabbatch{17}.spm.stats.fmri_spec.sess(8).multi_reg = {'/Users/benjaminsmith/Google Drive/oregon/data/DEV/bids_data/derivatives/auto-motion-fmriprep/sub-DEV023/sub-DEV023_ses-wave2_task-WTP_acq-4_run-1_desc-motion_regressors.txt'};
%         matlabbatch{17}.spm.stats.fmri_spec.sess(8).hpf = 128;
    end
end 
matlabbatch{length(matlabbatch)}.spm.stats.fmri_spec.fact = struct('name', {}, 'levels', {});
matlabbatch{length(matlabbatch)}.spm.stats.fmri_spec.bases.hrf.derivs = [0 0];
matlabbatch{length(matlabbatch)}.spm.stats.fmri_spec.volt = 1;
matlabbatch{length(matlabbatch)}.spm.stats.fmri_spec.global = 'None';
matlabbatch{length(matlabbatch)}.spm.stats.fmri_spec.mthresh = -Inf;
matlabbatch{length(matlabbatch)}.spm.stats.fmri_spec.mask = {'/Users/benjaminsmith/Google Drive/oregon/data/MNI152_T1_1mm_brain_mask.nii,1'};
matlabbatch{length(matlabbatch)}.spm.stats.fmri_spec.cvi = 'FAST';
mlb_spec_index = length(matlabbatch);
matlabbatch{length(matlabbatch)+1}.spm.stats.fmri_est.spmmat(1) = cfg_dep('fMRI model specification: SPM.mat File', substruct('.','val', '{}',{mlb_spec_index}, '.','val', '{}',{1}, '.','val', '{}',{1}), substruct('.','spmmat'));
matlabbatch{length(matlabbatch)}.spm.stats.fmri_est.write_residuals = 0;
matlabbatch{length(matlabbatch)}.spm.stats.fmri_est.method.Classical = 1;
mlb_est_index = length(matlabbatch);
mlb_contrasts_index = length(matlabbatch)+1;
%contrast preamble
matlabbatch{mlb_contrasts_index}.spm.stats.con.spmmat(1) = cfg_dep('Model estimation: SPM.mat File', substruct('.','val', '{}',{mlb_est_index}, '.','val', '{}',{1}, '.','val', '{}',{1}), substruct('.','spmmat'));

%previously modeled in DEV_scripts/fMRI/fx/models/WTP/fx_conditions_allwaves_contrast_design_all.xlsx
%we will have the same number of contrasts each time
%because we're only varying the number of sessions within each run.
%however, because we are varying the number of sessions included, we will
%need to vary the length of the weight vector

contrasts_time = {
    %T2>T1
    struct('name', 'HealthyLiked(T2>T1)', 'base_weights', [1 0 0 0 0 0 0 0 0]),
    struct('name', 'UnhealthyLiked(T2>T1)', 'base_weights', [0 1 0 0 0 0 0 0 0]),
    struct('name', 'HealthyDisliked(T2>T1)', 'base_weights', [0 0 1 0 0 0 0 0 0]),
    struct('name', 'UnhealthyDisliked(T2>T1)', 'base_weights', [0 0 0 1 0 0 0 0 0]),
    %T2<T1
    struct('name', 'HealthyLiked(T2<T1)', 'base_weights', [-1 0 0 0 0 0 0 0 0]),
    struct('name', 'UnhealthyLiked(T2<T1)', 'base_weights', [0 -1 0 0 0 0 0 0 0]),
    struct('name', 'HealthyDisliked(T2<T1)', 'base_weights', [0 0 -1 0 0 0 0 0 0]),
    struct('name', 'UnhealthyDisliked(T2<T1)', 'base_weights', [0 0 0 -1 0 0 0 0 0]),    %across waves
    };

for c_i = 1:length(contrasts_time)
    w1_weights = repmat(contrasts_time{c_i}.base_weights,1,length(included_runs_by_wave{1}));
    w2_weights = repmat(-contrasts_time{c_i}.base_weights,1,length(included_runs_by_wave{2}));
    contrasts_time{c_i}.weights = [ w1_weights w2_weights];
end 

%OK, now let's create the contrasts for the last four sets, contrasting
%healthy v. unhealthy and liked vs. disliked
%these are across sessions
%so it's a similar design to above, but we don't take the negation from w1
%to w2
% matlabbatch{19}.spm.stats.con.consess{9}.tcon.name = 'HealthyVSUnhealthy';
% matlabbatch{19}.spm.stats.con.consess{9}.tcon.weights = [0.0625 -0.0625 0.0625 -0.0625 0 0 0 0 0 0.0625 -0.0625 0.0625 -0.0625 0 0 0 0 0 0.0625 -0.0625 0.0625 -0.0625 0 0 0 0 0 0.0625 -0.0625 0.0625 -0.0625 0 0 0 0 0 0.0625 -0.0625 0.0625 -0.0625 0 0 0 0 0 0.0625 -0.0625 0.0625 -0.0625 0 0 0 0 0 0.0625 -0.0625 0.0625 -0.0625 0 0 0 0 0 0.0625 -0.0625 0.0625 -0.0625 0 0 0 0 0 0 0 0 0 0 0 0 0];
% matlabbatch{19}.spm.stats.con.consess{9}.tcon.sessrep = 'none';
% matlabbatch{19}.spm.stats.con.consess{10}.tcon.name = 'UnealthyVSHealthy';
% matlabbatch{19}.spm.stats.con.consess{10}.tcon.weights = [-0.0625 0.0625 -0.0625 0.0625 0 0 0 0 0 -0.0625 0.0625 -0.0625 0.0625 0 0 0 0 0 -0.0625 0.0625 -0.0625 0.0625 0 0 0 0 0 -0.0625 0.0625 -0.0625 0.0625 0 0 0 0 0 -0.0625 0.0625 -0.0625 0.0625 0 0 0 0 0 -0.0625 0.0625 -0.0625 0.0625 0 0 0 0 0 -0.0625 0.0625 -0.0625 0.0625 0 0 0 0 0 -0.0625 0.0625 -0.0625 0.0625 0 0 0 0 0 0 0 0 0 0 0 0 0];
% matlabbatch{19}.spm.stats.con.consess{10}.tcon.sessrep = 'none';
% matlabbatch{19}.spm.stats.con.consess{11}.tcon.name = 'HealthyLikedVsUnhealthyLiked';
% matlabbatch{19}.spm.stats.con.consess{11}.tcon.weights = [0.125 -0.125 0 0 0 0 0 0 0 0.125 -0.125 0 0 0 0 0 0 0 0.125 -0.125 0 0 0 0 0 0 0 0.125 -0.125 0 0 0 0 0 0 0 0.125 -0.125 0 0 0 0 0 0 0 0.125 -0.125 0 0 0 0 0 0 0 0.125 -0.125 0 0 0 0 0 0 0 0.125 -0.125 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0];
% matlabbatch{19}.spm.stats.con.consess{11}.tcon.sessrep = 'none';
% matlabbatch{19}.spm.stats.con.consess{12}.tcon.name = 'UnhealthyLikedVsHealthyLiked';
% matlabbatch{19}.spm.stats.con.consess{12}.tcon.weights = [-0.125 0.125 0 0 0 0 0 0 0 -0.125 0.125 0 0 0 0 0 0 0 -0.125 0.125 0 0 0 0 0 0 0 -0.125 0.125 0 0 0 0 0 0 0 -0.125 0.125 0 0 0 0 0 0 0 -0.125 0.125 0 0 0 0 0 0 0 -0.125 0.125 0 0 0 0 0 0 0 -0.125 0.125 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0];
% matlabbatch{19}.spm.stats.con.consess{12}.tcon.sessrep = 'none';

contrasts_conditions = {
    struct('name', 'HealthyVSUnhealthy', 'base_weights', [1 -1 1 -1 repmat(0,1,5)]),
    struct('name', 'UnealthyVSHealthy', 'base_weights', [-1 1 -1 1 repmat(0,1,5)]),
    struct('name', 'HealthyLikedVsUnhealthyLiked', 'base_weights', [1 -1 repmat(0,1,5)]),
    struct('name', 'UnhealthyLikedVsHealthyLiked', 'base_weights', [-1 1 repmat(0,1,5)])
    };

for c_i = 1:length(contrasts_conditions)
    w1_weights = repmat(contrasts_time{c_i}.base_weights,1,length(included_runs_by_wave{1}));
    w2_weights = repmat(contrasts_time{c_i}.base_weights,1,length(included_runs_by_wave{2}));
    contrasts_conditions{c_i}.weights = [ w1_weights w2_weights];
end 

contrasts_all = [contrasts_time; contrasts_conditions];

for c_i = 1:length(contrasts_all)

    matlabbatch{mlb_contrasts_index}.spm.stats.con.consess{1}.tcon.name = contrasts_all{c_i}.name;
    matlabbatch{mlb_contrasts_index}.spm.stats.con.consess{1}.tcon.weights = normalizePosAndNeg(contrasts_all{c_i}.weights);
    matlabbatch{mlb_contrasts_index}.spm.stats.con.consess{1}.tcon.sessrep = 'none';

end

%contrast postamble
matlabbatch{mlb_contrasts_index}.spm.stats.con.delete = 1;