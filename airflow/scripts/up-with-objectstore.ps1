Param(
  [string]$AirflowDir = (Split-Path -Parent $PSScriptRoot)
)

Set-Location $AirflowDir
docker compose -f docker-compose.yaml -f docker-compose.objectstore.yaml --env-file .env up -d @args
