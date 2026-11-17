import { useState } from "react";
import { Menu, X } from "lucide-react";
import { BrandMark } from "./BrandMark";
import { mailto, SITE_NAME } from "../config";
import { useLanguage } from "../i18n/LanguageContext";
import type { Lang } from "../content";

function LanguageSwitch() {
  const { lang, setLang, c } = useLanguage();
  const options: { value: Lang; label: string }[] = [
    { value: "en", label: "EN" },
    { value: "zh", label: "中文" },
  ];
  return (
    <div
      role="group"
      aria-label={c.nav.languageAria}
      className="flex rounded-full border border-hair bg-canvas p-0.5"
    >
      {options.map((option) => (
        <button
          key={option.value}
          type="button"
          onClick={() => setLang(option.value)}
          aria-pressed={lang === option.value}
          className={`rounded-full px-2.5 py-1 text-[11.5px] font-medium transition-colors ${
            lang === option.value
              ? "bg-white text-primary shadow-[0_1px_4px_rgba(23,43,77,0.12)]"
              : "text-muted hover:text-heading"
          }`}
        >
          {option.label}
        </button>
      ))}
    </div>
  );
}

export function Nav() {
  const [open, setOpen] = useState(false);
  const { c } = useLanguage();

  return (
    <header className="sticky top-0 z-50 border-b border-hair/80 bg-white/85 backdrop-blur-md">
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-5 lg:px-8">
        <a href="#top" className="flex items-center gap-2.5 text-[17px] font-bold tracking-tight text-navy">
          <BrandMark size={30} />
          {SITE_NAME}
        </a>

        <nav className="hidden items-center gap-7 lg:flex" aria-label="Primary">
          {c.nav.links.map((link) => (
            <a
              key={link.href}
              href={link.href}
              className="text-[13.5px] font-medium text-body transition-colors hover:text-primary"
            >
              {link.label}
            </a>
          ))}
        </nav>

        <div className="hidden items-center gap-3 lg:flex">
          <LanguageSwitch />
          <a
            href={mailto(c.subjects.sales)}
            className="rounded-full px-3 py-2 text-[13.5px] font-medium text-body transition-colors hover:text-heading"
          >
            {c.nav.contactSales}
          </a>
          <a
            href={mailto(c.subjects.demo)}
            className="rounded-full bg-primary px-4 py-2 text-[13.5px] font-semibold text-white shadow-[0_4px_14px_rgba(52,120,246,0.28)] transition-colors hover:bg-primary-deep"
          >
            {c.nav.requestDemo}
          </a>
        </div>

        <div className="flex items-center gap-2 lg:hidden">
          <LanguageSwitch />
          <button
            type="button"
            className="rounded-lg p-2 text-body"
            aria-expanded={open}
            aria-label={c.nav.menuAria}
            onClick={() => setOpen((v) => !v)}
          >
            {open ? <X size={20} /> : <Menu size={20} />}
          </button>
        </div>
      </div>

      {open && (
        <div className="border-t border-hair bg-white px-5 py-4 lg:hidden">
          {c.nav.links.map((link) => (
            <a
              key={link.href}
              href={link.href}
              onClick={() => setOpen(false)}
              className="block rounded-lg px-2 py-2.5 text-[14.5px] text-body hover:bg-canvas hover:text-heading"
            >
              {link.label}
            </a>
          ))}
          <div className="mt-3 flex gap-3">
            <a
              href={mailto(c.subjects.sales)}
              className="flex-1 rounded-full border border-hair px-4 py-2 text-center text-[13.5px] font-medium text-heading"
            >
              {c.nav.contactSales}
            </a>
            <a
              href={mailto(c.subjects.demo)}
              className="flex-1 rounded-full bg-primary px-4 py-2 text-center text-[13.5px] font-semibold text-white"
            >
              {c.nav.requestDemo}
            </a>
          </div>
        </div>
      )}
    </header>
  );
}
