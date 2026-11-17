---
title: CIEAV - Sovereign Personal AI Agent
emoji: 🛡️
colorFrom: purple
colorTo: indigo
sdk: static
pinned: false
license: apache-2.0
short_description: Sovereign Agent with 2PC Floor & PyBot Engine
---

# CIEAV: Sovereign Open-Source Personal AI Agent
### *Live Interactive Space featuring Two-Phase Commit (2PC) & PyBot Symbolic Engine*

[![Hugging Face Model](https://img.shields.io/badge/HuggingFace-Cieav--Model-yellow.svg)](https://huggingface.co/Aravindhan11/Cieav-model)
[![GitHub Repository](https://img.shields.io/badge/GitHub-cieav--personal--agent-purple.svg)](https://github.com/Aravindh-dev12/cieav-personal-agent)
[![PyBot Inspired](https://img.shields.io/badge/Architecture-Hugging%20Face%20PyBot-orange.svg)](https://github.com/huggingface/pybot)
[![Safety](https://img.shields.io/badge/Safety-Two--Phase%20Commit-green.svg)](https://github.com/Aravindh-dev12/cieav-personal-agent)

This interactive Space demonstrates the **CIEAV Sovereign Personal AI Agent**, incorporating:
1. **The PyBot Pure-Python Symbolic Engine** (inspired by [Hugging Face's PyBot](https://github.com/huggingface/pybot)): Zero neural network weights, 0 MB download, sub-2ms latency, and 100% immunity to prompt injection.
2. **Two-Phase Commit (2PC) Safety Floor**: Ephemeral 60s permits, pre-execution atomic snapshots, and lossless `/undo`.
3. **Monotone Risk Lattice**: Deterministic policies enforce the floor; language models can never downplay risk.
4. **Anti-Reward Hacking Defense**: Hard negative penalty floor ($-1.0$) eliminating apologetic sycophancy.

---

## 🎮 How to Test in the Live Interactive UI:
* **Test Attacks**: Click the preset attack buttons (Prompt Injection, Credential Leak, Apologetic Sycophancy) to watch the symbolic engine intercept them.
* **Observe 2PC Pipeline**: See the live transition from **PREPARE** (snapshot & permit) to **COMMIT** (execution & Ed25519 receipt).
* **Test `/undo`**: Modify state and hit `/undo` to experience instant, byte-for-byte rollback.
