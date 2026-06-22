# Prepare git repos for GitHub → Railway / Netlify
param(
  [string]$BackendRemote = "",
  [string]$FrontendRemote = ""
)

$ErrorActionPreference = "Stop"

function Init-Repo($Path, $Message, $Remote) {
  Push-Location $Path
  if (-not (Test-Path .git)) {
    git init
    git add .
    git commit -m $Message
    Write-Host "Created commit in $Path"
  } else {
    Write-Host "Git already initialized: $Path"
  }
  if ($Remote) {
    git remote remove origin 2>$null
    git remote add origin $Remote
    Write-Host "Remote: $Remote"
    Write-Host "Run: git push -u origin main"
  }
  Pop-Location
}

Init-Repo "e:\n8n_data\nextgic-agent (1)" "Add dashboard API, JWT auth, Railway deploy" $BackendRemote
Init-Repo "e:\n8n_data\Cursor\dashboard" "NEXTGIC AI Ops Center dashboard" $FrontendRemote

Write-Host ""
Write-Host "Next: push both repos, then follow DEPLOY.md Part A then Part B."
