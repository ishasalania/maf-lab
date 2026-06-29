"""Mock Infrastructure Tools for MAF Workshop.

These simulate production infrastructure APIs (Prometheus, K8s, PagerDuty, Slack).
Uses MAF's @tool decorator with proper type annotations and approval_mode.

Tools requiring human approval before execution are marked with
approval_mode="always_require" — this integrates with MAF's HITL workflow pattern.
"""

from typing import Annotated

from agent_framework import tool

# =============================================================================
# TRIAGE TOOLS (safe, read-only)
# =============================================================================


@tool(approval_mode="never_require")
def check_alert_history(
    service: Annotated[str, "The service name to check alert history for"],
) -> dict:
    """Check recent alert history for a service. Returns past incidents and patterns."""
    histories = {
        "payment-api": {
            "total_alerts_7d": 5,
            "recurring": True,
            "pattern": "Memory spikes every 6h correlating with batch job",
            "last_incident": "2024-11-13T14:22:00Z",
            "last_resolution": "Pod restart resolved — memory leak in connection pool",
            "mttr_minutes": 12,
        },
        "order-service": {
            "total_alerts_7d": 1,
            "recurring": False,
            "pattern": "No recurring pattern detected",
            "last_incident": "2024-11-10T08:15:00Z",
            "last_resolution": "Upstream dependency timeout — resolved by scaling",
            "mttr_minutes": 25,
        },
        "notification-service": {
            "total_alerts_7d": 0,
            "recurring": False,
            "pattern": "No prior alerts",
            "last_incident": None,
            "last_resolution": None,
            "mttr_minutes": None,
        },
    }
    return histories.get(service, {"total_alerts_7d": 0, "recurring": False, "pattern": "Unknown service"})


@tool(approval_mode="never_require")
def get_runbook(
    incident_type: Annotated[str, "The type of incident (e.g. 'high_latency', 'error_rate', 'oom')"],
) -> dict:
    """Retrieve the operations runbook for this incident type."""
    runbooks = {
        "high_latency": {
            "playbook_id": "RB-204",
            "title": "High Latency Response",
            "auto_remediation_allowed": True,
            "steps": [
                "1. Check metrics for resource exhaustion (CPU/Memory/Connections)",
                "2. Identify affected pods via logs",
                "3. If OOM: restart affected pod",
                "4. If connection pool: flush cache and restart",
                "5. Verify health check passes within 60s",
            ],
            "escalation_threshold_minutes": 15,
        },
        "error_rate": {
            "playbook_id": "RB-301",
            "title": "Error Rate Spike Response",
            "auto_remediation_allowed": True,
            "steps": [
                "1. Check dependency health (downstream services)",
                "2. Identify error patterns in logs",
                "3. If cascading: scale up replicas",
                "4. If dependency down: toggle circuit breaker",
                "5. Monitor error rate for 2 minutes",
            ],
            "escalation_threshold_minutes": 10,
        },
        "oom": {
            "playbook_id": "RB-150",
            "title": "Out-of-Memory Response",
            "auto_remediation_allowed": True,
            "steps": [
                "1. Identify pod with OOM kill",
                "2. Check memory profile in metrics",
                "3. Restart affected pod",
                "4. If recurring within 1h: scale horizontally",
            ],
            "escalation_threshold_minutes": 5,
        },
        "rate_limiting": {
            "playbook_id": "RB-410",
            "title": "Rate Limiting Response",
            "auto_remediation_allowed": False,
            "steps": [
                "1. Identify rate-limited provider",
                "2. Check current usage vs. quota",
                "3. Toggle feature flag to fallback provider",
                "4. Notify vendor relations team",
            ],
            "escalation_threshold_minutes": 20,
        },
    }
    return runbooks.get(incident_type, {"playbook_id": "NONE", "title": "No runbook found", "auto_remediation_allowed": False, "steps": ["Escalate to on-call engineer"]})


# =============================================================================
# DIAGNOSTICS TOOLS (safe, read-only)
# =============================================================================


