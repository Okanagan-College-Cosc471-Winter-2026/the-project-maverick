## General Information

This repository contains files from multiple research periods. **Each experiment folder can include the following machine learning models**:

- **XGBoost**
- **Random Forest** 
- **Multilayer Perceptron (MLP)**
- **Support Vector Regression (SVR)**

In addition to the models, the folders can contain experiment results, the associated datasets, or other relevant documents.

### Key Contents
- The latest XGBoost models are located in the "Fall 2025 Experiment" folder

---

## Accessing JupyterHub on the Fir Server

### Authentication Process
1. Navigate to [JupyterHub on the Fir Server](https://jupyterhub.fir.alliancecan.ca/) and enter your **DRAC credentials**
2. Complete the DUO authentication

### Server Configuration
When reaching the "Server Options" page:
- Select the following server configuration options:
    - Reservation: None
    - Partition: (grayed out)
    - Account: def-youry-ab_gpu
    - Time (hours): 3.0
    - Number of cores: 8
    - Memory (MB): 20000
    - GPU configuration: 1 x NVIDIA_H100_80GB_HBM3_2G.20GB
    - User interface: JupyterLab
- Feel free to customize the settings as needed for model execution

---

## Model Execution Steps

### Downloading and Uploading Models
After authentication, you should be directed to JupyterLab. 
1. Download an XGBoost model from the ["Fall Experiment 2025" folder](https://github.com/youry/AlgorithmicTrading/tree/main/Models/Fall%202025%20Experiment/XGBoost)
2. Upload the model notebook using the "Upload Files" icon in the left sidebar

### Preparation and Execution
1. Open the model notebook
2. Replace the following placeholders with your DRAC credentials:
   - 'username'
   - 'password'

3. Feel free to modify other credential strings if you need to

3. Installation and Setup
   - Run the first cell to install the necessary packages
   - **Restart the kernel** after package installation
        - Click the "Restart the Kernel" icon in the top menu

4. Model Execution
   - You should be able to run the model. Run the cells sequentially

---

## Notes
- Make sure that you have the necessary permissions to access the market tables. Contact team members to gain access.
- Contact support if you encounter any authentication or access issues with your DRAC account.
