echo "this file was designed to be run from the directly of a first-level output file"
echo "it identifies specifically why NIFTI files that were expected in this first-level run were not found."

grep -Hl "Item 'NIfTI file(s)', field 'val': Number of matching files (0) less than required (1)" *.log | grep -Po "DEV\d*" > dev_missing_nii_files.txt

DEV_MISSING_FILES=`cat dev_missing_nii_files.txt`

TASK_TO_CHECK=SST

# Create and execute batch job


for SUB in $DEV_MISSING_FILES; do
  echo $SUB

  FMRIPREP_FOLDER_PATH=/gpfs/projects/sanlab/shared/DEV/bids_data/derivatives/fmriprep/sub-$SUB
  BIDS_FOLDER=/gpfs/projects/sanlab/shared/DEV/bids_data/sub-$SUB
  HTML_LOG_PATH=/gpfs/projects/sanlab/shared/DEV/bids_data/derivatives/fmriprep/sub-$SUB.html

  if [[ -d "$FMRIPREP_FOLDER_PATH" ]]; then
    echo "$FMRIPREP_FOLDER_PATH exists. printing s6 files included..."
    S6_FILES_WILDCARD=$FMRIPREP_FOLDER_PATH/ses-wave1/func/s6*${TASK_TO_CHECK}*
    
      #count number of matching files
    filecount=$(ls $S6_FILES_WILDCARD 2> /dev/null | wc -l)
    if [ "$filecount" != "0" ]; then
      echo 's6 files found, printing...'
      ls -lh $S6_FILES_WILDCARD
    else
      echo "no s6 files found for task ${TASK_TO_CHECK} in fMRI prep folder:" 
      ls -lh $FMRIPREP_FOLDER_PATH/ses-wave1/func/s6*
      echo "checking BIDS folder for relevant data"
      BIDS_TASK_FILES_WILDCARD=$BIDS_FOLDER/ses-wave1/func/*${TASK_TO_CHECK}*
      
      #count number of matching files
      filecount=$(ls $BIDS_TASK_FILES_WILDCARD 2> /dev/null | wc -l)
      if [ "$filecount" != "0" ]; then
        echo "BIDS folder does contain ${TASK_TO_CHECK} files."
        echo "check $HTML_LOG_PATH"
      else
        echo "no ${TASK_TO_CHECK} in BIDS folder either."
        echo "First check the data was actually run in the Teams spreadsheet, then see if DICOMS were processed correctly."
      fi
      ls -lh $BIDS_FOLDER/ses-wave1/func/*
    fi
  else
    echo "$FMRIPREP_FOLDER_PATH does not exist"
    if [ -d "$BIDS_FOLDER" ]; then
        echo "$BIDS_FOLDER exists."
        
        if [ -f "$HTML_LOG_PATH" ]; then
          echo "fMRI prep log $HTML_LOG_PATH exists"
          echo "printing all ${TASK_TO_CHECK} files in the BIDS folder:"
          ls -lh $BIDS_FOLDER/ses-wave1/func/*${TASK_TO_CHECK}*
        else
          echo "fMRI prep log $HTML_LOG_PATH DOES NOT exist. seems like fMRIPrep was never run for this subject."
        fi


      else
        echo "$BIDS_FOLDER does not exist."
    fi
  fi
  echo ""
  echo ""
  echo ""
done
