
# KubePilot Doctor

KubePilot Doctor is the troubleshooting assistant for the KubePilot platform.

It is designed to help identify common Kubernetes issues quickly and explain them in simple, actionable language.

## Why This Exists

In real Kubernetes environments, failures are often spread across multiple objects:

- Pod status
- Container status
- Deployment status
- Service selectors
- Endpoints
- Events
- Argo CD sync state

KubePilot Doctor collects these signals and turns them into a practical diagnosis.

## Current Capabilities

| Check | What It Detects |
|---|---|
| Namespace | Missing namespace |
| Pods | Not Ready, Pending, Failed |
| Containers | ImagePullBackOff, CrashLoopBackOff, OOMKilled |
| Deployments | Desired vs ready replica mismatch |
| Services | Missing endpoints |
| Events | Recent Kubernetes warning events |
| Argo CD | OutOfSync or unhealthy Applications |

## Usage

```bash
python tools/kubepilot-doctor/doctor.py check namespace kubepilot-dev