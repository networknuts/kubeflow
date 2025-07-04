from kfp.v2.dsl import component, pipeline
import argparse

# 1. Single image for every step
COMMON_IMAGE = "python:3.9-slim"

# 2. One component that takes `username` and prints hello <username>
@component(base_image=COMMON_IMAGE)
def greet_op(username: str):
    """Greet the user by name."""
    print(f"hello {username}")

# 3. Pipeline now has a `username` parameter
@pipeline(
    name="hello-username-pipeline",
    description="A pipeline that says hello to the given username"
)
def hello_username_pipeline(username: str):
    # pass the pipeline parameter down into the component
    _ = greet_op(username=username)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Compile (and optionally submit) the hello-username pipeline"
    )
    parser.add_argument(
        "--username",
        type=str,
        required=True,
        help="The name to say hello to"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="hello_username_pipeline.yaml",
        help="Path to write the compiled pipeline spec"
    )
    parser.add_argument(
        "--submit",
        action="store_true",
        help="If set, immediately submit a run to Kubeflow (requires KFP endpoint configured)"
    )
    args = parser.parse_args()

    # 4. Compile → this YAML will have a required `username` field, so UI will prompt you.
    from kfp.v2 import compiler
    compiler.Compiler().compile(
        pipeline_func=hello_username_pipeline,
        package_path=args.output
    )
    print(f"✅  Compiled pipeline to {args.output}.  It will require `username` when you run it.")
