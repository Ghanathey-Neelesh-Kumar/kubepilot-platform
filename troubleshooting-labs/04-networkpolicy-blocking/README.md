
# Lab 04 — NetworkPolicy Blocking Traffic

## Problem

A NetworkPolicy blocks traffic to backend Pods.

## Broken Configuration

```yaml
podSelector:
  matchLabels:
    app.kubernetes.io/component: backend
ingress: []