disp("making batch...");

fileID=fopen(script_file);
textstuffcell=textscan(fileID, '%[^\n]');
fclose(fileID);

regexp=num2str(replacesid);
replaceexpr=num2str(subid);
disp(regexp);
disp(replaceexpr);
newtextcell=cellfun(@(x) regexprep(x, regexp, replaceexpr), textstuffcell{1}, 'UniformOutput', false);

newtext=strjoin(newtextcell, '\n');

eval(newtext);

[outdir, outfile] = fileparts(script_file);

outdirfull = fullfile(outdir,'sid_batches',outfile);

if ~exist(outdirfull, 'dir')
  mkdir(outdirfull);
end


disp(fullfile(outdirfull,strcat(num2str(sub),'_',outfile,'.mat')));

save(fullfile(outdirfull,strcat(num2str(sub),'_',outfile,'.mat')),'matlabbatch');
