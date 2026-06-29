"""Mock Infrastructure Tools for the Multi-Agent On-Call Workshop.

These tools simulate real production infrastructure APIs.
In a real system, these would call Prometheus, Kubernetes, PagerDuty, Slack, etc.

Each tool is designed to be used by a specific agent in the multi-agent pipeline:
- Triage Agent: check_alert_history, get_runbook
- Diagnostics Agent: get_metrics, get_logs, check_dependencies
- Remediation Agent: restart_pod, scale_service, flush_cache, toggle_feature_flag
- Verification Agent: get_health_status, run_smoke_test
- Communications Agent: post_to_slack, create_incident_ticket, update_status_page
"""

import json
import random
from datetime import datetime, timedelta
from typing import Annotated

from pydantic import Field


# =============================================================================
# TRIAGE TOOLS
# =============================================================================

def check_alert_history(
    service_name: Annotated[str, Field(description="Name of the service that triggered the alert")],
) -> str:
    """Check if this service has had similar alerts in the past 7 days.
    Returns historical alert data and any known resolutions."""
    
    history = {
        "payment-api": {
            "recent_alerts": 3,
            "last_occurrence": "2 days ago",
            "last_resolution": "Restarted pod-3 due to memory leak in payment processing batch job",
            "recurring_pattern": True,
            "known_issue": "JIRA-4521: Memory leak in PaymentBatchProcessor - fix scheduled for next sprint",
        },
        "user-service": {
            "recent_alerts": 0,
            "last_occurrence": "23 days ago",
            "last_resolution": "Certificate rotation resolved TLS handshake failures",
            "recurring_pattern": False,
            "known_issue": None,
        },
        "order-service": {
            "recent_alerts": 1,
            "last_occurrence": "5 days ago",
            "last_resolution": "Traffic spike from marketing campaign - auto-scaled to 8 replicas",
            "recurring_pattern": False,
            "known_issue": None,
        },
        "notification-service": {
            "recent_alerts": 7,
            "last_occurrence": "6 hours ago",
            "last_resolution": "Upstream email provider rate limiting - toggled feature flag to use backup provider",
            "recurring_pattern": True,
            "known_issue": "JIRA-4590: Migrate to new email provider with higher rate limits",
        },
    }
    
    data = history.get(service_name, {
        "recent_alerts": 0,
        "last_occurrence": "Never",
        "last_resolution": "No previous incidents on record",
        "recurring_pattern": False,
        "known_issue": None,
    })
    
    return json.dumps(data, indent=2)


def get_runbook(
    incident_type: Annotated[str, Field(description="Type of incident: 'high_latency', 'error_spike', 'pod_crash', 'dependency_failure', 'certificate_expiry'")],
) -> str:
    """Retrieve the operational runbook for a given incident type.
    Returns step-by-step remediation instructions."""
    
    runbooks = {
        "high_latency": {
            "title": "High Latency Runbook",
            "severity_threshold": "p95 > 2000ms for 5 minutes",
            "steps": [
                "1. Check pod resource utilization (CPU/memory)",
                "2. Check dependency health (database, cache, upstream services)",
                "3. If memory > 85%: restart affected pods",
                "4. If CPU > 90%: scale horizontally (add 2 replicas)",
                "5. If dependency slow: check connection pool exhaustion",
                "6. Verify resolution with smoke tests",
            ],
            "escalation": "If not resolved in 15 minutes, page on-call SRE lead",
            "auto_remediation_allowed": True,
        },
        "error_spike": {
            "title": "Error Rate Spike Runbook",
            "severity_threshold": "5xx rate > 5% for 3 minutes",
            "steps": [
                "1. Identify error patterns in logs",
                "2. Check recent deployments (rollback if < 30 min old)",
                "3. Check external dependency health",
                "4. If single pod: restart that pod",
                "5. If all pods: check shared dependency (DB, cache)",
                "6. Toggle feature flags to disable problematic features",
            ],
            "escalation": "If not resolved in 10 minutes, page engineering lead",
            "auto_remediation_allowed": True,
        },
        "pod_crash": {
            "title": "Pod CrashLoopBackOff Runbook",
            "severity_threshold": "Pod restart count > 3 in 10 minutes",
            "steps": [
                "1. Check pod logs for crash reason (OOM, panic, config error)",
                "2. If OOMKilled: increase memory limit and restart",
                "3. If config error: check recent ConfigMap changes",
                "4. If panic: collect core dump, restart with previous image",
                "5. Scale up healthy replicas to maintain capacity",
            ],
            "escalation": "If crash cause unclear, page service owner",
            "auto_remediation_allowed": True,
        },
        "dependency_failure": {
            "title": "Dependency Failure Runbook",
            "severity_threshold": "Dependency error rate > 50% for 2 minutes",
            "steps": [
                "1. Identify which dependency is failing",
                "2. Check dependency's status page",
                "3. If database: check connection pool, run failover if needed",
                "4. If external API: toggle feature flag to use fallback/cache",
                "5. If cache (Redis): flush and reconnect",
                "6. Enable circuit breaker if available",
            ],
            "escalation": "Contact dependency team if external service",
            "auto_remediation_allowed": True,
        },
        "certificate_expiry": {
            "title": "Certificate Expiry Runbook",
            "severity_threshold": "TLS cert expires in < 24 hours or already expired",
            "steps": [
                "1. Identify which certificate is expiring/expired",
                "2. Check cert-manager logs for renewal failures",
                "3. Manual renewal requires human approval",
                "4. DO NOT auto-remediate - escalate immediately",
            ],
            "escalation": "Page security team immediately",
            "auto_remediation_allowed": False,
        },
    }
    
    data = runbooks.get(incident_type, {
        "title": "Unknown Incident Type",
        "steps": ["No runbook available. Escalate to on-call SRE."],
        "escalation": "Page on-call SRE immediately",
        "auto_remediation_allowed": False,
    })
    
    return json.dumps(data, indent=2)


