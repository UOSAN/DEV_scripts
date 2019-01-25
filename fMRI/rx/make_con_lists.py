import os
from datetime import datetime

def main():
    """
    Create a text file that lists the full path to first level model contrast files - one text file per contrast.  
    """
    task = 'gng'
    study = 'REV'
    number_confiles = 12
    output_directory = os.path.join(os.path.sep, 'projects', 'sanlab', 'shared', study, study + '_scripts', 'fMRI', 'rx', 'prepost_analysis', task, 'confile_lists')
    check_dir(output_directory)
    toplevel_dir_confiles = os.path.join(os.path.sep, 'projects', 'sanlab', 'shared', study, 'bids_data', 'derivatives', 'prepost_analysis')
    confiles = get_confiles(number_confiles)
    subject_dir_fullpaths = get_subject_dirs(toplevel_dir_confiles)
    check_confiles(confiles, subject_dir_fullpaths, output_directory, task)


def check_dir(dir_fullpath:str):
    """
    Check if a directory exists. If not, create it.

    @type dir_fullpaths:        string
    @param dir_fullpaths:       Path to directory to check
    """
    if not os.path.isdir(dir_fullpath):
        os.mkdir(dir_fullpath)


def touch(path:str):
    """
    Create a new file.
    
    @type path:     string
    @param path:    path to - including name of - file to be created
    """
    with open(path, 'a'):
        os.utime(path, None)


def write_to_file(filename, message):
    """
    Write text to the specified text file.

    @type message:          string
    @param message:         text to be written to the file
    """
    with open(filename, 'a') as logfile:
        logfile.write(message + os.linesep)


def get_confiles(number_confiles:int):
    """
    Create a list of contrast file names.

    @type number_confiles:           numeric
    @param number_confiles:          number of contrast files that exist per participant

    @rtype:                          list
    @return:                         list of contrast nifti file names as strings
    """
    confiles = [ 'con_' + str(itervar).zfill(4) + '.nii' for itervar in range(1, number_confiles + 1)]
    return confiles


def get_subject_dirs(toplevel_dir_confiles):
    """
    Create a list containing each absolute path for the subject directories in the first level model output directory.

    @type toplevel_dir_confiles     string
    @param toplevel_dir_confiles    path to first level model output directory that contains subject specific directories

    @rtype:                         list
    @return                         list of paths to each subject's first level model output (at the subject-level directory)
    """
    subject_dir_fullpaths = [ os.path.join(toplevel_dir_confiles, d) for d in os.listdir(toplevel_dir_confiles) if 'sub-REV' in d]
    return subject_dir_fullpaths


def check_confiles(confiles, subject_dir_fullpaths, output_directory, task):
    for subject_dir_fullpath in subject_dir_fullpaths:
        for confile in confiles:
            output_textfile = os.path.join(output_directory, confile[0:-4] + datetime.now().strftime("%Y%m%d-%H%M") + '.txt')
            error_textfile = os.path.join(output_directory, 'missing_' + confile[0:-4] + datetime.now().strftime("%Y%m%d-%H%M") + '.txt')
            subject_confile_fullpath = os.path.join(subject_dir_fullpath, 'fx', task, confile)
            if not os.path.isfile(output_textfile):
                touch(output_textfile)
            if not os.path.isfile(error_textfile):
                touch(error_textfile)
            create_confile_reports(output_directory, confile, subject_confile_fullpath, output_textfile, error_textfile, subject_dir_fullpath, task)
    print('Done. Reports can be found in ' + output_directory)

                
def create_confile_reports(output_directory, confile, subject_confile_fullpath, output_textfile, error_textfile, subject_dir_fullpath, task):
        if os.path.isfile(subject_confile_fullpath):
            write_to_file(output_textfile, "'" + subject_confile_fullpath + "'")
        else:
            if os.path.isdir(os.path.join(subject_dir_fullpath, 'fx', task)):
                write_to_file(error_textfile, subject_confile_fullpath)


main()