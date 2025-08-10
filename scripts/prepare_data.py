import os
import pandas as pd
import numpy as np
import argparse

def prepare_data_main(raw_data_path: str, processed_data_path: str, preprocessing_report_path: str):
    """
    Simulates data preparation and saves processed data and a report.

    Args:
        raw_data_path: GCS path to the raw input data (for logging/reference).
        processed_data_path: The output path for the processed data (directory).
        preprocessing_report_path: The output path for the preprocessing report (file).
    """
    print(f"Simulating data preparation for {raw_data_path}...")

    # Ensure the output directory for processed_data exists.
    # KFP automatically sets .path for Dataset/Model to a directory.
    os.makedirs(processed_data_path, exist_ok=True)

    # Ensure the parent directory for preprocessing_report exists.
    # For Artifact, .path usually refers to the file itself, so its parent directory needs to exist.
    os.makedirs(os.path.dirname(preprocessing_report_path), exist_ok=True)

    dummy_data = pd.DataFrame({
        "feature_a": np.random.rand(100),
        "feature_b": np.random.randint(0, 10, 100),
        "target": np.random.randint(0, 2, 100)
    })

    processed_data_file = os.path.join(processed_data_path, "processed_data.csv")
    dummy_data.to_csv(processed_data_file, index=False)
    print(f"Processed data saved to: {processed_data_file}")

    with open(preprocessing_report_path, "w") as f:
        f.write("Preprocessing Summary:\n")
        f.write(f"  Number of rows: {len(dummy_data)}\n")
        f.write(f"  Number of columns: {len(dummy_data.columns)}\n")
        f.write("  Missing values handled: Yes (simulated)\n")

    print(f"Preprocessing report saved to: {preprocessing_report_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Prepare data component.")
    parser.add_argument("--raw-data-path", type=str, required=True,
                        help="GCS path to the raw input data.")
    parser.add_argument("--processed-data-path", type=str, required=True,
                        help="Output path for the processed data.")
    parser.add_argument("--preprocessing-report-path", type=str, required=True,
                        help="Output path for the preprocessing report.")
    
    args = parser.parse_args()
    
    prepare_data_main(
        raw_data_path=args.raw_data_path,
        processed_data_path=args.processed_data_path,
        preprocessing_report_path=args.preprocessing_report_path
    )
