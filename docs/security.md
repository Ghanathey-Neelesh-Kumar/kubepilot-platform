# Security Policy

KubePilot is a portfolio DevSecOps project that demonstrates Kubernetes security controls.

## Security Controls Implemented

- Non-root containers
- Dropped Linux capabilities
- Resource requests and limits
- Trivy container scanning
- Kyverno admission policies
- NetworkPolicy troubleshooting lab
- Kubernetes Secrets for database credentials

## Known Limitations

- Secrets are stored as Kubernetes Secrets for local simulation.
- External Secrets or Sealed Secrets are planned for future improvement.
- Trivy currently reports vulnerabilities in dev but does not block the pipeline.
