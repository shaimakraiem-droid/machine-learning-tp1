# churnlab

Churn prediction project on the IBM Telco Customer Churn dataset.

## Business question

A telecommunications company wants to identify customers who are likely to leave its service, so it can act before they do. The target column is **`Churn`** (`Yes` / `No`): each row is a customer, and the task is to predict `Churn` from the other customer attributes. `customerID` identifies a customer and is not a model feature.

## Environment setup

The project uses **Python 3.11** (3.12 is also accepted, see `requires-python` in `pyproject.toml`) and [uv](https://docs.astral.sh/uv/).

```sh
uv sync --locked
uv run python -c "import churnlab; print(churnlab.__version__)"   # expected: 0.1.0
```

`--locked` installs exactly the versions recorded in `uv.lock` and fails if the lock no longer matches `pyproject.toml`. If it fails, investigate the mismatch instead of re-locking silently.

To record the installed environment in `evidence/tp01/environment.json`:

```sh
uv run python scripts/record_environment.py
```

## Dataset source and verification

| Item | Value |
|---|---|
| Dataset | IBM Telco Customer Churn, 7,043 rows x 21 columns |
| Source repository | <https://github.com/IBM/telco-customer-churn-on-icp4d> |
| Pinned commit | `1fd6fd70906479be1712e64cfc0ea89f58466629` |
| File URL | [Telco-Customer-Churn.csv at that commit](https://raw.githubusercontent.com/IBM/telco-customer-churn-on-icp4d/1fd6fd70906479be1712e64cfc0ea89f58466629/data/Telco-Customer-Churn.csv) |
| Local path | `data/raw/telco.csv` (not committed) |
| SHA-256 | `16320c9c1ec72448db59aa0a26a0b95401046bef5d02fd3aeb906448e3055e91` |

Get the snapshot (downloaded only if absent) and record its source and hash in `data/raw/telco.source.json`:

```sh
uv run python scripts/download_data.py
```

Check the hash and produce a data overview in `reports/tp01_data_overview.json`:

```sh
uv run python scripts/inspect_telco.py
```

Both scripts stop with an error if the file's SHA-256 differs from the expected value. Expected overview: 7,043 rows, 21 columns, 5,174 `No` / 1,869 `Yes` (about 26.5% churn), 0 duplicate `customerID`, 11 whitespace-only `TotalCharges` values. The raw CSV must stay unchanged; cleaning happens in later steps.

## Project layout

| Path | Purpose |
|---|---|
| `pyproject.toml` | Project metadata, Python constraint and declared dependencies |
| `uv.lock` | Exact resolved package versions, used by `uv sync --locked` |
| `src/churnlab/` | Importable project code; `data.py` defines the pinned source and hashing |
| `scripts/` | Executable workflow steps (download, environment record, inspection) |
| `tests/` | Small behaviour checks: `uv run pytest` |
| `data/raw/` | Original input snapshot (ignored by Git) and its committed source metadata |
| `data/processed/` | Generated splits (later TPs) |
| `artifacts/` | Generated model files (later TPs) |
| `reports/` | Generated reports (ignored by Git) |
| `evidence/` | Small, non-sensitive evidence submitted with each TP |

## What this dataset is, and is not

This is a **single customer snapshot**: one row per customer with their current attributes and a churn label. It is **not** an event-time log (no dated history of when services, charges or churn happened), so we cannot tell what was known *before* a customer left. It is also **not** an intervention dataset: no retention action was randomly assigned, so it supports predicting churn, not measuring the causal effect of an offer on churn. Do not invent dates or treatments and present them as observed IBM data.
