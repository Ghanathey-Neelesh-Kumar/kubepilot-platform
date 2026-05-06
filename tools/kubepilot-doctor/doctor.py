import argparse
import json
import subprocess
import sys
from typing import Any, Dict, List, Optional


class Colors:
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BLUE = "\033[94m"
    BOLD = "\033[1m"
    RESET = "\033[0m"


def run_kubectl(args: List[str]) -> Optional[Dict[str, Any]]:
    command = ["kubectl"] + args + ["-o", "json"]

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True
        )
        return json.loads(result.stdout)

    except subprocess.CalledProcessError as error:
        print_error(f"kubectl command failed: {' '.join(command)}")
        print(error.stderr.strip())
        return None

    except json.JSONDecodeError:
        print_error("Failed to parse kubectl JSON output.")
        return None


def run_kubectl_text(args: List[str]) -> Optional[str]:
    command = ["kubectl"] + args

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout

    except subprocess.CalledProcessError as error:
        print_error(f"kubectl command failed: {' '.join(command)}")
        print(error.stderr.strip())
        return None


def print_header(title: str):
    print()
    print(f"{Colors.BOLD}{Colors.BLUE}{title}{Colors.RESET}")
    print("=" * len(title))


def print_ok(message: str):
    print(f"{Colors.GREEN}? {message}{Colors.RESET}")


def print_warn(message: str):
    print(f"{Colors.YELLOW}??  {message}{Colors.RESET}")


def print_error(message: str):
    print(f"{Colors.RED}? {message}{Colors.RESET}")


def print_info(message: str):
    print(f"{Colors.BLUE}??  {message}{Colors.RESET}")


def get_items(resource: Dict[str, Any]) -> List[Dict[str, Any]]:
    return resource.get("items", []) if resource else []


def check_namespace_exists(namespace: str) -> bool:
    ns = run_kubectl(["get", "namespace", namespace])
    if ns:
        print_ok(f"Namespace '{namespace}' exists.")
        return True

    print_error(f"Namespace '{namespace}' does not exist.")
    return False


def check_pods(namespace: str):
    print_header("Pod Health")

    pods_data = run_kubectl(["get", "pods", "-n", namespace])
    pods = get_items(pods_data)

    if not pods:
        print_error(f"No pods found in namespace '{namespace}'.")
        return

    unhealthy_found = False

    for pod in pods:
        pod_name = pod["metadata"]["name"]
        phase = pod["status"].get("phase", "Unknown")
        conditions = pod["status"].get("conditions", [])
        container_statuses = pod["status"].get("containerStatuses", [])

        ready_condition = next(
            (c for c in conditions if c.get("type") == "Ready"),
            {}
        )

        is_ready = ready_condition.get("status") == "True"

        if phase == "Running" and is_ready:
            print_ok(f"Pod {pod_name} is Running and Ready.")
            continue

        unhealthy_found = True
        print_warn(f"Pod {pod_name} is not healthy. Phase={phase}, Ready={is_ready}")

        for status in container_statuses:
            container_name = status.get("name", "unknown")
            restart_count = status.get("restartCount", 0)
            state = status.get("state", {})
            last_state = status.get("lastState", {})

            if restart_count > 0:
                print_warn(
                    f"Container '{container_name}' has restarted {restart_count} time(s)."
                )

            waiting = state.get("waiting")
            terminated = state.get("terminated")
            last_terminated = last_state.get("terminated")

            if waiting:
                reason = waiting.get("reason", "Unknown")
                message = waiting.get("message", "")

                print_error(f"Container '{container_name}' is waiting: {reason}")

                if reason in ["ImagePullBackOff", "ErrImagePull"]:
                    print_info("Likely cause: image name/tag is wrong, image is private, or image is not loaded into kind.")
                    print_info("Useful checks:")
                    print("  kubectl describe pod " + pod_name + " -n " + namespace)
                    print("  docker images | grep kubepilot")
                    print("  kind load docker-image <image>:<tag> --name <cluster-name>")

                elif reason == "CrashLoopBackOff":
                    print_info("Likely cause: application starts and crashes repeatedly.")
                    print_info("Useful checks:")
                    print("  kubectl logs " + pod_name + " -n " + namespace)
                    print("  kubectl logs " + pod_name + " -n " + namespace + " --previous")

                elif reason == "CreateContainerConfigError":
                    print_info("Likely cause: missing ConfigMap, Secret, or invalid environment reference.")
                    print_info("Useful checks:")
                    print("  kubectl describe pod " + pod_name + " -n " + namespace)
                    print("  kubectl get configmap,secret -n " + namespace)

                if message:
                    print(f"  Message: {message}")

            if terminated:
                reason = terminated.get("reason", "Unknown")
                exit_code = terminated.get("exitCode", "unknown")

                print_error(
                    f"Container '{container_name}' terminated. Reason={reason}, ExitCode={exit_code}"
                )

                if reason == "OOMKilled":
                    print_info("Likely cause: container exceeded memory limit.")
                    print_info("Suggested fix: increase memory limit or reduce application memory usage.")

            if last_terminated:
                reason = last_terminated.get("reason", "Unknown")
                if reason == "OOMKilled":
                    print_error(f"Container '{container_name}' was previously OOMKilled.")
                    print_info("Suggested fix: inspect memory limits and application memory usage.")

    if not unhealthy_found:
        print_ok("All pods look healthy.")


