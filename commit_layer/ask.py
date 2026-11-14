"""
CIEAV Meeting & Technical Defense Question-Answering Engine.
============================================================
Searches data/cieav_meeting_knowledge_base.json and answers any technical,
architectural, ML research, or interview question instantly with high precision.
"""

from __future__ import annotations
import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional


class CieavKnowledgeQA:
    """Instant local Q&A engine over the CIEAV technical defense knowledge base."""

    JSON_PATH = Path("data/cieav_meeting_knowledge_base.json")
    FALLBACK_PATH = Path("commit_layer/cieav_meeting_knowledge_base.json")

    def __init__(self):
        self.data: Dict[str, Any] = {}
        self.entries: List[Dict[str, Any]] = []
        self._load()

    def _load(self):
        target = self.JSON_PATH if self.JSON_PATH.exists() else self.FALLBACK_PATH
        if target.exists():
            try:
                self.data = json.loads(target.read_text(encoding="utf-8"))
                self.entries = self.data.get("entries", [])
            except Exception:
                self.entries = []

    def answer(self, query: str) -> Dict[str, Any]:
        """Search entries for best matching response."""
        if not self.entries:
            self._load()

        if not query or not query.strip():
            return {
                "status": "empty",
                "message": "Please ask a question or keyword (e.g., 'how does 2pc work', 'reward hacking', 'unsloth', 'huggingface')."
            }

        q_clean = re.sub(r"[^\w\s]", " ", query.lower()).strip()
        q_tokens = set(q_clean.split())

        best_score = -1
        best_entry: Optional[Dict[str, Any]] = None

        for entry in self.entries:
            score = 0
            # 1. Exact id or category match
            if entry.get("id", "").lower() in q_clean:
                score += 50
            if entry.get("category", "").lower() in q_clean:
                score += 20

            # 2. Question similarity
            entry_q = entry.get("question", "").lower()
            for token in q_tokens:
                if len(token) > 2 and token in entry_q:
                    score += 15

            # 3. Keywords match
            for kw in entry.get("keywords", []):
                kw_lower = kw.lower()
                if kw_lower in q_clean:
                    score += 35
                else:
                    kw_tokens = set(kw_lower.split())
                    overlap = len(kw_tokens & q_tokens)
                    if overlap > 0:
                        score += 10 * overlap

            # 4. Content matches
            full_text = entry.get("full_answer", "").lower()
            for token in q_tokens:
                if len(token) > 3 and token in full_text:
                    score += 3

            if score > best_score:
                best_score = score
                best_entry = entry

        if not best_entry or best_score <= 5:
            # General fallback to first entry (overview)
            best_entry = self.entries[0] if self.entries else {}

        return {
            "status": "success",
            "score": best_score,
            "entry": best_entry,
            "formatted_card": self.render_answer_card(query, best_entry)
        }

    def render_answer_card(self, query: str, entry: Dict[str, Any]) -> str:
        """Render a terminal card displaying the answer."""
        c_purple = "\033[38;2;168;85;247m"
        c_cyan = "\033[38;2;6;182;212m"
        c_emerald = "\033[38;2;16;185;129m"
        c_amber = "\033[38;2;245;158;11m"
        c_slate = "\033[38;2;148;163;184m"
        c_white = "\033[1;37m"
        rst = "\033[0m"

        cat = entry.get("category", "General Architecture")
        q = entry.get("question", query)
        short_a = entry.get("short_answer", "")
        full_a = entry.get("full_answer", "")
        key_takeaway = entry.get("key_takeaway", "")
        code_ex = entry.get("code_example", "")

        out = [
            f"{c_purple}╔══════════════════════════════════════════════════════════════════════════════════════════╗{rst}",
            f"{c_purple}║{rst}  {c_cyan}✨ CIEAV MEETING DEFENSE & TECHNICAL KNOWLEDGE BASE{rst}                                     {c_purple}║{rst}",
            f"{c_purple}╠══════════════════════════════════════════════════════════════════════════════════════════╣{rst}",
            f"  {c_white}Category :{rst} {c_amber}{cat}{rst}",
            f"  {c_white}Question :{rst} {c_cyan}{q}{rst}",
            f"{c_purple}╠══════════════════════════════════════════════════════════════════════════════════════════╣{rst}",
            f"  {c_emerald}💡 SHORT ANSWER (30-Second Summary):{rst}",
            f"  {short_a}\n",
            f"  {c_white}🔬 DEEP TECHNICAL EXPLANATION:{rst}",
        ]

        for line in full_a.splitlines():
            out.append(f"  {line}")

        if key_takeaway:
            out.append(f"\n  {c_amber}🎯 KEY TAKEAWAY FOR INTERVIEWERS / MEETING:{rst}")
            out.append(f"  {key_takeaway}")

        if code_ex:
            out.append(f"\n  {c_cyan}💻 RELEVANT COMMAND / CODE:{rst}")
            for cline in code_ex.splitlines():
                out.append(f"  {c_slate}{cline}{rst}")

        out.append(f"{c_purple}╚══════════════════════════════════════════════════════════════════════════════════════════╝{rst}")
        return "\n".join(out)


# Global singleton
cieav_qa = CieavKnowledgeQA()
