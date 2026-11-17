export const NAV_LINKS = [
  { label: "Platform", href: "#platform" },
  { label: "Solutions", href: "#solutions" },
  { label: "Security Assessment", href: "#how-it-works" },
  { label: "Resources", href: "#report" },
  { label: "Pricing", href: "#pricing" },
];

export const HERO_PROPS = [
  "Evidence-Based Security Assessment",
  "Actionable Remediation Guidance",
  "Clear Coverage & Risk Visibility",
];

export const VALUE_PROPS = [
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
];

export const PLATFORM_CARDS = [
  {
    title: "Infrastructure Exposure",
    body: "Understand whether AI inference services are exposed beyond their intended network boundaries.",
    visual: "exposure",
  },
  {
    title: "Security Configuration",
    body: "Review supported authentication, CORS, access and service configuration signals.",
    visual: "config",
  },
  {
    title: "Vulnerability Intelligence",
    body: "Match supported service and version information against available vulnerability intelligence.",
    visual: "intel",
  },
];

export const STEPS = [
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
];

export type CapabilityStatus = "Verified" | "Supported";

export const CAPABILITIES: { name: string; body: string; status: CapabilityStatus }[] = [
  { name: "Network Exposure Assessment", body: "Determine whether a service listens beyond its intended boundary.", status: "Verified" },
  { name: "Authentication Configuration Review", body: "Check whether model endpoints require credentials.", status: "Verified" },
  { name: "CORS Configuration Review", body: "Detect permissive or reflected cross-origin policies.", status: "Verified" },
  { name: "Model API Access Review", body: "Check whether unauthenticated users can enumerate models.", status: "Verified" },
  { name: "Rate Limiting Assessment", body: "Observe rate-limit signals on service endpoints.", status: "Verified" },
  { name: "Vulnerability Version Matching", body: "Compare detected service versions with known advisories.", status: "Verified" },
  { name: "Evidence-Based Findings", body: "Every finding carries the evidence that supports it.", status: "Supported" },
  { name: "JSON & PDF Reporting", body: "Structured machine data plus a readable assessment report.", status: "Supported" },
  { name: "Baseline Comparison", body: "Diff a new assessment against a stored baseline.", status: "Supported" },
];

export const SOLUTIONS = [
  {
    title: "AI Deployment Providers",
    body: "Verify the security posture of the environments you ship before customers rely on them.",
  },
  {
    title: "Enterprise IT Teams",
    body: "Get an independent view of self-hosted AI services inside your network.",
  },
  {
    title: "AI Application Companies",
    body: "Understand how your inference layer is configured and what to fix first.",
  },
  {
    title: "Private AI Infrastructure Operators",
    body: "Keep controlled environments aligned with your own security expectations.",
  },
];

export const FAQ = [
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
];
