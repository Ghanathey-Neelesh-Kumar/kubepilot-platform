# KubePilot Architecture Document v1.0

## 1. Project Overview

**KubePilot** is a production-style DevSecOps and Platform Engineering portfolio project built on Kubernetes.

The goal of this project is to demonstrate how a modern engineering team can safely build, deploy, secure, observe, and troubleshoot applications using cloud-native practices.

KubePilot is not just a simple Kubernetes deployment. It is designed as a mini **Internal Developer Platform (IDP)** that combines:

* Application delivery
* GitOps-based deployment
* CI/CD automation
* Container image security scanning
* Kubernetes policy enforcement
* Observability
* Logging
* Alerting
* Troubleshooting automation

This project is intended to showcase practical skills required for roles such as:

* DevOps Engineer
* Platform Engineer
* DevSecOps Engineer
* Kubernetes Engineer
* Cloud Native Engineer
* Site Reliability Engineer

---

## 2. Project Goal

The main goal of KubePilot is to answer one practical question:

> How can developers deploy applications safely to Kubernetes using an automated, secure, observable, and GitOps-driven platform?

In a real company, developers should not manually SSH into servers, edit Kubernetes resources directly, or depend on repeated manual DevOps tickets for every deployment.

Instead, the platform should provide a clear and reliable flow:

1. Developer pushes code to GitHub.
2. CI pipeline tests, builds, and scans the application.
3. A container image is pushed to a registry.
4. The GitOps repository is updated with the new image version.
5. Argo CD detects the change and deploys it to Kubernetes.
6. Kyverno validates whether the deployment follows security standards.
7. Prometheus, Grafana, Loki, and Alertmanager provide visibility into the running system.
8. KubePilot Doctor helps diagnose common Kubernetes failures.

---

## 3. High-Level Architecture

```text
[Developer]
    │
    ▼
[GitHub App Repo]
    │
    ▼
[GitHub Actions CI]
    │
    ├── Run tests
    ├── Build image
    ├── Trivy scan
    └── Push image + update GitOps repo
                     │
                     ▼
              [GitOps Repo]
                     │
                     ▼
                 [Argo CD]
                     │
                     ▼
         [Kubernetes Cluster: KubePilot]
                     │
   ┌─────────────────┼─────────────────────┐
   │                 │                     │
   ▼                 ▼                     ▼
[Frontend]       [Backend API]        [PostgreSQL]
   │                 │
   └─────── user traffic via Ingress ──────┘

Side Systems:
- Kyverno enforces security
- Prometheus collects metrics
- Grafana visualizes metrics and logs
- Loki stores logs
- Alertmanager triggers alerts
- KubePilot Doctor diagnoses common failures
```

---

## 4. Architecture Layers

KubePilot is designed using four major layers.

### 4.1 Application Layer

The application layer contains the actual application that runs on the platform.

Components:

* Frontend
* Backend API
* PostgreSQL database

The application itself is intentionally simple. The main focus of this project is not complex business logic. The main focus is the platform around the application.

The application will be a simple task management system for platform-related tasks.

Example tasks:

* Deploy backend service
* Review Kyverno policy
* Fix readiness probe
* Check Grafana dashboard
* Investigate failed pod

### 4.2 Delivery Layer

The delivery layer handles how code moves from a developer's laptop into Kubernetes.

Components:

* GitHub App Repository
* GitHub Actions
* Container Registry
* GitOps Repository
* Argo CD

This layer demonstrates CI/CD and GitOps working together.

### 4.3 Runtime Platform Layer

The runtime platform layer is the Kubernetes environment where the application runs.

Components:

* Kubernetes namespace
* Deployments
* Services
* ConfigMaps
* Secrets
* PersistentVolumeClaims
* Ingress
* Readiness probes
* Liveness probes
* Resource requests and limits

This layer demonstrates how applications should be deployed in a Kubernetes-native way.

### 4.4 Reliability and Security Layer

