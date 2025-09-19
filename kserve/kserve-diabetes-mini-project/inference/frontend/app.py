import os, json, time, hmac, hashlib
import requests
import streamlit as st
import redis

# ---------------- Config via ConfigMap/Env ----------------
INFERENCE_URL     = os.getenv("INFERENCE_URL", "").strip()
INFERENCE_BASE    = os.getenv("INFERENCE_BASE", "").rstrip("/")
MODEL_NAME        = os.getenv("MODEL_NAME", "diabetes-s3-model-serving").strip()
MODEL_VERSION     = os.getenv("MODEL_VERSION", "").strip()  # optional, if you expose it
INPUT_NAME        = os.getenv("INPUT_NAME", "predict").strip()
INPUT_DATATYPE    = os.getenv("INPUT_DATATYPE", "FP32").strip()
TIMEOUT_SECONDS   = float(os.getenv("TIMEOUT_SECONDS", "15"))
VERIFY_TLS        = os.getenv("VERIFY_TLS", "true").lower() == "true"

# Redis
REDIS_HOST        = os.getenv("REDIS_HOST", "redis")
REDIS_PORT        = int(os.getenv("REDIS_PORT", "6379"))
REDIS_DB          = int(os.getenv("REDIS_DB", "0"))
CACHE_TTL_SECONDS = int(os.getenv("CACHE_TTL_SECONDS", "86400"))  # 24h default
CACHE_ENABLED     = os.getenv("CACHE_ENABLED", "true").lower() == "true"
CACHE_SECRET      = os.getenv("CACHE_SECRET", "change-me")  # used to HMAC the key

# ---------------- Helpers ----------------
def build_infer_url() -> str:
    if INFERENCE_URL:
        return INFERENCE_URL
    if not INFERENCE_BASE:
        raise ValueError("Either INFERENCE_URL or INFERENCE_BASE must be set")
    return f"{INFERENCE_BASE}/v2/models/{MODEL_NAME}/infer"

def stable_features(features):
    """
    Normalize features for hashing: round floats to fixed precision, cast ints.
    Avoids tiny float diffs creating different keys.
    """
    norm = []
    for x in features:
        if isinstance(x, float):
            norm.append(round(x, 6))  # adjust precision as needed
        else:
            norm.append(int(x))
    return norm

def cache_key(features):
    norm = stable_features(features)
    blob = json.dumps(
        {"model": MODEL_NAME, "version": MODEL_VERSION, "features": norm},
        separators=(",", ":"), sort_keys=True
    )
    # HMAC for uniform key & to avoid huge keys; safe across pods
    digest = hmac.new(CACHE_SECRET.encode(), blob.encode(), hashlib.sha256).hexdigest()
    return f"diabetes:infer:{digest}"

@st.cache_resource(show_spinner=False)
def get_redis():
    try:
        r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)
        # simple ping for readiness; won’t raise if Redis is unauthenticated/open
        r.ping()
        return r
    except Exception:
        return None  # app will continue without cache

def infer_remote(features):
    payload = {
        "inputs": [
            {"name": INPUT_NAME, "shape": [1, 8], "datatype": INPUT_DATATYPE, "data": [features]}
        ]
    }
    url = build_infer_url()
    t0 = time.time()
    resp = requests.post(url, json=payload, timeout=TIMEOUT_SECONDS, verify=VERIFY_TLS,
                         headers={"Content-Type": "application/json"})
    latency = (time.time() - t0) * 1000.0
    resp.raise_for_status()
    return resp.json(), latency, payload, url

# ---------------- UI ----------------
st.set_page_config(page_title="Diabetes Inference (Cached)", page_icon="⚡", layout="centered")
st.title("⚡ Diabetes Risk Inference with Caching")

with st.expander("Connection details", expanded=False):
    st.code(
        f"MODEL_NAME={MODEL_NAME}\nMODEL_VERSION={MODEL_VERSION or '(not set)'}\n"
        f"INFERENCE_URL={INFERENCE_URL or '(built from base)'}\nINFERENCE_BASE={INFERENCE_BASE or '(not set)'}\n"
        f"REDIS_HOST={REDIS_HOST}:{REDIS_PORT} (db {REDIS_DB})\nCACHE_ENABLED={CACHE_ENABLED} TTL={CACHE_TTL_SECONDS}s",
        language="bash",
    )

