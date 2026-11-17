import { useState, type ReactNode } from "react";
import { motion, useReducedMotion } from "motion/react";
import {
  ArrowRight,
  Boxes,
  Building2,
  Check,
  ChevronDown,
  Database,
  FileText,
  GitCompareArrows,
  ListOrdered,
  Network,
  ShieldCheck,
} from "lucide-react";
import { BrandMark } from "./BrandMark";
import { CONTACT_EMAIL, mailto } from "../config";
import { useLanguage } from "../i18n/LanguageContext";
import type { TextPair } from "../content";

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
      <span className="text-[12px] font-semibold uppercase tracking-[0.16em] text-primary">{kicker}</span>
      <h2 className="mt-3 text-balance text-[30px] font-bold leading-tight tracking-[-0.025em] text-heading sm:text-[40px]">
        {title}
      </h2>
      {sub && <p className="mt-4 text-[16px] leading-relaxed text-muted">{sub}</p>}
    </div>
  );
}

const VALUE_ICONS = [Network, ShieldCheck, ListOrdered];

export function TrustStrip() {
  const { c } = useLanguage();
  return (
    <section className="border-y border-hair bg-white">
      <div className="mx-auto max-w-7xl px-5 py-20 lg:px-8">
        <SectionHead kicker={c.trust.kicker} title={c.trust.title} />
        <div className="mx-auto mt-12 grid max-w-5xl gap-5 md:grid-cols-3">
          {c.trust.items.map((item: TextPair, i: number) => {
            const Icon = VALUE_ICONS[i];
            return (
              <Reveal key={item.title} delay={i * 0.08}>
                <div className="card h-full rounded-2xl p-6">
                  <div className="mb-4 flex h-11 w-11 items-center justify-center rounded-xl bg-soft text-primary">
                    <Icon size={20} />
                  </div>
                  <h3 className="text-[17px] font-semibold text-heading">{item.title}</h3>
                  <p className="mt-2 text-[14.5px] leading-relaxed text-body">{item.body}</p>
                </div>
              </Reveal>
            );
          })}
        </div>
      </div>
    </section>
  );
}

function CardVisual({ kind }: { kind: "exposure" | "config" | "intel" }) {
  const { c } = useLanguage();
  const v = c.platform.visual;

  if (kind === "exposure") {
    return (
      <div className="relative flex h-40 items-center justify-center overflow-hidden rounded-xl border border-hair bg-canvas">
        <div className="grid-bg absolute inset-0 opacity-40" />
        <svg width="220" height="130" viewBox="0 0 220 130" role="img" aria-label={c.platform.cards[0].title}>
          <circle cx="110" cy="65" r="42" fill="rgba(52,120,246,0.05)" stroke="#3478F6" strokeOpacity="0.4" strokeDasharray="4 4" />
          <circle cx="110" cy="65" r="12" fill="rgba(52,120,246,0.14)" stroke="#3478F6" />
          <circle cx="44" cy="38" r="5" fill="#8B7CF6" />
          <circle cx="178" cy="96" r="5" fill="#DC5B63" />
          <path d="M44 38 C 72 40, 92 52, 102 62 M178 96 C 150 92, 128 82, 118 72" stroke="#94A3B8" strokeWidth="1.2" />
        </svg>
      </div>
    );
  }
  if (kind === "config") {
    return (
      <div className="flex h-40 flex-col justify-center gap-2.5 rounded-xl border border-hair bg-canvas p-5">
        {[
          [v.auth, v.unknown, "text-muted"],
          [v.cors, v.pass, "text-success"],
          [v.modelAccess, v.unknown, "text-muted"],
        ].map(([label, status, cls]) => (
          <div key={label} className="flex items-center justify-between rounded-lg border border-hair/70 bg-white px-3 py-2 text-[12.5px]">
            <span className="text-body">{label}</span>
            <span className={`font-mono text-[11px] ${cls}`}>{status}</span>
          </div>
        ))}
      </div>
    );
  }
  return (
    <div className="flex h-40 flex-col items-center justify-center gap-3 rounded-xl border border-hair bg-canvas">
      <div className="rounded-lg border border-primary/20 bg-soft px-3 py-1.5 font-mono text-[13px] text-primary">
        ollama · v0.40.4
      </div>
      <div className="flex items-center gap-2 rounded-lg border border-success/25 bg-success/10 px-3 py-1.5 text-[12px] text-success">
        <Check size={13} />
        {v.noAdvisories}
      </div>
    </div>
  );
}

