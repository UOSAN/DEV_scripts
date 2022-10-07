from nilearn.glm.first_level import spm_hrf


# get a canonical HRF for convolving with a BOLD response
def get_canonical_hrf():
    """Get a canonical HRF."""
    hrf = spm_hrf(1)
    return hrf

# convolve series with HRF

def convolve_with_hrf_function(series):
    """Convolve series with HRF function."""
    hrf = spm_hrf(1)
    return np.convolve(series, hrf)[:len(series)]



