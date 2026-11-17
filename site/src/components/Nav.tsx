import { useState } from "react";
import { Menu, X } from "lucide-react";
import { BrandMark } from "./BrandMark";
import { NAV_LINKS } from "../content";
import { mailto, SITE_NAME } from "../config";

export function Nav() {
  const [open, setOpen] = useState(false);

  return (
    <header className="sticky top-0 z-50 border-b border-line/70 bg-ink-950/75 backdrop-blur-md">
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-5 lg:px-8">
        <a href="#top" className="flex items-center gap-2.5 text-[15px] font-semibold text-mist">
          <BrandMark />
          {SITE_NAME}
        </a>

        <nav className="hidden items-center gap-7 lg:flex" aria-label="Primary">
          {NAV_LINKS.map((link) => (
            <a
              key={link.href}
              href={link.href}
              className="text-[13.5px] text-mut transition-colors hover:text-mist"
            >
              {link.label}
            </a>
          ))}
        </nav>

        <div className="hidden items-center gap-3 lg:flex">
          <a
            href={mailto("Contact Sales")}
            className="rounded-full px-4 py-2 text-[13.5px] font-medium text-mut transition-colors hover:text-mist"
          >
            Contact Sales
          </a>
          <a
            href={mailto("Request a Demo")}
            className="rounded-full bg-gradient-to-r from-brand-500 to-viol-500 px-4 py-2 text-[13.5px] font-semibold text-white shadow-[0_4px_20px_rgba(46,124,246,0.35)] transition-transform hover:-translate-y-px"
          >
            Request a Demo
          </a>
        </div>

        <button
          type="button"
          className="rounded-lg p-2 text-mut lg:hidden"
          aria-expanded={open}
          aria-label="Toggle menu"
          onClick={() => setOpen((v) => !v)}
        >
          {open ? <X size={20} /> : <Menu size={20} />}
        </button>
      </div>

      {open && (
        <div className="border-t border-line bg-ink-900 px-5 py-4 lg:hidden">
          {NAV_LINKS.map((link) => (
            <a
              key={link.href}
              href={link.href}
              onClick={() => setOpen(false)}
              className="block rounded-lg px-2 py-2.5 text-[14.5px] text-mut hover:bg-white/5 hover:text-mist"
            >
              {link.label}
            </a>
          ))}
          <div className="mt-3 flex gap-3">
            <a
              href={mailto("Contact Sales")}
              className="flex-1 rounded-full border border-line px-4 py-2 text-center text-[13.5px] text-mist"
            >
              Contact Sales
            </a>
            <a
              href={mailto("Request a Demo")}
              className="flex-1 rounded-full bg-gradient-to-r from-brand-500 to-viol-500 px-4 py-2 text-center text-[13.5px] font-semibold text-white"
            >
              Request a Demo
            </a>
          </div>
        </div>
      )}
    </header>
  );
}
