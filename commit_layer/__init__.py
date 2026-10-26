"""
Commit Layer for the Internet package.
"""
import sys
from pathlib import Path
from dotenv import load_dotenv, find_dotenv

# Ensure stdout and stderr handle UTF-8 cleanly on Windows CP1252 consoles
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
if hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Ensure environment variables from project root .env are loaded reliably
_env_path = Path(__file__).resolve().parent.parent / ".env"
if _env_path.exists():
    load_dotenv(dotenv_path=_env_path)
else:
    load_dotenv(find_dotenv(usecwd=True))

__version__ = "0.1.0"

from commit_layer.personal_agent import cieav_personal_agent, CieavPersonalAgent
from commit_layer.autonomous_workforce import autonomous_workforce, AutonomousWorkforceOrchestrator
from commit_layer.work_dispatcher import work_dispatcher, WorkDispatcher
from commit_layer.personal_agent_dashboard import dashboard_server, PersonalAgentDashboardServer
