#!/bin/bash

# --- Configuration Variables ---
# IMPORTANT: Update these variables with your Google Cloud project details.

# Your Google Cloud Project ID (e.g., "my-ml-project-123456")
# This is usually the alphanumeric ID, not just the display name.
PROJECT_ID="mlops"

# The region where you want to run your Vertex AI Pipeline (e.g., "us-central1", "us-east1")
REGION="us-east1"

# The GCS bucket to use as the pipeline root for storing artifacts.
# This bucket must exist and the service account running the pipeline must have
# 'Storage Object Admin' (or 'Storage Object Creator' + 'Storage Object Viewer') permissions.
# Example: "gs://mlops-pipelines"
GCS_BUCKET_NAME="mlops-pipelines"  # Do not include the gs:// prefix

GCS_BUCKET_PATH="gs://${GCS_BUCKET_NAME}/pipeline-root"

# The GCS path to your raw input data, if your pipeline expects one.
# Example: "gs://your-bucket-name/raw_data/data.csv"
RAW_DATA_GCS_PATH="gs://${GCS_BUCKET_NAME}/raw_data/data.csv"

# The service account email to use for running the pipeline job.
# If left empty, Vertex AI will typically use the Compute Engine default service account.
# Example: "your-custom-sa@your-project-id.iam.gserviceaccount.com"
# Ensure this service account has necessary permissions (Vertex AI User, Storage Object Admin).
SERVICE_ACCOUNT="" # Leave empty to use default, or provide your custom SA email

PREPARE_DATA_LOGIC_SCRIPT="prepare_data.py"
TRAIN_MODEL_LOGIC_SCRIPT="train_model.py"

# --- Internal Script Variables ---
PIPELINE_NAME="ml-training-pipeline"
PIPELINE_DISPLAY_NAME="${PIPELINE_NAME}-$(date +%Y%m%d%H%M%S)"
COMPILED_PIPELINE_LOCAL_PATH="ml_training_pipeline.json"

# --- Main Script Execution ---

echo "--- Starting Vertex AI Pipeline Automation ---"
echo "Project ID: ${PROJECT_ID}"
echo "Region: ${REGION}"
echo "Pipeline Root GCS Bucket: ${GCS_BUCKET_PATH}"
echo "Raw Data GCS Path: ${RAW_DATA_GCS_PATH}"
echo "Service Account: ${SERVICE_ACCOUNT:-Default Compute Engine SA}"

echo "Uploading component logic scripts to GCS..."
gsutil cp "./scripts/${PREPARE_DATA_LOGIC_SCRIPT}" "${GCS_BUCKET_PATH}/component_scripts/${PREPARE_DATA_LOGIC_SCRIPT}"
gsutil cp "./scripts/${TRAIN_MODEL_LOGIC_SCRIPT}" "${GCS_BUCKET_PATH}/component_scripts/${TRAIN_MODEL_LOGIC_SCRIPT}"
echo "Component logic scripts uploaded."

# Store the GCS paths for the logic scripts
PREPARE_DATA_LOGIC_GCS_PATH="${GCS_BUCKET_PATH}/component_scripts/${PREPARE_DATA_LOGIC_SCRIPT}"
TRAIN_MODEL_LOGIC_GCS_PATH="${GCS_BUCKET_PATH}/component_scripts/${TRAIN_MODEL_LOGIC_SCRIPT}"

# 1. Compile the pipeline Python script into a JSON file
echo ""
echo "--- Compiling the pipeline ---"
echo "Running: python pipeline_definition.py"

python pipeline_definition.py \
    "${PROJECT_ID}" \
    "${REGION}" \
    "${GCS_BUCKET_PATH}" \
    "${RAW_DATA_GCS_PATH}" \
    "${PREPARE_DATA_LOGIC_GCS_PATH}" \
    "${TRAIN_MODEL_LOGIC_GCS_PATH}" \
    "${SERVICE_ACCOUNT}"

SCRIPT_STATUS=$?

if [ $SCRIPT_STATUS -ne 0 ]; then
    echo "Error: Pipeline compilation or submission failed. Check the Python script output above."
    exit 1
fi
echo "Pipeline compilation and submission initiated by pipeline_definition.py."
echo "Check Vertex AI Pipelines in your Cloud Console for status."

