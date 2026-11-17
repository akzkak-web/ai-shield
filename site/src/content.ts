import { zh } from "./content.zh";

export type Lang = "en" | "zh";

export interface NavLink {
  label: string;
  href: string;
}

export interface TextPair {
  title: string;
  body: string;
}

export interface SiteContent {
  seo: {
    title: string;
    description: string;
    ogTitle: string;
    ogDescription: string;
  };
  nav: {
    links: NavLink[];
    contactSales: string;
    requestDemo: string;
    menuAria: string;
    languageAria: string;
  };
  hero: {
    badge: string;
    headline1: string;
    headline2: string;
    description: string;
    primaryCta: string;
    secondaryCta: string;
    props: string[];
    console: {
      title: string;
      demo: string;
      topology: string;
      scope: string;
      target: string;
      checks: string;
      supported: string;
      checkNames: string[];
      pass: string;
      unknown: string;
      coverage: string;
      coverageValue: string;
      footer: string[];
    };
  };
  trust: {
    kicker: string;
    title: string;
    items: TextPair[];
  };
  platform: {
    kicker: string;
    title: string;
    sub: string;
    cards: TextPair[];
    visual: {
      auth: string;
      cors: string;
      modelAccess: string;
      pass: string;
      unknown: string;
      noAdvisories: string;
      nodes: string[];
    };
  };
  process: {
    kicker: string;
    title: string;
    steps: TextPair[];
  };
  capabilities: {
    kicker: string;
    title: string;
    statusVerified: string;
    statusSupported: string;
    items: TextPair[];
    footnote: string;
  };
  report: {
    kicker: string;
    title: string;
    body: string;
    bullets: string[];
    cta: string;
    mock: {
      header: string;
      demo: string;
      engagement: string;
      target: string;
      targetValue: string;
      risk: string;
      severities: string[];
      findingTitle: string;
      evidence: string;
      remediation: string;
      coverage: string;
      coverageValue: string;
      limitations: string;
      limitationsBody: string;
    };
  };
  solutions: {
    kicker: string;
    title: string;
    items: TextPair[];
  };
  pricing: {
    kicker: string;
    title: string;
    quick: {
      label: string;
      price: string;
      unit: string;
      body: string;
      features: string[];
      cta: string;
    };
    enterprise: {
      label: string;
      title: string;
      body: string;
      features: string[];
      cta: string;
    };
    note: string;
  };
  faq: {
    kicker: string;
    title: string;
    items: { q: string; a: string }[];
  };
  finalCta: {
    title: string;
    body: string;
    primary: string;
    secondary: string;
  };
  footer: {
    tagline: string;
    product: string;
    solutions: string;
    resources: string;
    contact: string;
    platform: string;
    assessment: string;
    pricing: string;
    sampleReport: string;
    faq: string;
    privacy: string;
    terms: string;
    contactNote: string;
    copyright: string;
  };
  legal: {
    title: string;
    privacyTitle: string;
    privacyBody: string;
    termsTitle: string;
    termsBody: string;
  };
  subjects: {
    assessment: string;
    demo: string;
    sales: string;
    custom: string;
    team: string;
  };
}

