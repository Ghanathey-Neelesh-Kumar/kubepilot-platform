
# GitOps with Argo CD

KubePilot uses Argo CD to deploy Kubernetes manifests from Git.

## GitOps Flow

```text
Developer changes code or manifests
        |
        v
GitHub repository
        |
        v
Argo CD watches repository
        |
        v
Argo CD compares desired state with live cluster
        |
        v
Kubernetes cluster is synced
