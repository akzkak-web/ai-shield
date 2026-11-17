import {
  createContext,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import { getContent, type Lang, type SiteContent } from "../content";
import { SITE_URL } from "../config";

const STORAGE_KEY = "ai-shield-lang";

interface LanguageContextValue {
  lang: Lang;
  setLang: (lang: Lang) => void;
  c: SiteContent;
}

const LanguageContext = createContext<LanguageContextValue | null>(null);

function detectLang(): Lang {
  const path = window.location.pathname;
  if (path.startsWith("/zh")) return "zh";
  if (path.startsWith("/en")) return "en";
  try {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved === "zh" || saved === "en") return saved;
  } catch {
    /* storage unavailable */
  }
  return "en";
}

function localizedPath(lang: Lang, hash: string) {
  return `/${lang}/${hash}`;
}

function upsertMeta(selector: string, attr: "name" | "property", value: string, content: string) {
  let node = document.head.querySelector<HTMLMetaElement>(selector);
  if (!node) {
    node = document.createElement("meta");
    node.setAttribute(attr, value);
    document.head.appendChild(node);
  }
  node.setAttribute("content", content);
}

function upsertAlternate(hreflang: string, href: string) {
  let node = document.head.querySelector<HTMLLinkElement>(
    `link[rel="alternate"][hreflang="${hreflang}"]`
  );
  if (!node) {
    node = document.createElement("link");
    node.rel = "alternate";
    node.hreflang = hreflang;
    document.head.appendChild(node);
  }
  node.href = href;
}

function updateSeo(lang: Lang) {
  const c = getContent(lang);
  document.documentElement.lang = lang === "zh" ? "zh-CN" : "en";
  document.title = c.seo.title;
  upsertMeta('meta[name="description"]', "name", "description", c.seo.description);
  upsertMeta('meta[property="og:title"]', "property", "og:title", c.seo.ogTitle);
  upsertMeta(
    'meta[property="og:description"]',
    "property",
    "og:description",
    c.seo.ogDescription
  );

  let canonical = document.head.querySelector<HTMLLinkElement>('link[rel="canonical"]');
  if (!canonical) {
    canonical = document.createElement("link");
    canonical.rel = "canonical";
    document.head.appendChild(canonical);
  }
  canonical.href = `${SITE_URL}/${lang}/`;

  upsertAlternate("en", `${SITE_URL}/en/`);
  upsertAlternate("zh", `${SITE_URL}/zh/`);
  upsertAlternate("x-default", `${SITE_URL}/en/`);
}

export function LanguageProvider({ children }: { children: ReactNode }) {
  const [lang, setLangState] = useState<Lang>(detectLang);

  useEffect(() => {
    updateSeo(lang);
    const path = window.location.pathname;
    if (!/^\/(en|zh)(\/|$)/.test(path)) {
      window.history.replaceState(null, "", localizedPath(lang, window.location.hash));
    }
  }, [lang]);

  useEffect(() => {
    const onPopState = () => {
      const path = window.location.pathname;
      const next: Lang = path.startsWith("/zh") ? "zh" : "en";
      setLangState(next);
      updateSeo(next);
    };
    window.addEventListener("popstate", onPopState);
    return () => window.removeEventListener("popstate", onPopState);
  }, []);

  const value = useMemo<LanguageContextValue>(
    () => ({
      lang,
      c: getContent(lang),
      setLang: (next: Lang) => {
        if (next === lang) return;
        const hash = window.location.hash;
        const scrollY = window.scrollY;
        window.history.pushState(null, "", localizedPath(next, hash));
        try {
          localStorage.setItem(STORAGE_KEY, next);
        } catch {
          /* storage unavailable */
        }
        setLangState(next);
        updateSeo(next);
        requestAnimationFrame(() => {
          if (hash) {
            document.querySelector(hash)?.scrollIntoView();
          } else {
            window.scrollTo(0, scrollY);
          }
        });
      },
    }),
    [lang]
  );

  return <LanguageContext.Provider value={value}>{children}</LanguageContext.Provider>;
}

export function useLanguage() {
  const ctx = useContext(LanguageContext);
  if (!ctx) throw new Error("useLanguage must be used inside LanguageProvider");
  return ctx;
}
