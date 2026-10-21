# TP01 - Answers and evidence

**Author:** Shaima Kraiem
**Partner (reviewer):** sarahchammari04

## Notes on how this TP was run

- The instructor's `churnlab-2026` starter package was not available in this folder. The project was therefore rebuilt with the layout from the handout: `pyproject.toml`, `uv.lock`, `src/churnlab/`, `scripts/`, `tests/`, `data/raw/`, `data/processed/`, `artifacts/`, `reports/`. `k8s/` and `pipelines/` belong to later TPs and are not created yet.
- The lock file was generated locally with **uv 0.11.16**, not the uv 0.12.23 mentioned in the handout.
- `data/raw/telco.csv` was not downloaded. It was rebuilt from a local copy of the dataset and checked against the expected SHA-256 (`16320c9c...5e91`), which it matches exactly. `scripts/download_data.py` found the file present, so it only verified the hash and wrote `data/raw/telco.source.json`.

## Part A

**A1. Why do the original CSV, a fitted model and the training code have different roles?**

They are different kinds of objects and need different handling:

- The **original CSV** is an *input*. It records what the project received, so it must never be edited. It is identified by its source and its hash rather than by its name. It can be large or sensitive, so this project keeps it out of Git and commits only its source metadata (`data/raw/telco.source.json`).
- The **training source code** is the *recipe*. People write it, review it and change it, and Git versions it line by line.
- The **fitted model** is an *output*. Running the code on the data, in a given environment with a given configuration, produces it. It is a generated binary that should be rebuilt or stored with its lineage, not edited by hand or committed to Git.

Keeping these roles separate lets us answer "which code, which data and which environment produced this model?" Mixing them, for example by cleaning the raw CSV in place or committing models next to code, makes that question impossible to answer.

**A2. Why would including `Churn` among the model inputs invalidate the prediction task?**

`Churn` is the target, the very thing we want to predict. As an input it is **target leakage**: the model would simply copy the label and look almost perfect offline. In production the label is unknown at prediction time (we predict churn *before* the customer leaves), so that model would be useless.

## Part B

**B1.** `uv sync --locked` succeeded and `uv run python -c "import churnlab; print(churnlab.__version__)"` printed `0.1.0`.

**B2. Tasks**

1. Python constraint in `pyproject.toml`: `requires-python = ">=3.11,<3.13"`. One direct dependency: `numpy~=1.26.0`.
2. The same dependency in `uv.lock`: the `[[package]]` entry `name = "numpy"`, `version = "1.26.4"`, `source = { registry = "https://pypi.org/simple" }`. It lists the sdist and wheel URLs, each with its `sha256` hash. The `churnlab` entry also records the original requirement: `{ name = "numpy", specifier = "~=1.26.0" }`.
3. One transitive dependency from `uv tree`: `scipy v1.17.1`, required by `scikit-learn`. Another example is `six v1.17.0`, required by `python-dateutil`, itself required by `pandas`. We never asked for either directly.
4. Difference between the three:
   - `pyproject.toml` states **what we want**: the project metadata, the Python constraint and the direct dependencies as *ranges*. People edit it, and it is committed.
   - `uv.lock` states **what was resolved**: the exact version, source and file hashes of *every* package, transitive ones included, for all supported platforms. uv generates it, and it is committed so everyone installs the same selection.
   - `.venv/` is **what is installed on this machine**: a local, disposable directory built from the lock. It is never committed, and `uv sync --locked` can recreate it at any time, as Part D shows.

`uv tree` output:

```text
churnlab v0.1.0
├── numpy v1.26.4
├── pandas v2.2.3
│   ├── numpy v1.26.4
│   ├── python-dateutil v2.9.0.post0
│   │   └── six v1.17.0
│   ├── pytz v2026.5
│   └── tzdata v2026.5
├── scikit-learn v1.5.2
│   ├── joblib v1.6.0
│   │   └── cloudpickle v3.1.2
│   ├── numpy v1.26.4
│   ├── scipy v1.17.1
│   │   └── numpy v1.26.4
│   └── threadpoolctl v3.7.0
└── pytest v8.4.2 (group: dev)
    ├── iniconfig v2.3.1
    ├── packaging v26.3
    ├── pluggy v1.7.0
    └── pygments v2.21.0
```

