%designed to take a matlabbatch script file, run it in matlab, and save the resulting output as a mat file

disp("running script:")
disp(script_file);
fileID=fopen(script_file);
textstuffcell=textscan(fileID, '%[^\n]');
fclose(fileID);

newtext=strjoin(textstuffcell{1}, '\n');

eval(newtext);

[outdir, outfile] = fileparts(script_file);

outdirfull = fullfile(outdir,'sid_batches',outfile);

if ~exist(outdirfull, 'dir')
  mkdir(outdirfull);
end

save(fullfile(outdirfull,strcat(outfile,'.mat')),'matlabbatch');
