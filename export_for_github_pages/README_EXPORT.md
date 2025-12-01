# Export to GitHub Pages — Instructions

This folder contains a helper script to export the current local project into the GitHub Pages repository at `https://github.com/1samyak/hospital.github.io`.

Files:
- `push_to_remote.ps1` — PowerShell script that clones the remote repo to a temporary folder, copies your current workspace files into it (excluding `.git`), commits and pushes a branch (or force-updates remote branch when requested).

Quick overview and recommended workflow:

1. Choose how you want to publish:
   - Create a new branch and push (safe): use default `Mode=branch`. This will push a new branch like `export-from-local-YYYYMMDD-HHMMSS` to the remote — then open a Pull Request on GitHub to review/merge.
   - Overwrite remote branch (dangerous): use `Mode=force`. This will prompt for confirmation and then force-push to the remote default branch (`main` or `master`) and will replace the remote contents. Only use this if you really intend to replace what's on the Pages site.

2. How to run (PowerShell):

   Open `pwsh` in your project root (the root of this Flask project), then run:

```powershell
cd C:\Users\samya\OneDrive\Desktop\Hospital-Management-System
.\export_for_github_pages\push_to_remote.ps1 -RemoteRepo 'https://github.com/1samyak/hospital.github.io.git'
```

Optional parameters:
- `-BranchName 'my-export-branch'` — specify custom branch name.
- `-Mode 'force'` — overwrite remote default branch (requires explicit confirmation).

Authentication notes:
- If you cloned/pushed via HTTPS, you will be prompted for username/password. For GitHub, use a Personal Access Token (PAT) as password when prompted.
- Alternatively, configure SSH keys and use the SSH remote URL (e.g. `git@github.com:1samyak/hospital.github.io.git`).

What the script does:
- Clones the remote repo to a temp folder
- Checks out a new branch (or default branch for force mode)
- Removes existing files in the clone (except `.git`)
- Copies all files from your current working directory into the clone
- Commits and pushes the changes

Important:
- The script assumes you run it from your project root. If you run it from a different folder, double-check the `Copy` source path printed by the script.
- The script does not create a Pull Request. If you pushed a branch, go to the GitHub UI to open a PR and review before merging.
- Review the contents before force pushing. There is no undo for force-pushing other people's repositories.

Next steps I can take for you:
- Run the script locally for you (I cannot push from here). I can provide the exact command for your environment.
- Instead, clone the remote here and prepare the branch locally (I can prepare the branch files in a folder). Tell me which you prefer.