The reliability and security layer makes the project production-style.

Components:

* Trivy
* Kyverno
* Prometheus
* Grafana
* Loki
* Promtail
* Alertmanager
* KubePilot Doctor

This layer demonstrates security, monitoring, logging, alerting, and troubleshooting practices.

---

## 5. Application Architecture

### 5.1 Frontend

The frontend provides a simple user interface for interacting with the platform task system.

Responsibilities:

* Display platform tasks
* Create new tasks
* Call backend API endpoints
* Provide a simple user-facing entry point

Technology choice:

* HTML, CSS, and JavaScript for the first version
* Nginx as the web server

Reason:

The frontend should remain simple so the main focus stays on Kubernetes, GitOps, security, observability, and platform engineering.

### 5.2 Backend API

The backend provides REST API endpoints.

Initial endpoints:

```text
GET  /health
GET  /ready
GET  /api/tasks
POST /api/tasks
```

Responsibilities:

* Serve API requests
* Connect to PostgreSQL
* Store and retrieve tasks
* Expose health and readiness endpoints

Technology choice:

* Python Flask
* psycopg2 for PostgreSQL connection

Reason:

Flask is simple, easy to explain, and suitable for Kubernetes demonstrations involving health checks, readiness checks, logs, failures, and debugging.

### 5.3 PostgreSQL Database

PostgreSQL stores task data.

Responsibilities:

* Persist platform task records
* Provide database dependency for backend readiness checks
* Demonstrate Kubernetes persistent storage

---

## 6. Application Request Flow

```text
User Browser
    │
    ▼
Ingress
    │
    ▼
Frontend Service
    │
    ▼
Frontend Pod
    │
    ▼
Backend Service
    │
    ▼
Backend Pod
    │
    ▼
PostgreSQL Service
    │
    ▼
PostgreSQL Pod
```

### Explanation

1. The user accesses the application through Ingress.
2. Ingress routes traffic to the frontend service.
3. The frontend serves the web page.
4. The frontend calls the backend API.
5. The backend connects to PostgreSQL.
6. PostgreSQL stores and returns task data.

---

## 7. CI/CD and GitOps Architecture

KubePilot uses a GitOps-based deployment model.

### 7.1 Source Code Repository

The application repository contains:

* Frontend source code
* Backend source code
* Dockerfiles
* Unit tests
* GitHub Actions workflow

Recommended repository name:

```text
kubepilot-app
```

### 7.2 GitOps Repository

The GitOps repository contains:

* Kubernetes manifests
* Kustomize overlays
* Argo CD Application manifests
* Environment-specific configuration

Recommended repository name:

```text
kubepilot-gitops
```

### 7.3 Deployment Flow

```text
Developer pushes code
        │
        ▼
GitHub Actions starts
        │
        ├── Run tests
        ├── Build Docker image
        ├── Scan image using Trivy
        ├── Push image to registry
        └── Update image tag in GitOps repo
                  │
                  ▼
              Argo CD detects change
                  │
                  ▼
              Argo CD syncs app
                  │
                  ▼
          Kubernetes runs new version
```

### 7.4 Why GitOps?

GitOps makes Git the source of truth for application deployment.

Benefits:

* Clear deployment history
* Easy rollback
* Reduced manual changes
* Better auditability
* Consistent environments
* Automatic drift detection

---

## 8. Kubernetes Runtime Architecture

The Kubernetes runtime will contain the following resources.

### 8.1 Namespace

A dedicated namespace will isolate KubePilot resources.

Example:

```text
kubepilot
```

### 8.2 Frontend Resources

Resources:

* Deployment
* Service
* ConfigMap if needed
* Resource requests and limits
* Readiness probe
* Liveness probe

### 8.3 Backend Resources

Resources:

* Deployment
* Service
* ConfigMap
* Secret
* Resource requests and limits
* Readiness probe
* Liveness probe

### 8.4 PostgreSQL Resources

Resources:

