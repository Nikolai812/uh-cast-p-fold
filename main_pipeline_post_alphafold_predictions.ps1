# Base directory where the script is allowed to run
# $base_dir = "C:\Users\user\source\repos\uh-cast-p-fold"

# Get current directory as a STRING
$start_dir = (Get-Location).Path

Write-Host "Starting PostAlphaFold cavity predictions from directory: $start_dir"

# Verify the script is run from the expected directory
# if ($start_dir -ne $base_dir) {
#     Write-Warning "Exiting: this script must be run from: $base_dir"
#     Write-Error "Current directory is: $start_dir"
#     exit 1
# }

$base_dir = $start_dir

Write-Output "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
Write-Output "Starting pacupp script for JMOL"
wsl -d Ubuntu --exec /bin/bash -c "./run_pacupp.bash"
Write-Output "Pacupp over JMOL completed."
Write-Output ""
Write-Output "================================================================="
Write-Output ""
Write-Output "Starting local prankweb script"
wsl -d Ubuntu --exec /bin/bash -c "./run_prankweb.bash"
Write-Output "Local prankweb script completed. Starting python 4 predictions processing"
Write-Output "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"

python .\UI_SELENIUM\main.py
if ($LASTEXITCODE -ne 0) {
    Write-Output "Python 4-predictions: fatal error unhandled, terminating further execution"
    exit 1
}
Write-Output "4 cavity predictions completed"


# Copy UI_SELENIUM output to PYMOL_SCRIPTS input (with clean before copy)
python data_to_pm_input.py -c


# Write-Output "Starting consensus building and pymol scripts preparation"

$pymol_scripts = Join-Path $base_dir "PYMOL_SCRIPTS"
Write-Host "Changing directory to:"
Write-Host "   $pymol_scripts"
cd $pymol_scripts

Write-Host  "Starting pm_main.py script"

python .\pm_main.py

cd  $base_dir

Write-Host  "Returned to base dir:"
Write-Host  "  $base_dir"



