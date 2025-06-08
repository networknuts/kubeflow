#!/usr/bin/env python3
import argparse
import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

def main():
    parser = argparse.ArgumentParser(description="Insurance Fraud Training (Katib‐ready)")
    parser.add_argument('--clean_csv',    type=str, required=True,
                        help="Path to cleaned CSV")
    parser.add_argument('--prep_joblib',  type=str, required=True,
                        help="Path to preprocessor.joblib")
    parser.add_argument('--model_output', type=str, required=True,
                        help="Where to write final model bundle")
    parser.add_argument('--n_estimators', type=int, default=100,
                        help="Number of trees")
    parser.add_argument('--max_depth',    type=int, default=0,
                        help="Max tree depth (0 means None)")
    args = parser.parse_args()

    # 1. Load cleaned data
    df = pd.read_csv(args.clean_csv)
    X = df.drop('fraud_reported', axis=1)
    y = df['fraud_reported'].map({'Y':1,'N':0})

    # 2. Load and apply preprocessor
    pre = joblib.load(args.prep_joblib)
    X_fe = pre.transform(X)

    # 3. Build & train RF with Katib params
    depth = None if args.max_depth == 0 else args.max_depth
    clf = RandomForestClassifier(
        n_estimators=args.n_estimators,
        max_depth=depth,
        random_state=42,
        n_jobs=-1
    )
    clf.fit(X_fe, y)

    # 4. Evaluate on training (or a held-out split if you prefer)
    acc = accuracy_score(y, clf.predict(X_fe))
    # Katib expects a single line: <metric>=<value>
    print(f"accuracy={acc}")

    # 5. Persist the end‐to‐end bundle
    joblib.dump({'preprocessor': pre, 'model': clf}, args.model_output)

if __name__ == '__main__':
    main()
