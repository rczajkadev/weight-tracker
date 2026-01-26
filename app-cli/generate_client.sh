#!/bin/sh
set -e

root_dir=$(git rev-parse --show-toplevel)

openapi_path="${1:-$root_dir/app-api/src/WeightTracker.Api/openapi.json}"
output_path="${2:-$root_dir/app-cli/generated_client}"
venv_python="$root_dir/app-cli/.venv/Scripts/python.exe"

if [ ! -f "$venv_python" ]; then
  venv_python="$root_dir/app-cli/.venv/bin/python"
fi

if [ ! -f "$venv_python" ]; then
  echo "Python venv not found. Create it in $root_dir/app-cli/.venv first." >&2
  exit 1
fi

if [ ! -f "$openapi_path" ]; then
  echo "OpenAPI file not found: $openapi_path" >&2
  exit 1
fi

"$venv_python" -m openapi_python_client generate --path "$openapi_path" --output-path "$output_path" --overwrite
"$venv_python" -m pip install -e "$output_path"