# =============================================================================
# DIAGNOSTICS TOOLS
# =============================================================================

def get_metrics(
    service_name: Annotated[str, Field(description="Name of the service to get metrics for")],
    metric_type: Annotated[str, Field(description="Type of metric: 'cpu', 'memory', 'latency', 'error_rate', 'all'")] = "all",
) -> str:
    """Get current infrastructure metrics for a service.
    Returns CPU, memory, latency, error rates, and pod status."""
    
    metrics_db = {
        "payment-api": {
            "cpu_percent": 45.2,
            "memory_percent": 92.1,
            "memory_mb": 3891,
            "memory_limit_mb": 4096,
            "latency_p50_ms": 180,
            "latency_p95_ms": 2340,
            "latency_p99_ms": 4520,
            "error_rate_percent": 2.1,
            "request_rate_rpm": 1250,
            "pod_count": 4,
            "pods": [
                {"name": "payment-api-pod-1", "status": "Running", "cpu": 38.0, "memory_mb": 2100, "restarts": 0},
                {"name": "payment-api-pod-2", "status": "Running", "cpu": 41.0, "memory_mb": 2400, "restarts": 0},
                {"name": "payment-api-pod-3", "status": "Running", "cpu": 52.0, "memory_mb": 3891, "restarts": 4},
                {"name": "payment-api-pod-4", "status": "Running", "cpu": 49.0, "memory_mb": 2800, "restarts": 0},
            ],
        },
        "order-service": {
            "cpu_percent": 88.5,
            "memory_percent": 61.0,
            "memory_mb": 2500,
            "memory_limit_mb": 4096,
            "latency_p50_ms": 95,
            "latency_p95_ms": 3100,
            "latency_p99_ms": 8200,
            "error_rate_percent": 12.4,
            "request_rate_rpm": 3400,
            "pod_count": 3,
            "pods": [
                {"name": "order-service-pod-1", "status": "Running", "cpu": 91.0, "memory_mb": 2500, "restarts": 0},
                {"name": "order-service-pod-2", "status": "Running", "cpu": 89.0, "memory_mb": 2450, "restarts": 0},
                {"name": "order-service-pod-3", "status": "Running", "cpu": 86.0, "memory_mb": 2550, "restarts": 0},
            ],
        },
        "notification-service": {
            "cpu_percent": 22.0,
            "memory_percent": 35.0,
            "memory_mb": 1400,
            "memory_limit_mb": 4096,
            "latency_p50_ms": 450,
            "latency_p95_ms": 12000,
            "latency_p99_ms": 30000,
            "error_rate_percent": 67.3,
            "request_rate_rpm": 890,
            "pod_count": 2,
            "pods": [
                {"name": "notification-svc-pod-1", "status": "Running", "cpu": 20.0, "memory_mb": 1400, "restarts": 0},
                {"name": "notification-svc-pod-2", "status": "Running", "cpu": 24.0, "memory_mb": 1350, "restarts": 0},
            ],
        },
    }
    
    data = metrics_db.get(service_name, {
        "error": f"Service '{service_name}' not found in monitoring system",
        "available_services": list(metrics_db.keys()),
    })
    
    if metric_type != "all" and isinstance(data, dict) and "error" not in data:
        filtered = {k: v for k, v in data.items() if metric_type in k or k == "pods"}
        return json.dumps(filtered, indent=2)
    
    return json.dumps(data, indent=2)


