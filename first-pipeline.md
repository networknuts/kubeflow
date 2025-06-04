**Code for First Pipeline**

```python
# fashion_mnist_pipeline.py

from kfp.v2 import compiler
from kfp.v2.dsl import component, pipeline

@component(
    base_image='python:3.9',
    packages_to_install=['tensorflow','numpy']
)
def preprocess_op(
    dataset_uri: str,
    output_path: str,
) -> str:
    import tensorflow as tf, numpy as np
    # load & normalize
    (x_train, y_train), _ = tf.keras.datasets.fashion_mnist.load_data()
    x_train = x_train.astype('float32') / 255.0
    # save processed data
    np.savez(output_path, x=x_train, y=y_train)
    return output_path

@component(
    base_image='python:3.9',
    packages_to_install=['tensorflow','numpy']
)
def train_op(
    preprocessed_path: str,
    model_path: str,
) -> str:
    import numpy as np, tensorflow as tf
    # load processed data
    data = np.load(preprocessed_path + '.npz')
    x, y = data['x'], data['y']
    # simple CNN
    model = tf.keras.Sequential([
        tf.keras.layers.Reshape((28,28,1), input_shape=(28,28)),
        tf.keras.layers.Conv2D(32, 3, activation='relu'),
        tf.keras.layers.MaxPooling2D(),
        tf.keras.layers.Flatten(),
        tf.keras.layers.Dense(10, activation='softmax'),
    ])
    model.compile('adam', 'sparse_categorical_crossentropy', metrics=['accuracy'])
    model.fit(x, y, epochs=5)
    model.save(model_path)
    return model_path

@component(
    base_image='python:3.9',
    packages_to_install=['tensorflow','numpy']
)
def eval_op(
    model_path: str,
    preprocessed_path: str,
) -> None:
    import numpy as np, tensorflow as tf
    # load data & model
    data = np.load(preprocessed_path + '.npz')
    x, y = data['x'], data['y']
    model = tf.keras.models.load_model(model_path)
    loss, acc = model.evaluate(x, y)
    print(f'Test accuracy: {acc:.4f}')

@pipeline(
    name='fashion-mnist-3step',
    pipeline_root='s3://mlpipeline/pipeline_root'
)
def fashion_mnist_pipeline(
    dataset_uri: str,
    preprocess_output: str = '/mnt/data/processed',
    model_output: str = '/mnt/models/1',
):
    # 1. preprocess
    prep = preprocess_op(dataset_uri=dataset_uri, output_path=preprocess_output)
    # 2. train
    train = train_op(preprocessed_path=prep.output, model_path=model_output)
    # 3. evaluate
    eval_op(model_path=train.output, preprocessed_path=prep.output)

if __name__ == '__main__':
    compiler.Compiler().compile(
        pipeline_func=fashion_mnist_pipeline,
        package_path='fashion_mnist_pipeline.yaml'
    )
# fashion_mnist_pipeline.py

from kfp.v2 import compiler
from kfp.v2.dsl import component, pipeline

@component(
    base_image='python:3.9',
    packages_to_install=['tensorflow','numpy']
)
def preprocess_op(
    dataset_uri: str,
    output_path: str,
) -> str:
    import tensorflow as tf, numpy as np
    # load & normalize
    (x_train, y_train), _ = tf.keras.datasets.fashion_mnist.load_data()
    x_train = x_train.astype('float32') / 255.0
    # save processed data
    np.savez(output_path, x=x_train, y=y_train)
    return output_path

@component(
    base_image='python:3.9',
    packages_to_install=['tensorflow','numpy']
)
def train_op(
    preprocessed_path: str,
    model_path: str,
) -> str:
    import numpy as np, tensorflow as tf
    # load processed data
    data = np.load(preprocessed_path + '.npz')
    x, y = data['x'], data['y']
    # simple CNN
    model = tf.keras.Sequential([
        tf.keras.layers.Reshape((28,28,1), input_shape=(28,28)),
        tf.keras.layers.Conv2D(32, 3, activation='relu'),
        tf.keras.layers.MaxPooling2D(),
        tf.keras.layers.Flatten(),
        tf.keras.layers.Dense(10, activation='softmax'),
    ])
    model.compile('adam', 'sparse_categorical_crossentropy', metrics=['accuracy'])
    model.fit(x, y, epochs=5)
    model.save(model_path)
    return model_path

@component(
    base_image='python:3.9',
    packages_to_install=['tensorflow','numpy']
)
def eval_op(
    model_path: str,
    preprocessed_path: str,
) -> None:
    import numpy as np, tensorflow as tf
    # load data & model
    data = np.load(preprocessed_path + '.npz')
    x, y = data['x'], data['y']
    model = tf.keras.models.load_model(model_path)
    loss, acc = model.evaluate(x, y)
    print(f'Test accuracy: {acc:.4f}')

@pipeline(
    name='fashion-mnist-3step',
    pipeline_root='gs://<your-bucket>/pipeline_root'
)
def fashion_mnist_pipeline(
    dataset_uri: str,
    preprocess_output: str = '/mnt/data/processed',
    model_output: str = '/mnt/models/1',
):
    # 1. preprocess
    prep = preprocess_op(dataset_uri=dataset_uri, output_path=preprocess_output)
    # 2. train
    train = train_op(preprocessed_path=prep.output, model_path=model_output)
    # 3. evaluate
    eval_op(model_path=train.output, preprocessed_path=prep.output)

if __name__ == '__main__':
    compiler.Compiler().compile(
        pipeline_func=fashion_mnist_pipeline,
        package_path='fashion_mnist_pipeline.yaml'
    )

```
