# Lab 02 — Docker Basics

**Duration:** 45 minutes
**Prerequisites:** Lab 00; Docker running on your Ubuntu VM.

## Objectives

- Build a Docker image for the order service.
- Run and inspect a container on localhost.
- Understand layers, tags and basic security choices.

## Part A — Build the Order Service Image

From the `labs/app` directory:

```bash
cd labs/app
docker build -t order-service:lab02 --build-arg BUILD_ID=lab02 -f Dockerfile .
```

Check the result:

```bash
docker images order-service
```

Expected: an image tagged `order-service:lab02`.

## Part B — Run and Inspect

Run the container:

```bash
docker run -d --name order-lab02 -p 8080:8000 order-service:lab02
```

Test the health endpoint on localhost:

```bash
curl http://localhost:8080/health
# Expected: {"status":"ok","env":"production","build_id":"lab02"}
```

Note the difference from Lab 00: `env` is now `production` and `build_id` is
`lab02` — both were **baked into the image** (`ENV` and `--build-arg` in the
Dockerfile). Configuration travels with the artifact.

Inspect the running container:

```bash
docker ps
docker logs order-lab02
docker exec -it order-lab02 /bin/sh
# Inside the container:
whoami        # -> appuser (not root!)
ls -la /app
exit
```

## Part C — Explore Image Layers

```bash
docker history order-service:lab02
```

- Identify the layer that installs Python packages.
- Notice the `builder` stage does not appear in the final image — the
  multi-stage build copies only the installed packages across, keeping the
  runtime image small.

Compare sizes:

```bash
docker images | head -5
```

## Part D — Clean Up

```bash
docker stop order-lab02
docker rm order-lab02
```

## Expected Output

- Container responds on `http://localhost:8080/health`.
- Container user is `appuser`, not `root`.
- `docker history` shows a small number of slim final-stage layers.

## Verification Checklist

- [ ] Image built successfully.
- [ ] Container responds on port 8080.
- [ ] `docker logs` shows Uvicorn startup.
- [ ] `whoami` inside the container prints `appuser`.
- [ ] Container removed cleanly.

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `permission denied` on docker commands | `newgrp docker`, or log out/in (Lab 00 Part A). |
| Port 8080 in use | Map another port: `-p 8081:8000`, then curl 8081. |
| Health check fails | The app listens on `0.0.0.0:8000` inside the container — check `docker logs order-lab02` for startup errors. |

## Stretch Goal

Inspect image efficiency with `dive`:

```bash
DIVE_VERSION=0.12.0
curl -fsSL -o /tmp/dive.deb \
  "https://github.com/wagoodman/dive/releases/download/v${DIVE_VERSION}/dive_${DIVE_VERSION}_linux_amd64.deb"
sudo apt install /tmp/dive.deb
dive order-service:lab02
```

Try switching the base image to `python:3.12-alpine` and compare the image
size — and note what breaks (musl vs glibc wheels) before assuming smaller
is always better.