def get_logs(
    service_name: Annotated[str, Field(description="Name of the service to get logs for")],
    severity: Annotated[str, Field(description="Log severity filter: 'ERROR', 'WARN', 'ALL'")] = "ERROR",
    minutes: Annotated[int, Field(description="How many minutes of logs to retrieve")] = 5,
) -> str:
    """Retrieve recent log entries for a service.
    Returns structured log entries with timestamps and context."""
    
    logs_db = {
        "payment-api": [
            {"timestamp": "2026-06-29T02:41:12Z", "level": "ERROR", "pod": "payment-api-pod-3", "msg": "java.lang.OutOfMemoryError: Java heap space", "context": "PaymentBatchProcessor.processQueue()"},
            {"timestamp": "2026-06-29T02:41:13Z", "level": "ERROR", "pod": "payment-api-pod-3", "msg": "Container killed due to OOM: current usage 4096Mi exceeds limit", "context": "kubelet"},
            {"timestamp": "2026-06-29T02:41:14Z", "level": "WARN", "pod": "payment-api-pod-3", "msg": "Pod restarted (restart count: 4)", "context": "kubelet"},
            {"timestamp": "2026-06-29T02:41:45Z", "level": "WARN", "pod": "payment-api-pod-3", "msg": "Memory usage climbing rapidly: 3.2GB -> 3.8GB in 60 seconds", "context": "memory-monitor"},
            {"timestamp": "2026-06-29T02:42:01Z", "level": "ERROR", "pod": "payment-api-pod-3", "msg": "Connection pool exhausted: 50/50 connections in use, 23 requests queued", "context": "HikariCP"},
            {"timestamp": "2026-06-29T02:42:15Z", "level": "WARN", "pod": "payment-api-pod-1", "msg": "Increased latency detected on /api/v1/payments endpoint: p95=2340ms", "context": "latency-monitor"},
        ],
        "order-service": [
            {"timestamp": "2026-06-29T02:40:01Z", "level": "ERROR", "pod": "order-service-pod-1", "msg": "Timeout waiting for response from payment-api: 5000ms exceeded", "context": "PaymentClient.charge()"},
            {"timestamp": "2026-06-29T02:40:02Z", "level": "ERROR", "pod": "order-service-pod-2", "msg": "Timeout waiting for response from payment-api: 5000ms exceeded", "context": "PaymentClient.charge()"},
            {"timestamp": "2026-06-29T02:40:05Z", "level": "ERROR", "pod": "order-service-pod-3", "msg": "Circuit breaker OPEN for payment-api: 10 failures in 60s", "context": "CircuitBreaker"},
            {"timestamp": "2026-06-29T02:40:10Z", "level": "WARN", "pod": "order-service-pod-1", "msg": "Falling back to async payment processing queue", "context": "PaymentClient"},
            {"timestamp": "2026-06-29T02:41:00Z", "level": "ERROR", "pod": "order-service-pod-1", "msg": "Request queue depth: 450 (threshold: 100)", "context": "RequestQueueMonitor"},
            {"timestamp": "2026-06-29T02:41:30Z", "level": "ERROR", "pod": "order-service-pod-2", "msg": "HTTP 503 returned to client: upstream payment-api unavailable", "context": "OrderController.createOrder()"},
        ],
        "notification-service": [
            {"timestamp": "2026-06-29T02:38:00Z", "level": "ERROR", "pod": "notification-svc-pod-1", "msg": "SMTP connection refused: smtp.emailprovider.com:587 - rate limit exceeded", "context": "EmailSender"},
            {"timestamp": "2026-06-29T02:38:01Z", "level": "ERROR", "pod": "notification-svc-pod-1", "msg": "HTTP 429 Too Many Requests from email provider API", "context": "EmailProviderClient"},
            {"timestamp": "2026-06-29T02:38:30Z", "level": "WARN", "pod": "notification-svc-pod-1", "msg": "Email queue backlog: 2,340 messages pending delivery", "context": "QueueMonitor"},
            {"timestamp": "2026-06-29T02:39:00Z", "level": "ERROR", "pod": "notification-svc-pod-2", "msg": "Failed to send order confirmation to customer@example.com: provider rate limited", "context": "NotificationHandler"},
            {"timestamp": "2026-06-29T02:40:00Z", "level": "WARN", "pod": "notification-svc-pod-1", "msg": "Backup email provider (backup-smtp) not configured - feature flag 'use_backup_email' is OFF", "context": "EmailProviderSelector"},
        ],
    }
    
    logs = logs_db.get(service_name, [
        {"timestamp": "now", "level": "INFO", "pod": "unknown", "msg": f"No logs found for service '{service_name}'", "context": "log-collector"}
    ])
    
    if severity != "ALL":
        logs = [log for log in logs if log["level"] == severity or (severity == "ERROR" and log["level"] == "ERROR")]
    
    return json.dumps(logs[:10], indent=2)