const en: SiteContent = {
  seo: {
    title: "AI Shield - Secure Your AI Infrastructure",
    description:
      "AI Shield helps teams assess self-hosted AI environments, identify security misconfigurations, and turn technical findings into clear remediation actions.",
    ogTitle: "AI Shield - Secure Your AI Infrastructure",
    ogDescription:
      "Evidence-based security assessments for self-hosted AI inference environments. Know what's exposed. Understand what to fix.",
  },
  nav: {
    links: [
      { label: "Platform", href: "#platform" },
      { label: "Solutions", href: "#solutions" },
      { label: "Security Assessment", href: "#how-it-works" },
      { label: "Resources", href: "#report" },
      { label: "Pricing", href: "#pricing" },
    ],
    contactSales: "Contact Sales",
    requestDemo: "Request a Demo",
    menuAria: "Toggle menu",
    languageAria: "Switch language",
  },
  hero: {
    badge: "AI INFRASTRUCTURE SECURITY",
    headline1: "Secure Your AI Infrastructure.",
    headline2: "Know What's Exposed. Understand What to Fix.",
    description:
      "AI Shield helps teams assess self-hosted AI environments, identify security misconfigurations, and turn technical findings into clear remediation actions.",
    primaryCta: "Request a Security Assessment",
    secondaryCta: "Explore the Platform",
    props: [
      "Evidence-Based Security Assessment",
      "Actionable Remediation Guidance",
      "Clear Coverage & Risk Visibility",
    ],
    console: {
      title: "Assessment Console",
      demo: "DEMO DATA",
      topology: "Environment topology",
      scope: "scope: authorized target only",
      target: "target: authorized",
      checks: "Checks",
      supported: "6 supported",
      checkNames: [
        "Network exposure",
        "Authentication",
        "CORS policy",
        "Model API access",
        "Rate limiting",
        "Vulnerability match",
      ],
      pass: "pass",
      unknown: "unknown",
      coverage: "Coverage",
      coverageValue: "partial",
      footer: [
        "coverage: partial",
        "findings: 0 confirmed",
        "unknown checks reported, never treated as secure",
      ],
    },
  },
  trust: {
    kicker: "WHY AI SHIELD",
    title: "Visibility Into Your AI Infrastructure Security",
    items: [
      {
        title: "Understand Exposure",
        body: "Identify network exposure and risky service configurations.",
      },
      {
        title: "Validate Security Controls",
        body: "Assess authentication, CORS, access controls, and other supported security checks.",
      },
      {
        title: "Prioritize Remediation",
        body: "Turn findings into practical, evidence-backed recommendations.",
      },
    ],
  },
  platform: {
    kicker: "PLATFORM",
    title: "A Clearer View of Your AI Security Posture",
    sub: "Three lenses on the environments you run: what is reachable, what is misconfigured, and what is known to be vulnerable.",
    cards: [
      {
        title: "Infrastructure Exposure",
        body: "Understand whether AI inference services are exposed beyond their intended network boundaries.",
      },
      {
        title: "Security Configuration",
        body: "Review supported authentication, CORS, access and service configuration signals.",
      },
      {
        title: "Vulnerability Intelligence",
        body: "Match supported service and version information against available vulnerability intelligence.",
      },
    ],
    visual: {
      auth: "Authentication",
      cors: "CORS policy",
      modelAccess: "Model API access",
      pass: "pass",
      unknown: "unknown",
      noAdvisories: "no affected advisories",
      nodes: ["exposure", "auth", "cors", "cve"],
    },
  },
  process: {
    kicker: "PROCESS",
    title: "From Assessment to Action in Three Steps",
    steps: [
      {
        title: "Define Your Scope",
        body: "Specify the AI environment and authorized assessment target.",
      },
      {
        title: "Run Security Assessment",
        body: "Evaluate supported security controls and collect technical evidence.",
      },
      {
        title: "Review & Remediate",
        body: "Receive a structured report with findings, coverage information, and remediation guidance.",
      },
    ],
  },
  capabilities: {
    kicker: "CAPABILITIES",
    title: "Built for Real-World AI Deployments",
    statusVerified: "Verified",
    statusSupported: "Supported",
    items: [
      { title: "Network Exposure Assessment", body: "Determine whether a service listens beyond its intended boundary." },
      { title: "Authentication Configuration Review", body: "Check whether model endpoints require credentials." },
      { title: "CORS Configuration Review", body: "Detect permissive or reflected cross-origin policies." },
      { title: "Model API Access Review", body: "Check whether unauthenticated users can enumerate models." },
      { title: "Rate Limiting Assessment", body: "Observe rate-limit signals on service endpoints." },
      { title: "Vulnerability Version Matching", body: "Compare detected service versions with known advisories." },
      { title: "Evidence-Based Findings", body: "Every finding carries the evidence that supports it." },
      { title: "JSON & PDF Reporting", body: "Structured machine data plus a readable assessment report." },
      { title: "Baseline Comparison", body: "Diff a new assessment against a stored baseline." },
    ],
    footnote:
      "Ollama is the validated assessment target for the initial release. Detection exists for additional inference services, but real-environment verification is ongoing. Verified checks have completed real-service integration testing; supported capabilities ship with today's product.",
  },
  report: {
    kicker: "REPORT",
    title: "Security Findings You Can Actually Act On.",
    body: "Every assessment ends with a structured report: risk summary, finding severity, supporting evidence, coverage and limitations, and remediation recommendations.",
    bullets: [
      "Assessment overview and risk summary",
      "Findings with severity and evidence",
      "Coverage, limitations and remediation guidance",
    ],
    cta: "See a Sample Assessment Report",
    mock: {
      header: "AI SHIELD ASSESSMENT REPORT",
      demo: "DEMONSTRATION DATA",
      engagement: "engagement: AISHIELD-DEMO-001",
      target: "target:",
      targetValue: "authorized",
      risk: "Risk summary",
      severities: ["Critical", "High", "Medium", "Low"],
      findingTitle: "AUTH-001 · Missing authentication",
      evidence: "evidence: accessible_endpoints=['/v1/models', '/api/tags']",
      remediation:
        "remediation: enable API-key authentication, or add authentication at a reverse proxy.",
      coverage: "Coverage",
      coverageValue: "partial · 3 checks unverified",
      limitations: "Limitations",
      limitationsBody:
        "Read-only assessment. Unknown checks are reported, never treated as secure.",
    },
  },
  solutions: {
    kicker: "SOLUTIONS",
    title: "Security Confidence Across AI Deployments",
    items: [
      { title: "AI Deployment Providers", body: "Verify the security posture of the environments you ship before customers rely on them." },
      { title: "Enterprise IT Teams", body: "Get an independent view of self-hosted AI services inside your network." },
      { title: "AI Application Companies", body: "Understand how your inference layer is configured and what to fix first." },
      { title: "Private AI Infrastructure Operators", body: "Keep controlled environments aligned with your own security expectations." },
    ],
  },
  pricing: {
    kicker: "PRICING",
    title: "Straightforward Security Assessment Pricing",
    quick: {
      label: "AI SHIELD QUICK CHECK",
      price: "$15.00",
      unit: "/ assessment",
      body: "A focused security baseline assessment for one authorized Ollama environment.",
      features: [
        "Six supported assessment checks",
        "Technical evidence review",
        "Security findings summary",
        "Chinese PDF report",
        "Remediation recommendations",
        "One retest within the agreed scope",
      ],
      cta: "Request an Assessment",
    },
    enterprise: {
      label: "ENTERPRISE / CUSTOM",
      title: "Custom Assessment",
      body: "For multiple environments, retainer engagements, or an expanded scope agreed in writing.",
      features: [
        "Multiple authorized targets",
        "Tailored check selection",
        "Extended reporting and retesting",
      ],
      cta: "Contact Sales",
    },
    note:
      "Scope and exclusions are defined in writing before every engagement. AI Shield delivers a focused security baseline assessment; it is not comprehensive penetration testing, and no recurring subscriptions or automated billing are implied.",
  },
  faq: {
    kicker: "FAQ",
    title: "Frequently Asked Questions",
    items: [
      {
        q: "What is AI Shield?",
        a: "AI Shield is a security assessment platform for self-hosted AI inference environments. It inspects authorized targets with read-only checks and reports confirmed findings with evidence, severity, coverage and remediation guidance.",
      },
      {
        q: "Which AI environments are currently supported?",
        a: "Ollama is the validated assessment target for the initial release. Service detection exists for additional inference services, but they have not completed real-environment verification.",
      },
      {
        q: "What does an assessment include?",
        a: "Six supported checks: network exposure, authentication configuration, CORS configuration, model API access, rate limiting signals, and vulnerability version matching. Results are delivered as structured JSON and a readable PDF report.",
      },
      {
        q: "Do I need to provide access to my AI models?",
        a: "No. The assessment uses only read-only service endpoints such as version and model-list endpoints. Model weights and model data are never required.",
      },
      {
        q: "Does AI Shield send prompts to my models?",
        a: "No. The standard assessment performs read-only requests only. It does not send generation prompts to your models.",
      },
      {
        q: "How is assessment scope authorized?",
        a: "Every assessment starts with a written authorization and a scope confirmation listing the exact target, ports and allowed activities. Out-of-scope hosts are never touched.",
      },
      {
        q: "What will I receive after an assessment?",
        a: "A structured JSON result and a PDF report covering the assessment overview, findings with evidence and severity, remediation recommendations, coverage and limitations.",
      },
      {
        q: "Does a clean report guarantee that my system is secure?",
        a: "No. A clean grade means no confirmed findings for the checks that ran. Coverage is reported explicitly, and unverified checks are never presented as secure.",
      },
    ],
  },
  finalCta: {
    title: "Make Your AI Infrastructure More Secure.",
    body: "Get a clearer understanding of your AI deployment security posture with an evidence-based assessment.",
    primary: "Request a Security Assessment",
    secondary: "Contact Our Team",
  },
  footer: {
    tagline: "Evidence-based security assessments for self-hosted AI inference environments.",
    product: "Product",
    solutions: "Solutions",
    resources: "Resources",
    contact: "Contact",
    platform: "Platform",
    assessment: "Security Assessment",
    pricing: "Pricing",
    sampleReport: "Sample Report",
    faq: "FAQ",
    privacy: "Privacy Policy",
    terms: "Terms of Service",
    contactNote: "Assessments run on authorized targets only.",
    copyright: "© 2026 AI Shield. All rights reserved.",
  },
  legal: {
    title: "Legal",
    privacyTitle: "Privacy Policy",
    privacyBody:
      "Initial draft. AI Shield processes contact information provided through email inquiries solely to respond to assessment requests. Assessments operate on authorized targets and do not collect customer model data or model content.",
    termsTitle: "Terms of Service",
    termsBody:
      "Initial draft. Every engagement requires written authorization and a confirmed scope. Assessment results reflect observations at the time of testing and are not a long-term security guarantee. Legal counsel should finalize these documents before launch.",
  },
  subjects: {
    assessment: "Security Assessment Request",
    demo: "Request a Demo",
    sales: "Contact Sales",
    custom: "Custom Assessment Inquiry",
    team: "Contact the AI Shield Team",
  },
};

export const CONTENT: Record<Lang, SiteContent> = { en, zh };

export const getContent = (lang: Lang): SiteContent => CONTENT[lang];
