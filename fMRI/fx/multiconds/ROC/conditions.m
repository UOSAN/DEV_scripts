% This script pulls onsets and durations from the subject output files for
% ROC to create FX multicond files
%
% D.Cos 10/2018


%% Load data and intialize variables
%inputDir = '~/Dropbox (PfeiBer Lab)/Devaluation/Tasks/ROC/output';
inputDir = '~/Dropbox (University of Oregon)/UO-SAN Lab/Berkman Lab/Devaluation/Tasks/ROC/output';
%inputDir = '~/Dropbox (University of Oregon)/Berkman Lab/Devaluation/Tasks/ROC/output';
runNames = {'run1', 'run2', 'run3', 'run4'};
waveNames = {'1', '2'};

%writeDir = '~/Documents/code/sanlab/DEV_scripts/fMRI/fx/multiconds/ROC/condition';
writeDir = '~/Google Drive/oregon/code/DEV_scripts/fMRI/fx/multiconds/ROC/conditions';
studyName = 'DEV';
filePattern = 'run'; 
nTrials = 20;
rowNum = -1;

% list files in input directory
runFiles = dir(sprintf('%s/*%s*.mat', inputDir, filePattern));
filesCell = struct2cell(runFiles);

% extract subject IDs
subjectID = unique(extractBetween(filesCell(1,:), 1,6));

% exclude test responses
excluded = subjectID(cellfun(@isempty,regexp(subjectID, '[0-3]{1}[0-9]{2}')));
subjectID = subjectID(~cellfun(@isempty,regexp(subjectID, '[0-3]{1}[0-9]{2}')));
fprintf(1, 'Excluded: %s\n', excluded{:})

% initialize table
eventtable  = cell2table(cell(0,7), 'VariableNames', {'file', 'subjectID', 'wave', 'run', 'rating', 'rt', 'condition'});

trials = {};

nConds = 4;
condNames = {'lookNeutral', 'lookNoCrave', 'lookCrave', 'reappraiseCrave', 'instructions', 'ratings'};


