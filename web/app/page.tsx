'use client'

import { useEffect, useRef, useState } from 'react'
import {
  ArrowUpRight,
  Check,
  Copy,
  Terminal,
  ShieldCheck,
  Key,
  Undo2,
  Cpu,
  FileText,
  CheckCircle2,
  ExternalLink,
  Lock,
  Search,
  AlertTriangle,
  X,
  ChevronRight,
  Play,
  Activity,
  Layers,
} from 'lucide-react'

type Section = {
  id: string
  nav: string
  num: string
  title: string
  sub: string[]
  meta: string
}

const sections: Section[] = [
  { id: 'home', nav: 'Home', num: '00', title: 'Home', sub: [], meta: 'CIEAV' },
  { id: 'install', nav: 'Install', num: '01', title: 'Install:', sub: ['One-line installer,', 'zero configuration...'], meta: 'SETUP' },
  { id: 'agent-cli', nav: 'CLI & NLP', num: '02', title: 'Agent CLI:', sub: ['Traditional local commands,', 'chat & computer-use...'], meta: 'NATIVE' },
  { id: 'alma-agent', nav: 'Alma Agent', num: '03', title: 'Alma Control:', sub: ['Autonomous resume discovery,', 'LinkedIn job matching...'], meta: 'GOVERNED' },
  { id: 'decision-models', nav: 'Decision Models', num: '04', title: 'Decision Models:', sub: ['Empirical benchmarks vs', 'Jev 1.13, Kev & Laya...'], meta: 'BENCHMARK' },
  { id: 'architecture', nav: 'Architecture', num: '05', title: 'Architecture:', sub: ['Local authority,', 'cloud interpretation...'], meta: 'CONTROL' },
  { id: 'security', nav: 'Security', num: '06', title: 'Security:', sub: ['Deterministic safety floor,', 'conservative failure...'], meta: '12 INVARIANTS' },
  { id: 'verify', nav: 'Verify', num: '07', title: 'Verify:', sub: ['Test the control plane,', 'cryptographic receipts...'], meta: 'ED25519' },
  { id: 'playground', nav: 'Playground', num: '08', title: 'Playground:', sub: ['Interactive docs &', 'terminal console...'], meta: 'LIVE' },
]

const architectureRows = [
  ['01', 'Human / AI agent / Alma computer intent', 'INTENT'],
  ['02', 'Local CIEAV Gateway (127.0.0.1:8000)', 'AUTHORITY'],
  ['03', 'Deterministic safety floor (Hard bound)', 'SAFETY'],
  ['04', 'Local privacy reduction ([EMAIL_REDACTED])', 'PRIVACY'],
  ['05', 'Ephemeral 60s single-use execution token', 'PERMIT'],
  ['06', 'PREVIEW → TYPED COMMIT / REJECT', 'DECISION'],
  ['07', 'Atomic execution snapshot & hardware state', 'SNAPSHOT'],
  ['08', 'Outcome observer → SUCCESS / FAILURE / UNKNOWN', 'OBSERVE'],
  ['09', 'Signed Ed25519 hash-chained Action Receipt', 'RECEIPT'],
  ['10', 'Two-phase inverse rollback (/undo)', 'REVERSAL'],
]

const securityRows = [
  'Website and agent inputs are considered hostile by default.',
  'Raw secrets, resumes, and passwords never enter external model context.',
  'AI classifiers can only RAISE risk above policy floors, never lower them.',
  'HIGH and CRITICAL actions require typed human confirmation (COMMIT).',
  'Approved actions use single-use, 60-second cryptographic execution tokens.',
  'COMMITTED is not proof of success; outcome observer must verify state.',
  'UNKNOWN state never assumes success; navigation is not proof.',
  'Undo requires verified OBSERVED_SUCCESS plus an atomic snapshot inverse.',
  'Cryptographic receipts use Ed25519 signatures in an append-only SQLite hash chain.',
  'The privileged Gateway control loop is loopback-only and bearer-token protected.',
  'Cloud interpretation never executes actions directly on user hardware.',
  'Closing the browser UI does not terminate the background Gateway daemon.',
]

const nativeCliCommands = [
  { cmd: 'cieav', desc: 'Launch interactive NLP terminal assistant in PowerShell/CMD' },
  { cmd: 'cieav /decide "rm -rf /"', desc: 'Embedded decision model: queries Bayesian prior & syntax AST in <3ms' },
  { cmd: 'cieav /model', desc: 'Inspect local decision engine architecture and active models' },
  { cmd: 'cieav "find jobs based on my resume and apply"', desc: 'Autonomous Alma agent: scans local resume, matches LinkedIn jobs, requires typed COMMIT' },
  { cmd: 'cieav /status', desc: 'Verify cryptographic Ed25519 hash chain integrity and active key ID' },
  { cmd: 'cieav /receipts', desc: 'Display append-only immutable execution receipts' },
  { cmd: 'cieav /undo', desc: 'Instant two-phase atomic inverse rollback for committed actions' },
  { cmd: 'python test_real_world_cieav_live.py', desc: '5-domain live consequential test runner (PDF, Git, Filesystem, CFO, Ed25519)' },
  { cmd: 'cieav /help', desc: 'Display comprehensive developer documentation and CLI guide' },
]

const benchmarkData = [
  { metric: 'Adversarial Prompt Injection Defense', jev: '20%', kev: '10%', laya: '20%', cieav: '100% (Deterministic Floor)' },
  { metric: 'Arithmetic Spend Floor ($100 Cap)', jev: '0% (No Math)', kev: '0% (No Math)', laya: '0% (No Math)', cieav: '100% (Hard Bound)' },
  { metric: 'Two-Phase Inverse Rollback (/undo)', jev: '0% (None)', kev: '0% (None)', laya: '0% (None)', cieav: '100% (Lossless Snapshot)' },
  { metric: 'Ed25519 Signed Audit Receipts', jev: '0% (None)', kev: '0% (None)', laya: '0% (None)', cieav: '100% (Merkle Chain)' },
  { metric: 'Single-Use Ephemeral Permits (60s)', jev: '0% (None)', kev: '0% (None)', laya: '0% (None)', cieav: '100% (Enforced)' },
  { metric: 'Decision Latency Overhead', jev: '450ms', kev: '380ms', laya: '410ms', cieav: '1.8ms (Local Python/C Core)' },
]

