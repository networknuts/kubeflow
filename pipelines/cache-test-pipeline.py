from kfp.v2.dsl import component, pipeline
import time

@component(base_image="python:3.9-slim")
def slow_op(username: str):
    print(f"Hello {username}, starting slow step…")
    time.sleep(30)
    print("Done sleeping!")

@pipeline(name="cache-test-pipeline")
def cache_test_pipeline(username: str):
    # Explicitly leave caching enabled
    _ = slow_op(username=username)

if __name__ == "__main__":
    from kfp.v2 import compiler
    compiler.Compiler().compile(
        pipeline_func=cache_test_pipeline,
        package_path="cache_test_pipeline.yaml"
    )
