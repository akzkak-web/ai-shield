import { Nav } from "./components/Nav";
import { Hero } from "./components/Hero";
import { LanguageProvider } from "./i18n/LanguageContext";
import {
  Capabilities,
  FAQSection,
  FinalCTA,
  Footer,
  HowItWorks,
  Legal,
  Platform,
  Pricing,
  ReportPreview,
  Solutions,
  TrustStrip,
} from "./components/Sections";

export default function App() {
  return (
    <LanguageProvider>
      <Nav />
      <main id="top">
        <Hero />
        <TrustStrip />
        <Platform />
        <HowItWorks />
        <Capabilities />
        <ReportPreview />
        <Solutions />
        <Pricing />
        <FAQSection />
        <FinalCTA />
      </main>
      <Footer />
      <Legal />
    </LanguageProvider>
  );
}
