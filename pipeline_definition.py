import kfp
from kfp import dsl
from kfp.dsl import Dataset, Artifact, Input, Output
from kfp.compiler import Compiler
import os
import sys
import google.cloud.aiplatform as aiplatform # Added for pipeline submission

# Define component paths (relative to pipeline_definition.py)
PREPARE_DATA_COMPONENT_PATH = 'components/prepare_data.yaml'
TRAIN_MODEL_COMPONENT_PATH = 'components/train_model.yaml'

# Load components from YAML files
prepare_data_op = kfp.components.load_component_from_file(PREPARE_DATA_COMPONENT_PATH)
train_model_op = kfp.components.load_component_from_file(TRAIN_MODEL_COMPONENT_PATH)


@dsl.pipeline(
    name='ml-training-pipeline',
    description='A minimal Vertex AI pipeline for data prep and model training using separate YAML components and GCS-hosted logic.'
)
def minimal_training_pipeline(
    pipeline_root: str,
    raw_data_gcs_path: str = None,
    prepare_data_logic_gcs_path: str = '',
    train_model_logic_gcs_path: str = ''
):
    """
    Defines a minimal ML training pipeline using custom components with logic from GCS.

    Args:
        pipeline_root (str): The GCS bucket URI for pipeline artifacts.
        raw_data_gcs_path (str): The GCS path to the raw input data.
        prepare_data_logic_gcs_path (str): GCS path to the prepare_data_logic.py script.
        train_model_logic_gcs_path (str): GCS path to the train_model_logic.py script.
    """
    # Step 1: Prepare Data
    prepare_data_task = prepare_data_op(
        raw_data_path=raw_data_gcs_path,
        logic_script_path=prepare_data_logic_gcs_path
    )

    # Step 2: Train Model
    train_model_task = train_model_op(
        processed_data=prepare_data_task.outputs['processed_data'],
        logic_script_path=train_model_logic_gcs_path
    )

    # Optional: Define pipeline outputs if you want to explicitly expose them
    # dsl.OutputPath(train_model_task.outputs['trained_model'])
    # dsl.OutputPath(train_model_task.outputs['training_metrics'])

if __name__ == '__main__':
    # When this script is run, it will compile the pipeline and then submit it to Vertex AI.
    # It requires command-line arguments for project, region, pipeline root, and GCS paths for logic scripts.
    if len(sys.argv) < 7:
        print("Usage: python pipeline_definition.py <project_id> <region> <pipeline_root_gcs_path> <raw_data_gcs_path> <prepare_data_logic_gcs_path> <train_model_logic_gcs_path> <service_account_email>")
        sys.exit(1)

    project_id = sys.argv[1]
    region = sys.argv[2]
    pipeline_root_gcs_path = sys.argv[3]
    raw_data_gcs_path = sys.argv[4]
    prepare_data_script_path_for_pipeline = sys.argv[5]
    train_model_script_path_for_pipeline = sys.argv[6]
    service_account_email = sys.argv[7] # New argument for service account
    print(prepare_data_script_path_for_pipeline)
    print(train_model_script_path_for_pipeline)

    output_file_name = 'ml_training_pipeline.json'
    pipeline_job_display_name = f"{minimal_training_pipeline.name}-{os.getenv('BUILD_ID', os.getenv('K_REVISION', 'local'))}-{os.urandom(4).hex()}" # Unique display name

    print(f"Compiling pipeline to {output_file_name}")

    try:
        # Compile the pipeline
        kfp.compiler.Compiler().compile(
            pipeline_func=minimal_training_pipeline,
            package_path=output_file_name,
        )
        print(f"Pipeline compiled successfully to {output_file_name}")

        # Initialize Vertex AI SDK
        aiplatform.init(project=project_id, location=region, staging_bucket=pipeline_root_gcs_path)

        # Create and run the pipeline job
        job = aiplatform.PipelineJob(
            display_name=pipeline_job_display_name,
            template_path=output_file_name,
            pipeline_root=pipeline_root_gcs_path,
            parameter_values={
                'raw_data_gcs_path': raw_data_gcs_path,
                'pipeline_root': pipeline_root_gcs_path,
                'prepare_data_logic_gcs_path': prepare_data_script_path_for_pipeline,
                'train_model_logic_gcs_path': train_model_script_path_for_pipeline
            },
            enable_caching=False, # Set to True to enable caching for faster iterative development
            #service_account=service_account_email # Specify the service account for the pipeline run
        )

        print(f"Submitting pipeline job: {pipeline_job_display_name}...")
        job.submit()
        #print(f"Pipeline job submitted. View at: {job.console_uri}")

    except TypeError as e:
        print(f"Error: Pipeline compilation or submission failed due to TypeError: {e}")
        print("Please ensure your KFP SDK version is compatible with the Compiler.compile() arguments or pipeline function signature.")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred during pipeline execution: {e}")
        sys.exit(1)