export function Platform() {
  const { c } = useLanguage();
  const kinds = ["exposure", "config", "intel"] as const;
  return (
    <section id="platform" className="mx-auto max-w-7xl px-5 py-24 lg:px-8">
      <SectionHead kicker={c.platform.kicker} title={c.platform.title} sub={c.platform.sub} />
      <div className="mt-14 grid gap-5 md:grid-cols-3">
        {c.platform.cards.map((card, i) => (
          <Reveal key={card.title} delay={i * 0.08}>
            <div className="card h-full rounded-2xl p-5">
              <CardVisual kind={kinds[i]} />
              <h3 className="mt-5 text-[17px] font-semibold text-heading">{card.title}</h3>
              <p className="mt-2 text-[14.5px] leading-relaxed text-body">{card.body}</p>
            </div>
          </Reveal>
        ))}
      </div>
    </section>
  );
}

export function HowItWorks() {
  const { c } = useLanguage();
  return (
    <section id="how-it-works" className="border-y border-hair bg-soft/60">
      <div className="mx-auto max-w-7xl px-5 py-24 lg:px-8">
        <SectionHead kicker={c.process.kicker} title={c.process.title} />
        <div className="relative mx-auto mt-14 max-w-5xl">
          <div className="hairline-top absolute left-[16.6%] right-[16.6%] top-6 hidden md:block" />
          <div className="grid gap-10 md:grid-cols-3 md:gap-6">
            {c.process.steps.map((step, i) => (
              <Reveal key={step.title} delay={i * 0.1}>
                <div className="relative text-center">
                  <div className="relative z-10 mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-gradient-to-br from-primary to-secondary text-[17px] font-bold text-white shadow-[0_6px_18px_rgba(52,120,246,0.28)]">
                    {i + 1}
                  </div>
                  <h3 className="mt-5 text-[17px] font-semibold text-heading">{step.title}</h3>
                  <p className="mx-auto mt-2 max-w-xs text-[14.5px] leading-relaxed text-body">{step.body}</p>
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
  const { c } = useLanguage();
  return (
    <section className="mx-auto max-w-7xl px-5 py-24 lg:px-8">
      <SectionHead kicker={c.capabilities.kicker} title={c.capabilities.title} />
      <div className="mt-14 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {c.capabilities.items.map((cap, i) => {
          const verified = i < 6;
          return (
            <Reveal key={cap.title} delay={(i % 3) * 0.06}>
              <div className="card h-full rounded-2xl p-5">
                <div className="flex items-start justify-between gap-3">
                  <h3 className="text-[15.5px] font-semibold text-heading">{cap.title}</h3>
                  <span
                    className={`shrink-0 rounded-full border px-2.5 py-0.5 text-[10.5px] font-medium ${
                      verified
                        ? "border-success/25 bg-success/10 text-success"
                        : "border-hair bg-canvas text-muted"
                    }`}
                  >
                    {verified ? c.capabilities.statusVerified : c.capabilities.statusSupported}
                  </span>
                </div>
                <p className="mt-2 text-[13.5px] leading-relaxed text-body">{cap.body}</p>
              </div>
            </Reveal>
          );
        })}
      </div>
      <p className="mx-auto mt-8 max-w-3xl text-center text-[13.5px] leading-relaxed text-muted">
        {c.capabilities.footnote}
      </p>
    </section>
  );
}

function ReportMockup() {
  const { c } = useLanguage();
  const m = c.report.mock;
  const counts = [1, 1, 1, 0];
  const colors = ["bg-[#DC5B63]", "bg-[#F08A4B]", "bg-[#E6A23C]", "bg-[#7EA45C]"];

  return (
    <div className="relative mx-auto w-full max-w-md">
      <div className="absolute -inset-5 rounded-3xl bg-gradient-to-br from-primary/10 to-secondary/10" aria-hidden="true" />
      <div className="relative overflow-hidden rounded-2xl border border-hair bg-white shadow-[0_28px_70px_rgba(23,43,77,0.14)]">
        <div className="flex items-center justify-between gap-2 border-b border-hair bg-canvas/70 px-5 py-3">
          <span className="text-[12px] font-semibold tracking-wide text-heading">{m.header}</span>
          <span className="rounded-full bg-warning/15 px-2 py-0.5 text-[10px] font-semibold text-[#9a6a1f]">
            {m.demo}
          </span>
        </div>
        <div className="space-y-4 p-5">
          <div className="flex flex-wrap items-center justify-between gap-2 text-[12px] text-body">
            <span className="font-mono">{m.engagement}</span>
            <span className="font-mono">
              {m.target} {m.targetValue}
            </span>
          </div>
          <div>
            <p className="mb-2 text-[11px] font-semibold uppercase tracking-wide text-muted">{m.risk}</p>
            <div className="space-y-1.5">
              {m.severities.map((label, i) => (
                <div key={label} className="flex items-center gap-3">
                  <span className="w-14 text-[11.5px] text-body">{label}</span>
                  <div className="h-1.5 flex-1 overflow-hidden rounded-full bg-hair">
                    <div className={`h-full rounded-full ${colors[i]}`} style={{ width: `${counts[i] * 100}%` }} />
                  </div>
                  <span className="w-4 text-right font-mono text-[11px] text-muted">{counts[i]}</span>
                </div>
              ))}
            </div>
          </div>
          <div className="rounded-xl border border-hair bg-white p-4">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <span className="text-[12.5px] font-semibold text-heading">{m.findingTitle}</span>
              <span className="rounded-md bg-danger px-2 py-0.5 text-[10px] font-semibold text-white">
                {m.severities[0].toUpperCase()}
              </span>
            </div>
            <p className="mt-2 break-words font-mono text-[10.5px] leading-relaxed text-body">{m.evidence}</p>
            <p className="mt-2 text-[11.5px] leading-relaxed text-body">{m.remediation}</p>
          </div>
          <div className="rounded-xl border border-hair bg-canvas/70 p-4">
            <div className="flex flex-wrap items-center justify-between gap-2 text-[11.5px]">
              <span className="font-semibold text-heading">{m.coverage}</span>
              <span className="font-mono text-muted">{m.coverageValue}</span>
            </div>
            <p className="mt-2 text-[11px] leading-relaxed text-body">
              {m.limitations}: {m.limitationsBody}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

export function ReportPreview() {
  const { c } = useLanguage();
  const bulletIcons = [FileText, ShieldCheck, GitCompareArrows];
  return (
    <section id="report" className="border-y border-hair bg-white">
      <div className="mx-auto grid max-w-7xl items-center gap-14 px-5 py-24 lg:grid-cols-2 lg:px-8">
        <Reveal>
          <div>
            <span className="text-[12px] font-semibold uppercase tracking-[0.16em] text-primary">{c.report.kicker}</span>
            <h2 className="mt-3 text-[30px] font-bold leading-tight tracking-[-0.025em] text-heading sm:text-[40px]">
              {c.report.title}
            </h2>
            <p className="mt-4 max-w-lg text-[16px] leading-relaxed text-body">{c.report.body}</p>
            <ul className="mt-6 space-y-2.5 text-[14.5px] text-body">
              {c.report.bullets.map((bullet, i) => {
                const Icon = bulletIcons[i];
                return (
                  <li key={bullet} className="flex gap-2.5">
                    <Icon size={17} className="mt-0.5 shrink-0 text-primary" />
                    {bullet}
                  </li>
                );
              })}
            </ul>
            <a
              href="/assets/demo-assessment-report.pdf"
              className="mt-8 inline-flex items-center gap-2 rounded-full bg-primary px-6 py-3 text-[15px] font-semibold text-white shadow-[0_8px_24px_rgba(52,120,246,0.3)] transition-colors hover:bg-primary-deep"
            >
              {c.report.cta}
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
  const { c } = useLanguage();
  return (
    <section id="solutions" className="mx-auto max-w-7xl px-5 py-24 lg:px-8">
      <SectionHead kicker={c.solutions.kicker} title={c.solutions.title} />
      <div className="mt-14 grid gap-5 sm:grid-cols-2">
        {c.solutions.items.map((item, i) => {
          const Icon = SOLUTION_ICONS[i];
          return (
            <Reveal key={item.title} delay={(i % 2) * 0.08}>
              <div className="card flex h-full items-start gap-4 rounded-2xl p-6">
                <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-secondary/10 text-secondary">
                  <Icon size={20} />
                </div>
                <div>
                  <h3 className="text-[16.5px] font-semibold text-heading">{item.title}</h3>
                  <p className="mt-2 text-[14.5px] leading-relaxed text-body">{item.body}</p>
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
  const { c } = useLanguage();
  return (
    <section id="pricing" className="border-y border-hair bg-soft/50">
      <div className="mx-auto max-w-7xl px-5 py-24 lg:px-8">
        <SectionHead kicker={c.pricing.kicker} title={c.pricing.title} />
        <div className="mx-auto mt-14 grid max-w-4xl gap-6 md:grid-cols-2">
          <Reveal>
            <div className="h-full rounded-3xl border-2 border-primary/25 bg-white p-7 shadow-[0_18px_50px_rgba(52,120,246,0.1)]">
              <div className="flex items-center justify-between">
                <span className="rounded-full bg-soft px-3 py-1 text-[11.5px] font-semibold tracking-wide text-primary">
                  {c.pricing.quick.label}
                </span>
              </div>
              <div className="mt-5 flex items-baseline gap-1.5">
                <span className="text-5xl font-bold tracking-tight text-heading">{c.pricing.quick.price}</span>
                <span className="text-[14px] text-muted">{c.pricing.quick.unit}</span>
              </div>
              <p className="mt-3 text-[14px] leading-relaxed text-body">{c.pricing.quick.body}</p>
              <ul className="mt-6 space-y-2.5 text-[14px] text-body">
                {c.pricing.quick.features.map((item) => (
                  <li key={item} className="flex gap-2.5">
                    <Check size={16} className="mt-0.5 shrink-0 text-success" />
                    {item}
                  </li>
                ))}
              </ul>
              <a
                href={mailto(c.subjects.assessment)}
                className="mt-7 inline-flex w-full items-center justify-center gap-2 rounded-full bg-primary px-5 py-3 text-[14.5px] font-semibold text-white transition-colors hover:bg-primary-deep"
              >
                {c.pricing.quick.cta}
              </a>
            </div>
          </Reveal>
          <Reveal delay={0.08}>
            <div className="card flex h-full flex-col rounded-3xl p-7">
              <span className="w-fit rounded-full border border-hair bg-canvas px-3 py-1 text-[11.5px] font-semibold tracking-wide text-muted">
                {c.pricing.enterprise.label}
              </span>
              <h3 className="mt-5 text-[22px] font-semibold text-heading">{c.pricing.enterprise.title}</h3>
              <p className="mt-3 text-[14px] leading-relaxed text-body">{c.pricing.enterprise.body}</p>
              <ul className="mt-6 flex-1 space-y-2.5 text-[14px] text-body">
                {c.pricing.enterprise.features.map((item) => (
                  <li key={item} className="flex gap-2.5">
                    <Check size={16} className="mt-0.5 shrink-0 text-primary" />
                    {item}
                  </li>
                ))}
              </ul>
              <a
                href={mailto(c.subjects.custom)}
                className="mt-7 inline-flex w-full items-center justify-center gap-2 rounded-full border border-hair bg-white px-5 py-3 text-[14.5px] font-medium text-heading transition-colors hover:border-primary/40 hover:text-primary"
              >
                {c.pricing.enterprise.cta}
              </a>
            </div>
          </Reveal>
        </div>
        <p className="mx-auto mt-8 max-w-2xl text-center text-[13.5px] leading-relaxed text-muted">
          {c.pricing.note}
        </p>
      </div>
    </section>
  );
}

export function FAQSection() {
  const { c } = useLanguage();
  const [open, setOpen] = useState<number | null>(0);
  return (
    <section id="faq" className="mx-auto max-w-4xl px-5 py-24 lg:px-8">
      <SectionHead kicker={c.faq.kicker} title={c.faq.title} />
      <div className="mt-12 space-y-3">
        {c.faq.items.map((item, i) => (
          <div key={item.q} className="card overflow-hidden rounded-2xl">
            <button
              type="button"
              onClick={() => setOpen(open === i ? null : i)}
              aria-expanded={open === i}
              className="flex w-full items-center justify-between gap-4 px-6 py-4 text-left"
            >
              <span className="text-[15.5px] font-medium text-heading">{item.q}</span>
              <ChevronDown
                size={18}
                className={`shrink-0 text-muted transition-transform ${open === i ? "rotate-180" : ""}`}
              />
            </button>
            {open === i && (
              <p className="border-t border-hair px-6 py-4 text-[14.5px] leading-relaxed text-body">
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
  const { c } = useLanguage();
  return (
    <section className="relative overflow-hidden border-y border-hair bg-gradient-to-b from-soft/80 to-canvas">
      <div className="absolute inset-0 bg-[radial-gradient(560px_280px_at_18%_20%,rgba(52,120,246,0.12),transparent_62%),radial-gradient(520px_260px_at_82%_80%,rgba(139,124,246,0.12),transparent_62%)]" aria-hidden="true" />
      <div className="relative mx-auto max-w-4xl px-5 py-24 text-center lg:px-8">
        <h2 className="text-[32px] font-bold leading-tight tracking-[-0.025em] text-heading sm:text-[44px]">
          {c.finalCta.title}
        </h2>
        <p className="mx-auto mt-4 max-w-xl text-[16px] leading-relaxed text-body">{c.finalCta.body}</p>
        <div className="mt-8 flex flex-wrap items-center justify-center gap-4">
          <a
            href={mailto(c.subjects.assessment)}
            className="inline-flex items-center gap-2 rounded-full bg-primary px-6 py-3 text-[15px] font-semibold text-white shadow-[0_8px_24px_rgba(52,120,246,0.3)] transition-colors hover:bg-primary-deep"
          >
            {c.finalCta.primary}
            <ArrowRight size={17} />
          </a>
          <a
            href={mailto(c.subjects.team)}
            className="inline-flex items-center gap-2 rounded-full border border-hair bg-white px-6 py-3 text-[15px] font-medium text-heading transition-colors hover:border-primary/40 hover:text-primary"
          >
            {c.finalCta.secondary}
          </a>
        </div>
      </div>
    </section>
  );
}

export function Footer() {
  const { c } = useLanguage();
  return (
    <footer id="contact" className="bg-[#EEF3F9]">
      <div className="mx-auto max-w-7xl px-5 py-16 lg:px-8">
        <div className="grid gap-10 md:grid-cols-[1.4fr_1fr_1fr_1fr_1.2fr]">
          <div>
            <div className="flex items-center gap-2.5 text-[16px] font-bold text-navy">
              <BrandMark size={28} />
              AI Shield
            </div>
            <p className="mt-4 max-w-xs text-[13.5px] leading-relaxed text-muted">{c.footer.tagline}</p>
          </div>
          <FooterCol
            title={c.footer.product}
            links={[
              [c.footer.platform, "#platform"],
              [c.footer.assessment, "#how-it-works"],
              [c.footer.pricing, "#pricing"],
            ]}
          />
          <FooterCol
            title={c.footer.solutions}
            links={c.solutions.items.map((s) => [s.title, "#solutions"] as [string, string])}
          />
          <FooterCol
            title={c.footer.resources}
            links={[
              [c.footer.sampleReport, "#report"],
              [c.footer.faq, "#faq"],
              [c.footer.privacy, "#legal"],
              [c.footer.terms, "#legal"],
            ]}
          />
          <div>
            <h4 className="text-[13px] font-semibold uppercase tracking-wide text-heading">{c.footer.contact}</h4>
            <ul className="mt-4 space-y-2.5 text-[13.5px] text-muted">
              <li>
                <a href={`mailto:${CONTACT_EMAIL}`} className="transition-colors hover:text-primary">
                  {CONTACT_EMAIL}
                </a>
              </li>
              <li>{c.footer.contactNote}</li>
            </ul>
          </div>
        </div>
        <div className="mt-12 flex flex-col gap-3 border-t border-hair pt-6 text-[12.5px] text-muted sm:flex-row sm:items-center sm:justify-between">
          <span>{c.footer.copyright}</span>
          <div className="flex gap-6">
            <a href="#legal" className="transition-colors hover:text-primary">{c.footer.privacy}</a>
            <a href="#legal" className="transition-colors hover:text-primary">{c.footer.terms}</a>
          </div>
        </div>
      </div>
    </footer>
  );
}

function FooterCol({ title, links }: { title: string; links: [string, string][] }) {
  return (
    <div>
      <h4 className="text-[13px] font-semibold uppercase tracking-wide text-heading">{title}</h4>
      <ul className="mt-4 space-y-2.5 text-[13.5px] text-muted">
        {links.map(([label, href]) => (
          <li key={label}>
            <a href={href} className="transition-colors hover:text-primary">{label}</a>
          </li>
        ))}
      </ul>
    </div>
  );
}

export function Legal() {
  const { c } = useLanguage();
  return (
    <section id="legal" className="border-t border-hair bg-white">
      <div className="mx-auto max-w-4xl px-5 py-16 lg:px-8">
        <h2 className="text-[24px] font-semibold text-heading">{c.legal.title}</h2>
        <div className="mt-6 grid gap-8 md:grid-cols-2">
          <div>
            <h3 className="text-[16px] font-semibold text-heading">{c.legal.privacyTitle}</h3>
            <p className="mt-3 text-[13.5px] leading-relaxed text-muted">{c.legal.privacyBody}</p>
          </div>
          <div>
            <h3 className="text-[16px] font-semibold text-heading">{c.legal.termsTitle}</h3>
            <p className="mt-3 text-[13.5px] leading-relaxed text-muted">{c.legal.termsBody}</p>
          </div>
        </div>
      </div>
    </section>
  );
}
