"""Native CLI for CIEAV Commit Layer (inspired by Alma: alma.inc).

"The computer interface has changed little since the GUI made apps, windows,
menus, and files the main way to work.
AI changes what the computer can understand. The interface should change with it.
People should start with intent and context, not with the limits of an app."

Provides intent-first computing with deterministic safety floors and cryptographic commit receipts.
"""
from __future__ import annotations
import sys
import json
import argparse
from typing import Any

from commit_layer.intent import plan_intent, commit_plan
from commit_layer import gateway
from commit_layer import receipts
from commit_layer import sandbox

BANNER = r"""
   _____ _____ ______          __      __
  / ____|_   _|  ____|   /\    \ \    / /
 | |      | | | |__     /  \    \ \  / / 
 | |      | | |  __|   / /\ \    \ \/ /  
 | |____ _| |_| |____ / ____ \    \  /   
  \_____|_____|______/_/    \_\    \/    
  Commit Layer for the Internet | Native Intent Interface
"""


def color(text: str, code: str) -> str:
    """Return ANSI colored text if terminal supports it."""
    return f"\033[{code}m{text}\033[0m"


def print_card(title: str, lines: list[tuple[str, str]], border_color: str = "36"):
    """Print a clean terminal card box."""
    print(color(f"+-- [ {title} ] " + "-" * max(4, 52 - len(title)), border_color))
    for k, v in lines:
        print(color("|", border_color) + f"  {k:<20} {v}")
    print(color("+" + "-" * 60, border_color))


def cmd_intent(prompt: str, auto_confirm: bool = False):
    """Process an intent through the Commit Layer."""
    print(f"\nEvaluating Intent: {color(prompt, '1;37')}\n")
    plan = plan_intent(prompt)
    
    risk = plan["highest_risk"]
    risk_color = {
        "LOW": "32",
        "MEDIUM": "33",
        "HIGH": "31",
        "CRITICAL": "1;31"
    }.get(risk, "37")

    for idx, act in enumerate(plan["actions"], 1):
        lines = [
            ("Domain", act["domain"].upper()),
            ("Consequence Tool", color(act["tool"], "1;34")),
            ("Risk Assessment", color(act["risk"], risk_color)),
            ("Reasons", ", ".join(act["reasons"])),
            ("Redacted Args", json.dumps(act["args_redacted"])),
            ("Friction Decision", act["decision"]),
            ("Rollback Guarantee", color("YES (Inverse Action Available)", "32") if act["has_inverse"] else color("NO (Irreversible)", "33")),
        ]
        print_card(f"Action {idx}/{len(plan['actions'])}: {act['summary']}", lines)

    if plan["requires_typed_confirmation"]:
        phrase = plan["confirmation_phrase"]
        print(color(f"\n[!] HIGH RISK OPERATION: Typed confirmation required.", "1;31"))
        print(f"Please type exact phrase: {color(phrase, '1;33')}")
        if auto_confirm:
            typed = phrase
        else:
            typed = input("Confirmation > ").strip()
        
        commit_res = commit_plan(plan["plan_id"], approved_by="cli-user", typed_confirmation=typed)
    else:
        if not auto_confirm:
            ans = input(f"\nCommit this plan? [{color('Y', '32')}/n]: ").strip().lower()
            if ans not in ('', 'y', 'yes'):
                print(color("Plan aborted by user.", "33"))
                return
        commit_res = commit_plan(plan["plan_id"], approved_by="cli-user")

    if "error" in commit_res:
        print(color(f"\n[FAIL] {commit_res['error']}", "1;31"))
        return

    print(color(f"\n[SUCCESS] Plan committed cryptographically to audit ledger.", "1;32"))
    for r in commit_res.get("results", []):
        outcome = r.get("outcome", "UNKNOWN")
        undo_st = r.get("undo_state", "NONE")
        print(f"  * Action: {r.get('action_id')} | Outcome: {outcome} | Receipt: {r.get('receipt_id')}")
        if undo_st == "AVAILABLE":
            print(f"    (Undo available via: cieav undo {r.get('receipt_id')})")


def cmd_undo(receipt_id: str):
    """Safely undo a committed action."""
    print(f"\nRequesting compensating inverse for receipt: {receipt_id}")
    res = gateway.undo(receipt_id)
    if "error" in res:
        print(color(f"[FAIL] Undo refused: {res['error']}", "1;31"))
    else:
        print(color(f"[SUCCESS] Action undone successfully!", "1;32"))
        print(f"Details: {res.get('result')}")


def cmd_verify():
    """Verify cryptographic Ed25519 hash-chain integrity."""
    print("\nVerifying Ed25519 hash-chain ledger integrity...")
    valid, errors = receipts.verify_chain()
    if valid:
        all_r = receipts.get_all_receipts()
        print(color(f"[PASS] Cryptographic integrity intact across all {len(all_r)} audit receipts.", "1;32"))
    else:
        print(color(f"[ALERT] Tampering detected in audit ledger!", "1;31"))
        for err in errors:
            print(f"  - {err}")


