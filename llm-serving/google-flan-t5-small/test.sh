cat <<'JSON' | curl -s -X POST -H "Content-Type: application/json" http://localhost:8080/openai/v1/completions -d @- | jq .
{
  "model": "flan-t5-small-cpu",
  "prompt": "Translate to French: Hello, my name is aryan.",
  "max_tokens": 40,
  "temperature": 0.0
}
JSON
