"""
AI Shield - PDF Report Generator
"""
import os

from fpdf import FPDF
from typing import List, Dict


_LATIN_FONT_CANDIDATES = [
    # Latin + broad Unicode punctuation (including em dash), no CJK.
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    # Arial Unicode covers both Latin and CJK and can serve as primary.
    "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
    "C:/Windows/Fonts/arial.ttf",
]

_CJK_FONT_CANDIDATES = [
    # CJK fallback fonts. Latin coverage is not required here.
    "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttf",
    "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
    "/System/Library/Fonts/PingFang.ttc",
    "C:/Windows/Fonts/msyh.ttc",
    "C:/Windows/Fonts/arialuni.ttf",
]


def _find_font(candidates) -> str | None:
    for path in candidates:
        if os.path.isfile(path) and os.access(path, os.R_OK):
            return path
    return None


class PDFReport(FPDF):
    """Generate PDF security report."""

    def __init__(self, lang: str = "zh"):
        super().__init__()
        self.lang = lang
        self.set_auto_page_break(auto=True, margin=15)
        self._latin_font_path = _find_font(_LATIN_FONT_CANDIDATES)
        self._cjk_font_path = _find_font(_CJK_FONT_CANDIDATES)
        if self._latin_font_path:
            # Bold/italic styles reuse the same file when a separate style
            # font is unavailable; preserving text is more important than
            # exact typography in generated security reports.
            self.add_font("LatSans", "", self._latin_font_path)
            self.add_font("LatSans", "B", self._latin_font_path)
            self.add_font("LatSans", "I", self._latin_font_path)
            self.add_font("LatSans", "BI", self._latin_font_path)
        if self._cjk_font_path:
            self.add_font("CjkSans", "", self._cjk_font_path)
            self.add_font("CjkSans", "B", self._cjk_font_path)
            self.add_font("CjkSans", "I", self._cjk_font_path)
            self.add_font("CjkSans", "BI", self._cjk_font_path)
            self.set_fallback_fonts(["CjkSans"], exact_match=False)

    def _font(self, style: str = "") -> tuple[str, str]:
        if self._latin_font_path:
            return "LatSans", style
        return "Helvetica", style

    def _mono_font(self, style: str = "") -> tuple[str, str]:
        # Evidence/remediation keep proportional text when a Unicode-capable
        # primary font is available; otherwise use Courier for ASCII reports.
        if self._latin_font_path:
            return "LatSans", style
        return "Courier", style

    def header(self):
        self.set_font(*self._font("B"), 16)
        self.cell(0, 10, "AI Shield Security Report", 0, 1, "C")
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font(*self._font("I"), 8)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", 0, 0, "C")

    def add_title_page(self, result: Dict):
        """Add title page with summary."""
        self.add_page()
        self.ln(30)

        # Title
        self.set_font(*self._font("B"), 24)
        self.cell(0, 15, "AI Shield", 0, 1, "C")
        self.set_font(*self._font(), 14)
        self.cell(0, 10, "Local AI Security Scanner", 0, 1, "C")
        self.ln(20)

        # Grade circle
        grade = result.get("grade", "N/A")
        score = result.get("risk_score", 0)
        self.set_font(*self._font("B"), 48)
        if grade == "A":
            self.set_text_color(34, 197, 94)
        elif grade == "B":
            self.set_text_color(101, 163, 13)
        elif grade == "C":
            self.set_text_color(217, 119, 6)
        elif grade == "D":
            self.set_text_color(234, 88, 12)
        else:
            self.set_text_color(220, 38, 38)
        self.cell(0, 20, f"Grade: {grade}", 0, 1, "C")
        self.set_text_color(0, 0, 0)

        self.set_font(*self._font(), 12)
        self.cell(0, 10, f"Risk Score: {score}/100", 0, 1, "C")
        self.ln(20)

        # Scan info
        self.set_font(*self._font(), 10)
        info = [
            f"Target: {result.get('target', 'N/A')}",
            f"Scan Time: {result.get('start_time', 'N/A')}",
            f"Duration: {result.get('duration', 0)}s",
            f"Open Ports: {len(result.get('port_data', {}).get('open_ports', []))}",
            f"AI Services: {len([s for s in result.get('port_data', {}).get('services', []) if s.get('detected')])}",
            f"Coverage: {result.get('coverage_status', 'none')}",
        ]
        for line in info:
            self.cell(0, 8, line, 0, 1, "C")

    def add_findings_summary(self, result: Dict):
        """Add findings summary page."""
        self.add_page()
        self.set_font(*self._font("B"), 14)
        self.cell(0, 10, "Findings Summary", 0, 1, "L")
        self.ln(5)

        summary = result.get("summary", {})
        self.set_font(*self._font(), 11)

        colors = {
            "critical": (220, 38, 38),
            "high": (234, 88, 12),
            "medium": (217, 119, 6),
            "low": (101, 163, 13),
            "info": (37, 99, 235),
        }

        for severity, count in summary.items():
            r, g, b = colors.get(severity, (0, 0, 0))
            self.set_text_color(r, g, b)
            self.cell(0, 8, f"{severity.upper()}: {count}", 0, 1, "L")
        self.set_text_color(0, 0, 0)

        reasons = result.get("grade_reasons", [])
        if reasons:
            self.ln(4)
            self.set_font(*self._font("B"), 11)
            self.cell(0, 8, "Why this grade:", 0, 1, "L")
            self.set_font(*self._font(), 10)
            for reason in reasons:
                self.cell(0, 6, f"- {reason}", 0, 1, "L")

    def add_finding_detail(self, finding: Dict, index: int):
        """Add detailed finding page."""
        self.add_page()

        # Header
        severity = finding.get("severity", "info").upper()
        title = finding.get("title_en", finding.get("title_zh", "Unknown"))

        self.set_font(*self._font("B"), 12)
        self.cell(0, 10, f"Finding #{index + 1}: {title}", 0, 1, "L")

        # Severity badge
        colors = {
            "CRITICAL": (220, 38, 38),
            "HIGH": (234, 88, 12),
            "MEDIUM": (217, 119, 6),
            "LOW": (101, 163, 13),
            "INFO": (37, 99, 235),
        }
        r, g, b = colors.get(severity, (128, 128, 128))
        self.set_fill_color(r, g, b)
        self.set_text_color(255, 255, 255)
        self.set_font(*self._font("B"), 10)
        self.cell(30, 8, severity, 0, 0, "L", fill=True)
        self.set_text_color(0, 0, 0)
        self.ln(5)

        confidence = finding.get("confidence", "confirmed")
        self.set_font(*self._font("I"), 9)
        self.cell(0, 6, f"Confidence: {confidence}", 0, 1, "L")
        self.set_font(*self._font(), 10)

        # Service info
        self.set_font(*self._font(), 10)
        self.cell(0, 6, f"Service: {finding.get('service', 'N/A')}:{finding.get('port', 'N/A')}", 0, 1, "L")
        self.ln(3)

        # Description
        self.set_font(*self._font("B"), 10)
        self.cell(0, 6, "Description:", 0, 1, "L")
        self.set_font(*self._font(), 9)
        desc = finding.get("description_en", finding.get("description_zh", ""))
        self.multi_cell(0, 5, desc)
        self.ln(3)

        # Evidence
        self.set_font(*self._font("B"), 10)
        self.cell(0, 6, "Evidence:", 0, 1, "L")
        self.set_font(*self._mono_font(), 8)
        evidence = finding.get("evidence", "")
        self.multi_cell(0, 4, evidence)
        self.ln(3)

        # Recommendation
        self.set_font(*self._font("B"), 10)
        self.cell(0, 6, "Recommendation:", 0, 1, "L")
        self.set_font(*self._font(), 9)
        rec = finding.get("recommendation_en", finding.get("recommendation_zh", ""))
        self.multi_cell(0, 5, rec)
        self.ln(3)

        # Remediation script
        remediation = finding.get("remediation", "")
        if remediation:
            self.set_font(*self._font("B"), 10)
            self.cell(0, 6, "Remediation Command:", 0, 1, "L")
            self.set_font(*self._mono_font(), 8)
            self.set_fill_color(240, 240, 240)
            self.multi_cell(0, 5, remediation, fill=True)

    def generate(self, result: Dict, output_path: str):
        """Generate complete PDF report."""
        self.alias_nb_pages()

        # Title page
        self.add_title_page(result)

        # Findings summary
        self.add_findings_summary(result)

        # Individual findings
        findings = result.get("findings", [])
        for i, finding in enumerate(findings):
            self.add_finding_detail(finding, i)

        # Save
        self.output(output_path)
        return output_path


def generate_pdf_report(result: Dict, output_path: str, lang: str = "zh") -> str:
    """Generate PDF report from scan result."""
    pdf = PDFReport(lang)
    return pdf.generate(result, output_path)