def check_dependencies(
    service_name: Annotated[str, Field(description="Name of the service to check dependencies for")],
) -> str:
    """Check the health status of all dependencies for a given service.
    Returns dependency map with current health status."""
    
    deps_db = {
        "payment-api": {
            "dependencies": [
                {"name": "postgres-primary", "type": "database", "status": "healthy", "latency_ms": 12, "connection_pool": "48/50 used"},
                {"name": "redis-cache", "type": "cache", "status": "healthy", "latency_ms": 2, "hit_rate": "94%"},
                {"name": "stripe-api", "type": "external_api", "status": "healthy", "latency_ms": 180, "error_rate": "0.1%"},
                {"name": "rabbitmq", "type": "message_queue", "status": "healthy", "queue_depth": 12, "consumers": 4},
            ],
            "notes": "Connection pool near exhaustion on postgres-primary",
        },
        "order-service": {
            "dependencies": [
                {"name": "payment-api", "type": "internal_service", "status": "degraded", "latency_ms": 2340, "error_rate": "12.4%"},
                {"name": "postgres-orders", "type": "database", "status": "healthy", "latency_ms": 8, "connection_pool": "12/50 used"},
                {"name": "inventory-service", "type": "internal_service", "status": "healthy", "latency_ms": 45, "error_rate": "0.0%"},
                {"name": "redis-sessions", "type": "cache", "status": "healthy", "latency_ms": 1, "hit_rate": "98%"},
            ],
            "notes": "payment-api is degraded - causing cascading failures in order processing",
        },
        "notification-service": {
            "dependencies": [
                {"name": "email-provider-api", "type": "external_api", "status": "rate_limited", "latency_ms": 12000, "error_rate": "67%"},
                {"name": "backup-email-provider", "type": "external_api", "status": "unconfigured", "latency_ms": None, "error_rate": None},
                {"name": "postgres-notifications", "type": "database", "status": "healthy", "latency_ms": 5, "connection_pool": "8/50 used"},
                {"name": "rabbitmq", "type": "message_queue", "status": "healthy", "queue_depth": 2340, "consumers": 2},
            ],
            "notes": "Primary email provider is rate limiting. Backup provider feature flag is OFF.",
        },
    }
    
    data = deps_db.get(service_name, {"error": f"No dependency map found for '{service_name}'"})
    return json.dumps(data, indent=2)


# =============================================================================
# REMEDIATION TOOLS
# =============================================================================

def restart_pod(
    service_name: Annotated[str, Field(description="Name of the service")],
    pod_name: Annotated[str, Field(description="Specific pod to restart, e.g. 'payment-api-pod-3'")],
) -> str:
    """Restart a specific pod. Returns the new pod status after restart.
    This performs a graceful restart with a 30-second drain period."""
    
    return json.dumps({
        "action": "restart_pod",
        "pod": pod_name,
        "service": service_name,
        "status": "success",
        "details": {
            "old_pod_terminated": True,
            "new_pod_status": "Running",
            "new_pod_ready": True,
            "restart_duration_seconds": 18,
            "memory_after_restart_mb": 512,
            "connections_drained": 23,
        },
        "message": f"Pod {pod_name} restarted successfully. Memory reset from 3891MB to 512MB.",
    }, indent=2)


