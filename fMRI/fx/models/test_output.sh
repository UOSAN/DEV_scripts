TASK_TO_CHECK=SST

echo "Running a check to identify missing files for task $TASK_TO_CHECK"
echo ""
grep -Hl "Item 'NIfTI file(s)', field 'val': Number of matching files (0) less than required (1)" *.log | grep -Po "DEV\d*" > dev_missing_nii_files.txt

DEV_MISSING_FILES=`cat dev_missing_nii_files.txt`



# Create and execute batch job





for SUB in $DEV_MISSING_FILES; do
  echo $SUB

  FMRIPREP_FOLDER_PATH=/gpfs/projects/sanlab/shared/DEV/bids_data/derivatives/fmriprep/sub-$SUB
  BIDS_FOLDER=/gpfs/projects/sanlab/shared/DEV/bids_data/sub-$SUB
  TMP_DCM_2_BIDS_FOLDER=/gpfs/projects/sanlab/shared/DEV/bids_data/tmp_dcm2bids/sub-${SUB}_ses-wave1
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
      ls -lh $FMRIPREP_FOLDER_PATH/ses-wave1/func/*${TASK_TO_CHECK}*
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
        echo "also check the bids error logs printed below."
      fi
      #list bids data
      echo "bids folder data:"
      ls -lh $BIDS_FOLDER/ses-wave1/func/*
      echo "${TASK_TO_CHECK}-related data in the subject's tmp_dcm2bids folder:"
      ls -lh $TMP_DCM_2_BIDS_FOLDER/*${TASK_TO_CHECK}*
      echo "bids log files are:"
      ls -lh /gpfs/projects/sanlab/shared/DEV/DEV_scripts/org/bidsQC/conversion/logs_dcm2bids/*$SUB*
      
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
  #echo "checking for multiple SST files in BIDS:"
  #grep -Pn ".*SST.*" /gpfs/projects/sanlab/shared/DEV/DEV_scripts/org/bidsQC/conversion/logs_dcm2bids/*DEV188*
  echo "DCM files for this task are "
  ls -lhd /gpfs/projects/lcni/dcm/sanlab/Berkman/DEV/*$SUB*/Series*_${TASK_TO_CHECK}*

  echo ""
  echo ""
done

echo "this next step prints out some checks for errors or anomalies across ALL DEV subjects, working or not. This can be helpful for diagnosing problems."

echo "printing all subjects with more than one repetition across each task run based on BIDS logs:"
grep -Pn ".*SST.*has \d runs" /gpfs/projects/sanlab/shared/DEV/DEV_scripts/org/bidsQC/conversion/logs_dcm2bids/*

echo "printing all subjects where there's apparently no missing data for this task..."
grep -L "Item 'NIfTI file(s)', field 'val': Number of matching files (0) less than required (1)" *.log
echo "printing all subjects where there's IS no missing data for this task..."
grep "Item 'NIfTI file(s)', field 'val': Number of matching files (0) less than required (1)" *.log

echo "dcm directories for $TASK_TO_CHECK for all subjects"
ls -lhd /gpfs/projects/lcni/dcm/sanlab/Berkman/DEV/*/Series*_${TASK_TO_CHECK}*

