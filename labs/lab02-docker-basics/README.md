# Lab 02 — Docker Basics

**Duration:** 60 minutes  
**Prerequisites:** Lab 00; Docker running.

## Objectives

- Build a Docker image for the order service.
- Run and inspect a container.
- Understand layers, tags and basic security choices.

## Part A — Build the Order Service Image

From the `labs/app` directory:

```bash
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

Test the health endpoint:

```bash
curl http://localhost:8080/health
# Expected: {"status":"ok","env":"production","build_id":"lab02"}
```

Inspect the running container:

```bash
docker ps
docker logs order-lab02
docker exec -it order-lab02 /bin/sh
# Inside the container:
whoami
ls -la /app
exit
```

Notice the container runs as a non-root user (`appuser`) and contains only the files it needs.

## Part C — Explore Image Layers

```bash
docker history order-service:lab02
```

- Identify the layer that installs Python packages.
- Notice how the multi-stage build keeps the final image smaller.

## Part D — Clean Up

```bash
docker stop order-lab02
docker rm order-lab02
```

## Expected Output

- Container responds to `/health`.
- `docker history` shows a `builder` stage and a slim final stage.
- Container user is not `root`.

## Verification Checklist

- [ ] Image built successfully.
- [ ] Container starts and responds on port 8080.
- [ ] Logs show Uvicorn startup.
- [ ] Image uses a non-root user.
- [ ] Container removed cleanly.

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `permission denied` | On Linux, add your user to the `docker` group or use `sudo`. |
| Port 8080 in use | Map to a different port: `-p 8081:8000`. |
| Health check fails | Ensure the app listens on `0.0.0.0:8000` (it does in the Dockerfile). |

## Stretch Goal

Use Dive to inspect image efficiency:

```bash
brew install dive          # macOS
dive order-service:lab02
```

Try to make the image even smaller by switching to `python:3.12-alpine` and installing only build dependencies that are removed afterwards.
