# /app/train_iris.py
import argparse, os, time, json
from sklearn import datasets
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, precision_score, recall_score
from prometheus_client import CollectorRegistry, Gauge, push_to_gateway

def push_to_pg(addr, job, labels, metrics: dict):
    if not addr:
        return
    reg = CollectorRegistry()
    gauges = {k: Gauge(k, f"katib metric {k}", registry=reg) for k in metrics.keys()}
    for k, v in metrics.items():
        gauges[k].set(float(v))
    # groupings (labels) show up as Prometheus labels on Pushgateway
    push_to_gateway(addr, job=job, registry=reg, grouping_key=labels)

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--C", type=float, required=True)
    p.add_argument("--gamma", type=float, required=True)
    p.add_argument("--test_size", type=float, default=0.2)
    p.add_argument("--random_state", type=int, default=42)
    p.add_argument("--pushgateway", type=str, default=os.environ.get("PUSHGATEWAY_ADDR", ""))
    args = p.parse_args()

    iris = datasets.load_iris()
    X_train, X_test, y_train, y_test = train_test_split(
        iris.data, iris.target, test_size=args.test_size, random_state=args.random_state, stratify=iris.target
    )

    model = SVC(C=args.C, gamma=args.gamma, kernel="rbf", probability=False, random_state=args.random_state)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, average="macro", zero_division=0)
    recall = recall_score(y_test, y_pred, average="macro", zero_division=0)

    # ---- Katib metrics (StdOut collector reads these) ----
    # Use simple "name=value" lines (Katib default parser).
    print(f"accuracy={accuracy}")
    print(f"precision={precision}")
    print(f"recall={recall}")

    # ---- Pushgateway for Prometheus ----
    trial_name = os.environ.get("KATIB_TRIAL_NAME", "local")  # provided by Katib in trial pods
    labels = {
        "dataset": "iris",
        "algo": "svc_rbf",
        "trial": trial_name
    }
    metrics = {"accuracy": accuracy, "precision": precision, "recall": recall}
    job = f"katib_trial_metrics"
    if args.pushgateway:
        push_to_pg(args.pushgateway, job, labels, metrics)

if __name__ == "__main__":
    main()
