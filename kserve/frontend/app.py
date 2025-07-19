import os
import requests
import streamlit as st

# Read the KServe URL from an env var (or hard‑code your service DNS)
KSERVE_URL = os.environ.get(
    "KSERVE_URL",
    "http://iriskserve-predictor-00001-private.kubeflow-user-example-com:80/v1/models/1:predict"
)

st.title("🍃 Iris Species Predictor")

st.markdown(
    """
    Enter the four Iris measurements (in cm), then hit **Predict** to see
    whether it’s _setosa_, _versicolor_, or _virginica_.
    """
)

# 1. Get inputs
sepal_length = st.number_input("Sepal length", min_value=0.0, step=0.1, value=5.1)
sepal_width  = st.number_input("Sepal width",  min_value=0.0, step=0.1, value=3.5)
petal_length = st.number_input("Petal length", min_value=0.0, step=0.1, value=1.4)
petal_width  = st.number_input("Petal width",  min_value=0.0, step=0.1, value=0.2)

if st.button("Predict"):
    payload = {"instances": [[
        sepal_length, sepal_width, petal_length, petal_width
    ]]}
    try:
        resp = requests.post(KSERVE_URL, json=payload, timeout=5)
        resp.raise_for_status()
        preds = resp.json().get("predictions", [])
        if preds:
            idx = int(preds[0])
            species = ["setosa", "versicolor", "virginica"][idx]
            st.success(f"Predicted species: **{species}** (class {idx})")
        else:
            st.error("No prediction returned.")
    except Exception as e:
        st.error(f"Request failed: {e}")
