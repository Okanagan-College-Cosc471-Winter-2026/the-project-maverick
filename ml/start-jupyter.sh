#!/bin/bash
# Start Jupyter Lab for ML development

# Activate conda environment if it exists
if conda info --envs | grep -q "cosc471"; then
    echo "Activating cosc471 environment..."
    source $(conda info --base)/etc/profile.d/conda.sh
    conda activate cosc471
fi
