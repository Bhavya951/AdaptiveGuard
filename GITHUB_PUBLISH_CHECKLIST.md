# GitHub publishing checklist

- [x] Preserve the original research workspace and record the frozen Phase 1 aggregate evidence. The archived report digest matches the recorded SHA-256.
- [x] Match both public development datasets byte-for-byte against the saved development fixtures.
- [x] Exercise all 64 tests directly and in a clean offline virtual environment. Run the three demo scenarios and the documented development commands.
- [x] Include both paper references, the implementation walkthrough, the demo runbook, the interview guide and the AI assistance record.
- [x] Exclude actual credentials, all private result directories, protected fixture definitions, holdout packets and private review materials. The released generators contain distinct structural test fixtures in their held-out branches.
- [ ] Owner reviews external sharing of the historical aggregate results and confirms attribution. Hosted CI can be checked after publication.
- [ ] Select a license if you want to grant reuse rights. The package contains no license file.
- [ ] Create an empty GitHub repository when ready. Run the commands below from the extracted repository folder and substitute your repository URL.

```sh
git init -b main
git add --all
git diff --cached --stat
git diff --cached --name-only
git commit -m "Prepare AdaptiveGuard research portfolio"
git remote add origin https://github.com/YOUR-ACCOUNT/YOUR-REPOSITORY.git
git push -u origin main
```

The proposed Phase 2 scientific closeout requires independent label review, adjudication, protocol freeze and a separately authorized holdout run.
