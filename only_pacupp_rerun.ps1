# Base directory where the script is allowed to run
# $base_dir = "C:\Users\user\source\repos\uh-cast-p-fold"

# Get current directory as a STRING
$start_dir = (Get-Location).Path

Write-Host "Starting rerun only cavity plus predictions from directory: $start_dir"

# Verify the script is run from the expected directory
# if ($start_dir -ne $base_dir) {
#     Write-Warning "Exiting: this script must be run from: $base_dir"
#     Write-Error "Current directory is: $start_dir"
#     exit 1
# }

$base_dir = $start_dir
Write-Output "Starting pacupp script for JMOL"

wsl -d Ubuntu --exec /bin/bash -c "./run_pacupp.bash"

if ($LASTEXITCODE -ne 0) {
    Write-Output "run_pacupp.bash exited with error: terminating further execution"
    exit 1
}

Write-Output "Pacupp over JMOL completed. Starting post JMOL output handling and creating Excel files"
python .\UI_SELENIUM\main.py --rerun-prediction=pupp
if ($LASTEXITCODE -ne 0) {
    Write-Output "Python pacupp predictions: fatal error unhandled, terminating further execution"
    exit 1
}

python data_to_pm_input.py -c
Write-Output "only pacupp .ps1 script completed"


