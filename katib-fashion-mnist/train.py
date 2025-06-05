import argparse
import tensorflow as tf
from tensorflow.keras.datasets import fashion_mnist
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Flatten, Dense
from tensorflow.keras.optimizers import Adam

# -----------------------------
# ✅ Parse Command-Line Args
# -----------------------------
parser = argparse.ArgumentParser()
parser.add_argument("--learning-rate", type=float, default=0.001, help="Learning rate for optimizer")
parser.add_argument("--batch-size", type=int, default=32, help="Batch size for training")
args = parser.parse_args()

# -----------------------------
# 📥 Load and Preprocess Data
# -----------------------------
(x_train, y_train), (x_test, y_test) = fashion_mnist.load_data()
x_train, x_test = x_train / 255.0, x_test / 255.0  # normalize

# -----------------------------
# 🧠 Build and Compile Model
# -----------------------------
model = Sequential([
    Flatten(input_shape=(28, 28)),
    Dense(128, activation='relu'),
    Dense(10, activation='softmax')
])

model.compile(
    optimizer=Adam(learning_rate=args.learning_rate),
    loss='sparse_categorical_crossentropy',
    metrics=['accuracy']
)

# -----------------------------
# 🚀 Train and Evaluate
# -----------------------------
model.fit(x_train, y_train, batch_size=args.batch_size, epochs=5, verbose=2)
_, accuracy = model.evaluate(x_test, y_test, verbose=0)

# -----------------------------
# ✅ Output Result for Katib
# -----------------------------
print(f"accuracy={accuracy}")
