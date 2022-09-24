# get all series
# get masks
# iterate through series
# iterate through masks
# produce the vector for this mask/series

# for each trial [CS, CG, FS, FG], identify the moment the subject learns the class of the trial;
# this may be slightly different for Go and Stop trials. For Stop trials it is simply the moment of the tone;
# for Go trials it's harder to specify.
# for each TRIAL, you will end up with a data table with columns (a) time from trial class reveal to image; (b) separate columns for measurement of each ROI
# these can be concatenated across trials, runs, and subjects
# then create n_{ROI}*n_{trial classes} graphs of samples, where x is the time from trial class reveal to image, and y is the measurement. plot a lowess curve.
# potentially overlay the lowess curves for each trial type so that the response within each ROI can be easily compared.
