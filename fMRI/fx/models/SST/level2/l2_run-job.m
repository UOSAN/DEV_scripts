%this is an early file--I'm still working out how to do this efficiently
%ideally we would also generate the results but I am still working out how
%to do that.
%it also only does the latter part of the level2 analysis
%doesn't actually auto-generate the script files and there's potential to
%automate that too.

level_2_base_dir = '/Users/benjaminsmith/Google Drive/oregon/code/DEV_scripts/fMRI/fx/models/SST/level2/';

cd(level_2_base_dir)


job_folder_list = {'CGFollowing(CS-FS)','CS-FS(PrecedingCorrectGo)','CGFollowing(FS-CS)', 'FS-CS(PrecedingCorrectGo)'
    };
for job = job_folder_list
    cd(level_2_base_dir)
    disp(job{1});
    cd(['cg_following_failed_and_correct_stop_pss/attempt3_20220914/' job{1}])
    contrast_one_sample_design_estimate
    spm_jobman('run', matlabbatch);
end

for job = job_folder_list
    cd(level_2_base_dir)
    disp(job{1});
    cd(['cg_following_failed_and_correct_stop/attempt7_20220914/' job{1}])
    contrast_one_sample_design_estimate
    spm_jobman('run', matlabbatch);
end

cd('/Users/benjaminsmith/Google Drive/oregon/code/DEV_scripts/fMRI/fx/models/SST/level2/stop_failed_vs_correct/attempt_20220914/FailedStop-CorrectStop')
contrast_one_sample_design_estimate