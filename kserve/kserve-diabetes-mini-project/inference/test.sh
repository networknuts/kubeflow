curl -s -X POST \
  -H "Content-Type: application/json" \
  --data-binary @request-v2.json \
  http://localhost:8080/v2/models/diabetes-s3-model-serving/infer \
  | jq 