def scale_service(
    service_name: Annotated[str, Field(description="Name of the service to scale")],
    target_replicas: Annotated[int, Field(description="Desired number of replicas")],
) -> str:
    """Scale a service to the specified number of replicas.
    Returns the scaling status and estimated time to ready."""
    
    return json.dumps({
        "action": "scale_service",
        "service": service_name,
        "previous_replicas": 3,
        "target_replicas": target_replicas,
        "status": "scaling_in_progress",
        "new_pods_ready": target_replicas - 1,
        "estimated_ready_seconds": 45,
        "message": f"Scaling {service_name} from 3 to {target_replicas} replicas. {target_replicas - 3} new pods starting.",
    }, indent=2)


def flush_cache(
    cache_name: Annotated[str, Field(description="Name of the cache to flush, e.g. 'redis-cache'")],
) -> str:
    """Flush a cache instance. Use with caution - causes temporary cache miss spike."""
    
    return json.dumps({
        "action": "flush_cache",
        "cache": cache_name,
        "status": "success",
        "keys_evicted": 14523,
        "message": f"Cache '{cache_name}' flushed. Expect elevated latency for 2-3 minutes while cache warms up.",
        "warning": "Cache hit rate will drop temporarily. Monitor latency.",
    }, indent=2)


def toggle_feature_flag(
    flag_name: Annotated[str, Field(description="Name of the feature flag to toggle, e.g. 'use_backup_email'")],
    enabled: Annotated[bool, Field(description="Whether to enable (True) or disable (False) the flag")],
) -> str:
    """Toggle a feature flag. Used for graceful degradation and failover."""
    
    return json.dumps({
        "action": "toggle_feature_flag",
        "flag": flag_name,
        "new_state": "enabled" if enabled else "disabled",
        "status": "success",
        "propagation_time_seconds": 5,
        "message": f"Feature flag '{flag_name}' set to {'enabled' if enabled else 'disabled'}. Changes propagate within 5 seconds.",
        "affected_services": ["notification-service"] if "email" in flag_name else ["unknown"],
    }, indent=2)


# =============================================================================
# VERIFICATION TOOLS
# =============================================================================

def get_health_status(
    service_name: Annotated[str, Field(description="Name of the service to check health for")],
) -> str:
    """Check current health status of a service after remediation.
    Returns comprehensive health check results."""
    
    # Simulates post-remediation state (things are better now)
    return json.dumps({
        "service": service_name,
        "overall_status": "healthy",
        "checks": {
            "liveness": "passing",
            "readiness": "passing",
            "latency_p95_ms": 280,
            "error_rate_percent": 0.3,
            "cpu_percent": 42.0,
            "memory_percent": 48.0,
        },
        "message": f"Service {service_name} is healthy. All checks passing.",
    }, indent=2)


def run_smoke_test(
    service_name: Annotated[str, Field(description="Name of the service to run smoke tests against")],
) -> str:
    """Run a suite of smoke tests against a service to verify it's working correctly.
    Returns test results with pass/fail details."""
    
    tests = {
        "payment-api": [
            {"test": "POST /api/v1/payments - create payment", "status": "pass", "duration_ms": 245},
            {"test": "GET /api/v1/payments/:id - get payment", "status": "pass", "duration_ms": 32},
            {"test": "POST /api/v1/payments/:id/refund - refund", "status": "pass", "duration_ms": 310},
            {"test": "GET /health - health check", "status": "pass", "duration_ms": 5},
        ],
        "order-service": [
            {"test": "POST /api/v1/orders - create order", "status": "pass", "duration_ms": 180},
            {"test": "GET /api/v1/orders/:id - get order", "status": "pass", "duration_ms": 28},
            {"test": "PUT /api/v1/orders/:id/cancel - cancel", "status": "pass", "duration_ms": 95},
            {"test": "GET /health - health check", "status": "pass", "duration_ms": 3},
        ],
        "notification-service": [
            {"test": "POST /api/v1/notify/email - send email", "status": "pass", "duration_ms": 520},
            {"test": "POST /api/v1/notify/sms - send sms", "status": "pass", "duration_ms": 180},
            {"test": "GET /api/v1/notify/queue-depth - check queue", "status": "pass", "duration_ms": 8},
            {"test": "GET /health - health check", "status": "pass", "duration_ms": 4},
        ],
    }
    
    service_tests = tests.get(service_name, [
        {"test": "GET /health", "status": "pass", "duration_ms": 5}
    ])
    
    all_pass = all(t["status"] == "pass" for t in service_tests)
    
    return json.dumps({
        "service": service_name,
        "tests_run": len(service_tests),
        "tests_passed": sum(1 for t in service_tests if t["status"] == "pass"),
        "tests_failed": sum(1 for t in service_tests if t["status"] != "pass"),
        "overall": "PASS" if all_pass else "FAIL",
        "results": service_tests,
        "message": f"All {len(service_tests)} smoke tests passing for {service_name}." if all_pass else "Some tests failed.",
    }, indent=2)