def cmd_status():
    """Display real-time state of software, hardware, and ledger."""
    print("\n=== SOFTWARE STATUS ===")
    sw = getattr(sandbox, "software_registry", {})
    services = sw.get("services", {})
    for s_name, s_info in services.items():
        print(f"  * {s_name:<20} {s_info.get('status')} ({s_info.get('version')})")

    print("\n=== HARDWARE / TPM STATUS ===")
    hw = getattr(sandbox, "hardware_state", {})
    print(f"  TPM Status: {hw.get('tpm_status', 'Unknown')}")
    for d_name, d_info in hw.get("enrolled_devices", {}).items():
        print(f"  * {d_name:<20} {d_info.get('status')} [Firmware: {d_info.get('firmware')}, PCR Quote: {d_info.get('pcr_quote')}]")

    print("\n=== LEDGER BALANCES ===")
    for acc, bal in sandbox.bank_ledger.items():
        print(f"  * {acc:<20} ${bal:.2f}")


def repl():
    """Interactive Alma-style REPL prompt."""
    print(color(BANNER, "1;36"))
    print("Welcome to CIEAV Native Intent Interface.")
    print("Type your intent naturally across software, code, hardware TPM, payments, or access.")
    print("Type 'status', 'verify', or 'exit' anytime.\n")

    while True:
        try:
            prompt = input(color("cieav> ", "1;32")).strip()
            if not prompt:
                continue
            if prompt in ("exit", "quit"):
                print("Goodbye.")
                break
            if prompt == "status":
                cmd_status()
                continue
            if prompt == "verify":
                cmd_verify()
                continue
            if prompt.startswith("undo "):
                cmd_undo(prompt.split()[1])
                continue

            cmd_intent(prompt)
        except (KeyboardInterrupt, EOFError):
            print("\nExiting CIEAV.")
            break
        except Exception as e:
            print(color(f"Error: {e}", "31"))


def cmd_headroom(action: str, target: str = ""):
    """Headroom context optimization and CCR commands."""
    from commit_layer import headroom
    if action == "stats":
        st = headroom.vault.get_stats()
        print("\n=== HEADROOM CONTEXT OPTIMIZATION STATS ===")
        print(f"  * Total Raw Bytes:         {st['total_raw_bytes']:,} B")
        print(f"  * Total Compressed Bytes:  {st['total_compressed_bytes']:,} B")
        print(f"  * Bytes Saved:             {st['saved_bytes']:,} B")
        pct_str = f"{st['savings_pct']}%"
        print(f"  * Token Savings:           {color(pct_str, '1;32')}")
        print(f"  * Approx Tokens Saved:     {st['approx_saved_tokens']:,} tokens")
        print(f"  * Chunks in CCR Vault:     {st['chunks_stored']}")
        print(f"  * Chunks Restored:         {st['chunks_retrieved']}")
    elif action == "compress":
        comp_text, chunk_id, savings = headroom.compress(target)
        print(f"\n[Headroom Compressed: {savings}% tokens saved]")
        print(f"CCR Chunk ID: {color(chunk_id, '1;36')}")
        print(f"\n{comp_text}\n")
    elif action == "retrieve":
        raw = headroom.retrieve(target)
        if raw is None:
            print(color(f"[FAIL] Chunk '{target}' not found in CCR vault", "1;31"))
        else:
            print(f"\n[Headroom Restored Full Raw Text for {target}]:\n")
            print(raw)
    elif action == "mcp":
        import json
        from commit_layer.headroom.mcp import HEADROOM_MCP_TOOLS
        print("\n=== HEADROOM MCP SERVER CONFIGURATION ===")
        print(json.dumps({"mcpServers": {"headroom": {"command": "python", "args": ["-m", "commit_layer.cli", "headroom", "stats"]}}}, indent=2))
        print("\nSupported MCP Tools:", ", ".join(t["name"] for t in HEADROOM_MCP_TOOLS))


