# Base directory where the script is allowed to run
# $base_dir = "C:\Users\user\source\repos\uh-cast-p-fold"

# Get current directory as a STRING
$start_dir = (Get-Location).Path

Write-Host "Starting rerun only Cast-p-Fold plus predictions from directory: $start_dir"

# Verify the script is run from the expected directory
# if ($start_dir -ne $base_dir) {
#     Write-Warning "Exiting: this script must be run from: $base_dir"
#     Write-Error "Current directory is: $start_dir"
#     exit 1
# }

$base_dir = $start_dir

python .\UI_SELENIUM\main.py --rerun-prediction=cspf
if ($LASTEXITCODE -ne 0) {
    Write-Output "Castpfold predictions: fatal error unhandled, terminating further execution"
    exit 1
}

#python -m UI_SELENIUM.methods_summary
python data_to_pm_input.py -c
Write-Output "only castpfold plus .ps1 script completed"


