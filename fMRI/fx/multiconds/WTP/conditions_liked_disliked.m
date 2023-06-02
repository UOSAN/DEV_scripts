% This script pulls onsets and durations from the subject output files for
% WTP to create FX multicond files
%
% D.Cos 10/2018

%% Load data and intialize variables
%inputDir = '~/Dropbox (PfeiBer Lab)/Devaluation/Tasks/WTP/output';
inputDir = '~/Dropbox (University of Oregon)/UO-SAN Lab/Berkman Lab/Devaluation/Tasks/WTP/output';
runNames = {'run1', 'run2', 'run3', 'run4'};
waveNames = {'1', '2'};
writeDir = '/Users/benjaminsmith/Google Drive/oregon/code/DEV_scripts/fMRI/fx/multiconds/WTP/conditions_liked_disliked';
studyName = 'DEV';
filePattern = 'DEV.';
rowNum = -1;

condNames = {'liked','disliked'};
nConds = length(condNames);

% list files in input directory
runFiles = dir(sprintf('%s/*/*%s*.mat', inputDir, filePattern));
filesCell = struct2cell(runFiles);

% extract subject IDs
subjectID = unique(extractBetween(filesCell(1,:), 5,7));

% exclude test responses
excluded = subjectID(cellfun(@isempty,regexp(subjectID, '[0-2]{1}[0-9]{2}')));
subjectID = subjectID(~cellfun(@isempty,regexp(subjectID, '[0-2]{1}[0-9]{2}')));
fprintf(1, 'Excluded: %s\n', excluded{:})

% initialize table
eventtable  = cell2table(cell(0,9), 'VariableNames', {'subjectID', 'wave', 'run', 'foodpic', 'health', 'liking', 'liking_rating', 'bid', 'rt'});

trials = {};
%% Loop through subjects and runs and save names, onsets, and durations as .mat files
for i = 1:numel(subjectID)
    sub = subjectID{i};
    
    for j = 1:numel(waveNames)
        wave = waveNames{j};
        files = dir(fullfile(inputDir, sprintf('/%s%s/%s.%s.%s.mat', studyName, sub, studyName, sub, wave)));
        subFileName = {files.name};

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

                    % Check if run exists
                    if isfield(Data, (char(run))) && isfield(Data.(char(run)), 'FoodOnset')
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