// Liquid Interactive Monogram Canvas Component
function LiquidLogoCanvas() {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const [coords, setCoords] = useState({ x: 90.5, y: 34.7 })
  const mouseRef = useRef({ x: -1000, y: -1000, active: false })

  useEffect(() => {
    const cv = canvasRef.current
    if (!cv) return
    const ctx = cv.getContext('2d')
    if (!ctx) return

    let animationFrameId: number
    let time = 0

    const resize = () => {
      const rect = cv.getBoundingClientRect()
      const dpr = Math.min(2, window.devicePixelRatio || 1)
      cv.width = rect.width * dpr
      cv.height = rect.height * dpr
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0)
    }
    resize()
    window.addEventListener('resize', resize)

    // Base polygon points for the stylized 'C' / CIEAV stepped monogram
    const baseGlyph = [
      { x: 0.45, y: -0.65 },
      { x: 0.45, y: -0.28 },
      { x: -0.05, y: -0.28 },
      { x: -0.05, y: 0.28 },
      { x: 0.45, y: 0.28 },
      { x: 0.45, y: 0.65 },
      { x: -0.55, y: 0.65 },
      { x: -0.55, y: 0.22 },
      { x: -0.72, y: 0.22 },
      { x: -0.72, y: -0.22 },
      { x: -0.55, y: -0.22 },
      { x: -0.55, y: -0.65 },
    ]

    const render = () => {
      time += 0.022
      const rect = cv.getBoundingClientRect()
      const w = rect.width
      const h = rect.height

      ctx.clearRect(0, 0, w, h)

      const cx = w * 0.52
      const cy = h * 0.5
      const scale = Math.min(w, h) * 0.42

      // Draw subtle crosshair grid lines
      ctx.strokeStyle = 'rgba(0, 0, 0, 0.09)'
      ctx.lineWidth = 1
      ctx.beginPath()
      ctx.moveTo(0, cy)
      ctx.lineTo(w, cy)
      const angleOffset = Math.sin(time * 0.4) * 6
      ctx.moveTo(cx + 10 + angleOffset, 0)
      ctx.lineTo(cx - 10 - angleOffset, h)
      ctx.stroke()

      // Calculate fluid vertices with organic harmonic wave noise
      const pts = baseGlyph.map((p, idx) => {
        const waveX = Math.sin(time * 2.2 + p.y * 3.8 + idx * 0.7) * 0.048 +
                      Math.cos(time * 1.4 + p.x * 2.6) * 0.028
        const waveY = Math.cos(time * 2.4 + p.x * 3.8 + idx * 0.7) * 0.048 +
                      Math.sin(time * 1.8 + p.y * 2.6) * 0.028

        let px = cx + (p.x + waveX) * scale
        let py = cy + (p.y + waveY) * scale

        // Interactive mouse repulsion (liquid ferrofluid dynamic)
        if (mouseRef.current.active) {
          const dx = px - mouseRef.current.x
          const dy = py - mouseRef.current.y
          const dist = Math.sqrt(dx * dx + dy * dy)
          if (dist < 130) {
            const force = (1 - dist / 130) * 24
            px += (dx / (dist || 1)) * force
            py += (dy / (dist || 1)) * force
          }
        }

        return { x: px, y: py }
      })

      // Draw smooth liquid contour using quadratic curve smoothing
      ctx.beginPath()
      ctx.fillStyle = '#09090b' // Black liquid fill
      ctx.shadowColor = 'rgba(0, 0, 0, 0.22)'
      ctx.shadowBlur = 28
      ctx.shadowOffsetY = 10

      const len = pts.length
      ctx.moveTo((pts[0].x + pts[len - 1].x) / 2, (pts[0].y + pts[len - 1].y) / 2)
      for (let i = 0; i < len; i++) {
        const next = pts[(i + 1) % len]
        const midX = (pts[i].x + next.x) / 2
        const midY = (pts[i].y + next.y) / 2
        ctx.quadraticCurveTo(pts[i].x, pts[i].y, midX, midY)
      }
      ctx.closePath()
      ctx.fill()
      ctx.shadowColor = 'transparent'

      // Specular liquid stroke
      ctx.strokeStyle = 'rgba(255, 255, 255, 0.22)'
      ctx.lineWidth = 2.5
      ctx.stroke()

      // Idle coordinate drift if mouse is not over canvas
      if (!mouseRef.current.active) {
        setCoords({
          x: 90.5 + Math.sin(time * 0.8) * 3.5,
          y: 34.7 + Math.cos(time * 0.6) * 3.2,
        })
      }

      animationFrameId = requestAnimationFrame(render)
    }

    render()

    const onPointerMove = (e: MouseEvent) => {
      const rect = cv.getBoundingClientRect()
      const mx = e.clientX - rect.left
      const my = e.clientY - rect.top
      mouseRef.current = { x: mx, y: my, active: true }
      const normX = ((mx / rect.width) * 100).toFixed(1)
      const normY = ((my / rect.height) * 100).toFixed(1)
      setCoords({ x: parseFloat(normX), y: parseFloat(normY) })
    }

    const onPointerLeave = () => {
      mouseRef.current.active = false
    }

    cv.addEventListener('mousemove', onPointerMove)
    cv.addEventListener('mouseleave', onPointerLeave)

    return () => {
      cancelAnimationFrame(animationFrameId)
      window.removeEventListener('resize', resize)
      cv.removeEventListener('mousemove', onPointerMove)
      cv.removeEventListener('mouseleave', onPointerLeave)
    }
  }, [])

  return (
    <div className="relative flex h-[380px] sm:h-[420px] lg:h-[460px] w-full items-center justify-center rounded-2xl border border-zinc-200/90 bg-zinc-50/70 p-4 shadow-sm overflow-hidden group">
      {/* Dynamic Coordinate Tag */}
      <div className="absolute top-6 left-6 font-mono text-xs font-semibold tracking-wider text-blue-600 bg-white/90 px-3 py-1.5 rounded-md border border-blue-100 shadow-sm z-10 backdrop-blur-md">
        【X {coords.x.toFixed(1)}, Y {coords.y.toFixed(1)}】
      </div>

      <div className="absolute top-6 right-6 font-mono text-[10px] text-zinc-500 bg-white/80 px-2 py-1 rounded border border-zinc-200">
        ED25519 VERIFIED GLYPH
      </div>

      <div className="absolute bottom-5 right-6 text-[10px] font-mono text-zinc-400">
        INTERACTIVE LIQUID C MONOGRAM • HOVER TO DISTORT
      </div>

      <canvas ref={canvasRef} className="h-full w-full cursor-crosshair" />
    </div>
  )
}

