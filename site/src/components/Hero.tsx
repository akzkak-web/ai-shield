import { useReducedMotion } from "motion/react";
import { motion } from "motion/react";
import { ArrowRight, FileSearch, Gauge, Wrench } from "lucide-react";
import { HERO_PROPS } from "../content";
import { mailto } from "../config";

const ICONS = [FileSearch, Wrench, Gauge];

function ProductVisual() {
  return (
    <div className="glass relative mx-auto mt-16 max-w-5xl overflow-hidden rounded-2xl shadow-[0_40px_120px_rgba(3,7,18,0.8)]">
      <div className="flex items-center justify-between border-b border-line/70 px-4 py-3">
        <div className="flex items-center gap-2">
          <span className="h-2.5 w-2.5 rounded-full bg-rose-400/80" />
          <span className="h-2.5 w-2.5 rounded-full bg-amber-400/80" />
          <span className="h-2.5 w-2.5 rounded-full bg-teal-400/80" />
          <span className="ml-3 font-mono text-xs text-dim">Assessment Console</span>
        </div>
        <span className="rounded-full border border-amber-400/40 px-2.5 py-0.5 font-mono text-[10.5px] tracking-wide text-amber-400">
          DEMO DATA
        </span>
      </div>

      <div className="grid gap-0 lg:grid-cols-[1.15fr_1fr]">
        <div className="border-b border-line/70 p-5 lg:border-b-0 lg:border-r">
          <div className="mb-3 flex items-center justify-between">
            <span className="text-[13px] font-medium text-mut">Environment topology</span>
            <span className="font-mono text-[11px] text-dim">scope: authorized target only</span>
          </div>
          <svg viewBox="0 0 420 240" className="w-full" role="img" aria-label="Assessment topology visualization">
            <defs>
              <linearGradient id="edge" x1="0" y1="0" x2="1" y2="0">
                <stop offset="0" stopColor="#2E7CF6" stopOpacity="0.65" />
                <stop offset="1" stopColor="#8B5CF6" stopOpacity="0.65" />
              </linearGradient>
            </defs>
            {[
              "M210 130 C 250 70, 300 60, 340 78",
              "M210 130 C 250 190, 300 200, 340 182",
              "M210 130 C 170 60, 110 60, 66 82",
              "M210 130 C 170 200, 110 200, 66 178",
            ].map((d) => (
              <path key={d} d={d} stroke="url(#edge)" strokeWidth="1.4" fill="none" strokeDasharray="5 5" />
            ))}
            <circle cx="210" cy="130" r="34" fill="rgba(46,124,246,0.12)" stroke="#2E7CF6" strokeWidth="1.5" />
            <circle cx="210" cy="130" r="8" fill="#4E8DFF" />
            <text x="210" y="185" textAnchor="middle" fill="#9AA7BC" fontSize="11" fontFamily="monospace">
              ollama : 11434
            </text>
            {[
              { x: 340, y: 78, label: "exposure", ok: false },
              { x: 340, y: 182, label: "auth", ok: false },
              { x: 66, y: 82, label: "cors", ok: true },
              { x: 66, y: 178, label: "cve", ok: true },
            ].map((n) => (
              <g key={n.label}>
                <circle cx={n.x} cy={n.y} r="5" fill={n.ok ? "#2DD4BF" : "#FBBF24"} />
                <text x={n.x} y={n.y - 12} textAnchor="middle" fill="#6B7688" fontSize="10" fontFamily="monospace">
                  {n.label}
                </text>
              </g>
            ))}
          </svg>
        </div>

        <div className="p-5">
          <div className="mb-3 flex items-center justify-between">
            <span className="text-[13px] font-medium text-mut">Checks</span>
            <span className="font-mono text-[11px] text-dim">6 supported</span>
          </div>
          <ul className="space-y-2">
            {[
              ["Network exposure", "pass"],
              ["Authentication", "unknown"],
              ["CORS policy", "pass"],
              ["Model API access", "unknown"],
              ["Rate limiting", "unknown"],
              ["Vulnerability match", "pass"],
            ].map(([name, status]) => (
              <li key={name} className="flex items-center justify-between rounded-lg bg-white/[0.04] px-3 py-1.5 text-[12.5px]">
                <span className="text-mut">{name}</span>
                <span
                  className={
                    status === "pass"
                      ? "font-mono text-[11px] text-teal-400"
                      : "font-mono text-[11px] text-dim"
                  }
                >
                  {status}
                </span>
              </li>
            ))}
          </ul>
          <div className="mt-4">
            <div className="mb-1.5 flex justify-between text-[11.5px] text-dim">
              <span>Coverage</span>
              <span>partial</span>
            </div>
            <div className="h-1.5 overflow-hidden rounded-full bg-white/10">
              <div className="h-full w-[62%] rounded-full bg-gradient-to-r from-brand-500 to-viol-500" />
            </div>
          </div>
        </div>
      </div>

      <div className="border-t border-line/70 p-4">
        <div className="flex flex-wrap items-center gap-x-6 gap-y-2 text-[12px] text-mut">
          <span className="font-mono text-dim">coverage: partial</span>
          <span className="font-mono text-dim">findings: 0 confirmed</span>
          <span className="font-mono text-dim">unknown checks reported, never treated as secure</span>
        </div>
      </div>
    </div>
  );
}

