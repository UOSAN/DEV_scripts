import nibabel as nib
import glob
import os
import glob
import datetime

raise Exception("do not use this file. it is deprecated since dicom_correct has been modified.")
#want to print and log to a log file at the same time.
#set up a function that will do this
#pass args and kwargs to the print function
def print_and_log(message, end="\n", *args, **kwargs):
    print(message, end=end, *args, **kwargs)
    with open("bids_modify.log", "a") as f:
        f.write(str(message) + end)


#print the current datetime
print_and_log("Running modification script at " + str(datetime.datetime.now()))

#check out the dicom files and see what their units are

# itentify nii.gz files.
files_to_modify = glob.glob("../../../bids_data/sub-DEV*/ses-wave*/func/sub-DEV*_ses-wave*_bold.nii.gz")
files_to_modify.sort()
for i, fp in enumerate(files_to_modify):
    print_and_log(".", end="")
    img = nib.load(fp)
    if img.header.get_xyzt_units() != ('mm', 'sec'):
        print_and_log("\n")
        print_and_log(fp + " xytz units are not in mm and sec. Currently units are:")
        print_and_log(img.header.get_xyzt_units())
        print_and_log("Modifiying...",end="")
        img.header.set_xyzt_units('mm', 'sec')
        img.to_filename(fp)
        print_and_log("Successfully modified xytz units to mm and sec")

print_and_log("Complete.")

