# Lab 03 — Readiness Probe Failing

## Problem

The backend container starts correctly, but Kubernetes does not mark the Pod as Ready because the readiness probe points to the wrong path.

## Broken Configuration

```yaml
readinessProbe:
  httpGet:
    path: /wrong-ready-path
    port: 5000