* Deployment or StatefulSet
* Service
* Secret
* PersistentVolumeClaim

For the first version, PostgreSQL can run as a Deployment. Later, it can be improved to use StatefulSet for a more production-like setup.

### 8.5 Ingress

Ingress exposes the application externally.

Responsibilities:

* Route user traffic to the frontend
* Optionally route API traffic to the backend
* Provide a realistic production access pattern

---

## 9. Security Architecture

Security is applied at two important stages.

### 9.1 CI Pipeline Security

Trivy is used inside GitHub Actions to scan container images.

Responsibilities:

* Detect known vulnerabilities
* Produce scan output in CI logs
* Optionally fail the pipeline on critical vulnerabilities

### 9.2 Kubernetes Admission Security

Kyverno is used inside the Kubernetes cluster to enforce security policies.

Initial Kyverno policies:

* Disallow privileged containers
* Disallow `latest` image tag
* Require resource requests and limits
* Require readiness and liveness probes
* Require containers to run as non-root
* Require standard labels

### 9.3 Security Flow

```text
Developer commits code
        │
        ▼
GitHub Actions builds image
        │
        ▼
Trivy scans image
        │
        ▼
Image is pushed if accepted
        │
        ▼
Argo CD deploys manifests
        │
        ▼
Kyverno validates Kubernetes resources
        │
        ▼
Workload is admitted or rejected
```

---

## 10. Observability Architecture

KubePilot includes monitoring, logging, and alerting.

### 10.1 Monitoring with Prometheus

Prometheus collects metrics from Kubernetes and application components.

Metrics to monitor:

* Pod CPU usage
* Pod memory usage
* Pod restarts
* Deployment replica status
* HTTP request count
* API error rate
* API latency

### 10.2 Visualization with Grafana

Grafana provides dashboards for platform visibility.

Dashboards:

* Kubernetes cluster overview
* Application health dashboard
* Backend API dashboard
* Pod restart dashboard
* Logs dashboard using Loki

### 10.3 Logging with Loki and Promtail

Promtail collects logs from Kubernetes pods and sends them to Loki.

Loki stores logs and allows Grafana to query them.

Log examples:

* Backend startup logs
* Database connection logs
* API request logs
* Error logs
* CrashLoopBackOff investigation logs

### 10.4 Alerting with Alertmanager

Alertmanager handles alerts generated by Prometheus.

Example alerts:

* Backend pod down
* High pod restart count
* High memory usage
* PostgreSQL unavailable
* Application not ready

### 10.5 Observability Flow

```text
Kubernetes workloads
    │
    ├── metrics → Prometheus → Grafana
    │
    ├── logs    → Promtail → Loki → Grafana
    │
    └── alerts  → Prometheus Rules → Alertmanager
```

---

## 11. Troubleshooting Architecture

KubePilot includes a troubleshooting component called **KubePilot Doctor**.

KubePilot Doctor is a small CLI or script that helps diagnose common Kubernetes problems.

### 11.1 Purpose

The purpose of KubePilot Doctor is to convert raw Kubernetes troubleshooting signals into human-readable explanations.

Instead of only showing command output, it should explain:

* What is wrong
* Why it may be happening
* Which command confirms it
* How to fix it

### 11.2 Initial Checks

KubePilot Doctor should detect:

* Service selector mismatch
* Empty endpoints
* Wrong targetPort
* Readiness probe failure
* ImagePullBackOff
* CrashLoopBackOff
* OOMKilled
* NetworkPolicy blocking traffic
* Argo CD OutOfSync state

### 11.3 Example Output

```text
Issue detected: Service has no endpoints

Likely cause:
The Service selector does not match the labels on the target Pods.

Useful commands:
kubectl get svc backend-service -n kubepilot -o yaml
kubectl get pods -n kubepilot --show-labels
kubectl get endpoints backend-service -n kubepilot

Suggested fix:
Update the Service selector so it matches the Pod labels created by the Deployment.
```

