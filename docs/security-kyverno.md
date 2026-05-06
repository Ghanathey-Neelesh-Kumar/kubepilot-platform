
# Kyverno Security Policies

KubePilot uses Kyverno to enforce Kubernetes security and best-practice policies.

## Why Kyverno?

Kyverno is a Kubernetes-native policy engine. Policies are written as Kubernetes YAML, which makes them easy to understand and manage with GitOps.

## Installed Policies

| Policy | Mode | Purpose |
|---|---|---|
| disallow-privileged-containers | Enforce | Blocks privileged containers |
| disallow-latest-tag | Enforce | Blocks mutable latest image tag |
| require-requests-limits | Enforce | Requires CPU/memory requests and limits |
| require-run-as-non-root | Audit | Reports containers not explicitly running as non-root |
| require-health-probes | Audit | Reports containers missing readiness/liveness probes |

## Apply Policies

```bash
kubectl apply -f platform/kyverno/policies/


# Observability

KubePilot includes a production-style observability stack for metrics, logs, dashboards, and alerts.

## Components

| Component | Purpose |
|---|---|
| Prometheus | Collects metrics |
| Grafana | Visualizes metrics and logs |
| Alertmanager | Handles alerts |
| Loki | Stores logs |
| Grafana Alloy | Collects Kubernetes pod logs and sends them to Loki |

## Metrics Flow

```text
KubePilot Backend /metrics
        |
        v
ServiceMonitor
        |
        v
Prometheus
        |
        v
Grafana Dashboard