@tool(approval_mode="never_require")
def get_metrics(
    service: Annotated[str, "The service to query metrics for"],
    metric_type: Annotated[str, "Type of metric: 'cpu', 'memory', 'latency', 'error_rate', 'connections'"],
) -> dict:
    """Query Prometheus-style metrics for a service. Returns current and historical values."""
    metrics_db = {
        ("payment-api", "memory"): {
            "current_mb": 1847,
            "limit_mb": 2048,
            "utilization_pct": 90.2,
            "trend": "increasing",
            "pods": {
                "payment-api-pod-1": {"memory_mb": 512, "status": "healthy"},
                "payment-api-pod-2": {"memory_mb": 489, "status": "healthy"},
                "payment-api-pod-3": {"memory_mb": 846, "status": "OOMKilled"},
            },
        },
        ("payment-api", "latency"): {
            "p50_ms": 45,
            "p95_ms": 890,
            "p99_ms": 32000,
            "baseline_p99_ms": 200,
            "spike_factor": 160.0,
        },
        ("payment-api", "cpu"): {
            "current_pct": 34.5,
            "limit_pct": 80.0,
            "status": "normal",
        },
        ("payment-api", "connections"): {
            "active": 847,
            "max_pool": 100,
            "waiting": 312,
            "status": "pool_exhausted",
        },
        ("order-service", "error_rate"): {
            "current_pct": 23.4,
            "baseline_pct": 0.1,
            "spike_factor": 234.0,
            "top_errors": [
                {"code": 503, "count": 1247, "message": "Service Unavailable"},
                {"code": 504, "count": 892, "message": "Gateway Timeout"},
            ],
        },
        ("order-service", "latency"): {
            "p50_ms": 120,
            "p95_ms": 4500,
            "p99_ms": 12000,
            "baseline_p99_ms": 300,
            "spike_factor": 40.0,
        },
        ("notification-service", "error_rate"): {
            "current_pct": 67.2,
            "baseline_pct": 0.5,
            "spike_factor": 134.4,
            "top_errors": [
                {"code": 429, "count": 8934, "message": "Too Many Requests"},
            ],
        },
    }
    result = metrics_db.get((service, metric_type))
    if result:
        return {"service": service, "metric": metric_type, **result}
    return {"service": service, "metric": metric_type, "status": "no_data", "note": "Metric not available for this service"}


@tool(approval_mode="never_require")
def get_logs(
    service: Annotated[str, "The service to pull logs from"],
    severity: Annotated[str, "Log severity filter: 'error', 'warn', 'all'"] = "error",
) -> dict:
    """Pull recent logs from a service filtered by severity."""
    logs_db = {
        "payment-api": {
            "error": [
                {"timestamp": "2024-11-15T03:41:52Z", "level": "ERROR", "message": "java.lang.OutOfMemoryError: Java heap space", "pod": "payment-api-pod-3"},
                {"timestamp": "2024-11-15T03:41:53Z", "level": "ERROR", "message": "Connection pool exhausted — 312 requests waiting", "pod": "payment-api-pod-3"},
                {"timestamp": "2024-11-15T03:41:55Z", "level": "ERROR", "message": "Health check failed: /ready returned 503", "pod": "payment-api-pod-3"},
            ],
            "warn": [
                {"timestamp": "2024-11-15T03:40:00Z", "level": "WARN", "message": "Memory usage at 85% — approaching limit", "pod": "payment-api-pod-3"},
                {"timestamp": "2024-11-15T03:38:00Z", "level": "WARN", "message": "GC pause exceeded 500ms", "pod": "payment-api-pod-3"},
            ],
        },
        "order-service": {
            "error": [
                {"timestamp": "2024-11-15T03:42:01Z", "level": "ERROR", "message": "Upstream payment-api returned 503 — circuit breaker OPEN", "pod": "order-service-pod-1"},
                {"timestamp": "2024-11-15T03:42:01Z", "level": "ERROR", "message": "Timeout waiting for payment-api (30000ms exceeded)", "pod": "order-service-pod-2"},
                {"timestamp": "2024-11-15T03:42:03Z", "level": "ERROR", "message": "Cascading failure: 1247 requests queued, backpressure applied", "pod": "order-service-pod-1"},
            ],
            "warn": [
                {"timestamp": "2024-11-15T03:41:55Z", "level": "WARN", "message": "Retry budget exhausted for payment-api calls", "pod": "order-service-pod-2"},
            ],
        },
        "notification-service": {
            "error": [
                {"timestamp": "2024-11-15T03:42:10Z", "level": "ERROR", "message": "SendGrid API returned 429: Rate limit exceeded (100/min)", "pod": "notification-svc-pod-1"},
                {"timestamp": "2024-11-15T03:42:12Z", "level": "ERROR", "message": "Email queue depth: 8934, processing rate: 0/min", "pod": "notification-svc-pod-1"},
            ],
            "warn": [
                {"timestamp": "2024-11-15T03:40:00Z", "level": "WARN", "message": "Approaching SendGrid rate limit (89/100 per minute)", "pod": "notification-svc-pod-1"},
            ],
        },
    }
    service_logs = logs_db.get(service, {"error": [], "warn": []})
    if severity == "all":
        return {"service": service, "logs": service_logs["error"] + service_logs["warn"]}
    return {"service": service, "logs": service_logs.get(severity, [])}


