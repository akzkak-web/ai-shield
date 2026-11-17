# AI Shield Website V2

Light premium marketing website for AI Shield, a security assessment
platform for self-hosted AI inference environments.

## Stack

- React 19 + TypeScript
- Vite
- Tailwind CSS v4
- Motion (motion/react)
- Lucide icons
- Self-hosted variable fonts (Geist, Geist Mono via Fontsource)

## Local development

```bash
npm install
npm run dev
```

Open `/en/` or `/zh/`. Visiting `/` redirects to the saved language, or
English by default.

## Production build

```bash
npm run build
npm run preview
```

The build emits three static entry points:

- `dist/index.html` (English shell, canonical `/en/`)
- `dist/en/index.html`
- `dist/zh/index.html`

Deploy `dist/` to any static host that serves directory index files. The
site is designed for root-domain deployment.

## Internationalization

- English and Simplified Chinese dictionaries live in `src/content.ts`
  and `src/content.zh.ts`, sharing the typed `SiteContent` interface.
- `src/i18n/LanguageContext.tsx` handles language detection, URL routing,
  localStorage persistence, hash preservation and localized SEO metadata.
- Language switch: EN / 中文 in the navigation.
- URLs: `/en/` and `/zh/`; direct access works on the static build.

## Configuration before launch

1. **Contact channels.** `src/config.ts` defines the primary sales email
   (`sales@jiuzhanglabs.com`), secondary email
   (`raysmith0zero@gmail.com`), and the shared WhatsApp / Telegram number
   `+852 9765 4335`. All sales, demo and assessment CTAs use localized
   mailto subjects; WhatsApp opens with a localized prefilled message.
2. **Site origin.** Replace `https://aishield.example` in `src/config.ts`
   and in the canonical/hreflang tags of `index.html`, `en/index.html` and
   `zh/index.html` with the production domain.
3. **Legal pages.** The in-page `#legal` section contains clearly marked
   initial drafts for Privacy Policy and Terms of Service. Have counsel
   finalize them before launch.
4. **Sample report.** `public/assets/demo-assessment-report.pdf` is
   generated from demonstration data and labeled as such. Replace it from a
   real customer engagement when appropriate.

## Content integrity

- Ollama is the only assessment target with completed real-environment
  verification and is stated as such.
- The hero console and report preview are labeled demonstration data.
- No customer logos, certifications, adoption counts or endorsements are
  invented.
- Capabilities are split into verified checks and supported features.

## Validation performed

- `tsc --noEmit` and `vite build` pass.
- Playwright (system Chrome) against the production preview:
  - `/en/` and `/zh/` return 200 with correct `lang`, title and headline
  - EN to ZH switch updates the URL, persists and survives reload
  - `/` redirects to the persisted language
  - hash context (`#pricing`) survives a language switch
  - desktop 1440, tablet 768 and mobile 390 have no horizontal overflow
  - mobile menu opens and exposes navigation links
  - all internal anchors resolve, 8 mailto CTAs present
  - favicon, logo assets and sample PDF return 200
  - no console errors
