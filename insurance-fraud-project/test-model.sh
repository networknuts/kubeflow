#!/usr/bin/env bash
# test-model.sh – port-forward the KServe predictor service and send a test request

set -euo pipefail

NAMESPACE="kubeflow-user-example-com"
SERVICE="insurance-fraud-custom-predictor-00001-private"
LOCAL_PORT=8080
REMOTE_PORT=80

# Start port-forward in background
kubectl port-forward svc/${SERVICE} ${LOCAL_PORT}:${REMOTE_PORT} -n ${NAMESPACE} >/dev/null 2>&1 &
PF_PID=$!

# Ensure we clean up on exit
cleanup() {
  echo "Stopping port-forward (pid ${PF_PID})"
  kill ${PF_PID} || true
}
trap cleanup EXIT

# Give port-forward a moment to establish
sleep 2

# Send the test curl request
curl -X POST http://localhost:${LOCAL_PORT}/v1/models/insurance-fraud-custom:predict \
  -H "Content-Type: application/json" \
  -d '{
  "instances": [
    {
      "months_as_customer": 328,
      "age": 48,
      "policy_state": "OH",
      "policy_csl": "250/500",
      "policy_deductable": 1000,
      "policy_annual_premium": 1406.91,
      "umbrella_limit": 0,
      "insured_zip": "466132",
      "insured_sex": "MALE",
      "insured_education_level": "MD",
      "insured_occupation": "craft-repair",
      "insured_hobbies": "sleeping",
      "insured_relationship": "husband",
      "capital-gains": 53300,
      "capital-loss": 0,
      "incident_type": "Single Vehicle Collision",
      "collision_type": "Side Collision",
      "incident_severity": "Major Damage",
      "authorities_contacted": "Police",
      "incident_state": "SC",
      "incident_city": "Columbus",
      "incident_hour_of_the_day": 5,
      "number_of_vehicles_involved": 1,
      "property_damage": "YES",
      "bodily_injuries": 1,
      "witnesses": 2,
      "police_report_available": "YES",
      "total_claim_amount": 71610,
      "injury_claim": 6510,
      "property_claim": 13020,
      "vehicle_claim": 52080,
      "auto_make": "Saab",
      "auto_model": "92x",
      "auto_year": 2004
    }
  ]
}'

# Port-forward will be killed by the EXIT trap
