
# Lab 05 — CrashLoopBackOff

## Problem

The container starts and immediately exits with a failure code.

## Broken Configuration

```yaml
command: ["sh", "-c", "echo Starting app; echo Simulating crash; exit 1"]