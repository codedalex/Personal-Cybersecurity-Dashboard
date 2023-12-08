# Store the current execution policy
$currentPolicy = Get-ExecutionPolicy -Scope Process

# Set the execution policy to Bypass for the current session
Set-ExecutionPolicy -Scope Process Bypass

# Activate the virtual environment
.\venv\Scripts\Activate

# Restore the original execution policy
Set-ExecutionPolicy -Scope Process $currentPolicy
