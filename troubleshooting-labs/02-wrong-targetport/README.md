@'
# Lab 02 — Wrong targetPort

## Problem

The Service selector is correct, so endpoints exist, but the Service forwards traffic to the wrong container port.

## Broken Configuration

```yaml
ports:
  - port: 5000
    targetPort: 9999