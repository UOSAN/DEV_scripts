% This script pulls onsets and durations from the subject output files for
% WTP to create FX multicond files
%
% D.Cos 10/2018

%% Load data and intialize variables
%inputDir = '~/Dropbox (PfeiBer Lab)/Devaluation/Tasks/WTP/output';
inputDir = '~/Dropbox (University of Oregon)/UO-SAN Lab/Berkman Lab/Devaluation/Tasks/WTP/output';
runNames = {'run1', 'run2', 'run3', 'run4'};
waveNames = {'1', '2'};
writeDir = '/Users/benjaminsmith/Google Drive/oregon/code/DEV_scripts/fMRI/fx/multiconds/ROC/conditions';
studyName = 'DEV';
filePattern = 'run';
nTrials = 20;
rowNum = -1;

condNames = {'liked','disliked'};
nConds = length(condNames);

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
%% Loop through subjects and runs and save names, onsets, and durations as .mat files
for i = 1:numel(subjectID)
    sub = subjectID{i};
    
    for j = 1:numel(waveNames)
        wave = waveNames{j};
        files = dir(fullfile(inputDir, sprintf('%s_%s_*%s*.mat', sub, wave, filePattern)));
        subFileName = {files.name};
        
        if numel(files) > length(runNames)
            warning('Excess of files. Subject %s has %d files for wave %s. Expected %d. If there are duplicate files the last one will be selected.', sub, numel(files), wave,length(runNames))
        end
        if numel(files) < length(runNames)
            warning('Run files missing. Subject %s has %d files for wave %s. Expected %d', sub, numel(files), wave,length(runNames))
        end


        % log missing trial info
        trials{i+j+rowNum,1} = sprintf('%s%s', studyName, sub);
        trials{i+j+rowNum,2} = sprintf('%s', wave);

        %% Load text file
        if ~isempty(subFileName)
            subFile = sprintf('%s/%s%s/%s', inputDir, studyName, sub, subFileName{end}); %select the last file
            if exist(subFile)
                load(subFile);

                for k = 1:numel(runNames)
                    run = runNames{k};
                    
                    if ~contains(run_info.stimulus_input_file, 'beh')
                    	warning('Behavioral version of task was run for subject %s wave %s %s.', sub, wave, run)
                    	continue
                    end


                        %% Pull onsets and durations
                        % Trials
                        idxs_all = find(~cellfun(@isempty,run_info.tag(:,1)));
                        idxs_image = idxs_all(2:3:length(idxs_all));
                        durations = num2cell(run_info.durations(idxs_image));
                        durations([durations{:}] == 0) = []; % remove incomplete trials
                        onsets = num2cell(run_info.onsets(idxs_image));
                        %onsets([onsets{:}] == 0) = []; % remove incomplete trials
                        onsets = onsets(1:length(durations)); % remove incomplete trials to match durations
                        
                        % Instructions
                        idxs_instructions = idxs_all(1:3:length(idxs_all));
                        durations{length(durations)+1} = run_info.durations(idxs_instructions)';
                        durations{length(durations)}(durations{length(durations)}(:) == 0) = []; % remove incomplete trials
                        
                        onsets{length(onsets)+1} = run_info.onsets(idxs_instructions)';
                        %onsets{length(onsets)}(onsets{length(onsets)}(:) == 0) = []; % remove incomplete trials
                        onsets{length(onsets)} = onsets{length(onsets)}(1:length(durations{length(durations)})); % remove incomplete trials to match durations
 
                        % Ratings
                        idxs_ratings = idxs_all(3:3:length(idxs_all));
                        ratings = run_info.responses(idxs_ratings)';
                        onsets{length(onsets)+1} = run_info.onsets(idxs_ratings)';
                        onsets{length(onsets)}(onsets{length(onsets)}(:) == 0) = []; % remove incomplete trials
                        durations{length(durations)+1} = run_info.durations(idxs_ratings)';
                        if length(durations{length(durations)}) > length(onsets{length(onsets)})
                            durations{length(durations)} = durations{length(durations)}(1:length(onsets{length(onsets)})); % remove incomplete trials
                        end
                    	

                        %% Pull onsets
                        trial_onsets = Data.(char(run)).FoodOnset;
                        trial_durations = Data.(char(run)).FoodDuration;
                        trial_names = Data.(char(run)).Cond;
                        
                        names = condNames;
                        %create empty cell arrays
                        durations = cell(1,length(names));
                        onsets = cell(1,length(names));
                        
                        for a = 1:length(trial_onsets)
                            % finding conditions  that trial a is in  
                            cond_i = -1; 
                            for b = 1:length(condNames)
                                if endsWith(trial_names{a},strcat('_', condNames{b}))
                                    cond_i = b;
                                end 
                            end 
                            % produces error message if cannot find match
                            % for condition
                            if cond_i == -1
                                ME = MException('Could not find match');
                                throw(ME)
                            end 
                            %assign onset
                            durations{cond_i}(end+1,:)=trial_durations{a};
                            onsets{cond_i}(end+1,:)=trial_onsets{a};
                            
                            
                        end
                        
                        
                        %% Define output file name
                        outputName = sprintf('%s%s_%s_WTP%d.mat', studyName, sub, wave, k);

                        %% Save as .mat file and clear
                        if ~exist(writeDir); mkdir(writeDir); end

                        if ~(isempty(onsets{1}) && isempty(onsets{2}))
                            save(fullfile(writeDir,outputName),'names','onsets','durations');
                        else
                            warning('File is empty. Did not save %s.', outputName);
                        end
                        
                        %aim is to create 'names', 'durations', 'onsets'
                        %each has one element for each condition
                        %and then within each of them
                        %there is one element for each trial in that
                        %condition.

                        %% Log missing trial info
                        trials{i+j+rowNum,k+2} = length(onsets);

                        %% Add subject data to table
                        %% we did this in betaseries, no need to do it again.

                        
                        clear names onsets durations;
                    else
                        warning('Subject %s%s wave %s is missing %s', studyName, sub, wave, run)
                    end
                end
            end
        else
            warning('Unable to load subject %s%s wave %s.', studyName, sub, wave)
        end
    end
    rowNum = rowNum+1;
end
  
% save missing trial info
table = cell2table(trials,'VariableNames',[{'subjectID'}, {'wave'}, runNames{:}]);
writetable(table,fullfile(writeDir, 'trials.csv'),'Delimiter',',')
fprintf('\nTrial info saved in %s\n', fullfile(writeDir, 'trials.csv'))
