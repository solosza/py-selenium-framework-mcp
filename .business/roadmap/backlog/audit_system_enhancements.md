# Audit System Enhancements

**Status:** Idea
**Created:** 2026-01-15
**Target Version:** v1.2 (Retention Policy), v2.0 (Advanced Analytics)
**Effort:** v1.2: 3-4 hours, v2.0: 8-10 hours
**Impact:** Medium (compliance), High (enterprise)

---

## Context

The audit system provides progressive audit trail capturing all tool calls, decisions, and state changes. Currently implemented via PostToolUse hook writing to `tests/_audit/audit_log_*.json`.

While functional, it lacks:
- Retention policies
- Advanced analytics
- Export capabilities
- Compliance reporting

---

## Problem

**Current State:**
- ✅ JSON logs written after each quality gate pass
- ✅ Captures: tool calls, inputs, outputs, timestamps, workflow ID
- ✅ PostToolUse hook automation
- ❌ No retention policy (logs accumulate indefinitely)
- ❌ No analytics (can't query patterns, trends)
- ❌ No export formats (compliance needs CSV, PDF)
- ❌ No compliance reporting (EU AI Act requires 3-year retention)

**What Works:**
```json
{
  "timestamp": "2026-01-14T23:13:11.156117Z",
  "workflow_id": "parabank10_20260114",
  "type": "mcp_tool",
  "tool_name": "qg_preflight",
  "args": {...},
  "result": {...},
  "gate_status": "PASS"
}
```

**What's Missing:**
- Retention policy (delete logs older than X days)
- Query interface (find all failures in last 30 days)
- Export to CSV, PDF, HTML for compliance
- Aggregation (success rate per step, avg execution time)

---

## Proposed Enhancements

### v1.2: Retention Policy + Basic Cleanup

**Features:**
- Configurable retention period (default: 90 days for dev, 3 years for enterprise)
- Automated cleanup job (runs on startup, deletes old logs)
- Archive to compressed storage before deletion
- Configuration via environment variable: `AUDIT_RETENTION_DAYS`

**Implementation:**
```python
# mcp_server/tools/audit/retention.py
class AuditRetentionManager:
    def __init__(self, retention_days: int = 90):
        self.retention_days = retention_days

    def cleanup_old_logs(self):
        """Delete logs older than retention_days, archive first."""
        cutoff_date = datetime.now() - timedelta(days=self.retention_days)

        for log_file in self._find_old_logs(cutoff_date):
            self._archive_log(log_file)  # Compress to .tar.gz
            self._delete_log(log_file)
```

**Effort:** 3-4 hours

---

### v2.0: Advanced Analytics + Compliance Reporting

**Features:**
- SQLite index for fast queries (audit_log.db alongside JSON files)
- Query interface: Find by workflow, step, date range, status
- Aggregation: Success rate, avg execution time, failure patterns
- Export formats: CSV (spreadsheet), PDF (reports), HTML (dashboards)
- Compliance reporting: EU AI Act 3-year audit trail

**Implementation:**
```python
# mcp_server/tools/audit/analytics.py
class AuditAnalytics:
    def query(self, filters: dict) -> List[dict]:
        """Query audit logs with filters."""
        # workflow_id, step, date_range, status

    def aggregate(self, metric: str, group_by: str) -> dict:
        """Aggregate metrics (success_rate, avg_duration)."""

    def export_compliance_report(self, format: str) -> Path:
        """Export compliance report (CSV, PDF, HTML)."""
```

**Example Queries:**
```python
# Find all failures in Step 11 (last 30 days)
analytics.query({
    "step": "qg_execution",
    "status": "FAIL",
    "date_range": ("2025-12-15", "2026-01-15")
})

# Success rate per step (last 90 days)
analytics.aggregate(
    metric="success_rate",
    group_by="step"
)

# Export EU AI Act compliance report (3 years)
analytics.export_compliance_report(
    format="pdf",
    date_range=("2023-01-15", "2026-01-15")
)
```

**Effort:** 8-10 hours

---

## Value

**Benefits:**

**v1.2 (Retention Policy):**
- ✅ Prevents disk space bloat
- ✅ Configurable retention (dev vs enterprise)
- ✅ Archive before delete (no data loss)
- ✅ Compliance-ready (3-year retention for EU AI Act)

**v2.0 (Advanced Analytics):**
- ✅ Fast queries (SQLite index)
- ✅ Pattern detection (which steps fail most?)
- ✅ Compliance reporting (export for audits)
- ✅ Dashboards (success rates, trends)
- ✅ Enterprise-ready (3-year audit trail)

**Platform Impact:**
- **QA Vertical:** Dev retention (90 days), faster debugging
- **Consumer Vertical:** User task history, export for personal records
- **Agent Management:** Multi-agent execution analytics
- **Enterprise:** EU AI Act compliance (3-year retention, PDF reports)

---

## Configuration

**Environment Variables:**
```bash
# Retention policy
AUDIT_RETENTION_DAYS=90        # Dev: 90 days, Enterprise: 1095 (3 years)
AUDIT_ARCHIVE_PATH=tests/_audit/archive/  # Compressed logs

# Analytics (v2.0)
AUDIT_DB_PATH=tests/_audit/audit_log.db   # SQLite index
AUDIT_EXPORT_PATH=tests/_reports/audit/   # Compliance reports
```

---

## Implementation Plan

**v1.2 (Retention Policy):**
1. Create `AuditRetentionManager` class
2. Add retention config to environment variables
3. Archive logs to `.tar.gz` before deletion
4. Run cleanup on MCP server startup
5. Test with 90-day and 3-year retention

**v2.0 (Advanced Analytics):**
1. Create `AuditAnalytics` class with SQLite backend
2. Index audit logs on startup (background job)
3. Implement query, aggregate, export methods
4. Add compliance report templates (CSV, PDF, HTML)
5. Build dashboard UI (optional, web-based)

---

## Next Steps

1. Move to `.business/roadmap/backlog/` when ready to implement
2. Create PRD for v1.2 (retention policy)
3. Implement v1.2 for MVP+1 release
4. Follow with v2.0 after enterprise validation
