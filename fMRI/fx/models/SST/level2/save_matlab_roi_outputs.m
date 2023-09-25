output_filename = '/Users/benjaminsmith/Dropbox (University of Oregon)/UO-SAN Lab/Berkman Lab/Devaluation/analysis_files/level2/SST/health_conditions_groups_20230908/Unhealthy_NoGo(W2-W1)/rois_raw.csv';
writecell( ...
    {'y_neurosynth_response_inhibition_sfg_mean', ...
    'y_neurosynth_response_inhibition_right_frontal_pole_mean'}, ...
    output_filename )

roi_data = [y_neurosynth_response_inhibition_sfg_mean y_neurosynth_response_inhibition_right_frontal_pole_mean];
writematrix(roi_data, output_filename,'WriteMode','append')

% insula
% y_neurosynth_response_inhibition_insula_mean = mean(y,2);
output_filename = '/Users/benjaminsmith/Dropbox (University of Oregon)/UO-SAN Lab/Berkman Lab/Devaluation/analysis_files/level2/SST/health_conditions_groups_20230908/Unhealthy_NoGo(W2-W1)/rois_raw_insula.csv';
writecell( ...
    {'y_neurosynth_response_inhibition_insula_mean'}, ...
    output_filename )

roi_data = [y_neurosynth_response_inhibition_insula_mean ];
writematrix(roi_data, output_filename,'WriteMode','append');
