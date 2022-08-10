% example of how to build a parametric modulation in SPM.
% this can be included in the original file, simply saving it with the DEV*_1_SST1.mat file.
% that file is gnerated by the muldicodes python code, so we need to work out how to create that in python.
%
pmod = struct('name',{''},'param',{},'poly',{});
pmod(1).name{1}='condition_1_regressor_1'
pmod(1).param{1}=[1 2 4 5 6]
pmod(2).name{1}='condition_2_regressor_1';
pmod(2).param{1}=[1 2 4 5];
pmod(2).poly{1}=1;


%EXAMPLE:'
%Make an empty pmod structure: '
  pmod = struct('name',{''},'param',{},'poly',{});
%Specify one parametric regressor for the first condition: '
  pmod(1).name{1}  = 'regressor1';
  pmod(1).param{1} = [1 2 4 5 6];
  pmod(1).poly{1}  = 1;
%Specify 2 parametric regressors for the second condition: '
  pmod(2).name{1}  = 'regressor2-1';
  pmod(2).param{1} = [1 3 5 7]; 
  pmod(2).poly{1}  = 1;
  pmod(2).name{2}  = 'regressor2-2';
  pmod(2).param{2} = [2 4 6 8 10];
  pmod(2).poly{2}  = 1;
  