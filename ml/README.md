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

## Workflow

1. **Explore data** → `notebooks/01_eda.ipynb`
2. **Feature engineering** → `notebooks/02_features.ipynb`
3. **Train model** → `python training/train.py`
4. **Evaluate** → `python evaluation/evaluate.py`
5. **Save model** → `models/xgboost_v1.joblib`
