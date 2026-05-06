# Lab 04 — ImagePullBackOff

## Problem

Kubernetes cannot pull the container image.

## Broken Configuration

```yaml
image: ghcr.io/does-not-exist/kubepilot-backend:missing-tag