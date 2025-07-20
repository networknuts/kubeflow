#!/usr/bin/env python3
import argparse
import json
import pandas as pd
from minio import Minio
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

def download_from_minio(endpoint, access_key, secret_key, bucket, object_name, dst_path):
    """
    Download an object from MinIO to a local file.
    """
    client = Minio(
        endpoint,
        access_key=access_key,
        secret_key=secret_key,
        secure=endpoint.endswith(":443")
    )
    client.fget_object(bucket, object_name, dst_path)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--minio-endpoint",   type=str,   required=True)
    parser.add_argument("--minio-access-key", type=str,   required=True)
    parser.add_argument("--minio-secret-key", type=str,   required=True)
    parser.add_argument("--minio-bucket",     type=str,   required=True)
    parser.add_argument("--minio-object",     type=str,   required=True,
                        help="Name of the CSV object in the bucket")
    parser.add_argument("--local-path",       type=str,   default="/tmp/diabetes.csv",
                        help="Local path to download the CSV before loading")
    parser.add_argument("--penalty",          type=str,   default="l2",
                        choices=["l1", "l2"], help="Regularization penalty")
    parser.add_argument("--C",                type=float, default=1.0,
                        help="Inverse of regularization strength")
    parser.add_argument("--max_iter",         type=int,   default=300,
                        help="Maximum number of solver iterations")
    parser.add_argument("--test_size",        type=float, default=0.2,
                        help="Proportion of data to use as test set")
    parser.add_argument("--random_state",     type=int,   default=0,
                        help="Random seed for train/test split")
    args = parser.parse_args()

    # 1. Download CSV from MinIO
    download_from_minio(
        endpoint    = args.minio_endpoint,
        access_key  = args.minio_access_key,
        secret_key  = args.minio_secret_key,
        bucket      = args.minio_bucket,
        object_name = args.minio_object,
        dst_path    = args.local_path,
    )

    # 2. Load data
    df = pd.read_csv(args.local_path)
    X = df.drop("Outcome", axis=1)
    y = df["Outcome"]

    # 3. Train/test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=args.test_size, random_state=args.random_state
    )

    # 4. Select solver based on penalty
    solver = "liblinear" if args.penalty == "l1" else "lbfgs"
    clf = LogisticRegression(
        penalty   = args.penalty,
        C         = args.C,
        max_iter  = args.max_iter,
        solver    = solver
    )

    # 5. Train
    clf.fit(X_train, y_train)

    # 6. Evaluate
    preds = clf.predict(X_test)
    acc = accuracy_score(y_test, preds)
    print(f"accuracy={acc:.4f}")

    # 7. Save JSON metrics (optional, for JSON collector)
    with open("/app/metrics.json", "w") as f:
        json.dump({"accuracy": acc}, f)

if __name__ == "__main__":
    main()

