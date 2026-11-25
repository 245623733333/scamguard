# Push to GitHub
1. github.com -> New repository -> name `scamguard`, **Public**, do NOT add README/.gitignore. Create.
2. In the project folder:
```
git init
git add .
git commit -m "ScamGuard: on-device SMS scam detection (PS3)"
git branch -M main
git remote add origin https://github.com/<your-username>/scamguard.git
git push -u origin main
```
(Password prompt: use a Personal Access Token from GitHub Settings > Developer settings, or `gh auth login`.)
3. Open the repo link in a private browser window to confirm it is public. Paste that link in the form.
