# Simple Vertex AI Pipeline Example

This project demonstrates how to build, package, and run a simple, two-step machine learning pipeline on Google Cloud's Vertex AI Pipelines. The pipeline is constructed using separate component definitions (YAML), with the core logic in Python scripts, and is orchestrated by the Vertex AI SDK.

The pipeline consists of two components:
1.  **`prepare-data`**: Simulates a data preparation process.
2.  **`train-model`**: Simulates a model training process using the prepared data.

This example is designed to showcase best practices, including:
* Decoupling component interfaces (YAML) from implementation logic (Python).
* Dynamically loading component logic from Google Cloud Storage (GCS).
* Using a shell script to configure and trigger the pipeline run.
* Handling Python dependencies within an ephemeral container environment.

## Project Structure

```bash
vertex_pipeline/
├── components/
│   ├── prepare_data.yaml
│   └── train_model.yaml
├── scripts/
│   ├── prepare_data.py
│   └── train_model.py
├── pipeline_definition.py
├── run_pipeline.sh
├── README.md
└── requirements.txt
```

## Prerequisites

Before you begin, ensure you have the following:

1.  **A Google Cloud Project** with the Vertex AI and Cloud Build APIs enabled.
2.  **Google Cloud SDK (`gcloud`)** installed and authenticated. Run `gcloud auth login` and `gcloud config set project YOUR_PROJECT_ID`.
3.  **A Google Cloud Storage (GCS) Bucket** to store pipeline artifacts and scripts.
4.  **Python 3.8+** installed on your local machine.
5.  **Virtual Env** create a python virtual environment (Optional).
5.  **Required Python Libraries**. Install them by running:
    ```bash
    pip install -r requirements.txt
    ```

## Setup Instructions

### 1. Configure the Pipeline Runner

Open the `run_pipeline.sh` script and update the configuration variables at the top of the file with your specific GCP project details.

```bash
# --- Configuration ---
PROJECT_ID="your-gcp-project-id"
REGION="your-gcp-region"         # e.g., us-east1
GCS_BUCKET_NAME="your-gcs-bucket-name" # Do not include the gs:// prefix
```

### 2. Make the Script Executable
In your terminal, grant execute permissions to the shell script:

```bash
chmod +x run_pipeline.sh
```
### 3. How to Run the Pipeline
Execute the main script from your terminal:

```bash
./run_pipeline.sh
```

This script will:

Create unique GCS paths for this pipeline run.

Upload your component Python scripts (prepare_data.py, train_model.py) to GCS.

Execute pipeline_definition.py, which compiles the pipeline and submits it to Vertex AI.

You can monitor the pipeline's progress in the Google Cloud Console under Vertex AI > Pipelines.