# Inputs
col1, col2 = st.columns(2)
with col1:
    pregnancies    = st.number_input("Pregnancies", min_value=0, max_value=20, value=0)
    glucose        = st.number_input("Glucose", min_value=0.0, max_value=250.0, value=88.0, step=1.0)
    blood_pressure = st.number_input("BloodPressure", min_value=0.0, max_value=180.0, value=60.0, step=1.0)
    skin_thickness = st.number_input("SkinThickness", min_value=0.0, max_value=100.0, value=35.0, step=1.0)
with col2:
    insulin = st.number_input("Insulin", min_value=0.0, max_value=1000.0, value=1.0, step=1.0)
    bmi     = st.number_input("BMI", min_value=0.0, max_value=80.0, value=45.7, step=0.1, format="%.1f")
    dpf     = st.number_input("DiabetesPedigreeFunction", min_value=0.0, max_value=5.0, value=0.27, step=0.01, format="%.2f")
    age     = st.number_input("Age", min_value=1, max_value=120, value=20)

left, right = st.columns(2)
with left:
    bypass_cache = st.toggle("Bypass cache", value=False, help="Force fresh call to model")
with right:
    clear_cache = st.button("Clear all cache (danger)")

if clear_cache and CACHE_ENABLED and get_redis():
    get_redis().flushdb()
    st.warning("Cache cleared.")

if st.button("Run Inference", use_container_width=True):
    features = [
        int(pregnancies),
        float(glucose),
        float(blood_pressure),
        float(skin_thickness),
        float(insulin),
        float(bmi),
        float(dpf),
        int(age),
    ]
    key = cache_key(features)
    r = get_redis() if CACHE_ENABLED else None

    # Try cache
    if r and not bypass_cache:
        cached = r.get(key)
        if cached:
            obj = json.loads(cached)
            st.info(f"Served from cache · stored_at={obj.get('stored_at')}")
            st.code(json.dumps(obj["result_json"], indent=2), language="json")
            st.metric("Predicted (cached)", obj.get("pred_label", "n/a"))
            if obj.get("prob") is not None:
                st.write(f"Probability (cached): **{obj['prob']:.3f}**")
            with st.expander("Cached record", expanded=False):
                st.code(json.dumps(obj, indent=2), language="json")
            st.stop()

    # Else call model
    try:
        result_json, latency_ms, sent_payload, used_url = infer_remote(features)
        # Quick extractor (same as earlier)
        pred_label, prob = None, None
        if isinstance(result_json, dict) and "outputs" in result_json:
            out0 = result_json["outputs"][0]
            data = out0.get("data")
            if data:
                if isinstance(data[0], list):
                    vec = data[0]
                    if len(vec) == 1:
                        prob = float(vec[0]); pred_label = 1 if prob >= 0.5 else 0
                    elif len(vec) == 2:
                        prob = float(vec[1]); pred_label = 1 if prob >= 0.5 else 0
                elif isinstance(data[0], (int, float)):
                    val = data[0]
                    if float(val) in (0.0, 1.0):
                        pred_label = int(val)
                    else:
                        prob = float(val); pred_label = 1 if prob >= 0.5 else 0

        st.success(f"Inference OK · {latency_ms:.1f} ms")
        st.code(json.dumps(result_json, indent=2), language="json")
        if pred_label is not None:
            st.metric("Predicted Outcome", f"{pred_label}")
        if prob is not None:
            st.write(f"Probability: **{prob:.3f}**")

        # Save to cache
        if r:
            record = {
                "model": MODEL_NAME,
                "version": MODEL_VERSION,
                "features": stable_features(features),
                "result_json": result_json,
                "pred_label": pred_label,
                "prob": prob,
                "latency_ms": latency_ms,
                "stored_at": int(time.time()),
            }
            r.set(key, json.dumps(record), ex=CACHE_TTL_SECONDS if CACHE_TTL_SECONDS > 0 else None)

        with st.expander("Request sent", expanded=False):
            st.code(json.dumps(sent_payload, indent=2), language="json")
            st.text(f"POST {used_url}")

    except requests.HTTPError as e:
        st.error(f"HTTP error: {e.response.status_code} {e.response.text}")
    except Exception as e:
        st.error(f"Error: {e}")