@tool(approval_mode="never_require")
def check_dependencies(
    service: Annotated[str, "The service to check dependency health for"],
) -> dict:
    """Check the health of a service's upstream and downstream dependencies."""
    deps = {
        "payment-api": {
            "upstream": [
                {"service": "order-service", "status": "degraded", "note": "Sending high volume of retries"},
                {"service": "checkout-ui", "status": "healthy", "note": ""},
            ],
            "downstream": [
                {"service": "postgres-primary", "status": "healthy", "note": "Connections normal"},
                {"service": "redis-cache", "status": "healthy", "note": "Hit rate 94%"},
                {"service": "stripe-api", "status": "healthy", "note": "Latency normal"},
            ],
        },
        "order-service": {
            "upstream": [
                {"service": "checkout-ui", "status": "healthy", "note": ""},
                {"service": "mobile-app", "status": "healthy", "note": ""},
            ],
            "downstream": [
                {"service": "payment-api", "status": "unhealthy", "note": "503 errors, circuit breaker OPEN"},
                {"service": "inventory-service", "status": "healthy", "note": ""},
                {"service": "notification-service", "status": "degraded", "note": "Slow responses"},
            ],
        },
        "notification-service": {
            "upstream": [
                {"service": "order-service", "status": "healthy", "note": ""},
                {"service": "user-service", "status": "healthy", "note": ""},
            ],
            "downstream": [
                {"service": "sendgrid-api", "status": "rate_limited", "note": "429 responses, quota: 100/min"},
                {"service": "twilio-api", "status": "healthy", "note": "SMS fallback available"},
            ],
        },
    }
    return deps.get(service, {"upstream": [], "downstream": [], "note": "Unknown service"})


# =============================================================================
# REMEDIATION TOOLS (dangerous — require approval in HITL mode)
# =============================================================================


@tool(approval_mode="always_require")
def restart_pod(
    service: Annotated[str, "The service that owns the pod"],
    pod_id: Annotated[str, "The specific pod ID to restart (e.g. 'payment-api-pod-3')"],
    reason: Annotated[str, "Reason for restart — logged for audit trail"],
) -> dict:
    """Restart a specific pod. This causes brief downtime for requests routed to this pod."""
    return {
        "action": "restart_pod",
        "service": service,
        "pod": pod_id,
        "status": "success",
        "downtime_seconds": 8,
        "message": f"Pod {pod_id} restarted successfully. New instance healthy after 8s.",
    }


@tool(approval_mode="always_require")
def scale_service(
    service: Annotated[str, "The service to scale"],
    target_replicas: Annotated[int, "The desired number of replicas"],
    reason: Annotated[str, "Reason for scaling — logged for audit trail"],
) -> dict:
    """Scale a service to a target replica count. Affects resource allocation and cost."""
    current = {"payment-api": 3, "order-service": 4, "notification-service": 2}
    return {
        "action": "scale_service",
        "service": service,
        "previous_replicas": current.get(service, 2),
        "target_replicas": target_replicas,
        "status": "success",
        "message": f"Scaled {service} to {target_replicas} replicas. New pods healthy.",
        "estimated_cost_increase_pct": (target_replicas - current.get(service, 2)) * 15,
    }


@tool(approval_mode="always_require")
def flush_cache(
    service: Annotated[str, "The service whose cache to flush"],
    cache_type: Annotated[str, "Cache type: 'redis', 'local', 'cdn'"],
) -> dict:
    """Flush a service's cache. May cause temporary latency spike as cache warms up."""
    return {
        "action": "flush_cache",
        "service": service,
        "cache_type": cache_type,
        "status": "success",
        "entries_cleared": 12847,
        "message": f"Cache flushed for {service}. Expect elevated latency for 30-60s during warm-up.",
    }


