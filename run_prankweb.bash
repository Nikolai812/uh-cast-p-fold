#!/bin/bash
# This script implements local run for prank2web predictions. It is to replace prank2web predictions via web automation
# due to failure of https://prankweb.cz/ site in August 2026.

# Save the current working directory
log_dir="logs"
mkdir -p "$log_dir"
timestamp=$(date +"%y%m%d_%H%M")

logfile="$(pwd)/${log_dir}/run_prankweb_bash_${timestamp}.log"

echo "Started run_prankweb.bash script at $(date '+%Y-%m-%d %H:%M:%S')" | tee -a "$logfile"
start_dir=$(pwd)

echo "Start directory: $start_dir" | tee -a "$logfile"
echo "Logfile defined as $logfile" | tee -a "$logfile"

#CONFIGURATION: Prankweb script location (hardcoded) and output directories
prankweb_dir="/mnt/c/pipeline/J17Pipeline_P2Rank/p2rank_2.6-alpha"
prankweb_output_dir="$prankweb_dir/test_output"

# CONFIGURATION: PDB files input directory, pacupp python feed up directory
# (Normal place- inside the uh-cast-p-fold project.)
# pipeline_base="/mnt/c/Users/user/source/repos/uh-cast-p-fold"
pipeline_base=$start_dir

# Former configuration with inputs and outputs inside the pipeline base directory
# input_dir="$pipeline_base/UI_SELENIUM/input"
# Modern configuration with external data lake -AGAIN HARDCODED!!!
input_dir="$pipeline_base/../kosloff-abdulghani-cavity-pipeline-data/input"

# (input_dir="/mnt/c/Users/user/Ubuntu/INPUT_PDB")

echo "!!!!!!!!!!! LOGGING DIRECTORY CONFIGURATION:" | tee -a "$logfile"
echo "prankweb_dir=$prankweb_dir" | tee -a "$logfile"
echo "prankweb_output_dir=$prankweb_output_dir" | tee -a "$logfile"
echo "pipeline_base=$pipeline_base" | tee -a "$logfile"
echo "input_dir=$input_dir" | tee -a "$logfile"

echo "!!!!!!!!!!!" | tee -a "$logfile"
echo "   " | tee -a "$logfile"
echo "   " | tee -a "$logfile"
echo "--------Beginning with previous results cleaning---------" | tee -a "$logfile"
echo "+++++++ Cleaning the prankweb_output_dir: $prankweb_output_dir" | tee -a "$logfile"
rm -rf "$prankweb_output_dir"/*

# List all .pdb files in the input directory
echo "Listing .pdb files in $input_dir:" | tee -a "$logfile"
ls "$input_dir"/*.pdb 2>/dev/null || echo "No .pdb files found in $input_dir at $(date '+%Y-%m-%d %H:%M:%S')" | tee -a "$logfile"

# Gather all .pdb files into an array (Enable nullglob so unmatched patterns expand to nothing),
shopt -s nullglob
pdb_input_files=("$input_dir"/*.pdb)

echo " "

# Check if any .pdb files were found
if [ ${#pdb_input_files[@]} -eq 0 ]; then
    echo "No .pdb files found in $input_dir, exiting" | tee -a "$logfile"
    echo "!!!!+++ EXITING, NO PDB FILES ++++!!!!!!!!!!!" | tee -a "$logfile"
    exit 1
fi

# Going tp pacupp directory
cd "$prankweb_dir" || { echo "Failed to go to $prankweb_dir at $(date '+%Y-%m-%d %H:%M:%S')" | tee -a "$logfile"; exit 1; }
echo "we are inside: $(pwd) at $(date '+%Y-%m-%d %H:%M:%S')" | tee -a "$logfile"

echo ""
echo ""
echo "!!!! Before subshell: JAVA_HOME= $JAVA_HOME"
# echo "PATH=$PATH"

(
  echo "!!!!!!!! entering Java 17 subshell !!!!!!!!!"
  export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
  export PATH="$JAVA_HOME/bin:$PATH"

  echo "JAVA_HOME= $JAVA_HOME"
  # echo "PATH=$PATH"

# Loop through each .pdb file
  for current_pdb in "${pdb_input_files[@]}"; do
    echo "Processing $current_pdb at $(date '+%Y-%m-%d %H:%M:%S')" | tee -a "$logfile"
    ./prank predict -f $current_pdb
    DELAY=2
  done

  echo "!!!!!!!! leaving Java 17 subshell !!!!!!!!!"
)
echo ""
echo ""
echo "!!!! After subshell JAVA_HOME= $JAVA_HOME"
# echo "PATH=$PATH"
echo ""
echo ""

# Probably, no special directory will be used for feed_up prank2web
# echo "Copying pacupp spreadsheet lists from  $pacupp_spreadsheet_lists_dir to $pacupp_python_feedup (with force overwrite)" | tee -a "$logfile"
# mkdir -p "$pacupp_python_feedup"
# cp -f "$pacupp_spreadsheet_lists_dir"/*.txt "$pacupp_python_feedup"/



# Return to the original directory
cd "$start_dir" || { echo "Failed to return to $start_dir" | tee -a "$logfile"; exit 1; }
echo "Returned to directory: $(pwd)" | tee -a "$logfile"
echo "exiting run_prankweb.bash script at $(date '+%Y-%m-%d %H:%M:%S')" | tee -a "$logfile"