**B3.** `numpy ~= 1.26.0` means `>=1.26.0, <1.27.0`, so any 1.26.x release is allowed. `numpy==1.26.4` allows exactly one version. This project declares the range in `pyproject.toml`, and the lock records the version actually selected (1.26.4). The `~=` operator only *assumes* that patch releases are compatible. A version number alone does not guarantee it, which is why we also need the lock.

## Part C

**C2. Results of `scripts/inspect_telco.py`** (full report: `evidence/tp01/data-overview.json`)

| Observation | Expected | Observed |
|---|---:|---:|
| SHA-256 | `16320c9c...5e91` | `16320c9c1ec72448db59aa0a26a0b95401046bef5d02fd3aeb906448e3055e91` |
| Rows | 7,043 | 7,043 |
| Columns | 21 | 21 |
| `Churn = No` | 5,174 | 5,174 |
| `Churn = Yes` | 1,869 | 1,869 |
| Churn proportion | ~26.54% | 26.537% |
| Duplicate customer IDs | 0 | 0 |
| Whitespace-only `TotalCharges` | 11 | 11 |

**C3. Interpretation**

1. **Why classification?** The target `Churn` is a *category* with two values, `Yes` and `No`. We predict which class a customer belongs to, or the probability of `Yes`, not a continuous quantity. It is a binary classification task.
2. **Class balance and accuracy.** Only about 26.5% of customers churn. A model that always answers `No` already reaches **73.5% accuracy** while finding zero churners, the customers the business cares about. Accuracy alone would therefore look good for a useless model. Later we should report precision, recall and F1 on the `Yes` class, a confusion matrix, and ROC-AUC or PR-AUC, and take the cost of missing a churner into account.
3. **Why is `TotalCharges` read as object/string?** Eleven rows contain a single space (`" "`) instead of a number. pandas cannot convert `" "` to a float, so it keeps the whole column as `object` (strings) rather than `float64`. All 11 rows have `tenure = 0`: they are new customers who have not been billed yet.
4. **Why can `isna()` miss them?** `isna()` only detects real missing markers (`NaN`, `None`). `" "` is a non-empty string, so pandas does not treat it as missing, and here `df["TotalCharges"].isna().sum()` returns **0**. To find these values you have to strip whitespace and compare with `""`, as the script does, or convert with `pd.to_numeric(..., errors="coerce")`.
5. **Evidence that a teammate used the same file.** The **SHA-256 of the bytes** (`16320c9c...5e91`), recorded with the commit-pinned source URL in `data/raw/telco.source.json` and checked by the script. The shape and counts (7,043 x 21, 5,174 / 1,869) support it, but the hash is the decisive proof: two files with the same name can differ, whereas identical hashes mean identical bytes.

## Part D

**D1. Recreation procedure**

1. `pyproject.toml`, `uv.lock` and `data/raw/telco.csv` were left unchanged (verified by hash before and after).
2. `evidence/tp01/environment.json` was saved as `evidence/tp01/environment-before.json`.
3. `.venv/` was renamed to `.venv-backup/` with `mv`, the terminal equivalent of renaming in the file manager.
4. `uv sync --locked`, `uv run python scripts/record_environment.py` and `uv run python scripts/inspect_telco.py` were run again.
5. Comparison:

| Check | Before | After | Same? |
|---|---|---|---|
| Python | 3.11.1 | 3.11.1 | yes |
| churnlab / pandas / numpy / scikit-learn | 0.1.0 / 2.2.3 / 1.26.4 / 1.5.2 | 0.1.0 / 2.2.3 / 1.26.4 / 1.5.2 | yes |
| `uv.lock` SHA-256 | unchanged | unchanged | yes |
| Dataset SHA-256 | `16320c9c...5e91` | `16320c9c...5e91` | yes |
| Data overview report | n/a | `diff` shows no difference | yes |

6. After verification, `.venv-backup/` was deleted.

**D2. What has been reproduced**

| Item | Evidence produced in TP01 | Remaining limitation |
|---|---|---|
| Code | Git commits `666b891` (initial project), `836a8c4` (README branch) and merge commit `bf366a4` on `main` | Uncommitted edits are not identified by a commit |
| Package selections | `pyproject.toml`, `uv.lock` | The interpreter (here python.org CPython 3.11.1) and the platform still influence which wheels get installed |
| Installed environment | `environment-before.json` and `environment.json`, which are identical | They do not capture every OS, compiler, BLAS or hardware detail |
| Source data | Commit-pinned source URL and SHA-256 in `data/raw/telco.source.json` | A hash proves which bytes were used, not that the labels are correct or free of leakage |
| Trained model | Not produced in TP01 | Needs later evidence: training code version, configuration, random seeds, data splits and model artifact |