%% Loop through subjects and runs and save names, onsets, and durations as .mat files
for i = 1:numel(subjectID)
    sub = subjectID{i};
    for i1 = 1:numel(waveNames)
        wave = waveNames{i1};
        %files = dir(fullfile(inputDir, sprintf('%s_%s*.mat', sub, filePattern)));
        files = dir(fullfile(inputDir, sprintf('%s_%s_*%s*.mat', sub, wave, filePattern)));
    
        % warn if there are not 2 files
        if numel(files) ~= length(runNames)
            warning(sub)
            warning('Incorrect number of files. Subject %s has %d files.', sub, numel(files))
        end
        
        % log missing trial info
        missing{i,1} = sprintf('%s%s', studyName, sub);
        
        for j = 1:numel(runNames)
            %% Load text file
            run = runNames{j};
            %runFile = dir(fullfile(inputDir, sprintf('%s_%s%s*.mat', sub, filePattern, run)));
            runFile = dir(fullfile(inputDir, sprintf('%s_%s_*%s*.mat', sub, wave, run)));
            
            subFileName = {runFile.name};
            
            if ~isempty(subFileName)
                subFile = sprintf('%s/%s', inputDir, subFileName{end}); %select the last file
                if numel(subFileName)>1
                        warning([sprintf('there was more than one runfile for this run. Runfiles were:\n'),sprintf('%s; ',subFileName{:}),sprintf('\nof those, selected the last one, %s',subFile)])
                end

    
                if exist(subFile)
                    load(subFile);
    
                    %% Initialize names 
                    names = condNames;
                    
                    %% Pull onsets
                    for a = 1:nConds
                        idxs = find(strcmp(run_info.tag(:), num2str(a)));
                        idxs_image = idxs(2:3:length(idxs));
                        idxs_ratings_cond = idxs(3:3:length(idxs));
                        ratings_cond = run_info.responses(idxs_ratings_cond)';
                        onsets{a} = run_info.onsets(idxs_image)';
                        onsets{a}(find(cellfun(@isempty,ratings_cond))) = []; % remove missing trials
                    end
    
                    % Instructions
                    idxs_all = find(~cellfun(@isempty,run_info.tag(:,1)));
                    idxs_instructions = idxs_all(1:3:length(idxs_all));
                    onsets{nConds+1} = run_info.onsets(idxs_instructions)';
                    onsets{nConds+1}(onsets{nConds+1} == 0) = []; % remove incomplete trials
    
                    % Ratings
                    idxs_ratings = idxs_all(3:3:length(idxs_all));
                    ratings = run_info.responses(idxs_ratings)';
                    onsets{nConds+2} = run_info.onsets(idxs_ratings)';
                    onsets{nConds+2}(find(cellfun(@isempty,ratings))) = []; % remove missing trials
    
                    %% Create durations
                    durations = onsets;
    
                    % image conditions
                    for b = 1:nConds
                        durations{b} = repelem(5, length(durations{b}))';
                    end
    
                    % instructions
                    durations{nConds+1} = repelem(2, length(durations{nConds+1}))';
    
                    % ratings (duration = rt)
                    durations{nConds+2} = run_info.rt(idxs_ratings)';
                    durations{nConds+2}(find(cellfun(@isempty,ratings))) = []; % remove missing trials
                    
                    %% Pull onsets and durations for missed responses (if any)
                    % Missing responses are coded from image onset to rating
                    % offset (9 seconds). Exclude incomplete trials.
                    if sum(cellfun(@isempty,ratings) > 0)
                        idxs_missing = idxs_ratings(find(cellfun(@isempty,ratings)))-1;
                        if sum(run_info.onsets(idxs_missing)) > 0
                            names(nConds+3) = {'noResponse'};
                            onsets(nConds+3) = {run_info.onsets(idxs_missing)'};
                            onsets{nConds+3}(onsets{nConds+3} == 0) = []; % remove incomplete trials
                            durations(nConds+3) = {repelem(9, length(onsets{nConds+3}))'};
                        end
                    end

                    %% need to remove CONDITIONS for any empty conditions because these will cause level 1 errors
                    % these need to be handled pretty carefully
                    % when doing level 2 analyses we need to ensure we
                    % don't just assume a condition always corresponds to
                    % the same numbered beta file.
                    if cellfun('length',onsets)~=cellfun('length',durations)
                        error('for %s %s %s, length of onsets does not match length of durations',sub,wave,run)
                    end
                    %great, we know the lengths are the same so we can now
                    %remove from names, onsets, and durations
                    if any(cellfun('length',onsets)==0)
                        warning(['for ' sub ' ' wave ' ' run ', some conditions had no trials and were excluded.'])
                        warning(names{cellfun('length',onsets)==0})
                        zero_length_conditions = cellfun('length',onsets)==0;
                        names = names(~zero_length_conditions);
                        onsets = onsets(~zero_length_conditions);
                        durations = durations(~zero_length_conditions);

                    end

    
                    %% Define output file name
                    %outputName = sprintf('%s%s_ROC%d.mat', studyName, sub, j);
                    %% Define output file name
                    outputName = sprintf('%s_%s_ROC_%s.mat', sub, wave, run);

    
                    %% Save as .mat file and clear
                    if ~exist(writeDir); mkdir(writeDir); end
                    
                    if any(~cellfun('isempty', onsets)) % if any of the conditions aren't empty
                        save(fullfile(writeDir,outputName),'names','onsets','durations');
                    else %all conditions are empty.
                        warning('File is empty. Did not save %s.', outputName);
                    end
                    
                    %% Log missing trial info
                    missing{i,j+1} = sum(cellfun(@isempty,ratings));
                    
                    clear names onsets durations;
                end
            else
                warning('Unable to load subject %s run %s; file not found.', sub, run);
            end
        end
    end
end
  
% save missing trial info
missing(cellfun('isempty', missing)) = {NaN};
table = cell2table(missing,'VariableNames',[{'subjectID'}, runNames{:}]);
writetable(table,fullfile(writeDir, 'missing.csv'),'Delimiter',',')
fprintf('\nMissing trial info saved in %s\n', fullfile(writeDir, 'missing.csv'))