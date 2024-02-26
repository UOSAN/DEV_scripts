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

%can get the number of runs with numel(included_runs)
%-----------------------------------------------------------------------
% Job saved on 01-Aug-2023 14:12:41 by cfg_util (rev $Rev: 7345 $)
% spm SPM - SPM12 (7771)
% cfg_basicio BasicIO - Unknown
%-----------------------------------------------------------------------
for run_i = 1:length(included_runs_by_wave{1})
    run_name = included_runs_by_wave{1}(run_i);
    %just use the index because this is the first part of content in
    %matlabbatch
    matlabbatch{run_i}.cfg_basicio.file_dir.file_ops.file_fplist.dir = {'/projects/sanlab/shared/DEV/bids_data/derivatives/fmriprep_2022/sub-DEV001/ses-wave1/func/'};
    matlabbatch{run_i}.cfg_basicio.file_dir.file_ops.file_fplist.filter = sprintf('s6_sub-DEV001_ses-wave1_task-WTP_acq-%d_space-MNI152NLin2009cAsym_desc-preproc_bold.nii',run_name);
    matlabbatch{run_i}.cfg_basicio.file_dir.file_ops.file_fplist.rec = 'FPList';

end

wave_file_selector_first_mlb_index{1} = length(matlabbatch)+1;
for run_i = 1:length(included_runs_by_wave{1})
    run_name = included_runs_by_wave{1}(run_i);
    file_selector_string = sprintf('File Selector (Batch Mode): Selected Files (s6_sub-DEV001_ses-wave1_task-WTP_acq-%d_space-MNI152NLin2009cAsym_desc-preproc_bold.nii)',run_name);
    matlabbatch{length(matlabbatch)+1}.spm.util.exp_frames.files(1) = cfg_dep(file_selector_string, substruct('.','val', '{}',{run_i}, '.','val', '{}',{1}, '.','val', '{}',{1}, '.','val', '{}',{1}), substruct('.','files'));
    matlabbatch{length(matlabbatch)}.spm.util.exp_frames.frames = Inf;

end

for run_i = 1:length(included_runs_by_wave{2})
    run_name = included_runs_by_wave{2}(run_i);
    matlabbatch{length(matlabbatch)+1}.cfg_basicio.file_dir.file_ops.file_fplist.dir = {'/projects/sanlab/shared/DEV/bids_data/derivatives/fmriprep_2022/sub-DEV001/ses-wave2/func'};
    matlabbatch{length(matlabbatch)}.cfg_basicio.file_dir.file_ops.file_fplist.filter = sprintf('s6_sub-DEV001_ses-wave2_task-WTP_acq-%d_space-MNI152NLin2009cAsym_desc-preproc_bold.nii',run_name);
    matlabbatch{length(matlabbatch)}.cfg_basicio.file_dir.file_ops.file_fplist.rec = 'FPList';

end

wave_file_selector_first_mlb_index{2} = length(matlabbatch)+1;
for run_i = 1:length(included_runs_by_wave{2})
    run_name = included_runs_by_wave{2}(run_i);
    mlb_iterator = length(matlabbatch)+1;
    mlb_lookback = mlb_iterator - 4; %this is a reference back to the file filter.
    file_selector_string = sprintf('File Selector (Batch Mode): Selected Files (s6_sub-DEV001_ses-wave2_task-WTP_acq-%d_space-MNI152NLin2009cAsym_desc-preproc_bold.nii)',run_name);
    matlabbatch{mlb_iterator}.spm.util.exp_frames.files(1) = cfg_dep(file_selector_string, substruct('.','val', '{}',{mlb_lookback}, '.','val', '{}',{1}, '.','val', '{}',{1}, '.','val', '{}',{1}), substruct('.','files'));
    matlabbatch{mlb_iterator}.spm.util.exp_frames.frames = Inf;

end

matlabbatch{length(matlabbatch)+1}.spm.stats.fmri_spec.dir = {'/projects/sanlab/shared/DEV/nonbids_data/fMRI/fx/models/WTP/all_waves/conditions/sub-DEV001'};
matlabbatch{length(matlabbatch)}.spm.stats.fmri_spec.timing.units = 'secs';
matlabbatch{length(matlabbatch)}.spm.stats.fmri_spec.timing.RT = 2;
matlabbatch{length(matlabbatch)}.spm.stats.fmri_spec.timing.fmri_t = 72;
matlabbatch{length(matlabbatch)}.spm.stats.fmri_spec.timing.fmri_t0 = 36;
spec_i = 0;
for wave_i = 1:length(included_runs_by_wave)
    for run_i = 1:length(included_runs_by_wave{wave_i})
        run_name = included_runs_by_wave{wave_i}(run_i);
        %we don't need to specify wave names because for this analysis
        %there are always exactly 2 waves
        %spec_i = (wave_i - 1) + run_i; %going from 1 to 8 assuming all runs present
        spec_i = spec_i + 1; %going through all of the runs. don't assume presence of any
        file_selector_mlb_index = wave_file_selector_first_mlb_index{wave_i} + (run_i-1);
        matlabbatch{length(matlabbatch)}.spm.stats.fmri_spec.sess(spec_i).scans(1) = cfg_dep('Expand image frames: Expanded filename list.', substruct('.','val', '{}',{file_selector_mlb_index}, '.','val', '{}',{1}, '.','val', '{}',{1}), substruct('.','files'));
        matlabbatch{length(matlabbatch)}.spm.stats.fmri_spec.sess(spec_i).cond = struct('name', {}, 'onset', {}, 'duration', {}, 'tmod', {}, 'pmod', {}, 'orth', {});
        matlabbatch{length(matlabbatch)}.spm.stats.fmri_spec.sess(spec_i).multi = {sprintf('/projects/sanlab/shared/DEV/DEV_scripts/fMRI/fx/multiconds/WTP/conditions/DEV001_%d_WTP%d.mat',wave_i,run_name)};
        matlabbatch{length(matlabbatch)}.spm.stats.fmri_spec.sess(spec_i).regress = struct('name', {}, 'val', {});
        matlabbatch{length(matlabbatch)}.spm.stats.fmri_spec.sess(spec_i).multi_reg = {sprintf('/projects/sanlab/shared/DEV/bids_data/derivatives/auto-motion-fmriprep/sub-DEV001/sub-DEV001_ses-wave%d_task-WTP_acq-%d_run-1_desc-motion_regressors.txt',wave_i,run_name)};
        matlabbatch{length(matlabbatch)}.spm.stats.fmri_spec.sess(spec_i).hpf = 128;
    end
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

disp(contrasts_all)
for c_i = 1:length(contrasts_all)
    disp(c_i)
    matlabbatch{mlb_contrasts_index}.spm.stats.con.consess{1}.tcon.name = contrasts_all{c_i}.name;
    matlabbatch{mlb_contrasts_index}.spm.stats.con.consess{1}.tcon.weights = normalizePosAndNeg(contrasts_all{c_i}.weights);
    matlabbatch{mlb_contrasts_index}.spm.stats.con.consess{1}.tcon.sessrep = 'none';

end

%contrast postamble
matlabbatch{mlb_contrasts_index}.spm.stats.con.delete = 1;


throw_error = 1/0;