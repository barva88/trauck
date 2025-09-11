Push instructions for trauck repo

This file contains exact safe commands to push the current local snapshot (branch `x`) and update remote branches.

1) Authenticate with GitHub CLI (recommended):

   brew install gh
   gh auth login
   gh auth status

2) Push backup branch `x`:

   git checkout x
   git push origin x

3) Create remote backup of origin/dev (optional but recommended):

   git fetch origin
   git checkout -b backup/origin-dev-before-merge origin/dev
   git push origin backup/origin-dev-before-merge:backup/origin-dev-before-merge

4) Update remote branches from local prepared branches (choose one):

Option A (create PRs for review - recommended):

   git push origin x:merge-from-x
   gh pr create --base dev --head merge-from-x --title "Merge x -> dev" --body "Sync changes from local x"

Option B (push directly - use only if you have confirmed no remote work will be overwritten):

   git checkout merge/dev-with-x
   git push origin merge/dev-with-x:dev

   git checkout local-main
   git push origin local-main:main

   git checkout local-prod
   git push origin local-prod:prod

5) After pushing, rotate the Gmail App Password in Google Account settings and do not commit `.env`.

6) If `.env` was pushed accidentally, contact the maintainer to purge history using BFG or git filter-repo.
