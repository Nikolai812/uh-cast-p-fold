# Base directory where the script is allowed to run
# $base_dir = "C:\Users\user\source\repos\uh-cast-p-fold"

# Get current directory as a STRING
$start_dir = (Get-Location).Path

Write-Host "Starting rerun only cavity plus predictions from directory: $start_dir"

# # Verify the script is run from the expected directory
# if ($start_dir -ne $base_dir) {
#     Write-Warning "Exiting: this script must be run from: $base_dir"
#     Write-Error "Current directory is: $start_dir"
#     exit 1
# }

$base_dir = $start_dir

python .\UI_SELENIUM\main.py --rerun-prediction=cvpl
if ($LASTEXITCODE -ne 0) {
    Write-Output "Cavityplus redictions: fatal error unhandled, terminating further execution"
    exit 1
}

python data_to_pm_input.py -c
Write-Output "only cavity plus .ps1 script completed"


