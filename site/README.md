# AI Shield Website

Marketing website for AI Shield, a security assessment platform for
self-hosted AI inference environments.

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

## Production build

```bash
npm run build
npm run preview
```

The build output is written to `dist/` and can be deployed to any static
host (GitHub Pages, Cloudflare Pages, Netlify, object storage, etc.).

## Configuration before launch

1. **Contact destination.** All sales and demo CTAs point to a single
   configurable email address defined in `src/config.ts`
   (`CONTACT_EMAIL`). Replace `sales@aishield.example` with the real
   address. No backend, CRM or form service is required.
2. **Legal pages.** The footer links Privacy Policy and Terms of Service
   to the in-page `#legal` section, which currently contains clearly marked
   initial drafts. Have counsel finalize them before launch.
3. **Sample report.** The report download in the Report section serves
   `public/assets/demo-assessment-report.pdf`, generated from demonstration
   data (labeled as such). Regenerate it from a real engagement before using
   it in sales conversations if desired.
4. **Localization.** All page copy lives in `src/content.ts`, ready to be
   moved to an i18n structure for a future Chinese version.

## Content integrity notes

- Ollama is the only validated assessment target and is stated as such.
- The hero console, report mockup and sample PDF are explicitly labeled as
  demonstration data.
- No customer logos, certifications, adoption counts or endorsements are
  invented.
