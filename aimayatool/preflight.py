from __future__ import absolute_import

VALID_SEVERITIES = ("info", "warning", "error")


def preflight_result(category, message, severity="info", valid=True):
    """Return one deterministic, non-mutating preflight guidance record."""
    category = str(category or "").strip()
    message = str(message or "").strip()
    severity = str(severity or "").strip().lower()
    if not category:
        raise ValueError("Preflight category is required.")
    if not message:
        raise ValueError("Preflight message is required.")
    if severity not in VALID_SEVERITIES:
        raise ValueError("Unsupported preflight severity: {0}".format(severity))
    return {"valid": bool(valid), "severity": severity, "category": category, "message": message}


def preflight_ok(category="general", message="Ready."):
    return preflight_result(category, message, severity="info", valid=True)


def preflight_issue(category, message, severity="error"):
    return preflight_result(category, message, severity=severity, valid=False)
