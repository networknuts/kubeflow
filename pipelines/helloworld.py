from kfp.v2.dsl import component, pipeline

# 1. Define each step as a @component, specifying its container image
@component(
    base_image="python:3.9-slim",  # e.g. use your own build: myregistry/preprocess:latest
    packages_to_install=[]         # optional: list pip packages if you need them
)
def preprocess_op():
    """Preprocessing step: just prints hello world."""
    print("hello world")

@component(
    base_image="python:3.9-slim",  # e.g. myregistry/train:latest
)
def train_op():
    """Training step: just prints hello world."""
    print("hello world")

@component(
    base_image="python:3.9-slim",  # e.g. myregistry/eval:latest
)
def eval_op():
    """Evaluation step: just prints hello world."""
    print("hello world")

# 2. Assemble the pipeline
@pipeline(
    name="hello-world-3-step-pipeline-with-images",
    description="A simple 3-step pipeline where each step runs in its own container image"
)
def hello_world_pipeline():
    preprocess = preprocess_op()
    train      = train_op().after(preprocess)
    eval_      = eval_op().after(train)

# 3. Compile to a pipeline package
if __name__ == "__main__":
    from kfp.v2 import compiler
    compiler.Compiler().compile(
        pipeline_func=hello_world_pipeline,
        package_path="hello_world_pipeline_with_images.yaml"
    )