---

## 12. Troubleshooting Labs

The project will include practical broken scenarios.

Each troubleshooting lab will contain:

```text
broken.yaml
symptoms.md
diagnosis-commands.md
fix.yaml
explanation.md
```

Initial labs:

```text
01-service-selector-mismatch
02-wrong-targetport
03-readiness-probe-failing
04-networkpolicy-blocking
05-imagepullbackoff
06-crashloopbackoff
07-argocd-outofsync
08-oomkilled
```

These labs will make the project valuable for:

* Portfolio demonstration
* YouTube tutorials
* LinkedIn technical posts
* Interview discussions
* Kubernetes certification practice

---

## 13. Environment Architecture

KubePilot will support multiple environments.

Initial environments:

* dev
* staging
* prod

Folder structure:

```text
gitops/
  environments/
    dev/
    staging/
    prod/
```

Each environment can have different values for:

* Replica count
* Resource limits
* Image tags
* Ingress hostnames
* Configuration values
* Policy strictness

### Why multiple environments?

Multiple environments demonstrate real-world platform maturity.

Benefits:

* Safer testing
* Controlled promotion
* Clear separation of concerns
* Better GitOps structure
* More realistic portfolio project

---

## 14. Repository Structure

### 14.1 Recommended Final Repository Model

For a production-style setup, use two repositories.

#### Repository 1: Application Repository

```text
kubepilot-app/
├── README.md
├── apps/
│   ├── frontend/
│   └── backend/
├── docker-compose.yml
├── .github/
│   └── workflows/
│       └── ci.yml
└── tests/
```

#### Repository 2: GitOps Repository

```text
kubepilot-gitops/
├── README.md
├── apps/
│   ├── frontend/
│   ├── backend/
│   └── postgres/
├── environments/
│   ├── dev/
│   ├── staging/
│   └── prod/
├── platform/
│   ├── argocd/
│   ├── kyverno/
│   ├── monitoring/
│   ├── logging/
│   └── alerting/
└── troubleshooting-labs/
```

### 14.2 Beginner-Friendly Single Repository Model

During initial development, everything can be kept in one repository.

```text
kubepilot-platform/
├── README.md
├── docs/
│   ├── architecture.md
│   ├── setup-guide.md
│   ├── deployment-flow.md
│   ├── security.md
│   ├── observability.md
│   └── troubleshooting.md
├── apps/
│   ├── frontend/
│   └── backend/
├── docker/
│   └── docker-compose.yml
├── k8s/
│   ├── base/
│   └── overlays/
│       ├── dev/
│       ├── staging/
│       └── prod/
├── gitops/
│   ├── argocd-apps/
│   └── environments/
│       ├── dev/
│       ├── staging/
│       └── prod/
├── platform/
│   ├── argocd/
│   ├── kyverno/
│   ├── monitoring/
│   ├── logging/
│   └── alerting/
├── troubleshooting-labs/
│   ├── 01-service-selector-mismatch/
│   ├── 02-wrong-targetport/
│   ├── 03-readiness-probe-failing/
│   ├── 04-networkpolicy-blocking/
│   ├── 05-imagepullbackoff/
│   ├── 06-crashloopbackoff/
│   ├── 07-argocd-outofsync/
│   └── 08-oomkilled/
└── tools/
    └── kubepilot-doctor/
```

For the first version, the single repository model is easier. Later, the project can be split into separate `kubepilot-app` and `kubepilot-gitops` repositories.

---

## 15. Technology Stack