def main():
    parser = argparse.ArgumentParser(description="CIEAV Alma-Native CLI Interface")
    subparsers = parser.add_subparsers(dest="command")

    # intent command
    p_intent = subparsers.add_parser("intent", help="Execute a natural language intent")
    p_intent.add_argument("prompt", help="Natural language intent statement")
    p_intent.add_argument("-y", "--yes", action="store_true", help="Auto-confirm without prompt")

    # undo command
    p_undo = subparsers.add_parser("undo", help="Undo a committed action by receipt ID")
    p_undo.add_argument("receipt_id", help="Receipt ID to compensate")

    # verify command
    subparsers.add_parser("verify", help="Verify cryptographic hash-chain ledger")

    # status command
    subparsers.add_parser("status", help="Show system, software, hardware, and bank state")

    # headroom command
    p_headroom = subparsers.add_parser("headroom", help="Headroom context optimization and CCR vault")
    p_headroom.add_argument("subaction", choices=["stats", "compress", "retrieve", "mcp"], help="Action to perform")
    p_headroom.add_argument("target", nargs="?", default="", help="Text to compress or chunk ID to retrieve")

    # morning command
    p_morning = subparsers.add_parser("morning", help="Generate autonomous morning intelligence briefing")
    p_morning.add_argument("--time", default="", help="Schedule daily time (e.g. 08:00)")
    p_morning.add_argument("--limit", type=float, default=None, help="Set daily budget limit")
    p_morning.add_argument("--auto", action="store_true", help="Unattended background scheduled run")

    # workforce command
    p_workforce = subparsers.add_parser("workforce", help="Autonomous Codebase Workforce & AST Health Scanner")
    p_workforce.add_argument("action", nargs="?", default="scan", choices=["scan", "heal", "status"], help="Workforce action")

    # daemon command
    p_daemon = subparsers.add_parser("daemon", help="Workforce Sentinel background watcher daemon")
    p_daemon.add_argument("action", nargs="?", default="status", choices=["start", "stop", "status"], help="Daemon control")

    # work command
    p_work = subparsers.add_parser("work", help="Assign a task to personal agent or squad")
    p_work.add_argument("task", help="Natural language directive or task")
    p_work.add_argument("--agent", default=None, help="Assigned agent persona (e.g. Researcher, Codex, Sentinel)")
    p_work.add_argument("--squad", default=None, help="Assigned squad (e.g. Product Team, Engineering Squad)")
    p_work.add_argument("--no-open", dest="no_open", action="store_true", help="Do not launch browser dashboard automatically")

    # personal-agent command
    p_pa = subparsers.add_parser("personal-agent", help="Personal agent workspace and dashboard commands")
    p_pa.add_argument("subaction", choices=["setup", "dashboard", "status"], help="Action to execute")

    args = parser.parse_args()

    if args.command == "morning":
        from commit_layer.tools.morning_briefing_agent import morning_briefing_agent
        if args.limit is not None:
            morning_briefing_agent.set_daily_limit(args.limit)
        if args.time:
            morning_briefing_agent.setup_windows_schedule(args.time)
        res = morning_briefing_agent.generate_full_briefing(auto_notify=True)
        if not args.auto:
            print(morning_briefing_agent.render_cli_dossier(res))
    elif args.command == "intent":
        cmd_intent(args.prompt, auto_confirm=args.yes)
    elif args.command == "undo":
        cmd_undo(args.receipt_id)
    elif args.command == "verify":
        cmd_verify()
    elif args.command == "status":
        cmd_status()
    elif args.command == "headroom":
        cmd_headroom(args.subaction, args.target)
    elif args.command == "workforce":
        from commit_layer.autonomous_workforce import autonomous_workforce
        res = autonomous_workforce.run_workforce_inspection()
        print(res["dossier"])
    elif args.command == "daemon":
        from commit_layer.autonomous_workforce import autonomous_workforce
        if args.action == "start":
            res = autonomous_workforce.daemon.start()
            print(f"\n[CIEAV WORKFORCE DAEMON] {res['message']}\n")
        elif args.action == "stop":
            res = autonomous_workforce.daemon.stop()
            print(f"\n[CIEAV WORKFORCE DAEMON] {res['message']}\n")
        else:
            res = autonomous_workforce.daemon.status()
            st_col = "ACTIVE" if res["is_running"] else "STOPPED"
            print(f"\n[CIEAV WORKFORCE DAEMON] Status: {st_col} | Watched: {res['watched_files_count']} files\n")
    elif args.command == "work":
        from commit_layer.work_dispatcher import work_dispatcher
        res = work_dispatcher.dispatch(
            task=args.task,
            agent=args.agent,
            squad=args.squad,
            auto_open=not getattr(args, "no_open", False)
        )
        print(res["card"])
    elif args.command == "personal-agent":
        from commit_layer.personal_agent_dashboard import dashboard_server, load_settings, save_settings
        if args.subaction == "setup":
            st = load_settings()
            save_settings(st)
            print("\n[CIEAV PERSONAL AGENT] Workspace setup complete! Configured for local CPU Qwen GGUF on port 6796.\n")
            print("  • Dashboard URL: http://127.0.0.1:6796")
            print("  • Start working: cieav work \"your task\"\n")
        elif args.subaction == "dashboard":
            res = dashboard_server.spawn_daemon_process(auto_open=True)
            print(f"\n[CIEAV PERSONAL AGENT] {res['message']}\n")
        elif args.subaction == "status":
            st = dashboard_server.get_status()
            alive_col = "\033[1;32mONLINE\033[0m" if st["is_running"] else "\033[1;33mSTANDBY (Run 'cieav personal-agent dashboard')\033[0m"
            print(f"\n[CIEAV PERSONAL AGENT STATUS]")
            print(f"  • Dashboard Service : {alive_col}")
            print(f"  • URL               : {st['url']}")
            print(f"  • Model Provider    : {st['model_provider']} ({st['model_name']})")
            print(f"  • Active Threads    : {st['active_threads_count']}")
            print(f"  • Spend Cap         : ${st['spend_cap_usd']:.2f} USD\n")
    else:
        repl()



if __name__ == "__main__":
    main()
