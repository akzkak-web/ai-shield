/**
 * Site configuration.
 *
 * CONTACT_EMAIL is the single configurable contact destination. CTAs use
 * mailto links with a prefilled subject, so no backend or CRM is required.
 * Replace the placeholder before going live.
 */
export const CONTACT_EMAIL = "sales@jiuzhanglabs.com";
export const SECONDARY_EMAIL = "raysmith0zero@gmail.com";

export const WHATSAPP_NUMBER = "85297654335";
export const WHATSAPP_DISPLAY = "+852 9765 4335";
export const TELEGRAM_URL = "tg://resolve?phone=85297654335";

export const whatsappUrl = (text: string) =>
  `https://wa.me/${WHATSAPP_NUMBER}?text=${encodeURIComponent(text)}`;

/** Public site origin used for canonical and hreflang URLs. */
export const SITE_URL = "https://akzkak-web.github.io/ai-shield";

export const mailto = (subject: string) =>
  `mailto:${CONTACT_EMAIL}?subject=${encodeURIComponent(subject)}`;

export const SITE_NAME = "AI Shield";
