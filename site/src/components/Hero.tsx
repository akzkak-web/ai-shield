import { motion, useReducedMotion } from "motion/react";
import { ArrowRight, FileSearch, Gauge, Wrench } from "lucide-react";
import { mailto } from "../config";
import { useLanguage } from "../i18n/LanguageContext";

function ProductVisual() {
  const { c } = useLanguage();
  const consoleCopy = c.hero.console;
  const statuses = ["pass", "unknown", "pass", "unknown", "unknown", "pass"];
  const nodePositions = [
    { x: 340, y: 78 },
    { x: 340, y: 182 },
    { x: 66, y: 82 },
    { x: 66, y: 178 },
  ];

  return (
    <div className="card relative mx-auto mt-14 max-w-5xl overflow-hidden rounded-2xl">
      <div className="flex items-center justify-between border-b border-hair bg-white px-4 py-3">
        <div className="flex items-center gap-2">
          <span className="h-2.5 w-2.5 rounded-full bg-danger/50" />
          <span className="h-2.5 w-2.5 rounded-full bg-warning/60" />
          <span className="h-2.5 w-2.5 rounded-full bg-success/55" />
          <span className="ml-3 font-mono text-xs text-muted">{consoleCopy.title}</span>
        </div>
        <span className="rounded-full border border-warning/40 bg-warning/10 px-2.5 py-0.5 font-mono text-[10.5px] tracking-wide text-[#9a6a1f]">
          {consoleCopy.demo}
        </span>
      </div>

      <div className="grid lg:grid-cols-[1.15fr_1fr]">
        <div className="border-b border-hair bg-canvas/60 p-5 lg:border-b-0 lg:border-r">
          <div className="mb-3 flex flex-wrap items-center justify-between gap-2">
            <span className="text-[13px] font-medium text-body">{consoleCopy.topology}</span>
            <span className="font-mono text-[11px] text-muted">{consoleCopy.scope}</span>
          </div>
          <svg viewBox="0 0 420 240" className="w-full" role="img" aria-label={consoleCopy.topology}>
            <defs>
              <linearGradient id="hero-edge" x1="0" y1="0" x2="1" y2="0">
                <stop offset="0" stopColor="#3478F6" stopOpacity="0.45" />
                <stop offset="1" stopColor="#8B7CF6" stopOpacity="0.45" />
              </linearGradient>
            </defs>
            {[
              "M210 130 C 250 70, 300 60, 340 78",
              "M210 130 C 250 190, 300 200, 340 182",
              "M210 130 C 170 60, 110 60, 66 82",
              "M210 130 C 170 200, 110 200, 66 178",
            ].map((d) => (
              <path key={d} d={d} stroke="url(#hero-edge)" strokeWidth="1.4" fill="none" strokeDasharray="5 5" />
            ))}
            <circle cx="210" cy="130" r="34" fill="rgba(52,120,246,0.08)" stroke="#3478F6" strokeWidth="1.5" />
            <circle cx="210" cy="130" r="8" fill="#3478F6" />
            <text x="210" y="185" textAnchor="middle" fill="#64748B" fontSize="11" fontFamily="monospace">
              ollama : 11434
            </text>
            {nodePositions.map((node, i) => (
              <g key={consoleCopy.checkNames[i]}>
                <circle cx={node.x} cy={node.y} r="5" fill={i % 2 === 0 ? "#16A37A" : "#E6A23C"} />
                <text x={node.x} y={node.y - 12} textAnchor="middle" fill="#64748B" fontSize="10" fontFamily="monospace">
                  {c.platform.visual.nodes[i]}
                </text>
              </g>
            ))}
          </svg>
        </div>

        <div className="bg-white p-5">
          <div className="mb-3 flex items-center justify-between">
            <span className="text-[13px] font-medium text-body">{consoleCopy.checks}</span>
            <span className="font-mono text-[11px] text-muted">{consoleCopy.supported}</span>
          </div>
          <ul className="space-y-2">
            {consoleCopy.checkNames.map((name, i) => {
              const status = statuses[i];
              return (
                <li
                  key={name}
                  className="flex items-center justify-between rounded-lg border border-hair/70 bg-canvas px-3 py-1.5 text-[12.5px]"
                >
                  <span className="text-body">{name}</span>
                  <span
                    className={`font-mono text-[11px] ${
                      status === "pass" ? "text-success" : "text-muted"
                    }`}
                  >
                    {status === "pass" ? consoleCopy.pass : consoleCopy.unknown}
                  </span>
                </li>
              );
            })}
          </ul>
          <div className="mt-4">
            <div className="mb-1.5 flex justify-between text-[11.5px] text-muted">
              <span>{consoleCopy.coverage}</span>
              <span>{consoleCopy.coverageValue}</span>
            </div>
            <div className="h-1.5 overflow-hidden rounded-full bg-hair">
              <div className="h-full w-[62%] rounded-full bg-gradient-to-r from-primary to-secondary" />
            </div>
          </div>
        </div>
      </div>

      <div className="border-t border-hair bg-white p-4">
        <div className="flex flex-wrap items-center gap-x-6 gap-y-2 text-[12px] text-muted">
          {consoleCopy.footer.map((line) => (
            <span key={line} className="font-mono">
              {line}
            </span>
          ))}
        </div>
      </div>
    </div>
  );
}