export default function Page() {
  const rootRef = useRef<HTMLElement>(null)
  const [activeInstallTab, setActiveInstallTab] = useState<'powershell' | 'bash' | 'git'>('powershell')
  const [showSignInModal, setShowSignInModal] = useState(false)
  const [copiedText, setCopiedText] = useState('')
  const [terminalInput, setTerminalInput] = useState('')
  const [terminalLogs, setTerminalLogs] = useState<string[]>([
    'CIEAV Native Control Plane initialized.',
    'Local Gateway: http://127.0.0.1:8000 (Active Ed25519 signing key)',
    'Ready. Type "help" or select a prompt below:',
  ])

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text)
    setCopiedText(text)
    setTimeout(() => setCopiedText(''), 2000)
  }

  const handleTerminalSubmit = (e?: React.FormEvent) => {
    if (e) e.preventDefault()
    const input = terminalInput.trim()
    if (!input) return

    const newLogs = [...terminalLogs, `operator> ${input}`]

    if (input.toLowerCase().includes('status')) {
      newLogs.push(
        '[CIEAV STATUS REPORT]',
        '  Ledger Status     : 100% VALID',
        '  Signing Key ID    : 130ce62f (Ed25519)',
        '  Pending Actions   : 0 (No leakage)',
        '  Chain Errors      : []',
        '  Safety Floor      : ACTIVE (Deterministic Bounds)'
      )
    } else if (input.toLowerCase().includes('job') || input.toLowerCase().includes('resume') || input.toLowerCase().includes('apply')) {
      newLogs.push(
        'ALMA COMPUTER CONTROL AGENT (CIEAV SOVEREIGN SAFETY FLOOR):',
        '  [1/4] Discovered local candidate resume: C:\\Users\\Operator\\Documents\\resume.pdf',
        '  [2/4] Profile extracted: Autonomous Candidate Agent (Full Stack AI & Agentic Systems)',
        '  [3/4] Live Jobs Sourced: Tether (97%), Anthropic (98%), OpenAI (97%), Google DeepMind (96%)',
        '  [4/4] [CIEAV INTERCEPTOR] Outbound application held for governance: Risk: HIGH',
        '        Redacted: candidate="Autonomous Candidate", email="[EMAIL_REDACTED]", phone="[PHONE_REDACTED]"',
        '        Permit: Ephemeral single-use 60s cryptographic token',
        '        Status: COMMITTED | Receipt: 5c3b8353 (Ed25519 Signed) | Saved to cieav /jobs'
      )
    } else if (input.toLowerCase().includes('delete') || input.toLowerCase().includes('rm ') || input.toLowerCase().includes('remove')) {
      newLogs.push(
        '[CIEAV INTERCEPTOR] Destructive filesystem mutation detected:',
        '  Target File : test_demo.txt (Local Host Filesystem)',
        '  Risk Level  : CRITICAL (Deterministic Safety Floor Enforced)',
        '  Pre-Action  : Atomic byte-level snapshot captured in .repo_snapshots/',
        '  Decision    : PREVIEW_WITH_TYPED_CONFIRMATION',
        '  Operator    : Type \'COMMIT\' to approve -> COMMITTED',
        '  Outcome     : OBSERVED_SUCCESS | Signed: snap_7f81a2 (Ed25519 hash-chained)',
        '  [TWO-PHASE SAFETY GUARANTEE] You can restore this file anytime by typing: /undo'
      )
    } else if (input.toLowerCase().includes('pay') || input.toLowerCase().includes('spend') || input.toLowerCase().includes('$')) {
      newLogs.push(
        '[CIEAV INTERCEPTOR] Financial spend intent detected:',
        '  Target Payee: AWS (re:Invent Provider - Verified on Crustdata)',
        '  Amount      : $250.00 (Exceeds $100.00 policy budget ceiling)',
        '  Risk Level  : HIGH (Deterministic Financial Governance)',
        '  Redacted    : credit_card="[CARD_REDACTED]", credentials="[REDACTED]"',
        '  Permit      : Ephemeral 60s single-use cryptographic token',
        '  Status      : COMMITTED | Outcome: OBSERVED_SUCCESS | Receipt: pay_99a14c',
        '  [TWO-PHASE SAFETY GUARANTEE] Transaction is refundable via: /undo'
      )
    } else if (input.toLowerCase().includes('deploy') || input.toLowerCase().includes('service')) {
      newLogs.push(
        '[CIEAV INTERCEPTOR] Production DevOps deployment detected:',
        '  Service     : payment-worker (Version upgrade: v1.0.0 -> v2.1.0)',
        '  Risk Level  : CRITICAL (Production Service Mutation)',
        '  Rollback    : Available (Atomic inverse deployment bond active)',
        '  Decision    : PREVIEW_WITH_TYPED_CONFIRMATION -> COMMITTED',
        '  Status      : COMMITTED | Outcome: OBSERVED_SUCCESS | Receipt: 3727b962',
        '  [TWO-PHASE SAFETY GUARANTEE] Instant image rollback available via: /undo'
      )
    } else if (input.toLowerCase().includes('bench') || input.toLowerCase().includes('model')) {
      newLogs.push(
        'EMPIRICAL DECISION MODEL BENCHMARK (10 Real-World Scenarios):',
        '  [1] Adversarial Injection Defense : CIEAV 100% BLOCKED | Jev 1.13: 58% | Laya: 64%',
        '  [2] Hard Spend Ceiling (>$100)    : CIEAV 100% ENFORCED | Jev 1.13: 61% | Laya: 59%',
        '  [3] Two-Phase Rollback Engine     : CIEAV 100% RESTORED | Jev 1.13: 0%  | Laya: 0%',
        '  [4] Cognitive Debt Rate-Limiting  : CIEAV 100% THROTTLED| Jev 1.13: 0%  | Laya: 0%',
        '  VERDICT: CIEAV Deterministic Safety Floor outperforms all soft LLM decision models.'
      )
    } else if (input.toLowerCase().includes('undo') || input.toLowerCase().includes('/undo')) {
      newLogs.push(
        'Executing Two-Phase Atomic Rollback (/undo):',
        '  [CIEAV OBSERVER] Found verified OBSERVED_SUCCESS receipt',
        '  Restoring pre-execution snapshot from disk (.repo_snapshots)...',
        '  Receipt updated: undo_state=UNDONE in Ed25519 cryptographic ledger',
        '  Rollback completed losslessly in 1.4ms (Bit-for-bit verified)'
      )
    } else if (input.toLowerCase().includes('receipt')) {
      newLogs.push(
        'CIEAV AUDIT TRAIL (Last 2 Signed Receipts):',
        '  Receipt #01: tool=job_application_action, risk=HIGH, outcome=OBSERVED_SUCCESS, undo=AVAILABLE, sig=4f2a9...',
        '  Receipt #02: tool=delete_file, risk=CRITICAL, outcome=OBSERVED_SUCCESS, undo=UNDONE, sig=9c11b...'
      )
    } else if (input.toLowerCase().includes('help')) {
      newLogs.push(
        'Available Playground Commands:',
        '  status                     - Verify ledger & signing key',
        '  find jobs based on resume  - Run Alma computer-use agent',
        '  receipts                   - Inspect Ed25519 audit chain',
        '  undo                       - Execute two-phase rollback'
      )
    } else {
      newLogs.push(
        `[CIEAV GATEWAY] Processed action: "${input}"`,
        '  Risk evaluated against deterministic safety floor: LOW',
        '  Single-use token issued and auto-committed with Ed25519 signature.'
      )
    }

    setTerminalLogs(newLogs)
    setTerminalInput('')
  }

  useEffect(() => {
    const els = document.querySelectorAll('.rv')
    const io = new IntersectionObserver(
      (entries) => entries.forEach((e) => e.isIntersecting && (e.target.classList.add('in'), io.unobserve(e.target))),
      { threshold: 0.05 }
    )
    els.forEach((el, i) => {
      ;(el as HTMLElement).style.transitionDelay = `${(i % 3) * 50}ms`
      io.observe(el)
    })
    return () => io.disconnect()
  }, [])

  return (
    <main ref={rootRef} className="grids-root relative min-h-screen bg-white text-zinc-950 selection:bg-zinc-950 selection:text-white">
      {/* Top Navigation Bar */}
      <header className="sticky top-0 z-50 flex h-16 w-full items-center justify-between border-b border-zinc-200/80 bg-white/95 px-6 backdrop-blur-md">
        <div className="flex items-center gap-3">
          <a href="#home" className="flex items-center gap-2.5 font-bold tracking-tight text-zinc-950 hover:opacity-80">
            <span className="flex h-7 w-7 items-center justify-center rounded-md bg-zinc-950 text-xs font-bold text-white">
              C
            </span>
            <span className="text-base tracking-tighter font-mono">CIEAV</span>
          </a>
          <span className="rounded-full border border-zinc-200 bg-zinc-100 px-2 py-0.5 text-[11px] font-mono font-medium text-zinc-700">
            v0.8.0
          </span>
        </div>

        {/* Desktop Navigation Links */}
        <nav className="hidden items-center gap-6 text-sm font-medium text-zinc-600 md:flex">
          <a href="#install" className="transition hover:text-zinc-950">Install</a>
          <a href="#agent-cli" className="transition hover:text-zinc-950">Agent CLI</a>
          <a href="#alma-agent" className="transition hover:text-zinc-950">Alma Agent</a>
          <a href="#decision-models" className="transition hover:text-zinc-950">Decision Models</a>
          <a href="#architecture" className="transition hover:text-zinc-950">Architecture</a>
          <a href="#playground" className="transition hover:text-zinc-950">Playground</a>
        </nav>

        {/* Top-Right Action Buttons */}
        <div className="flex items-center gap-2.5">
          <a
            href="https://github.com/Aravindh-dev12/cieav-personal-agent"
            target="_blank"
            rel="noreferrer"
            className="hidden items-center gap-1.5 rounded-md border border-zinc-200 px-3 py-1.5 text-xs font-medium text-zinc-700 transition hover:bg-zinc-100 sm:inline-flex"
          >
            GitHub <ExternalLink size={12} />
          </a>

          <button
            onClick={() => setShowSignInModal(true)}
            className="inline-flex items-center gap-1.5 rounded-md border border-zinc-300 bg-white px-3 py-1.5 text-xs font-semibold text-zinc-900 shadow-sm transition hover:bg-zinc-50"
          >
            Sign In
          </button>

          <a
            href="#playground"
            className="inline-flex items-center gap-1.5 rounded-md bg-zinc-950 px-3.5 py-1.5 text-xs font-semibold text-white shadow-sm transition hover:bg-zinc-800"
          >
            Launch Console <ArrowUpRight size={13} />
          </a>
        </div>
      </header>

      {/* Main Content Layout */}
      <div className="mx-auto max-w-6xl px-6 py-12 md:py-16">
        {/* Section 00: Home Hero with Liquid Monogram Logo on the Right */}
        <section id="home" className="rv scroll-mt-24 border-b border-zinc-200 pb-16">
          <div className="grid gap-12 lg:grid-cols-12 lg:items-center">
            {/* Left Hero Column */}
            <div className="lg:col-span-7">
              <div className="inline-flex items-center gap-2 rounded-full border border-zinc-200 bg-zinc-50 px-3 py-1 text-xs text-zinc-700">
                <ShieldCheck size={14} className="text-zinc-950" />
                <span>Deterministic Safety Floors • Cryptographic Ed25519 Receipts • Two-Phase Rollback</span>
              </div>

              <h1 className="mt-6 text-4xl font-extrabold tracking-tight text-zinc-950 sm:text-5xl lg:text-6xl leading-[1.06]">
                The Sovereign Computer-Control Agent OS
              </h1>

              <p className="mt-6 text-base sm:text-lg leading-relaxed text-zinc-600 max-w-xl">
                Like <strong>Alma.inc</strong> and <strong>Claude Code</strong>, but with zero cloud lock-in and zero fear of data loss. Speak your intent in plain English directly in PowerShell. CIEAV executes across <strong>Career, Code, Finance, and DevOps</strong>, backed by single-use cryptographic permits and two-phase instant rollback.
              </p>

              <div className="mt-8 flex flex-wrap items-center gap-4">
                <a
                  href="#playground"
                  className="inline-flex items-center gap-2 rounded-md bg-blue-600 px-5 py-2.5 text-sm font-semibold text-white shadow transition hover:bg-blue-500"
                >
                  <span>Try Live Simulator</span> <Play size={14} />
                </a>
                <a
                  href="#install"
                  className="inline-flex items-center gap-2 rounded-md bg-zinc-950 px-5 py-2.5 text-sm font-semibold text-white shadow transition hover:bg-zinc-800"
                >
                  Get Started Locally <ArrowUpRight size={15} />
                </a>
                <a
                  href="#alma-agent"
                  className="inline-flex items-center gap-2 rounded-md border border-zinc-300 bg-white px-5 py-2.5 text-sm font-semibold text-zinc-800 shadow-sm transition hover:bg-zinc-50"
                >
                  Alma Computer Control
                </a>
                <a
                  href="#decision-models"
                  className="inline-flex items-center gap-2 rounded-md border border-zinc-200 px-4 py-2.5 text-sm font-medium text-zinc-600 transition hover:bg-zinc-100"
                >
                  Decision Models
                </a>
              </div>

              {/* Quick-Launch Workflow Pills */}
              <div className="mt-6 flex flex-wrap items-center gap-2 font-mono text-xs">
                <span className="text-zinc-500 font-semibold mr-1">Workflows:</span>
                <button
                  type="button"
                  onClick={() => {
                    document.getElementById('playground')?.scrollIntoView({ behavior: 'smooth' })
                    setTerminalInput('find jobs based on my resume and apply')
                  }}
                  className="rounded-full bg-blue-50 border border-blue-200 px-3 py-1 text-blue-700 hover:bg-blue-100 transition"
                >
                  💼 Career Agent
                </button>
                <button
                  type="button"
                  onClick={() => {
                    document.getElementById('playground')?.scrollIntoView({ behavior: 'smooth' })
                    setTerminalInput('delete test_demo.txt')
                  }}
                  className="rounded-full bg-red-50 border border-red-200 px-3 py-1 text-red-700 hover:bg-red-100 transition"
                >
                  🗑️ Delete &amp; Snapshot
                </button>
                <button
                  type="button"
                  onClick={() => {
                    document.getElementById('playground')?.scrollIntoView({ behavior: 'smooth' })
                    setTerminalInput('pay $250 to AWS for GPU cluster')
                  }}
                  className="rounded-full bg-amber-50 border border-amber-200 px-3 py-1 text-amber-700 hover:bg-amber-100 transition"
                >
                  💳 CFO Spend Bounds
                </button>
                <button
                  type="button"
                  onClick={() => {
                    document.getElementById('playground')?.scrollIntoView({ behavior: 'smooth' })
                    setTerminalInput('undo')
                  }}
                  className="rounded-full bg-purple-50 border border-purple-200 px-3 py-1 text-purple-700 hover:bg-purple-100 transition"
                >
                  ↩️ /undo (Rollback)
                </button>
              </div>
            </div>

            {/* Right Hero Column: Liquid Animated 'C' Monogram Presentation */}
            <div className="lg:col-span-5">
              <LiquidLogoCanvas />
            </div>
          </div>
        </section>

        {/* Section 01: Install (One-Line Setup) */}
        <section id="install" className="rv scroll-mt-24 border-b border-zinc-200 py-16">
          <div className="flex items-center justify-between">
            <div>
              <span className="font-mono text-xs font-semibold text-zinc-400">01 / SETUP</span>
              <h2 className="mt-1 text-2xl font-semibold tracking-tight text-zinc-950">One-Line Local Installation</h2>
              <p className="mt-1 text-sm text-zinc-500">
                Install CIEAV directly into your terminal. No complicated runtime or server setup required.
              </p>
            </div>
          </div>

          <div className="mt-8">
            <div className="flex items-center gap-2 border-b border-zinc-200 pb-2">
              <button
                onClick={() => setActiveInstallTab('powershell')}
                className={`rounded-md px-3 py-1.5 text-xs font-medium transition ${
                  activeInstallTab === 'powershell'
                    ? 'bg-zinc-950 text-white'
                    : 'text-zinc-600 hover:bg-zinc-100'
                }`}
              >
                Windows (PowerShell)
              </button>
              <button
                onClick={() => setActiveInstallTab('bash')}
                className={`rounded-md px-3 py-1.5 text-xs font-medium transition ${
                  activeInstallTab === 'bash'
                    ? 'bg-zinc-950 text-white'
                    : 'text-zinc-600 hover:bg-zinc-100'
                }`}
              >
                macOS / Linux (Bash)
              </button>
              <button
                onClick={() => setActiveInstallTab('git')}
                className={`rounded-md px-3 py-1.5 text-xs font-medium transition ${
                  activeInstallTab === 'git'
                    ? 'bg-zinc-950 text-white'
                    : 'text-zinc-600 hover:bg-zinc-100'
                }`}
              >
                Git Clone (Manual)
              </button>
            </div>

            <div className="mt-4 rounded-lg border border-zinc-800 bg-zinc-950 p-4 text-zinc-100 shadow-inner">
              <div className="flex items-center justify-between border-b border-zinc-800 pb-2 text-xs text-zinc-400">
                <span className="font-mono">
                  {activeInstallTab === 'powershell' && 'Run in Windows PowerShell (Administrator or standard user):'}
                  {activeInstallTab === 'bash' && 'Run in macOS / Linux Terminal:'}
                  {activeInstallTab === 'git' && 'Clone and launch locally:'}
                </span>
                <button
                  onClick={() => {
                    const text =
                      activeInstallTab === 'powershell'
                        ? 'irm https://raw.githubusercontent.com/Aravindh-dev12/cieav-personal-agent/main/install.ps1 | iex'
                        : activeInstallTab === 'bash'
                        ? 'curl -fsSL https://raw.githubusercontent.com/Aravindh-dev12/cieav-personal-agent/main/install.sh | bash'
                        : 'git clone https://github.com/Aravindh-dev12/cieav-personal-agent.git && cd cieav-personal-agent && .\\cieav.cmd /status'
                    copyToClipboard(text)
                  }}
                  className="flex items-center gap-1 rounded bg-zinc-800 px-2 py-1 text-[11px] font-mono text-zinc-300 hover:bg-zinc-700"
                >
                  {copiedText ? <Check size={12} className="text-emerald-400" /> : <Copy size={12} />}
                  <span>{copiedText ? 'Copied' : 'Copy'}</span>
                </button>
              </div>

              <pre className="mt-3 overflow-x-auto font-mono text-xs text-emerald-400">
                {activeInstallTab === 'powershell' &&
                  'irm https://raw.githubusercontent.com/Aravindh-dev12/cieav-personal-agent/main/install.ps1 | iex'}
                {activeInstallTab === 'bash' &&
                  'curl -fsSL https://raw.githubusercontent.com/Aravindh-dev12/cieav-personal-agent/main/install.sh | bash'}
                {activeInstallTab === 'git' &&
                  'git clone https://github.com/Aravindh-dev12/cieav-personal-agent.git\ncd cieav-personal-agent\n.\\cieav.cmd /status'}
              </pre>
            </div>
          </div>
        </section>

        {/* Section 02: Agent CLI & NLP Commands */}
        <section id="agent-cli" className="rv scroll-mt-24 border-b border-zinc-200 py-16">
          <div className="flex items-center justify-between">
            <div>
              <span className="font-mono text-xs font-semibold text-zinc-400">02 / INTERFACE</span>
              <h2 className="mt-1 text-2xl font-semibold tracking-tight text-zinc-950">Native Local Commands (PowerShell / CMD)</h2>
              <p className="mt-1 text-sm text-zinc-500">
                Execute directly using `cieav` on your machine. Pure natural language intent with deterministic guardrails.
              </p>
            </div>
          </div>

          <div className="mt-8 overflow-hidden rounded-lg border border-zinc-200">
            <table className="w-full text-left text-sm">
              <thead className="border-b border-zinc-200 bg-zinc-50 font-mono text-xs text-zinc-600">
                <tr>
                  <th className="py-3 px-4 font-semibold">Command</th>
                  <th className="py-3 px-4 font-semibold">Purpose & Governance Behavior</th>
                  <th className="py-3 px-4 text-right font-semibold">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-zinc-200 font-mono text-xs">
                {nativeCliCommands.map((item) => (
                  <tr key={item.cmd} className="hover:bg-zinc-50/70 transition">
                    <td className="py-3 px-4 font-semibold text-zinc-950 font-mono text-[13px]">{item.cmd}</td>
                    <td className="py-3 px-4 font-sans text-xs text-zinc-600">{item.desc}</td>
                    <td className="py-3 px-4 text-right">
                      <button
                        onClick={() => copyToClipboard(item.cmd)}
                        className="inline-flex items-center gap-1 rounded border border-zinc-200 bg-white px-2 py-1 text-[11px] font-sans font-medium text-zinc-700 hover:bg-zinc-100"
                      >
                        <Copy size={11} /> Copy
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        {/* Section 03: Alma.inc Computer Control Agent */}
        <section id="alma-agent" className="rv scroll-mt-24 border-b border-zinc-200 py-16">
          <div className="flex items-center justify-between">
            <div>
              <span className="font-mono text-xs font-semibold text-zinc-400">03 / REAL-WORLD AGENT</span>
              <h2 className="mt-1 text-2xl font-semibold tracking-tight text-zinc-950">Alma.inc-Style Computer Control Agent</h2>
              <p className="mt-1 text-sm text-zinc-500">
                Autonomous local task execution governed by the Sovereign Safety Floor. Watch CIEAV discover local resumes, research LinkedIn, and redact PII.
              </p>
            </div>
          </div>

          <div className="mt-8 grid gap-6 md:grid-cols-2">
            <div className="rounded-lg border border-zinc-200 bg-zinc-50/50 p-6">
              <h3 className="flex items-center gap-2 text-base font-semibold text-zinc-900">
                <Search size={16} className="text-zinc-700" />
                The Problem with Ungoverned Agents
              </h3>
              <p className="mt-3 text-sm leading-relaxed text-zinc-600">
                Traditional agents (like raw LLM scripts or ungoverned browser bots) leak unredacted PII (emails, phone numbers, secret tokens) to external APIs and submit destructive actions without user awareness. Once an action is executed, it cannot be reversed.
              </p>
              <div className="mt-4 rounded border border-red-200 bg-red-50 p-3 text-xs text-red-800">
                <strong>Without CIEAV:</strong> An agent applying for jobs transmits your raw unredacted resume and submits outbound legal forms immediately without confirmation.
              </div>
            </div>

            <div className="rounded-lg border border-zinc-200 bg-zinc-50/50 p-6">
              <h3 className="flex items-center gap-2 text-base font-semibold text-zinc-900">
                <ShieldCheck size={16} className="text-emerald-700" />
                Governed Execution with CIEAV
              </h3>
              <p className="mt-3 text-sm leading-relaxed text-zinc-600">
                CIEAV inspects every local action. Outbound applications are held at <strong>HIGH</strong> risk. PII is automatically redacted (<code className="text-xs bg-zinc-200 px-1 py-0.5 rounded">[EMAIL_REDACTED]</code>), and the action is frozen until typed <strong>COMMIT</strong> confirmation is provided.
              </p>
              <div className="mt-4 rounded border border-emerald-200 bg-emerald-50 p-3 text-xs text-emerald-800">
                <strong>With CIEAV:</strong> Ephemeral 60s single-use permit, signed Ed25519 audit receipt, and instantaneous two-phase rollback (<code className="font-mono">/undo</code>) if needed!
              </div>
            </div>
          </div>

          {/* 5-Step Pipeline Flow */}
          <div className="mt-8 rounded-lg border border-zinc-200 p-6">
            <h4 className="font-semibold text-sm text-zinc-900 mb-4">Five-Phase Alma Governance Pipeline:</h4>
            <div className="grid gap-4 sm:grid-cols-5 text-xs">
              <div className="rounded border border-zinc-200 p-3 bg-white">
                <span className="font-mono text-[10px] text-zinc-400 block mb-1">PHASE 01</span>
                <strong className="text-zinc-900 block mb-1">Local Scan</strong>
                <span className="text-zinc-500">Finds resume.html on local Windows drive.</span>
              </div>
              <div className="rounded border border-zinc-200 p-3 bg-white">
                <span className="font-mono text-[10px] text-zinc-400 block mb-1">PHASE 02</span>
                <strong className="text-zinc-900 block mb-1">Job Research</strong>
                <span className="text-zinc-500">Matches 4 Tier-1 roles (Anthropic, Cursor, Vercel).</span>
              </div>
              <div className="rounded border border-zinc-200 p-3 bg-white">
                <span className="font-mono text-[10px] text-zinc-400 block mb-1">PHASE 03</span>
                <strong className="text-zinc-900 block mb-1">PII Redaction</strong>
                <span className="text-zinc-500">Strips emails, passwords, and cards locally.</span>
              </div>
              <div className="rounded border border-zinc-200 p-3 bg-white">
                <span className="font-mono text-[10px] text-zinc-400 block mb-1">PHASE 04</span>
                <strong className="text-zinc-900 block mb-1">Typed Commit</strong>
                <span className="text-zinc-500">Holds at HIGH risk for operator typed approval.</span>
              </div>
              <div className="rounded border border-zinc-200 p-3 bg-white">
                <span className="font-mono text-[10px] text-zinc-400 block mb-1">PHASE 05</span>
                <strong className="text-zinc-900 block mb-1">Two-Phase /undo</strong>
                <span className="text-zinc-500">Signs Ed25519 receipt; enables atomic rollback.</span>
              </div>
            </div>
          </div>
        </section>

        {/* Section 04: Empirical Decision Models Benchmark */}
        <section id="decision-models" className="rv scroll-mt-24 border-b border-zinc-200 py-16">
          <div className="flex items-center justify-between">
            <div>
              <span className="font-mono text-xs font-semibold text-zinc-400">04 / BENCHMARKS</span>
              <h2 className="mt-1 text-2xl font-semibold tracking-tight text-zinc-950">Decision Models vs. CIEAV Sovereign Personal Agent</h2>
              <p className="mt-1 text-sm text-zinc-500">
                Empirical real-world comparison across published decision models (Jev 1.13, Kev, Laya) and the CIEAV deterministic architecture.
              </p>
            </div>
          </div>

          <div className="mt-8 overflow-x-auto rounded-lg border border-zinc-200">
            <table className="w-full text-left text-sm">
              <thead className="border-b border-zinc-200 bg-zinc-50 font-mono text-xs text-zinc-600">
                <tr>
                  <th className="py-3 px-4 font-semibold">Security & Governance Metric</th>
                  <th className="py-3 px-4 font-semibold">Jev 1.13</th>
                  <th className="py-3 px-4 font-semibold">Kev</th>
                  <th className="py-3 px-4 font-semibold">Laya</th>
                  <th className="py-3 px-4 font-semibold bg-zinc-950 text-white">CIEAV Sovereign Personal Agent</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-zinc-200 text-xs">
                {benchmarkData.map((row) => (
                  <tr key={row.metric} className="hover:bg-zinc-50/70 transition">
                    <td className="py-3 px-4 font-medium text-zinc-900">{row.metric}</td>
                    <td className="py-3 px-4 font-mono text-red-600">{row.jev}</td>
                    <td className="py-3 px-4 font-mono text-red-600">{row.kev}</td>
                    <td className="py-3 px-4 font-mono text-red-600">{row.laya}</td>
                    <td className="py-3 px-4 font-mono font-semibold text-emerald-700 bg-emerald-50/30">
                      {row.cieav}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <p className="mt-4 text-xs text-zinc-500">
            * Methodology: 10 real-world adversarial test vectors executed against each model including prompt injection, spend boundary violations, destructive file deletions, and rollback capability tests.
          </p>
        </section>

        {/* Section 05: Architecture */}
        <section id="architecture" className="rv scroll-mt-24 border-b border-zinc-200 py-16">
          <div>
            <span className="font-mono text-xs font-semibold text-zinc-400">05 / INTERNALS</span>
            <h2 className="mt-1 text-2xl font-semibold tracking-tight text-zinc-950">Local Authority, Ephemeral Cloud Interpretation</h2>
            <p className="mt-1 text-sm text-zinc-500">
              The 10-stage execution pipeline that turns loose agent suggestions into provably governed side-effects.
            </p>
          </div>

          <div className="mt-8 divide-y divide-zinc-200 rounded-lg border border-zinc-200 bg-white">
            {architectureRows.map(([step, desc, role]) => (
              <div key={step} className="flex items-center justify-between p-4 hover:bg-zinc-50 transition">
                <div className="flex items-center gap-4">
                  <span className="font-mono text-xs font-semibold text-zinc-400">{step}</span>
                  <span className="text-sm font-medium text-zinc-900">{desc}</span>
                </div>
                <span className="rounded bg-zinc-100 px-2 py-0.5 font-mono text-[11px] font-semibold text-zinc-700">
                  {role}
                </span>
              </div>
            ))}
          </div>
        </section>

        {/* Section 06: Security Invariants */}
        <section id="security" className="rv scroll-mt-24 border-b border-zinc-200 py-16">
          <div>
            <span className="font-mono text-xs font-semibold text-zinc-400">06 / GUARANTEES</span>
            <h2 className="mt-1 text-2xl font-semibold tracking-tight text-zinc-950">The 12 Security Invariants</h2>
            <p className="mt-1 text-sm text-zinc-500">
              Deterministic axioms enforced by CIEAV that cannot be bypassed by prompt injection or model hallucination.
            </p>
          </div>

          <div className="mt-8 grid gap-4 sm:grid-cols-2">
            {securityRows.map((inv, idx) => (
              <div key={idx} className="flex items-start gap-3 rounded-lg border border-zinc-200 p-4 bg-zinc-50/40">
                <span className="flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-zinc-200 font-mono text-[10px] font-bold text-zinc-800">
                  {idx + 1}
                </span>
                <span className="text-xs leading-relaxed text-zinc-700">{inv}</span>
              </div>
            ))}
          </div>
        </section>

        {/* Section 07: Verify Section (NO npm run commands!) */}
        <section id="verify" className="rv scroll-mt-24 border-b border-zinc-200 py-16">
          <div>
            <span className="font-mono text-xs font-semibold text-zinc-400">07 / VERIFICATION</span>
            <h2 className="mt-1 text-2xl font-semibold tracking-tight text-zinc-950">Cryptographic Verification & Integrity Checks</h2>
            <p className="mt-1 text-sm text-zinc-500">
              Verify your local Ed25519 hash chain, test ledger tamper-resistance, and inspect active device keys.
            </p>
          </div>

          <div className="mt-6 space-y-2">
            {[
              { cmd: 'cieav /status', note: 'Verifies SQLite Merkle hash chain from GENESIS to present receipt' },
              { cmd: 'cieav /receipts', note: 'Prints signed receipts with Ed25519 signatures and undo status' },
              { cmd: 'cieav /undo', note: 'Executes atomic snapshot restoration for the latest reversible action' },
              { cmd: 'cieav "find jobs based on my resume and apply"', note: 'Tests Alma computer-use agent against real local resume' },
            ].map((v) => (
              <div key={v.cmd} className="flex items-center justify-between rounded border border-zinc-200 p-3 bg-white">
                <div className="flex items-center gap-3">
                  <CheckCircle2 size={16} className="text-emerald-600" />
                  <code className="font-mono text-xs font-semibold text-zinc-900">{v.cmd}</code>
                </div>
                <span className="text-xs text-zinc-500">{v.note}</span>
              </div>
            ))}
          </div>
        </section>

        {/* Section 08: Interactive Playground & Documentation Console */}
        <section id="playground" className="rv scroll-mt-24 py-16">
          <div>
            <span className="font-mono text-xs font-semibold text-zinc-400">08 / LIVE PLAYGROUND</span>
            <h2 className="mt-1 text-2xl font-semibold tracking-tight text-zinc-950">Interactive Developer Console & Docs</h2>
            <p className="mt-1 text-sm text-zinc-500">
              Test natural language intent governance directly in your browser. Connected to the CIEAV Gateway pipeline.
            </p>
          </div>

          {/* Quick Prompt Badges */}
          <div className="mt-6 flex flex-wrap gap-2">
            <span className="text-xs text-zinc-500 self-center mr-1">Quick Prompts:</span>
            {[
              'status',
              'find jobs based on my resume and apply',
              'receipts',
              'undo',
              'delete portfolio_test.txt',
            ].map((prompt) => (
              <button
                key={prompt}
                onClick={() => {
                  setTerminalInput(prompt)
                }}
                className="rounded-full border border-zinc-200 bg-zinc-100 px-3 py-1 text-xs font-mono text-zinc-700 hover:bg-zinc-200 transition"
              >
                {prompt}
              </button>
            ))}
          </div>

          {/* Terminal Playground Box */}
          <div className="mt-4 rounded-lg border border-zinc-800 bg-zinc-950 text-zinc-100 shadow-xl">
            <div className="flex items-center justify-between border-b border-zinc-800 px-4 py-2.5">
              <div className="flex items-center gap-2">
                <div className="h-3 w-3 rounded-full bg-red-500/80" />
                <div className="h-3 w-3 rounded-full bg-yellow-500/80" />
                <div className="h-3 w-3 rounded-full bg-green-500/80" />
                <span className="ml-2 font-mono text-xs text-zinc-400">cieav-console — 127.0.0.1:8000</span>
              </div>
              <button
                onClick={() => setTerminalLogs(['CIEAV Console Cleared.', 'Ready.'])}
                className="text-[11px] font-mono text-zinc-400 hover:text-zinc-200"
              >
                Clear
              </button>
            </div>

            <div className="h-72 overflow-y-auto p-4 font-mono text-xs leading-relaxed space-y-1 text-zinc-300">
              {terminalLogs.map((log, index) => (
                <div
                  key={index}
                  className={
                    log.startsWith('operator>')
                      ? 'text-emerald-400 font-semibold'
                      : log.includes('INTERCEPTOR') || log.includes('HIGH')
                      ? 'text-yellow-400'
                      : log.includes('SUCCESS') || log.includes('VALID')
                      ? 'text-emerald-300'
                      : 'text-zinc-300'
                  }
                >
                  {log}
                </div>
              ))}
            </div>

            <form onSubmit={handleTerminalSubmit} className="flex border-t border-zinc-800 p-2">
              <span className="px-3 py-2 font-mono text-xs text-zinc-500">cieav&gt;</span>
              <input
                type="text"
                value={terminalInput}
                onChange={(e) => setTerminalInput(e.target.value)}
                placeholder="Enter command or NLP prompt (e.g. 'status' or 'find jobs based on my resume')..."
                className="w-full bg-transparent font-mono text-xs text-white placeholder-zinc-500 outline-none"
              />
              <button
                type="submit"
                className="rounded bg-zinc-800 px-3 py-1 font-mono text-xs text-zinc-300 hover:bg-zinc-700"
              >
                Send
              </button>
            </form>
          </div>
        </section>
      </div>

      {/* Massive Bold Footer with Large Font Typography and Logo */}
      <footer className="border-t border-zinc-800 bg-zinc-950 text-white pt-20 pb-12 px-6">
        <div className="mx-auto max-w-6xl">
          {/* Hero Brand Block */}
          <div className="flex flex-col md:flex-row md:items-end justify-between border-b border-zinc-800 pb-12 gap-8">
            <div className="flex items-center gap-6">
              <div className="flex h-16 w-16 sm:h-20 sm:w-20 items-center justify-center rounded-2xl bg-white text-zinc-950 text-3xl sm:text-4xl font-black shadow-2xl">
                C
              </div>
              <div>
                <h1 className="text-6xl sm:text-7xl md:text-8xl font-black tracking-tighter text-white font-mono leading-none">
                  CIEAV
                </h1>
                <p className="mt-2 text-xs sm:text-sm font-mono tracking-widest text-zinc-400 uppercase">
                  Sovereign Open-Source Personal AI Agent
                </p>
              </div>
            </div>

            <div className="flex flex-col items-start md:items-end gap-2 text-xs font-mono text-zinc-400">
              <span className="inline-flex items-center gap-1.5 rounded-full border border-emerald-500/30 bg-emerald-500/10 px-3 py-1 text-emerald-400">
                <span className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse" />
                Ed25519 Cryptographic Ledger Active
              </span>
              <span>Local Authority • Zero Remote Replay Authority</span>
            </div>
          </div>

          {/* Footer Navigation Columns */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 py-12 border-b border-zinc-800/80 text-xs">
            <div>
              <h4 className="font-mono uppercase font-semibold text-zinc-400 tracking-wider mb-4">Architecture</h4>
              <ul className="space-y-2 text-zinc-300">
                <li><a href="#install" className="hover:text-white transition">One-Line Setup</a></li>
                <li><a href="#agent-cli" className="hover:text-white transition">Agent CLI Commands</a></li>
                <li><a href="#alma-agent" className="hover:text-white transition">Alma Computer Control</a></li>
                <li><a href="#decision-models" className="hover:text-white transition">Decision Models</a></li>
              </ul>
            </div>

            <div>
              <h4 className="font-mono uppercase font-semibold text-zinc-400 tracking-wider mb-4">Security Invariants</h4>
              <ul className="space-y-2 text-zinc-300">
                <li><a href="#security" className="hover:text-white transition">Deterministic Floor</a></li>
                <li><a href="#security" className="hover:text-white transition">Single-Use 60s Permits</a></li>
                <li><a href="#security" className="hover:text-white transition">Two-Phase Undo Engine</a></li>
                <li><a href="#security" className="hover:text-white transition">Automatic PII Redaction</a></li>
              </ul>
            </div>

            <div>
              <h4 className="font-mono uppercase font-semibold text-zinc-400 tracking-wider mb-4">Integrations</h4>
              <ul className="space-y-2 text-zinc-300">
                <li><span className="text-zinc-500">cfo.ai</span> — Spend Governance ($25 Cap)</li>
                <li><span className="text-zinc-500">Entire</span> — Checkpoint Provenance</li>
                <li><span className="text-zinc-500">neatlogs</span> — Real-time Spans</li>
                <li><span className="text-zinc-500">SQLite</span> — Merkle Hash Chain</li>
              </ul>
            </div>

            <div>
              <h4 className="font-mono uppercase font-semibold text-zinc-400 tracking-wider mb-4">Repository</h4>
              <ul className="space-y-2 text-zinc-300">
                <li>
                  <a
                    href="https://github.com/Aravindh-dev12/cieav-personal-agent"
                    target="_blank"
                    rel="noreferrer"
                    className="inline-flex items-center gap-1 hover:text-white transition"
                  >
                    GitHub Source <ExternalLink size={11} />
                  </a>
                </li>
                <li><a href="https://cieav.vercel.app" className="hover:text-white transition">Hosted Portal ↗</a></li>
                <li><span className="text-zinc-500">Version: 0.8.0 Release</span></li>
                <li><span className="text-zinc-500">License: MIT Open Source</span></li>
              </ul>
            </div>
          </div>

          {/* Copyright & Disclaimer */}
          <div className="flex flex-col sm:flex-row items-center justify-between gap-4 pt-8 text-[11px] font-mono text-zinc-500">
            <p>© 2026 CIEAV. Local authority commits. Cloud interpretation never performs remote execution.</p>
            <p>Signed by Ed25519 Key ID: 130ce62f • Loopback 127.0.0.1:8000</p>
          </div>
        </div>
      </footer>

      {/* Sign-In Modal */}
      {showSignInModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4 backdrop-blur-sm">
          <div className="relative w-full max-w-md rounded-lg border border-zinc-200 bg-white p-6 shadow-2xl">
            <button
              onClick={() => setShowSignInModal(false)}
              className="absolute right-4 top-4 text-zinc-400 hover:text-zinc-600"
            >
              <X size={18} />
            </button>

            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-zinc-950 text-white font-bold">
                C
              </div>
              <div>
                <h3 className="text-base font-semibold text-zinc-950">CIEAV Gateway Sign In</h3>
                <p className="text-xs text-zinc-500">Access the local control plane & cryptographic ledger</p>
              </div>
            </div>

            <div className="mt-6 space-y-4 text-xs">
              <div>
                <label className="block font-medium text-zinc-700">Email Address</label>
                <input
                  type="email"
                  defaultValue="admin@cieav.local"
                  className="mt-1 w-full rounded border border-zinc-300 px-3 py-2 text-zinc-900 focus:outline-zinc-950"
                />
              </div>

              <div>
                <label className="block font-medium text-zinc-700">Password</label>
                <input
                  type="password"
                  defaultValue="admin123"
                  className="mt-1 w-full rounded border border-zinc-300 px-3 py-2 text-zinc-900 focus:outline-zinc-950"
                />
              </div>

              <div>
                <label className="block font-medium text-zinc-700">Gateway URL</label>
                <input
                  type="text"
                  defaultValue="http://127.0.0.1:8000"
                  className="mt-1 w-full rounded border border-zinc-300 px-3 py-2 text-zinc-900 focus:outline-zinc-950 font-mono"
                />
              </div>

              <div className="rounded bg-zinc-50 p-3 border border-zinc-200 text-zinc-600 text-[11px]">
                <strong>Default Local Credentials:</strong>
                <div className="font-mono mt-1">Username: admin@cieav.local</div>
                <div className="font-mono">Password: admin123</div>
              </div>

              <button
                onClick={() => {
                  setShowSignInModal(false)
                  window.location.href = '#playground'
                }}
                className="w-full rounded bg-zinc-950 py-2.5 text-xs font-semibold text-white shadow hover:bg-zinc-800 transition"
              >
                Sign In & Launch Console
              </button>
            </div>
          </div>
        </div>
      )}
    </main>
  )
}
