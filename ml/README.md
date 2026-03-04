# ML Development - Project Maverick

## Quick Start

### 1. Activate Environment
```bash
conda activate cosc471
```

### 2. Start Jupyter
Open the `ml/notebooks` directory in VS Code and select the `cosc471` kernel.

### 3. Run Training Script
```bash
# For long training, use tmux to avoid disconnects
tmux new -s training
conda activate cosc471
python training/train.py
```

## Directory Structure

```
ml/
├── notebooks/      # Jupyter notebooks (EDA, experiments)
├── data/           # Datasets (gitignored for large files)
├── features/       # Feature engineering code
├── models/         # Saved model artifacts (.joblib)
├── training/       # Training scripts
├── evaluation/     # Metrics and analysis
├── configs/        # Hyperparameter configs
├── environment.yml # Conda environment spec
└── requirements.txt
```

## Resource Optimization

This VPS has **30 CPU cores** and **50GB RAM**. Maximize usage:

```python
import xgboost as xgb

model = xgb.XGBRegressor(
    n_jobs=-1,           # Use all 30 cores
    tree_method='hist',  # Fast, memory-efficient
)
```

## Common Commands

```bash
# Activate environment
conda activate cosc471

# Deactivate
conda deactivate

# Update environment from yml
conda env update -f environment.yml

# Export current environment
conda env export > environment.yml

# List installed packages
conda list

# Run tests
pytest tests/ml/
```

## Serving Data to DRAC

The script `ml/scripts/serve_parquet.sh` exposes the processed CSV files over a public HTTPS URL so they can be downloaded from DRAC (or any remote machine).

### How it works

```
[processed_csv/]  →  [python HTTP server :8000]  →  [Serveo SSH tunnel]  →  public HTTPS URL
```

1. **Python HTTP server** — serves `ml/data/processed_csv/` on `localhost:8000`. No auth, plain file listing.
2. **Serveo tunnel** — opens an SSH reverse tunnel (`-R 80:localhost:8000 serveo.net`) that gives a public `https://*.serveousercontent.com` URL. No install required, uses system SSH.

### Run it (on this machine)

```bash
bash ml/scripts/serve_parquet.sh
```

Output will print the public URL, e.g.:
```
Public URL: https://cd4b1e8ff5eaf0e6-184-67-221-54.serveousercontent.com
```

The URL changes every time the tunnel restarts. Copy it into your DRAC notebook.

### Download on DRAC (notebook cell)

```python
import subprocess, pandas as pd, os

BASE_URL = "https://<url-from-script>"  # update this each run
TICKERS = ["AAPL","AMD","AMZN","BABA","BAC","BA","C","CSCO","CVX","DIS",
           "F","GE","GOOGL","IBM","INTC","JNJ","JPM","KO","MCD","META",
           "MSFT","NFLX","NVDA","PFE","T","TSLA","VZ","WMT","XOM"]

os.makedirs("parquet_data", exist_ok=True)
data = {}
for ticker in TICKERS:
    path = f"parquet_data/{ticker}.csv"
    subprocess.run(["wget", "-q", "-c", "--tries=5", "--timeout=60",
                    "-O", path, f"{BASE_URL}/{ticker}.csv"], check=True)
    data[ticker] = pd.read_csv(path, parse_dates=["date"])
    print(f"{ticker}: {len(data[ticker])} rows")
```

Uses `wget -c` (resume on failure) to handle large files and unstable SSL connections.

### Stop the server

```bash
kill <HTTP_PID> <TUNNEL_PID>   # PIDs printed by the script
```

### Available tickers (29)

`AAPL AMD AMZN BABA BAC BA C CSCO CVX DIS F GE GOOGL IBM INTC JNJ JPM KO MCD META MSFT NFLX NVDA PFE T TSLA VZ WMT XOM`

Data spans **2020–2025** (5-min bars), merged from FMP (2020–2023) and Google Drive (2023–2025).

---

## Workflow

1. **Explore data** → `notebooks/01_eda.ipynb`
2. **Feature engineering** → `notebooks/02_features.ipynb`
3. **Train model** → `python training/train.py`
4. **Evaluate** → `python evaluation/evaluate.py`
5. **Save model** → `models/xgboost_v1.joblib`

```
  Connection details for your ML code:
  - Host: localhost
  - Port: 5432
  - Database: market_data
  - User: mluser
  - Password: mlpassword
  
  ```