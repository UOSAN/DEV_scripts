
#implemented based on nistats.hemodynamic_models.spm_hrf
get_hrf <- function(tr, oversampling = 50, time_length = 32, onset = 0,
                delay = 6, undershoot = 16, dispersion = 1,
                u_dispersion = 1, ratio = 0.167) {
    dt <- tr / oversampling
    time_stamps <- seq(0, time_length, length.out = round(as.numeric(time_length) / dt))
    time_stamps <- time_stamps - onset

    # define peak and undershoot gamma functions
    peak_gamma <- dgamma((time_stamps  - dt)/dispersion, shape= delay / dispersion)
    undershoot_gamma <- dgamma((time_stamps -dt)/u_dispersion, shape=  undershoot / u_dispersion)

    # calculate the hrf
    hrf <- peak_gamma - ratio * undershoot_gamma
    hrf = hrf/sum(hrf)
    return(hrf)
}