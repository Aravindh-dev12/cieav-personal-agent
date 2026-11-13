# CIEAV ML post-training architecture

This directory is the Python-first GPU/research side of CIEAV's model pipeline. The shipped cross-platform authority runtime remains Node/TypeScript plus native OS components.

## Runtime split

**Python = ML orchestration. Node/TypeScript = deterministic authority and canonical verification.**

Python owns datasets, SFT, DPO, KTO, RLVR/GRPO, process supervision, rollout generation, curriculum selection, active failure mining, adversarial replay, calibration experiments, scale-out training, and distillation. Python may launch or call the canonical Node verifier, but it cannot mint permits or commit actions.

The Node verifier owns canonical deterministic reward/safety semantics and advertises `authority:false`. The production CIEAV runtime separately owns permits, commit, receipts, observed outcome, and verified undo. This split is identical on Windows, macOS, and Linux.

`ml/cieav_rlvr/` contains the Python control package:

- `verifier.py` — authenticated loopback client for canonical Node reward/promotion endpoints.
- `node_runtime.py` — cross-platform Python supervisor that launches the local Node verifier and strips unrelated authority/provider secrets from its environment.
- `train_trl.py` — Python training entrypoint. GRPO uses `--verifier-mode auto` by default, so Python launches the Node verifier automatically. `--verifier-mode external` is available for distributed workers using an explicitly configured loopback verifier.

Run the cross-language boundary locally after building core:

```bash
npm run build -w @cieav/contracts
npm run build -w @cieav/core
python scripts/ml-python-node-smoke.py
```

## Safety boundary

Models interpret; CIEAV deterministic code authorizes. No trained model, reward model, process verifier, Python worker, or LLM judge can mint a permit, commit an action, mark UNKNOWN as success, or authorize undo. Promotion requires deterministic held-out evaluation.

## Training stages

1. `SFT` — teach CIEAV schemas, consequence reasoning, abstention format, and process traces.
2. `DPO` — improve explanations, refusals, previews, and friction preferences.
3. `KTO` — optional binary production-feedback alignment when paired preferences are unavailable.
4. `RLVR/GRPO` — optimize against CIEAV deterministic Node verifiers from Python training workers.
5. `PROCESS` — add step/fact/policy-check credit from process traces.
6. `SOFT_RLVR` — partial credit for checklist-like semantic requirements; never authority.
7. `AGENTIC_RL` — train multi-turn tool trajectories with permit, approval, commit, outcome, and undo invariants.
8. `CALIBRATION` — reward correct confidence and abstention on insufficient evidence.
9. `ADVERSARIAL` — held-out reward-hacking, prompt-injection, secret-leakage, and policy-conflict suites.
10. `DISTILL` — distill the qualified teacher into a smaller local semantic model, then re-run the complete promotion gate.

## Frameworks

Prototype/single-node training uses Python with PyTorch + Transformers + TRL + PEFT, alongside **Unsloth** (`ml/train_unsloth.py`) for ultra-fast, memory-efficient GRPO / RLVR and DPO post-training on Qwen-3.5 with custom Triton kernels and direct GGUF export. Scale-out RL uses verl with Ray and vLLM/SGLang rollouts. These frameworks optimize models only; canonical reward and hard-safety semantics live in `packages/core/src/ml-*.ts` and are consumed through the authenticated Node verifier boundary rather than reimplemented as an independent Python authority.

## Data flow

`evals/cases.v1.json` -> `dataset/build_from_evals.py` -> JSONL training/eval records -> Python TRL/verl rollout -> authenticated loopback Node verifier -> held-out promotion report.

Never train and promote on the same verifier corpus. Keep separate train, validation, adversarial, and promotion partitions; promotion corpora must be immutable/versioned for each release candidate.
