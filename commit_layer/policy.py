"""Deterministic risk rules – the safety floor.

AI can never lower these.  The classifier can only RAISE risk above this floor.
"""
from __future__ import annotations
from commit_layer.models import Action, RiskLevel


def evaluate(action: Action) -> tuple[RiskLevel, list[str]]:
    """Evaluate an action and return (risk_level, reasons)."""
    tool = action.tool_name
    args = action.args

    # ── Read-only & optimization tools ─────────────────────────
    if tool.startswith(('read_', 'get_', 'list_', 'headroom_')) or tool in ('track_consumer_expenses', 'inspect_expenses'):
        return RiskLevel.LOW, ["Read-only expense tracking & order history inspection (strictly non-mutating)"]

    # ── Autonomous Workforce & Codebase Architecture ───────────
    if tool in ('autonomous_file_scan', 'workforce_daemon_ctl', 'personal_agent_work'):
        return RiskLevel.LOW, ["Autonomous workforce inspection & background daemon control (non-destructive)"]

    if tool == 'autonomous_file_update':
        return RiskLevel.CRITICAL, ["Autonomous AST-certified file mutation with atomic snapshot rollback"]

    # ── Morning Briefing & Autonomous Daily Intelligence ──────────
    if tool in ('generate_morning_briefing', 'set_daily_budget_limit', 'setup_morning_schedule'):
        return RiskLevel.LOW, ["Governed autonomous morning intelligence briefing & daily schedule coordination"]

    # ── Application, Sandbox & Web Service Control (Hands-Free Computer Use) ─
    if tool in ('open_application', 'close_application', 'launch_app', 'browser_interactive_action', 'run_desktop_app', 'run_entire_app', 'sandbox_execute', 'sandbox_commit_worktree', 'memory_hive_action'):
        return RiskLevel.LOW, ["User-directed application or sandboxed execution (strictly contained and reversible)"]

    # ── Email Intelligence & Inspection ─────────────────────────
    if tool in ('inspect_gmail_application_views', 'inspect_email', 'search_email'):
        return RiskLevel.LOW, ["Read-only email intelligence and search query inspection"]

    # ── Notes & Knowledge Vault ─────────────────────────────────
    if tool == 'take_note':
        return RiskLevel.LOW, ["Personal markdown knowledge vault mutation (reversible)"]

    # ── Email & WhatsApp ────────────────────────────────────────
    if tool in ('send_email', 'email_dispatch', 'send_gmail', 'gmail_compose_and_dispatch'):
        return RiskLevel.MEDIUM, ["Governed outbound email / Gmail communication"]

    if tool == 'whatsapp_message':
        return RiskLevel.MEDIUM, ["Governed WhatsApp communication via native deep link"]

    # ── GitHub & DevOps ─────────────────────────────────────────
    if tool == 'github_devops':
        op = args.get('operation', 'list_issues')
        if op in ('list_issues', 'view_issue'):
            return RiskLevel.LOW, ["Read-only GitHub issue query"]
        if op == 'scaffold_project':
            return RiskLevel.LOW, ["Local project directory and template scaffolding (reversible)"]
        return RiskLevel.HIGH, [f"Remote DevOps operation ({op})"]

    # ── Payments ────────────────────────────────────────────────
    if tool in ('send_payment', 'flaky_payment', 'payment'):
        amount = float(args.get('amount', 0))
        if amount > 500:
            return RiskLevel.CRITICAL, [f"Payment amount ${amount:.2f} > $500"]
        if amount >= 100:
            return RiskLevel.HIGH, [f"Payment amount ${amount:.2f} >= $100"]
        return RiskLevel.MEDIUM, [f"Payment amount ${amount:.2f} < $100"]

    # ── Destructive / privileged operations ─────────────────────
    if tool == 'delete_file':
        return RiskLevel.CRITICAL, ["Destructive file operation"]

    if tool == 'grant_access':
        return RiskLevel.CRITICAL, ["Access control modification"]

    # ── Software & Code operations ──────────────────────────────
    if tool == 'run_terminal_command':
        return RiskLevel.CRITICAL, ["Arbitrary shell/terminal execution in host environment"]

    if tool == 'deploy_service':
        return RiskLevel.CRITICAL, ["Production service deployment / container reconfiguration"]

    if tool in ('modify_code_file', 'repo_file_action'):
        op = args.get('operation', 'modify')
        return RiskLevel.CRITICAL, [f"Live repository filesystem action ({op})"]

    # ── Hardware & Physical operations ──────────────────────────
    if tool == 'power_cycle_device':
        return RiskLevel.CRITICAL, ["Physical hardware reboot/power cycle"]

    if tool == 'tpm_sign_attestation':
        return RiskLevel.HIGH, ["Hardware-backed TPM 2.0 enclave cryptographic signing"]

    # ── External Connectors (Open-Agent-Connector) ──────────────
    if tool == 'dispatch_connector_action':
        connector_id = args.get('connector_id', '')
        if connector_id in ('github', 'slack'):
            return RiskLevel.MEDIUM, [f"External service action dispatched via connector: {connector_id}"]
        return RiskLevel.HIGH, [f"External HTTP webhook dispatched via connector: {connector_id}"]

    if tool == 'job_application_action':
        company = args.get('company', 'Target Company')
        return RiskLevel.HIGH, [f"Outbound job application and candidate PII transmission to {company}"]

    # ── Windows OS & System Maintenance ────────────────────────
    if tool == 'inspect_recycle_bin':
        return RiskLevel.LOW, ["Host OS query: Read-only Windows Recycle Bin inspection"]

    if tool == 'empty_recycle_bin':
        return RiskLevel.CRITICAL, ["Host OS mutation: Permanent, irreversible purge of Windows Recycle Bin"]

    # ── Intentional Computing & GAI Playbooks ──────────────────
    if tool in ('intentional_execute', 'playbook_replay'):
        target_str = str(args.get('intent', '')) + ' ' + str(args.get('slug', '')) + ' ' + str(args.get('target', ''))
        target_lower = target_str.lower()
        if any(k in target_lower for k in ('buy', 'sell', 'order', 'password', 'keychain', 'delete', 'fund', 'transfer')):
            return RiskLevel.CRITICAL, [f"Sensitive host intentional operation matching keyword in '{target_str.strip()}'"]
        return RiskLevel.LOW, ["Direct host intentional computing & procedural UI playbook replay"]

    # ── Reflex Automation & Self-Repair Engine ─────────────────
    if tool in ('reflex_simulate_procedure', 'reflex_ask_knowledge'):
        return RiskLevel.LOW, ["Deterministic Reflex simulation / permission-filtered documentation query"]

    if tool == 'reflex_run_procedure':
        return RiskLevel.LOW, ["Deterministic checked procedure execution under step verification"]

    # ── Unknown tool → HIGH ─────────────────────────────────────
    return RiskLevel.HIGH, [f"Unknown tool: {tool}"]