## Part E

- Commits: `666b891 Initialize Telco churn project` and `81cfe51 Add TP01 evidence` on `main`, and `836a8c4 Document reproducible Telco onboarding` on `docs/telco-onboarding`.
- GitHub repository: <https://github.com/shaimakraiem-droid/machine-learning-tp1>
- Pull request URL: <https://github.com/shaimakraiem-droid/machine-learning-tp1/pull/1>
- Partner review on the PR: sarahchammari04 commented « bbb » ([comment](https://github.com/shaimakraiem-droid/machine-learning-tp1/pull/1#issuecomment-6321289737)), and I replied « ml » ([reply](https://github.com/shaimakraiem-droid/machine-learning-tp1/pull/1#issuecomment-6321295195)). These comments do not contain a substantive review question. Before merging, I checked the change myself from a fresh environment: I removed `.venv/`, ran `uv sync --locked` and `scripts/inspect_telco.py` again, and got the same dataset hash and the same counts as stated in the README.
- Merge commit on `main`: `bf366a4` (Merge pull request #1 from shaimakraiem-droid/docs/telco-onboarding)

`git log --oneline --graph --decorate -8` after `git switch main` and `git pull`:

```text
*   bf366a4 (HEAD -> main, origin/main, origin/HEAD) Merge pull request #1 from shaimakraiem-droid/docs/telco-onboarding
|\
| * 836a8c4 (origin/docs/telco-onboarding, docs/telco-onboarding) Document reproducible Telco onboarding
* | 81cfe51 Add TP01 evidence
|/
* 666b891 (exercise/local-recovery) Initialize Telco churn project
```

PR description (to paste when opening the PR):

> **Document reproducible Telco onboarding**
>
> This PR rewrites `README.md` so that a teammate can set up and check the project without guessing. It covers:
> - the business question and the target column (`Churn`);
> - the Python version (3.11) and the setup command `uv sync --locked`;
> - the dataset source pinned to an IBM commit, its SHA-256, and the download and inspection commands;
> - the purpose of each project directory;
> - why this customer snapshot is neither an event-time log nor an intervention dataset.
>
> **Verification performed**
> - `uv sync --locked`: succeeds and leaves `uv.lock` unchanged; `import churnlab` prints `0.1.0`.
> - `uv run python scripts/download_data.py`: the hash matches `16320c9c...5e91`.
> - `uv run python scripts/inspect_telco.py`: 7,043 rows, 21 columns, 5,174 No / 1,869 Yes, 0 duplicate IDs, 11 whitespace-only `TotalCharges`, as stated in the README.
> - `uv run pytest`: 3 passed.
> - The environment was recreated from scratch after removing `.venv/`; the environment and data records are identical before and after.

## Part F

Commands run on the disposable branch `exercise/local-recovery`:

```text
## F1 (discard an unstaged edit)
$ git diff -- README.md
+Temporary sentence F1.
$ git restore README.md
$ git diff -- README.md
(no output: the edit is gone)

## F2 (unstage without deleting)
$ git add README.md
$ git diff --cached -- README.md
+Temporary sentence F2.
$ git restore --staged README.md
$ git status --short
 M README.md
$ git diff -- README.md
+Temporary sentence F2.
(the edit is still in the file, just no longer staged)
$ git restore README.md
$ git switch main
```

**Difference between F1 and F2.**

- `git restore README.md` copies the staged (index) version back over the **working file**. The unstaged edit is **destroyed**, and since it was never staged or committed, Git cannot bring it back.
- `git restore --staged README.md` only resets the **index** entry to the `HEAD` version. The file on disk keeps the edit: `git status` shows ` M` and `git diff` still shows it. It just won't be part of the next commit. This command *unstages*; the first one *discards*.

## What TP01 does not reproduce yet

- The trained model: no training code, configuration, random seeds or artifacts exist yet.
- Data cleaning and train/test splits, including how the 11 blank `TotalCharges` values will be handled (TP02).
- The exact Python interpreter and system libraries, which the lock file does not pin.
- Label quality, and the absence of leakage in the features.
- An independent check by another person: the PR comments contain no substantive review question, so nobody else has yet run the setup and the inspection on another machine (Part E4).