export function Hero() {
  const reduce = useReducedMotion();
  const enter = (delay: number) =>
    reduce
      ? {}
      : {
          initial: { opacity: 0, y: 18 },
          animate: { opacity: 1, y: 0 },
          transition: { duration: 0.65, delay, ease: [0.16, 1, 0.3, 1] as const },
        };

  return (
    <section className="relative overflow-hidden">
      <div className="grid-bg absolute inset-0" aria-hidden="true" />
      <div className="orb orb-a left-[-220px] top-[-160px] h-[480px] w-[480px] bg-brand-500/25" aria-hidden="true" />
      <div className="orb orb-b right-[-180px] top-[-80px] h-[420px] w-[420px] bg-viol-500/20" aria-hidden="true" />

      <div className="relative mx-auto max-w-7xl px-5 pb-24 pt-24 text-center lg:px-8 lg:pt-32">
        <motion.div {...enter(0)}>
          <span className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/[0.04] px-4 py-1.5 text-[12.5px] tracking-wide text-viol-300">
            <span className="h-1.5 w-1.5 rounded-full bg-teal-400" />
            AI INFRASTRUCTURE SECURITY
          </span>
        </motion.div>

        <motion.h1
          {...enter(0.08)}
          className="mx-auto mt-7 max-w-4xl text-[42px] font-bold leading-[1.08] tracking-[-0.025em] text-mist sm:text-6xl lg:text-[72px]"
        >
          Secure Your AI Infrastructure.
          <br />
          <span className="text-grad">Know What&apos;s Exposed. Understand What to Fix.</span>
        </motion.h1>

        <motion.p {...enter(0.16)} className="mx-auto mt-6 max-w-2xl text-[16.5px] leading-relaxed text-mut">
          AI Shield helps teams assess self-hosted AI environments, identify security
          misconfigurations, and turn technical findings into clear remediation actions.
        </motion.p>

        <motion.div {...enter(0.24)} className="mt-9 flex flex-wrap items-center justify-center gap-4">
          <a
            href={mailto("Security Assessment Request")}
            className="inline-flex items-center gap-2 rounded-full bg-gradient-to-r from-brand-500 to-viol-500 px-6 py-3 text-[15px] font-semibold text-white shadow-[0_10px_36px_rgba(46,124,246,0.4)] transition-transform hover:-translate-y-0.5"
          >
            Request a Security Assessment
            <ArrowRight size={17} />
          </a>
          <a
            href="#platform"
            className="inline-flex items-center gap-2 rounded-full border border-white/15 bg-white/[0.04] px-6 py-3 text-[15px] font-medium text-mist transition-colors hover:bg-white/[0.09]"
          >
            Explore the Platform
          </a>
        </motion.div>

        <motion.div {...enter(0.32)} className="mx-auto mt-8 flex max-w-3xl flex-wrap items-center justify-center gap-x-10 gap-y-3">
          {HERO_PROPS.map((label, i) => {
            const Icon = ICONS[i];
            return (
              <span key={label} className="flex items-center gap-2 text-[13.5px] text-mut">
                <Icon size={15} className="text-brand-400" />
                {label}
              </span>
            );
          })}
        </motion.div>

        <motion.div {...enter(0.4)}>
          <ProductVisual />
        </motion.div>
      </div>
    </section>
  );
}