@tool(approval_mode="always_require")
def toggle_feature_flag(
    flag_name: Annotated[str, "The feature flag to toggle (e.g. 'use_sendgrid', 'circuit_breaker_order_svc')"],
    enabled: Annotated[bool, "Whether to enable (True) or disable (False) the flag"],
    reason: Annotated[str, "Reason for toggling — logged for audit trail"],
) -> dict:
    """Toggle a feature flag. This immediately affects all traffic to the service."""
    return {
        "action": "toggle_feature_flag",
        "flag": flag_name,
        "new_state": "enabled" if enabled else "disabled",
        "status": "success",
        "affected_services": ["notification-service"] if "sendgrid" in flag_name else ["order-service"],
        "message": f"Flag '{flag_name}' set to {'enabled' if enabled else 'disabled'}. Change propagated in <1s.",
    }


@tool(approval_mode="always_require")
def escalate_to_human(
    service: Annotated[str, "The affected service"],
    severity: Annotated[str, "Current severity assessment"],
    summary: Annotated[str, "Brief summary of the situation for the on-call engineer"],
) -> dict:
    """Escalate to on-call engineer via PagerDuty. Use when auto-remediation is not safe."""
    return {
        "action": "escalate",
        "service": service,
        "paged_engineer": "oncall@company.com",
        "status": "acknowledged",
        "message": f"Escalation sent. On-call engineer acknowledged within 2 minutes.",
    }


# =============================================================================
# VERIFICATION TOOLS (safe, read-only)
# =============================================================================


@tool(approval_mode="never_require")
def get_health_status(
    service: Annotated[str, "The service to health-check"],
) -> dict:
    """Run health check against a service's /ready and /live endpoints."""
    # Simulates post-remediation health (assumes fix was applied)
    return {
        "service": service,
        "ready": True,
        "live": True,
        "response_time_ms": 12,
        "checks": {
            "database": "pass",
            "cache": "pass",
            "downstream_deps": "pass",
        },
        "message": f"All health checks passing for {service}.",
    }


@tool(approval_mode="never_require")
def run_smoke_test(
    service: Annotated[str, "The service to run smoke tests against"],
    test_suite: Annotated[str, "Which test suite: 'basic', 'full', 'critical_path'"] = "critical_path",
) -> dict:
    """Run smoke tests against a service to verify it's functioning correctly."""
    suites = {
        "basic": {"tests_run": 5, "passed": 5, "failed": 0, "duration_s": 3},
        "critical_path": {"tests_run": 12, "passed": 12, "failed": 0, "duration_s": 8},
        "full": {"tests_run": 47, "passed": 46, "failed": 1, "duration_s": 45},
    }
    result = suites.get(test_suite, suites["basic"])
    return {
        "service": service,
        "suite": test_suite,
        **result,
        "status": "pass" if result["failed"] == 0 else "fail",
        "message": f"Smoke tests {'all passed' if result['failed'] == 0 else 'FAILED — see details'}.",
    }


# =============================================================================
# COMMUNICATIONS TOOLS (side-effect, but non-destructive)
# =============================================================================


@tool(approval_mode="never_require")
def post_to_slack(
    channel: Annotated[str, "Slack channel (e.g. '#incidents', '#platform-team')"],
    message: Annotated[str, "The message to post"],
    severity: Annotated[str, "Message severity for formatting: 'critical', 'warning', 'resolved'"],
) -> dict:
    """Post a message to a Slack channel."""
    return {
        "action": "slack_post",
        "channel": channel,
        "status": "sent",
        "thread_id": "T-20241115-0342",
        "message": f"Posted to {channel}: {message[:80]}...",
    }


@tool(approval_mode="never_require")
def create_incident_ticket(
    title: Annotated[str, "Ticket title"],
    severity: Annotated[str, "Severity: P1/P2/P3/P4"],
    description: Annotated[str, "Detailed description of the incident"],
    root_cause: Annotated[str, "Identified root cause"],
    resolution: Annotated[str, "Steps taken to resolve"],
) -> dict:
    """Create an incident ticket in the tracking system (e.g., Jira/ServiceNow)."""
    return {
        "action": "create_ticket",
        "ticket_id": "INC-2024-0893",
        "title": title,
        "severity": severity,
        "status": "created",
        "assigned_to": "platform-oncall",
        "message": f"Ticket INC-2024-0893 created: {title}",
    }


@tool(approval_mode="never_require")
def update_status_page(
    service: Annotated[str, "The affected service"],
    status: Annotated[str, "Status: 'investigating', 'identified', 'monitoring', 'resolved'"],
    message: Annotated[str, "Public-facing status message"],
) -> dict:
    """Update the public status page for customers."""
    return {
        "action": "status_page_update",
        "service": service,
        "status": status,
        "published": True,
        "message": f"Status page updated: {service} — {status}",
    }
