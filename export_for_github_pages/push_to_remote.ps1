<#
.SYNOPSIS
  Clone a remote GitHub Pages repo, copy local project files into it, commit and push a branch.

.PARAMETER RemoteRepo
  The remote repository URL to clone (e.g. https://github.com/1samyak/hospital.github.io.git)

.PARAMETER BranchName
  The branch name to create and push. If not provided a timestamped branch is created.

.PARAMETER Mode
  "branch" (default) — create a new branch with copied files and push it.
  "force" — overwrite remote `main` (or specified default branch) by pushing a force update. Use with extreme caution.

.NOTES
  This script runs locally and requires Git to be installed and accessible in PATH.
  It does NOT open pull requests; it simply pushes a branch (or force-updates a branch if Mode=force).
  You will be prompted for credentials if needed. Consider using an SSH remote or a PAT for automation.
#>

param(
    [Parameter(Mandatory=$false)][string]$RemoteRepo = 'https://github.com/1samyak/hospital.github.io.git',
    [Parameter(Mandatory=$false)][string]$BranchName = $("export-from-local-$(Get-Date -Format 'yyyyMMdd-HHmmss')"),
    [ValidateSet('branch','force')][string]$Mode = 'branch'
)

function ThrowIfNoGit {
    $git = Get-Command git -ErrorAction SilentlyContinue
    if (-not $git) {
        throw "Git is not found in PATH. Please install Git and try again.";
    }
}

function Copy-WorkspaceTo($source, $dest) {
    # Delete everything except .git in destination
    Get-ChildItem -Path $dest -Force | Where-Object { $_.Name -ne '.git' } | ForEach-Object {
        if ($_.PSIsContainer) { Remove-Item $_.FullName -Recurse -Force -ErrorAction SilentlyContinue }
        else { Remove-Item $_.FullName -Force -ErrorAction SilentlyContinue }
    }

    # Copy items from source (current dir) into dest
    Get-ChildItem -Path $source -Force | Where-Object { $_.Name -ne '.git' } | ForEach-Object {
        $target = Join-Path $dest $_.Name
        if ($_.PSIsContainer) {
            Copy-Item $_.FullName -Destination $target -Recurse -Force
        } else {
            Copy-Item $_.FullName -Destination $target -Force
        }
    }
}

Write-Host "Preparing to export workspace to remote repo: $RemoteRepo" -ForegroundColor Cyan
ThrowIfNoGit

$temp = Join-Path $env:TEMP "hospital_pages_export_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
if (Test-Path $temp) { Remove-Item $temp -Recurse -Force }
New-Item -Path $temp -ItemType Directory | Out-Null

Write-Host "Cloning remote repository into temporary folder: $temp" -ForegroundColor Cyan
git clone $RemoteRepo $temp
if ($LASTEXITCODE -ne 0) { throw "git clone failed. Check the remote URL and your network/credentials." }

Push-Location $temp
try {
    # Determine remote default branch (attempt 'main' then 'master')
    $defaultBranch = 'main'
    $branches = git ls-remote --symref origin HEAD 2>$null | Select-String 'ref: refs/heads/' -AllMatches | ForEach-Object { ($_ -split 'ref: refs/heads/')[1].Trim() }
    if (-not $branches) { $branches = @('main','master') }
    if ($branches -contains 'main') { $defaultBranch = 'main' } elseif ($branches -contains 'master') { $defaultBranch = 'master' }

    if ($Mode -eq 'force') {
        Write-Warning "Mode=force: this will overwrite the remote '$defaultBranch' branch. Proceed only if you are sure."
        $confirm = Read-Host "Type 'YES' to continue and overwrite remote '$defaultBranch'"
        if ($confirm -ne 'YES') { throw 'Aborted by user.' }
    }

    if ($Mode -eq 'branch') {
        git checkout -b $BranchName
    } else {
        git checkout $defaultBranch
    }

    # Copy local workspace contents (current working directory where script was started) into clone, excluding .git
    $source = (Get-Location).Path
    # Use the directory where the script was launched (assumes user runs from project root)
    $caller = Get-Location -Stack 1 -ErrorAction SilentlyContinue
    if ($caller) { $source = $caller.Path }
    if ($source -eq $temp) { $source = $PWD.Path }

    Write-Host "Copying files from: $source" -ForegroundColor Yellow
    Copy-WorkspaceTo -source $source -dest $temp

    git add -A
    $commitMsg = "Export project from local workspace on $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
    git commit -m $commitMsg
    if ($LASTEXITCODE -ne 0) { Write-Host "No changes to commit or commit failed." }

    if ($Mode -eq 'branch') {
        git push origin $BranchName
        if ($LASTEXITCODE -ne 0) { throw 'git push failed. Check credentials and remote permissions.' }
        Write-Host "Pushed branch '$BranchName' to remote. Open a Pull Request to merge." -ForegroundColor Green
    } else {
        # force push to default branch
        git push origin $defaultBranch --force
        if ($LASTEXITCODE -ne 0) { throw 'git push --force failed. Check credentials and remote permissions.' }
        Write-Host "Force-pushed changes to '$defaultBranch'. Remote is overwritten." -ForegroundColor Red
    }
}
finally {
    Pop-Location
}

Write-Host "Temporary working folder: $temp" -ForegroundColor DarkCyan
Write-Host "If push succeeded, create a Pull Request at the remote to merge into the Pages site (or merge directly if you used force)." -ForegroundColor Cyan

Write-Host "Done." -ForegroundColor Green
