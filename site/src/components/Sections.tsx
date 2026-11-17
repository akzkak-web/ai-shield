import { useState, type ReactNode } from "react";
import { motion, useReducedMotion } from "motion/react";
import {
  ArrowRight,
  Boxes,
  Building2,
  ChevronDown,
  Database,
  FileText,
  GitCompareArrows,
  ListOrdered,
  Network,
  ShieldCheck,
} from "lucide-react";
import { BrandMark } from "./BrandMark";
import {
  CAPABILITIES,
  FAQ,
  PLATFORM_CARDS,
  SOLUTIONS,
  STEPS,
  VALUE_PROPS,
} from "../content";
import { CONTACT_EMAIL, mailto } from "../config";

function Reveal({
  children,
  delay = 0,
  className,
}: {
  children: ReactNode;
  delay?: number;
  className?: string;
}) {
  const reduce = useReducedMotion();
  return (
    <motion.div
      className={className}
      initial={reduce ? false : { opacity: 0, y: 22 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: "-70px" }}
      transition={{ duration: 0.6, delay, ease: [0.16, 1, 0.3, 1] }}
    >
      {children}
    </motion.div>
  );
}

function SectionHead({ kicker, title, sub }: { kicker: string; title: string; sub?: string }) {
  return (
    <div className="mx-auto max-w-2xl text-center">
      <span className="text-[12.5px] font-semibold uppercase tracking-[0.16em] text-viol-400">{kicker}</span>
      <h2 className="mt-3 text-[32px] font-bold leading-tight tracking-[-0.02em] text-mist sm:text-[42px]">
        {title}
      </h2>
      {sub && <p className="mt-4 text-[16px] leading-relaxed text-mut">{sub}</p>}
    </div>
  );
}

const VALUE_ICONS = [Network, ShieldCheck, ListOrdered];

export function TrustStrip() {
  return (
    <section className="border-t border-line/60 bg-ink-900/60">
      <div className="mx-auto max-w-7xl px-5 py-16 lg:px-8">
        <SectionHead
          kicker="Why AI Shield"
          title="Visibility Into Your AI Infrastructure Security"
        />
        <div className="mx-auto mt-12 grid max-w-5xl gap-5 md:grid-cols-3">
          {VALUE_PROPS.map((item, i) => {
            const Icon = VALUE_ICONS[i];
            return (
              <Reveal key={item.title} delay={i * 0.08}>
                <div className="glass h-full rounded-2xl p-6">
                  <div className="mb-4 flex h-11 w-11 items-center justify-center rounded-xl bg-brand-500/15 text-brand-400">
                    <Icon size={20} />
                  </div>
                  <h3 className="text-[17px] font-semibold text-mist">{item.title}</h3>
                  <p className="mt-2 text-[14.5px] leading-relaxed text-mut">{item.body}</p>
                </div>
              </Reveal>
            );
          })}
        </div>
      </div>
    </section>
  );
}

function CardVisual({ kind }: { kind: string }) {
  if (kind === "exposure") {
    return (
      <div className="relative flex h-40 items-center justify-center overflow-hidden rounded-xl border border-line/70 bg-ink-950/60">
        <div className="absolute inset-0 grid-bg opacity-60" />
        <svg width="220" height="130" viewBox="0 0 220 130" role="img" aria-label="Exposure boundary visualization">
          <circle cx="110" cy="65" r="42" fill="none" stroke="#2E7CF6" strokeOpacity="0.5" strokeDasharray="4 4" />
          <circle cx="110" cy="65" r="12" fill="rgba(78,141,255,0.25)" stroke="#4E8DFF" />
          <circle cx="44" cy="38" r="5" fill="#A78BFA" />
          <circle cx="178" cy="96" r="5" fill="#FB7185" />
          <path d="M44 38 C 72 40, 92 52, 102 62 M178 96 C 150 92, 128 82, 118 72" stroke="#6B7688" strokeWidth="1.2" />
        </svg>
      </div>
    );
  }
  if (kind === "config") {
    return (
      <div className="flex h-40 flex-col justify-center gap-2.5 rounded-xl border border-line/70 bg-ink-950/60 p-5">
        {[
          ["Authentication", "unknown", "text-dim"],
          ["CORS policy", "pass", "text-teal-400"],
          ["Model API access", "unknown", "text-dim"],
        ].map(([label, status, cls]) => (
          <div key={label} className="flex items-center justify-between rounded-lg bg-white/[0.04] px-3 py-2 text-[12.5px]">
            <span className="text-mut">{label}</span>
            <span className={`font-mono text-[11px] ${cls}`}>{status}</span>
          </div>
        ))}
      </div>
    );
  }
  return (
    <div className="flex h-40 flex-col items-center justify-center gap-3 rounded-xl border border-line/70 bg-ink-950/60">
      <div className="rounded-lg border border-line bg-white/[0.04] px-3 py-1.5 font-mono text-[13px] text-brand-300">
        ollama · v0.40.4
      </div>
      <div className="flex items-center gap-2 rounded-lg border border-teal-400/30 bg-teal-400/10 px-3 py-1.5 text-[12px] text-teal-400">
        no affected advisories
      </div>
    </div>
  );
}

