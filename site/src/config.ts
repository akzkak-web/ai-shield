/**
 * Site configuration.
 *
 * CONTACT_EMAIL is the single configurable contact destination. CTAs use
 * mailto links with a prefilled subject, so no backend or CRM is required.
 * Replace the placeholder before going live.
 */
export const CONTACT_EMAIL = "sales@aishield.example";

/** Public site origin used for canonical and hreflang URLs. */
export const SITE_URL = "https://aishield.example";

export const mailto = (subject: string) =>
  `mailto:${CONTACT_EMAIL}?subject=${encodeURIComponent(subject)}`;

export const SITE_NAME = "AI Shield";