# =============================================================================
# COMMUNICATIONS TOOLS
# =============================================================================

def post_to_slack(
    channel: Annotated[str, Field(description="Slack channel to post to, e.g. '#incidents' or '#engineering'")],
    message: Annotated[str, Field(description="The incident message/update to post")],
    severity: Annotated[str, Field(description="Severity level for formatting: 'critical', 'warning', 'resolved'")] = "warning",
) -> str:
    """Post an incident update to a Slack channel.
    Returns confirmation of the posted message."""
    
    emoji = {"critical": "🔴", "warning": "🟡", "resolved": "🟢"}.get(severity, "⚪")
    
    return json.dumps({
        "action": "post_to_slack",
        "channel": channel,
        "status": "sent",
        "message_preview": f"{emoji} {message[:100]}...",
        "timestamp": datetime.now().isoformat(),
        "thread_id": "incident-2026-06-29-0241",
    }, indent=2)


def create_incident_ticket(
    title: Annotated[str, Field(description="Incident ticket title")],
    description: Annotated[str, Field(description="Detailed description of the incident and resolution")],
    severity: Annotated[str, Field(description="Ticket severity: 'P1', 'P2', 'P3'")] = "P2",
    service: Annotated[str, Field(description="Affected service name")] = "unknown",
) -> str:
    """Create a post-incident ticket for tracking and post-mortem.
    Returns the ticket ID and URL."""
    
    ticket_id = f"INC-{random.randint(10000, 99999)}"
    
    return json.dumps({
        "action": "create_incident_ticket",
        "ticket_id": ticket_id,
        "title": title,
        "severity": severity,
        "service": service,
        "status": "created",
        "url": f"https://jira.company.com/browse/{ticket_id}",
        "assigned_to": "on-call-sre-team",
        "message": f"Incident ticket {ticket_id} created successfully.",
    }, indent=2)


def update_status_page(
    service_name: Annotated[str, Field(description="Service to update status for")],
    status: Annotated[str, Field(description="New status: 'operational', 'degraded', 'partial_outage', 'major_outage'")],
    message: Annotated[str, Field(description="Public-facing status message")],
) -> str:
    """Update the public status page for a service.
    Returns confirmation of the status page update."""
    
    return json.dumps({
        "action": "update_status_page",
        "service": service_name,
        "new_status": status,
        "message": message,
        "status": "updated",
        "url": f"https://status.company.com/services/{service_name}",
        "public_message_posted": True,
    }, indent=2)


def escalate_to_human(
    reason: Annotated[str, Field(description="Why automated remediation cannot handle this")],
    service_name: Annotated[str, Field(description="Affected service")],
    findings: Annotated[str, Field(description="Summary of diagnostics findings so far")],
) -> str:
    """Escalate an incident to a human operator when automated remediation is not possible.
    Pages the on-call engineer with full context."""
    
    return json.dumps({
        "action": "escalate_to_human",
        "status": "paged",
        "on_call_engineer": "Sarah Chen (SRE Lead)",
        "page_method": "PagerDuty + SMS + Phone",
        "context_provided": {
            "service": service_name,
            "reason": reason,
            "diagnostics_summary": findings,
        },
        "message": "On-call engineer paged with full incident context. ETA response: 5-10 minutes.",
    }, indent=2)
