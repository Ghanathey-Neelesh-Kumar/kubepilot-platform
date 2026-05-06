# Lab 01 — Service Selector Mismatch

## Problem

A Kubernetes Service cannot route traffic to backend Pods because its selector does not match the Pod labels.

## Broken Resource

```yaml
selector:
  app.kubernetes.io/name: kubepilot
  app.kubernetes.io/component: wrong-backend