from kfp.v2.dsl import component, pipeline
import os

# 1. Use the same base image for every step
COMMON_IMAGE = "python:3.9-slim"

@component(
    base_image=COMMON_IMAGE,
    packages_to_install=["minio"]
)
def create_and_upload_op(
    username: str,
    output_path: str = "hello.txt"
):
    """
    1. Writes 'hello <username>' to /tmp/hello.txt
    2. Connects to MinIO (env vars MINIO_USER, MINIO_PASS)
    3. Uploads as pipeline-artifacts/<output_path>
    """
    from minio import Minio

    # 1. Write the file locally
    local_file = "/tmp/hello.txt"
    with open(local_file, "w") as f:
        f.write(f"hello {username}")

    # 2. Read MinIO creds & endpoint (assumed injected into pod env)
    endpoint = os.getenv("MINIO_ENDPOINT", "minio-service.kubeflow:9000")
    access_key = os.environ["MINIO_USER"]
    secret_key = os.environ["MINIO_PASS"]

    # 3. Upload via MinIO client
    client = Minio(
        endpoint,
        access_key=access_key,
        secret_key=secret_key,
        secure=False
    )

    bucket = "pipeline-artifacts"
    if not client.bucket_exists(bucket):
        client.make_bucket(bucket)

    client.fput_object(bucket, output_path, local_file)
    print(f"Uploaded {local_file} to {bucket}/{output_path}")

@pipeline(
    name="minio-artifact-pipeline",
    description="Creates a file and uploads it to MinIO via ENV creds"
)
def artifact_pipeline(username: str):
    # This task will read MINIO_USER & MINIO_PASS from its pod's env
    create_and_upload_op(username=username)

if __name__ == "__main__":
    import argparse
    from kfp.v2 import compiler

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--username", type=str, required=True,
        help="Name to say hello to"
    )
    parser.add_argument(
        "--output", type=str, default="minio_artifact_pipeline.yaml",
        help="Where to write the compiled pipeline spec"
    )
    args = parser.parse_args()

    compiler.Compiler().compile(
        pipeline_func=artifact_pipeline,
        package_path=args.output
    )
    print(f"Compiled pipeline spec written to {args.output}. It will prompt for `username` in the UI.")
