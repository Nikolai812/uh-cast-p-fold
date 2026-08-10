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
Write-Output "Starting pacupp script for JMOL"
wsl -d Ubuntu --exec /bin/bash -c "./run_pacupp.bash"
Write-Output "Pacupp over JMOL completed. Starting python 4 predictions processing"

Write-Output "Starting local prankweb script"
wsl -d Ubuntu --exec /bin/bash -c "./run_prankweb.bash"
Write-Output "Local prankweb script completed"

python .\UI_SELENIUM\main.py
if ($LASTEXITCODE -ne 0) {
    Write-Output "Python 4-predictions: fatal error unhandled, terminating further execution"
    exit 1
}
Write-Output "4 predictions .ps1 script completed"