export function Platform() {
  return (
    <section id="platform" className="mx-auto max-w-7xl px-5 py-24 lg:px-8">
      <SectionHead
        kicker="Platform"
        title="A Clearer View of Your AI Security Posture"
        sub="Three lenses on the environments you run: what is reachable, what is misconfigured, and what is known to be vulnerable."
      />
      <div className="mt-14 grid gap-5 md:grid-cols-3">
        {PLATFORM_CARDS.map((card, i) => (
          <Reveal key={card.title} delay={i * 0.08}>
            <div className="glass group h-full rounded-2xl p-5">
              <CardVisual kind={card.visual} />
              <h3 className="mt-5 text-[17px] font-semibold text-mist">{card.title}</h3>
              <p className="mt-2 text-[14.5px] leading-relaxed text-mut">{card.body}</p>
            </div>
          </Reveal>
        ))}
      </div>
    </section>
  );
}

export function HowItWorks() {
  return (
    <section id="how-it-works" className="border-t border-line/60 bg-ink-900/40">
      <div className="mx-auto max-w-7xl px-5 py-24 lg:px-8">
        <SectionHead
          kicker="Process"
          title="From Assessment to Action in Three Steps"
        />
        <div className="relative mx-auto mt-14 max-w-5xl">
          <div className="hairline-top absolute left-[16.6%] right-[16.6%] top-6 hidden md:block" />
          <div className="grid gap-10 md:grid-cols-3 md:gap-6">
            {STEPS.map((step, i) => (
              <Reveal key={step.title} delay={i * 0.1}>
                <div className="relative text-center">
                  <div className="relative z-10 mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-gradient-to-br from-brand-500 to-viol-500 text-[17px] font-bold text-white shadow-[0_6px_24px_rgba(46,124,246,0.4)]">
                    {i + 1}
                  </div>
                  <h3 className="mt-5 text-[17px] font-semibold text-mist">{step.title}</h3>
                  <p className="mx-auto mt-2 max-w-xs text-[14.5px] leading-relaxed text-mut">{step.body}</p>
                </div>
              </Reveal>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}

export function Capabilities() {
  return (
    <section className="mx-auto max-w-7xl px-5 py-24 lg:px-8">
      <SectionHead
        kicker="Capabilities"
        title="Built for Real-World AI Deployments"
      />
      <div className="mt-14 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {CAPABILITIES.map((cap, i) => (
          <Reveal key={cap.name} delay={(i % 3) * 0.06}>
            <div className="glass h-full rounded-2xl p-5">
              <div className="flex items-start justify-between gap-3">
                <h3 className="text-[15.5px] font-semibold text-mist">{cap.name}</h3>
                <span
                  className={`shrink-0 rounded-full border px-2.5 py-0.5 text-[10.5px] font-medium ${
                    cap.status === "Verified"
                      ? "border-teal-400/35 bg-teal-400/10 text-teal-400"
                      : "border-line bg-white/[0.04] text-dim"
                  }`}
                >
                  {cap.status}
                </span>
              </div>
              <p className="mt-2 text-[13.5px] leading-relaxed text-mut">{cap.body}</p>
            </div>
          </Reveal>
        ))}
      </div>
      <p className="mx-auto mt-8 max-w-3xl text-center text-[13.5px] leading-relaxed text-dim">
        Ollama is the validated assessment target for the initial release. Detection exists for
        additional inference services, but real-environment verification is ongoing. Verified checks
        have completed real-service integration testing; supported capabilities ship with today&apos;s product.
      </p>
    </section>
  );
}

function ReportMockup() {
  return (
    <div className="relative mx-auto w-full max-w-md">
      <div className="absolute -inset-4 rounded-3xl bg-gradient-to-br from-brand-500/25 to-viol-500/20 blur-2xl" aria-hidden="true" />
      <div className="relative overflow-hidden rounded-2xl border border-white/10 bg-gradient-to-b from-[#F6F8FC] to-[#E9EEF6] text-ink-950 shadow-[0_36px_90px_rgba(3,7,18,0.75)]">
        <div className="flex items-center justify-between border-b border-ink-950/10 bg-white/70 px-5 py-3">
          <span className="text-[12.5px] font-semibold tracking-wide text-ink-700">AI SHIELD ASSESSMENT REPORT</span>
          <span className="rounded-full bg-amber-400/20 px-2 py-0.5 text-[10px] font-semibold text-amber-600">
            DEMONSTRATION DATA
          </span>
        </div>
        <div className="space-y-4 p-5">
          <div className="flex items-center justify-between text-[12px] text-ink-700">
            <span className="font-mono">engagement: AISHIELD-DEMO-001</span>
            <span className="font-mono">target: authorized</span>
          </div>
          <div>
            <p className="mb-2 text-[11px] font-semibold uppercase tracking-wide text-ink-700">Risk summary</p>
            <div className="space-y-1.5">
              {[
                ["Critical", 1, "bg-[#DC2626]"],
                ["High", 1, "bg-[#EA580C]"],
                ["Medium", 1, "bg-[#D97706]"],
                ["Low", 0, "bg-[#65A30D]"],
              ].map(([label, count, color]) => (
                <div key={label} className="flex items-center gap-3">
                  <span className="w-16 text-[11.5px] text-ink-700">{label}</span>
                  <div className="h-1.5 flex-1 overflow-hidden rounded-full bg-ink-950/10">
                    <div className={`h-full rounded-full ${color}`} style={{ width: `${(count as number) * 100}%` }} />
                  </div>
                  <span className="w-4 text-right font-mono text-[11px] text-ink-700">{count}</span>
                </div>
              ))}
            </div>
          </div>
          <div className="rounded-xl border border-ink-950/10 bg-white p-4">
            <div className="flex items-center justify-between">
              <span className="text-[12.5px] font-semibold">AUTH-001 · Missing authentication</span>
              <span className="rounded-md bg-[#DC2626] px-2 py-0.5 text-[10px] font-semibold text-white">CRITICAL</span>
            </div>
            <p className="mt-2 font-mono text-[10.5px] leading-relaxed text-ink-700">
              evidence: accessible_endpoints=[&apos;/v1/models&apos;, &apos;/api/tags&apos;]
            </p>
            <p className="mt-2 text-[11.5px] leading-relaxed text-ink-700">
              remediation: enable API-key authentication, or add authentication at a reverse proxy.
            </p>
          </div>
          <div className="rounded-xl border border-ink-950/10 bg-white p-4">
            <div className="flex items-center justify-between text-[11.5px]">
              <span className="font-semibold">Coverage</span>
              <span className="font-mono text-ink-700">partial · 3 checks unverified</span>
            </div>
            <p className="mt-2 text-[11px] leading-relaxed text-ink-700">
              Limitations: read-only assessment. Unknown checks are reported, never treated as secure.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

export function ReportPreview() {
  return (
    <section id="report" className="border-t border-line/60 bg-ink-900/40">
      <div className="mx-auto grid max-w-7xl items-center gap-14 px-5 py-24 lg:grid-cols-2 lg:px-8">
        <Reveal>
          <div>
            <span className="text-[12.5px] font-semibold uppercase tracking-[0.16em] text-viol-400">Report</span>
            <h2 className="mt-3 text-[32px] font-bold leading-tight tracking-[-0.02em] text-mist sm:text-[42px]">
              Security Findings You Can Actually Act On.
            </h2>
            <p className="mt-4 max-w-lg text-[16px] leading-relaxed text-mut">
              Every assessment ends with a structured report: risk summary, finding severity,
              supporting evidence, coverage and limitations, and remediation recommendations.
            </p>
            <ul className="mt-6 space-y-2.5 text-[14.5px] text-mut">
              <li className="flex gap-2.5"><FileText size={17} className="mt-0.5 shrink-0 text-brand-400" />Assessment overview and risk summary</li>
              <li className="flex gap-2.5"><ShieldCheck size={17} className="mt-0.5 shrink-0 text-teal-400" />Findings with severity and evidence</li>
              <li className="flex gap-2.5"><GitCompareArrows size={17} className="mt-0.5 shrink-0 text-viol-400" />Coverage, limitations and remediation guidance</li>
            </ul>
            <a
              href="/assets/demo-assessment-report.pdf"
              className="mt-8 inline-flex items-center gap-2 rounded-full bg-gradient-to-r from-brand-500 to-viol-500 px-6 py-3 text-[15px] font-semibold text-white shadow-[0_10px_36px_rgba(46,124,246,0.4)] transition-transform hover:-translate-y-0.5"
            >
              See a Sample Assessment Report
              <ArrowRight size={17} />
            </a>
          </div>
        </Reveal>
        <Reveal delay={0.1}>
          <ReportMockup />
        </Reveal>
      </div>
    </section>
  );
}

const SOLUTION_ICONS = [Building2, Network, Boxes, Database];

export function Solutions() {
  return (
    <section id="solutions" className="mx-auto max-w-7xl px-5 py-24 lg:px-8">
      <SectionHead
        kicker="Solutions"
        title="Security Confidence Across AI Deployments"
      />
      <div className="mt-14 grid gap-5 sm:grid-cols-2">
        {SOLUTIONS.map((item, i) => {
          const Icon = SOLUTION_ICONS[i];
          return (
            <Reveal key={item.title} delay={(i % 2) * 0.08}>
              <div className="glass flex h-full items-start gap-4 rounded-2xl p-6">
                <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-viol-500/15 text-viol-400">
                  <Icon size={20} />
                </div>
                <div>
                  <h3 className="text-[16.5px] font-semibold text-mist">{item.title}</h3>
                  <p className="mt-2 text-[14.5px] leading-relaxed text-mut">{item.body}</p>
                </div>
              </div>
            </Reveal>
          );
        })}
      </div>
    </section>
  );
}

export function Pricing() {
  return (
    <section id="pricing" className="border-t border-line/60 bg-ink-900/40">
      <div className="mx-auto max-w-7xl px-5 py-24 lg:px-8">
        <SectionHead
          kicker="Pricing"
          title="Straightforward Security Assessment Pricing"
        />
        <div className="mx-auto mt-14 grid max-w-4xl gap-6 md:grid-cols-2">
          <Reveal>
            <div className="rounded-3xl bg-gradient-to-br from-brand-500/60 via-viol-500/30 to-white/5 p-px shadow-[0_24px_80px_rgba(5,9,22,0.7)]">
              <div className="flex h-full flex-col rounded-[calc(1.5rem-1px)] bg-ink-900 p-7">
                <div className="flex items-center justify-between">
                  <span className="rounded-full border border-viol-400/40 px-3 py-1 text-[11.5px] tracking-wide text-viol-300">
                    AI SHIELD QUICK CHECK
                  </span>
                </div>
                <div className="mt-5 flex items-baseline gap-1.5">
                  <span className="text-5xl font-bold tracking-tight text-mist">¥399</span>
                  <span className="text-[14px] text-mut">/ assessment</span>
                </div>
                <p className="mt-3 text-[14px] leading-relaxed text-mut">
                  A focused security baseline assessment for one authorized Ollama environment.
                </p>
                <ul className="mt-6 flex-1 space-y-2.5 text-[14px] text-mut">
                  {[
                    "Six supported assessment checks",
                    "Technical evidence review",
                    "Security findings summary",
                    "Chinese PDF report",
                    "Remediation recommendations",
                    "One retest within the agreed scope",
                  ].map((item) => (
                    <li key={item} className="flex gap-2.5">
                      <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-teal-400" />
                      {item}
                    </li>
                  ))}
                </ul>
                <a
                  href={mailto("Quick Check Assessment Request")}
                  className="mt-7 inline-flex items-center justify-center gap-2 rounded-full bg-gradient-to-r from-brand-500 to-viol-500 px-5 py-3 text-[14.5px] font-semibold text-white transition-transform hover:-translate-y-0.5"
                >
                  Request an Assessment
                </a>
              </div>
            </div>
          </Reveal>
          <Reveal delay={0.08}>
            <div className="glass flex h-full flex-col rounded-3xl p-7">
              <span className="rounded-full border border-line px-3 py-1 text-[11.5px] tracking-wide text-dim">
                ENTERPRISE / CUSTOM
              </span>
              <h3 className="mt-5 text-[22px] font-semibold text-mist">Custom Assessment</h3>
              <p className="mt-3 text-[14px] leading-relaxed text-mut">
                For multiple environments, retainer engagements, or an expanded scope agreed in writing.
              </p>
              <ul className="mt-6 flex-1 space-y-2.5 text-[14px] text-mut">
                <li className="flex gap-2.5"><span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-brand-400" />Multiple authorized targets</li>
                <li className="flex gap-2.5"><span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-brand-400" />Tailored check selection</li>
                <li className="flex gap-2.5"><span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-brand-400" />Extended reporting and retesting</li>
              </ul>
              <a
                href={mailto("Custom Assessment Inquiry")}
                className="mt-7 inline-flex items-center justify-center gap-2 rounded-full border border-white/15 bg-white/[0.04] px-5 py-3 text-[14.5px] font-medium text-mist transition-colors hover:bg-white/[0.09]"
              >
                Contact Sales
              </a>
            </div>
          </Reveal>
        </div>
        <p className="mx-auto mt-8 max-w-2xl text-center text-[13.5px] leading-relaxed text-dim">
          Scope and exclusions are defined in writing before every engagement. AI Shield delivers a
          focused security baseline assessment; it is not comprehensive penetration testing, and no
          recurring subscriptions or automated billing are implied.
        </p>
      </div>
    </section>
  );
}

export function FAQSection() {
  const [open, setOpen] = useState<number | null>(0);
  return (
    <section id="faq" className="mx-auto max-w-4xl px-5 py-24 lg:px-8">
      <SectionHead kicker="FAQ" title="Frequently Asked Questions" />
      <div className="mt-12 space-y-3">
        {FAQ.map((item, i) => (
          <div key={item.q} className="glass overflow-hidden rounded-2xl">
            <button
              type="button"
              onClick={() => setOpen(open === i ? null : i)}
              aria-expanded={open === i}
              className="flex w-full items-center justify-between gap-4 px-6 py-4 text-left"
            >
              <span className="text-[15.5px] font-medium text-mist">{item.q}</span>
              <ChevronDown
                size={18}
                className={`shrink-0 text-mut transition-transform ${open === i ? "rotate-180" : ""}`}
              />
            </button>
            {open === i && (
              <p className="border-t border-line/60 px-6 py-4 text-[14.5px] leading-relaxed text-mut">
                {item.a}
              </p>
            )}
          </div>
        ))}
      </div>
    </section>
  );
}

export function FinalCTA() {
  return (
    <section className="relative overflow-hidden border-t border-line/60">
      <div className="absolute inset-0 bg-[radial-gradient(640px_320px_at_18%_18%,rgba(46,124,246,0.22),transparent_62%),radial-gradient(560px_300px_at_82%_82%,rgba(139,92,246,0.2),transparent_62%)]" aria-hidden="true" />
      <div className="relative mx-auto max-w-4xl px-5 py-24 text-center lg:px-8">
        <h2 className="text-[34px] font-bold leading-tight tracking-[-0.02em] text-mist sm:text-[46px]">
          Make Your AI Infrastructure More Secure.
        </h2>
        <p className="mx-auto mt-4 max-w-xl text-[16px] leading-relaxed text-mut">
          Get a clearer understanding of your AI deployment security posture with an
          evidence-based assessment.
        </p>
        <div className="mt-8 flex flex-wrap items-center justify-center gap-4">
          <a
            href={mailto("Security Assessment Request")}
            className="inline-flex items-center gap-2 rounded-full bg-gradient-to-r from-brand-500 to-viol-500 px-6 py-3 text-[15px] font-semibold text-white shadow-[0_10px_36px_rgba(46,124,246,0.4)] transition-transform hover:-translate-y-0.5"
          >
            Request a Security Assessment
            <ArrowRight size={17} />
          </a>
          <a
            href={mailto("Contact the AI Shield Team")}
            className="inline-flex items-center gap-2 rounded-full border border-white/15 bg-white/[0.04] px-6 py-3 text-[15px] font-medium text-mist transition-colors hover:bg-white/[0.09]"
          >
            Contact Our Team
          </a>
        </div>
      </div>
    </section>
  );
}

export function Footer() {
  return (
    <footer id="contact" className="border-t border-line/60 bg-[#070b14]">
      <div className="mx-auto max-w-7xl px-5 py-16 lg:px-8">
        <div className="grid gap-10 md:grid-cols-[1.4fr_1fr_1fr_1fr_1.2fr]">
          <div>
            <div className="flex items-center gap-2.5 text-[15px] font-semibold text-mist">
              <BrandMark size={28} />
              AI Shield
            </div>
            <p className="mt-4 max-w-xs text-[13.5px] leading-relaxed text-dim">
              Evidence-based security assessments for self-hosted AI inference environments.
            </p>
          </div>
          <FooterCol
            title="Product"
            links={[
              ["Platform", "#platform"],
              ["Security Assessment", "#how-it-works"],
              ["Pricing", "#pricing"],
            ]}
          />
          <FooterCol
            title="Solutions"
            links={SOLUTIONS.map((s) => [s.title, "#solutions"] as [string, string])}
          />
          <FooterCol
            title="Resources"
            links={[
              ["Sample Report", "#report"],
              ["FAQ", "#faq"],
              ["Privacy Policy", "#legal"],
              ["Terms of Service", "#legal"],
            ]}
          />
          <div>
            <h4 className="text-[13px] font-semibold uppercase tracking-wide text-mut">Contact</h4>
            <ul className="mt-4 space-y-2.5 text-[13.5px] text-dim">
              <li><a href={`mailto:${CONTACT_EMAIL}`} className="transition-colors hover:text-mist">{CONTACT_EMAIL}</a></li>
              <li>Assessments run on authorized targets only.</li>
            </ul>
          </div>
        </div>
        <div className="mt-12 flex flex-col gap-3 border-t border-line/60 pt-6 text-[12.5px] text-dim sm:flex-row sm:items-center sm:justify-between">
          <span>© 2026 AI Shield. All rights reserved.</span>
          <div className="flex gap-6">
            <a href="#legal" className="transition-colors hover:text-mist">Privacy Policy</a>
            <a href="#legal" className="transition-colors hover:text-mist">Terms of Service</a>
          </div>
        </div>
      </div>
    </footer>
  );
}

function FooterCol({ title, links }: { title: string; links: [string, string][] }) {
  return (
    <div>
      <h4 className="text-[13px] font-semibold uppercase tracking-wide text-mut">{title}</h4>
      <ul className="mt-4 space-y-2.5 text-[13.5px] text-dim">
        {links.map(([label, href]) => (
          <li key={label}>
            <a href={href} className="transition-colors hover:text-mist">{label}</a>
          </li>
        ))}
      </ul>
    </div>
  );
}

export function Legal() {
  return (
    <section id="legal" className="border-t border-line/60 bg-ink-900/40">
      <div className="mx-auto max-w-4xl px-5 py-16 lg:px-8">
        <h2 className="text-[24px] font-semibold text-mist">Legal</h2>
        <div className="mt-6 grid gap-8 md:grid-cols-2">
          <div>
            <h3 className="text-[16px] font-semibold text-mist">Privacy Policy</h3>
            <p className="mt-3 text-[13.5px] leading-relaxed text-dim">
              Initial draft. AI Shield processes contact information provided through email
              inquiries solely to respond to assessment requests. Assessments operate on authorized
              targets and do not collect customer model data or model content.
            </p>
          </div>
          <div>
            <h3 className="text-[16px] font-semibold text-mist">Terms of Service</h3>
            <p className="mt-3 text-[13.5px] leading-relaxed text-dim">
              Initial draft. Every engagement requires written authorization and a confirmed scope.
              Assessment results reflect observations at the time of testing and are not a
              long-term security guarantee. Legal counsel should finalize these documents before launch.
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}
