# server.py
import joblib
import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict, Any

MODEL_PATH = "/app/fraud_pipeline_final.joblib"

# load once
bundle = joblib.load(MODEL_PATH)
pre, clf = bundle['preprocessor'], bundle['model']

app = FastAPI()

class BatchRequest(BaseModel):
    instances: List[Dict[str, Any]]

@app.post("/v1/models/insurance-fraud-custom:predict")
def predict(req: BatchRequest):
    # 1️⃣ Reconstruct the DataFrame with all original columns
    df = pd.DataFrame(req.instances)

    # 2️⃣ Use your fitted preprocessor (with both numeric + OHE pipelines)
    X_fe = pre.transform(df)

    # 3️⃣ Predict
    preds = clf.predict(X_fe).tolist()
    return {"predictions": preds}
