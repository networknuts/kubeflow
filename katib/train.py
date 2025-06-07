#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
train.py

A self-contained script to train a logistic regression model on the Iris dataset,
suitable for Kubeflow Katib hyperparameter tuning. It splits the data into training
and test sets, fits a sklearn LogisticRegression model with provided hyperparameters,
and prints out the accuracy metric in Katib’s required format.

Usage example:
    python3 train.py --penalty l2 --tol 0.001 --C 0.5 --max-iter 10
"""

import argparse         # For parsing command-line arguments
import random           # Python’s built-in pseudo-random number generator
import warnings         # To suppress any non-critical warnings
import numpy as np      # Fundamental package for numerical computations

# sklearn provides datasets, model classes, and utility functions
from sklearn import datasets
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split

# -----------------------------------------------------------------------------------
# GLOBAL CONSTANTS
# -----------------------------------------------------------------------------------
# Seed for all random operations to ensure reproducibility
RANDOM_STATE: int = 1337

# Suppress warnings (e.g. convergence warnings from sklearn)
warnings.filterwarnings("ignore")

# Seed both Python’s and NumPy’s RNGs
random.seed(RANDOM_STATE)
np.random.seed(RANDOM_STATE)


def main(penalty: str, tol: float, C: float, max_iter: int) -> None:
    """
    Main training function.

    Args:
        penalty (str): Regularization norm ('l1', 'l2', 'elasticnet', or 'none').
        tol (float): Tolerance for stopping criteria.
        C (float): Inverse of regularization strength; smaller values specify stronger regularization.
        max_iter (int): Maximum number of iterations taken for the solvers to converge.

    Steps:
        1. Load the Iris dataset.
        2. Split into train/test sets.
        3. Initialize the LogisticRegression model with the given hyperparameters.
        4. Fit the model on the training data.
        5. Predict on the test set.
        6. Compute and print accuracy in Katib format.
    """
    # 1. Load dataset from sklearn
    iris = datasets.load_iris()
    X = iris.data    # feature matrix, shape = (150, 4)
    y = iris.target  # target vector, shape = (150,)

    # 2. Split into train and test sets
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,         # 20% held out for testing
        random_state=RANDOM_STATE
    )

    # 3. Create LogisticRegression model with user-specified hyperparameters
    clf = LogisticRegression(
        penalty=penalty,
        tol=tol,
        C=C,
        max_iter=max_iter,
        random_state=RANDOM_STATE,
        solver='lbfgs',        # default solver; supports l2 and none
        multi_class='auto'     # automatically selects ‘ovr’ or ‘multinomial’
    )

    # 4. Train the model
    clf.fit(X_train, y_train)

    # 5. Predict on test data
    y_pred = clf.predict(X_test)

    # 6. Evaluate accuracy
    acc = accuracy_score(y_test, y_pred)

    # Katib expects metrics printed as: <metric-name>=<metric-value>
    # Here we report only 'accuracy' for hyperparameter tuning.
    print(f"accuracy={acc:.4f}")


if __name__ == "__main__":
    # -----------------------------------------------------------------------------------
    # COMMAND-LINE ARGUMENT PARSING
    # -----------------------------------------------------------------------------------
    parser = argparse.ArgumentParser(
        description="Train a LogisticRegression model on Iris for Katib hyperparameter tuning."
    )

    # Define required hyperparameter arguments
    parser.add_argument(
        "--penalty",
        type=str,
        choices=["l1", "l2", "elasticnet", "none"],
        required=True,
        help="Regularization norm to use (l1, l2, elasticnet, or none)"
    )
    parser.add_argument(
        "--tol",
        type=float,
        required=True,
        help="Tolerance for stopping criteria (e.g. 0.0001)"
    )
    parser.add_argument(
        "--C",
        type=float,
        required=True,
        help="Inverse of regularization strength; smaller values = stronger regularization"
    )
    parser.add_argument(
        "--max-iter",
        type=int,
        required=True,
        help="Maximum number of iterations for the solver to converge"
    )

    # Parse the arguments and call main()
    args = parser.parse_args()
    main(
        penalty=args.penalty,
        tol=args.tol,
        C=args.C,
        max_iter=args.max_iter,
    )