def check_deployments(namespace: str):
    print_header("Deployment Health")

    deployments_data = run_kubectl(["get", "deployments", "-n", namespace])
    deployments = get_items(deployments_data)

    if not deployments:
        print_warn(f"No deployments found in namespace '{namespace}'.")
        return

    for deployment in deployments:
        name = deployment["metadata"]["name"]
        spec_replicas = deployment.get("spec", {}).get("replicas", 0)
        status = deployment.get("status", {})

        available = status.get("availableReplicas", 0)
        ready = status.get("readyReplicas", 0)
        updated = status.get("updatedReplicas", 0)

        if ready == spec_replicas and available == spec_replicas:
            print_ok(
                f"Deployment {name}: desired={spec_replicas}, ready={ready}, available={available}."
            )
        else:
            print_warn(
                f"Deployment {name}: desired={spec_replicas}, ready={ready}, available={available}, updated={updated}."
            )
            print_info("Useful checks:")
            print(f"  kubectl describe deployment {name} -n {namespace}")
            print(f"  kubectl rollout status deployment/{name} -n {namespace}")


def check_services_and_endpoints(namespace: str):
    print_header("Service and Endpoint Health")

    services_data = run_kubectl(["get", "services", "-n", namespace])
    endpoints_data = run_kubectl(["get", "endpoints", "-n", namespace])

    services = get_items(services_data)
    endpoints = get_items(endpoints_data)

    if not services:
        print_warn(f"No services found in namespace '{namespace}'.")
        return

    endpoint_map = {
        ep["metadata"]["name"]: ep
        for ep in endpoints
    }

    for service in services:
        service_name = service["metadata"]["name"]
        service_type = service["spec"].get("type", "ClusterIP")
        selector = service["spec"].get("selector", {})
        ports = service["spec"].get("ports", [])

        if not selector:
            print_warn(f"Service {service_name} has no selector. Type={service_type}")
            continue

        endpoint = endpoint_map.get(service_name)
        subsets = endpoint.get("subsets", []) if endpoint else []

        if not subsets:
            print_error(f"Service {service_name} has no endpoints.")
            print_info("Likely cause: selector mismatch or target pods are not Ready.")
            print_info("Useful checks:")
            print(f"  kubectl describe svc {service_name} -n {namespace}")
            print(f"  kubectl get pods -n {namespace} --show-labels")
            print(f"  kubectl get endpoints {service_name} -n {namespace}")
            continue

        endpoint_count = 0
        for subset in subsets:
            endpoint_count += len(subset.get("addresses", []))

        if endpoint_count > 0:
            port_summary = ", ".join(
                f"{p.get('port')}->{p.get('targetPort', p.get('port'))}"
                for p in ports
            )
            print_ok(
                f"Service {service_name} has {endpoint_count} endpoint(s). Ports: {port_summary}"
            )
        else:
            print_error(f"Service {service_name} has endpoint subsets but no ready addresses.")
            print_info("Likely cause: pods exist but are not Ready.")


def check_recent_events(namespace: str):
    print_header("Recent Warning Events")

    events_data = run_kubectl(["get", "events", "-n", namespace])
    events = get_items(events_data)

    warnings = [
        e for e in events
        if e.get("type") == "Warning"
    ]

    if not warnings:
        print_ok("No warning events found.")
        return

    for event in warnings[-10:]:
        reason = event.get("reason", "Unknown")
        message = event.get("message", "")
        involved = event.get("involvedObject", {})
        kind = involved.get("kind", "Unknown")
        name = involved.get("name", "Unknown")

        print_warn(f"{kind}/{name}: {reason}")
        if message:
            print(f"  {message}")


def check_argocd_app(app_name: Optional[str]):
    print_header("Argo CD Health")

    if app_name:
        app_data = run_kubectl(["get", "application", app_name, "-n", "argocd"])
        apps = [app_data] if app_data else []
    else:
        apps_data = run_kubectl(["get", "applications", "-n", "argocd"])
        apps = get_items(apps_data)

    if not apps:
        print_warn("No Argo CD Applications found.")
        return

    for app in apps:
        name = app["metadata"]["name"]
        status = app.get("status", {})
        sync_status = status.get("sync", {}).get("status", "Unknown")
        health_status = status.get("health", {}).get("status", "Unknown")

        if sync_status == "Synced" and health_status == "Healthy":
            print_ok(f"Argo CD app {name}: Synced and Healthy.")
        else:
            print_warn(
                f"Argo CD app {name}: Sync={sync_status}, Health={health_status}"
            )
            print_info("Useful checks:")
            print(f"  kubectl describe application {name} -n argocd")
            print(f"  kubectl get application {name} -n argocd -o yaml")


def check_namespace(namespace: str, argocd_app: Optional[str] = None):
    print_header("KubePilot Doctor Diagnosis")
    print_info(f"Namespace: {namespace}")

    if not check_namespace_exists(namespace):
        sys.exit(1)

    check_pods(namespace)
    check_deployments(namespace)
    check_services_and_endpoints(namespace)
    check_recent_events(namespace)

    if argocd_app:
        check_argocd_app(argocd_app)


def main():
    parser = argparse.ArgumentParser(
        description="KubePilot Doctor - Kubernetes troubleshooting helper"
    )

    subparsers = parser.add_subparsers(dest="command")

    check_parser = subparsers.add_parser(
        "check",
        help="Run health checks"
    )

    check_parser.add_argument(
        "target",
        choices=["namespace", "argocd"],
        help="Target type to check"
    )

    check_parser.add_argument(
        "name",
        nargs="?",
        help="Namespace name or Argo CD application name"
    )

    check_parser.add_argument(
        "--argocd-app",
        help="Optional Argo CD application name linked to this namespace"
    )

    args = parser.parse_args()

    if args.command == "check":
        if args.target == "namespace":
            if not args.name:
                print_error("Namespace name is required.")
                sys.exit(1)

            check_namespace(args.name, args.argocd_app)

        elif args.target == "argocd":
            check_argocd_app(args.name)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