const PROP_ICONS = [FileSearch, Wrench, Gauge];

export function Hero() {
  const { c } = useLanguage();
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
    <section className="relative overflow-hidden bg-canvas">
      <div className="grid-bg absolute inset-0" aria-hidden="true" />
      <div className="orb orb-a left-[-200px] top-[-180px] h-[460px] w-[460px] bg-primary/10" aria-hidden="true" />
      <div className="orb orb-b right-[-160px] top-[-60px] h-[400px] w-[400px] bg-secondary/10" aria-hidden="true" />

      <div className="relative mx-auto max-w-7xl px-5 pb-24 pt-24 text-center lg:px-8 lg:pt-28">
        <motion.div {...enter(0)}>
          <span className="inline-flex items-center gap-2 rounded-full border border-hair bg-white px-4 py-1.5 text-[12px] font-semibold tracking-[0.12em] text-primary">
            <span className="h-1.5 w-1.5 rounded-full bg-success" />
            {c.hero.badge}
          </span>
        </motion.div>

        <motion.h1
          {...enter(0.08)}
          className="mx-auto mt-7 max-w-4xl text-balance text-[40px] font-bold leading-[1.12] tracking-[-0.03em] text-heading sm:text-6xl lg:text-[68px]"
        >
          {c.hero.headline1}
          <br />
          <span className="text-grad">{c.hero.headline2}</span>
        </motion.h1>

        <motion.p {...enter(0.16)} className="mx-auto mt-6 max-w-2xl text-[16.5px] leading-relaxed text-muted">
          {c.hero.description}
        </motion.p>

        <motion.div {...enter(0.24)} className="mt-9 flex flex-wrap items-center justify-center gap-4">
          <a
            href={mailto(c.subjects.assessment)}
            className="inline-flex items-center gap-2 rounded-full bg-primary px-6 py-3 text-[15px] font-semibold text-white shadow-[0_8px_24px_rgba(52,120,246,0.3)] transition-colors hover:bg-primary-deep"
          >
            {c.hero.primaryCta}
            <ArrowRight size={17} />
          </a>
          <a
            href="#platform"
            className="inline-flex items-center gap-2 rounded-full border border-hair bg-white px-6 py-3 text-[15px] font-medium text-heading transition-colors hover:border-primary/40 hover:text-primary"
          >
            {c.hero.secondaryCta}
          </a>
        </motion.div>

        <motion.div {...enter(0.32)} className="mx-auto mt-8 flex max-w-5xl flex-wrap items-center justify-center gap-x-8 gap-y-3">
          {c.hero.props.map((label, i) => {
            const Icon = PROP_ICONS[i];
            return (
              <span key={label} className="flex items-center gap-2 text-[13.5px] text-body">
                <Icon size={15} className="text-primary" />
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