| Area                 | Tool                                     |
| -------------------- | ---------------------------------------- |
| Frontend             | HTML, CSS, JavaScript, Nginx             |
| Backend              | Python Flask                             |
| Database             | PostgreSQL                               |
| Containerization     | Docker                                   |
| Local Development    | Docker Compose                           |
| Orchestration        | Kubernetes                               |
| Local Cluster        | kind or Minikube                         |
| CI/CD                | GitHub Actions                           |
| GitOps               | Argo CD                                  |
| Image Scanning       | Trivy                                    |
| Policy Enforcement   | Kyverno                                  |
| Monitoring           | Prometheus                               |
| Dashboards           | Grafana                                  |
| Logging              | Loki, Promtail                           |
| Alerting             | Alertmanager                             |
| Troubleshooting      | KubePilot Doctor                         |
| Packaging / Overlays | Kustomize initially, Helm later optional |

---

## 16. Implementation Roadmap

### Phase 1: Local Application

Goal:

Build and run the basic application locally.

Deliverables:

* Frontend app
* Backend API
* PostgreSQL database
* Dockerfiles
* Docker Compose setup
* Health and readiness endpoints

### Phase 2: Kubernetes Deployment

Goal:

Run the application inside Kubernetes.

Deliverables:

* Namespace
* Deployments
* Services
* ConfigMap
* Secret
* PVC
* Ingress
* Probes
* Resource requests and limits

### Phase 3: GitOps with Argo CD

Goal:

Deploy the application using GitOps.

Deliverables:

* GitOps folder structure
* Argo CD Application manifests
* Auto-sync configuration
* Manual sync demonstration
* OutOfSync demonstration
* Rollback demonstration

### Phase 4: CI/CD Automation

Goal:

Automate image build, scan, push, and GitOps update.

Deliverables:

* GitHub Actions workflow
* Docker image build
* Trivy image scan
* Image push to registry
* GitOps repo update

### Phase 5: Security Policies

Goal:

Enforce Kubernetes security standards.

Deliverables:

* Kyverno installation
* Policy to block latest tag
* Policy to require resource limits
* Policy to require non-root containers
* Policy to block privileged containers
* Policy testing examples

### Phase 6: Observability

Goal:

Add monitoring, logging, and alerting.

Deliverables:

* Prometheus
* Grafana
* Loki
* Promtail
* Alertmanager
* Dashboards
* Example alerts

### Phase 7: Troubleshooting Labs

Goal:

Create realistic Kubernetes failure scenarios.

Deliverables:

* Broken manifests
* Symptoms documentation
* Diagnosis commands
* Fixed manifests
* Explanation files

### Phase 8: KubePilot Doctor

Goal:

Build a troubleshooting assistant.

Deliverables:

* CLI or script
* Service checks
* Pod checks
* Endpoint checks
* Event checks
* Human-readable diagnosis output

### Phase 9: Portfolio Polish

Goal:

Make the project presentation-ready.

Deliverables:

* Professional README
* Architecture diagram
* Screenshots
* Demo video script
* LinkedIn launch post
* Resume bullet points
* Interview explanation

---

## 17. Final Architecture Summary

KubePilot demonstrates a complete cloud-native delivery platform.

It starts from a developer commit and ends with a secure, observable application running on Kubernetes.

The platform includes:

* Source code management with GitHub
* CI automation with GitHub Actions
* Image scanning with Trivy
* GitOps deployment with Argo CD
* Kubernetes runtime architecture
* Security policy enforcement with Kyverno
* Monitoring with Prometheus
* Visualization with Grafana
* Logging with Loki and Promtail
* Alerting with Alertmanager
* Troubleshooting automation with KubePilot Doctor

This architecture is designed to show practical, job-ready skills in Kubernetes, DevOps, DevSecOps, GitOps, and Platform Engineering.

---

## 18. Portfolio Positioning Statement

KubePilot can be described as:

> A production-style Internal Developer Platform built on Kubernetes that enables developers to deploy applications safely using GitOps, CI/CD automation, policy enforcement, observability, logging, alerting, and automated troubleshooting workflows.

This project is suitable for demonstrating real-world experience in:

* Kubernetes application deployment
* GitOps workflows
* DevSecOps practices
* Platform engineering concepts
* Observability and monitoring
* Kubernetes troubleshooting
* CI/CD automation
* Cloud-native architecture design
