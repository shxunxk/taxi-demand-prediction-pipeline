# Local stack: Airflow (orchestration) + optional MinIO (object storage)

This layout mirrors how teams separate **control plane** (schedulers) from **data plane** (S3-compatible storage).

## Orchestration only (Airflow)

```bash
cd airflow
cp .env.example .env   # edit GITHUB_REPO_URL, paths, optional MinIO section
docker compose -f docker-compose.yaml up -d
```

- UI: http://localhost:8080 (default `airflow` / `airflow` unless changed in compose)

## Airflow + MinIO (recommended for S3-style pipelines)

Use **two compose files**. The object store is a **separate** file on purpose: in production, storage is almost always a managed service or dedicated cluster, not merged into the scheduler deployment.

```bash
docker compose -f docker-compose.yaml -f ../minio/docker-compose.objectstore.yaml --env-file .env up -d
```

| Service        | URL / endpoint |
|----------------|----------------|
| Airflow        | http://localhost:8080 |
| MinIO S3 API   | http://localhost:9000 (host) — **http://minio:9000** from other containers |
| MinIO console  | http://localhost:9001 |

Set in `.env`:

- `MINIO_ROOT_USER` / `MINIO_ROOT_PASSWORD` — admin only (console, break-glass); do not put these in app code.
- `MINIO_PIPELINE_ACCESS_KEY` / `MINIO_PIPELINE_SECRET_KEY` — application identity; the init job creates this user and grants access (same idea as IAM user + keys in AWS).
- `S3_ENDPOINT_URL=http://minio:9000` — used inside workers (`boto3` `endpoint_url`).

`docker-compose.objectstore.yaml` pins MinIO and `mc` image tags. Bump tags together when you upgrade.

## Object storage only

```bash
docker compose -f ../minio/docker-compose.objectstore.yaml --env-file .env up -d
```

By default MinIO runs on its own Docker network `taxi_minio_platform` so the stacks remain separate.
To run them on the same network (not recommended for production), start both from the repository root and specify the same network name manually.

## Industry notes (how this differs from “one big compose”)

- **Separation of concerns:** Airflow does not “own” blobs; it calls an HTTP API with scoped credentials — same as calling AWS S3 from MWAA or Composer.
- **Least privilege:** Pipeline tasks should use **pipeline** keys from `.env`, not MinIO root — the `minio-init` job creates the user; root is for admins only.
- **Pinning:** Production pipelines pin image digests or release tags; `latest` is avoided in the object-store file.
- **Production:** Replace MinIO with **Amazon S3**, **GCS**, or **Azure Blob**, keep the same env var names in CI/CD secrets; endpoint and keys come from the cloud provider.

## Stop

```bash
docker compose -f docker-compose.yaml -f ../minio/docker-compose.objectstore.yaml down
```

MinIO files live in volume `minio-data` until you `docker compose ... down -v`.
