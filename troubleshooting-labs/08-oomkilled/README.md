# Lab 08 — OOMKilled

## Problem

The container exceeds its memory limit and Kubernetes kills it.

## Broken Configuration

```yaml
limits:
  memory: 32Mi