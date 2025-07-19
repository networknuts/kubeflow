import requests
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split

# 1) Prepare your test split
X, y = load_iris(return_X_y=True)
_, X_test, _, y_test = train_test_split(
    X, y, test_size=0.2, random_state=1337
)

# 2) Call the KServe V1 endpoint for all instances
response = requests.post(
    "http://localhost:8080/v1/models/1:predict",
    json={"instances": X_test.tolist()}
)
preds = response.json()["predictions"]

# 3) Compute accuracy
accuracy = sum(int(p)==int(t) for p, t in zip(preds, y_test.tolist())) / len(y_test)
print(f"Accuracy on full test set: {accuracy:.4f}")
