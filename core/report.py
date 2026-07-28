"""
AI Shield - PDF Report Generator
"""
from fpdf import FPDF
from datetime import datetime
from typing import List, Dict


class PDFReport(FPDF):
    """Generate PDF security report."""

    def __init__(self, lang: str = "zh"):
        super().__init__()
        self.lang = lang
        self.set_auto_page_break(auto=True, margin=15)

    def header(self):
        self.set_font("Helvetica", "B", 16)
        self.cell(0, 10, "AI Shield Security Report", 0, 1, "C")
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", 0, 0, "C")

    def add_title_page(self, result: Dict):
        """Add title page with summary."""
        self.add_page()
        self.ln(30)

        # Title
        self.set_font("Helvetica", "B", 24)
        self.cell(0, 15, "AI Shield", 0, 1, "C")
        self.set_font("Helvetica", "", 14)
        self.cell(0, 10, "Local AI Security Scanner", 0, 1, "C")
        self.ln(20)

        # Grade circle
        grade = result.get("grade", "N/A")
        score = result.get("risk_score", 0)
        self.set_font("Helvetica", "B", 48)
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

        self.set_font("Helvetica", "", 12)
        self.cell(0, 10, f"Risk Score: {score}/100", 0, 1, "C")
        self.ln(20)

        # Scan info
        self.set_font("Helvetica", "", 10)
        info = [
            f"Target: {result.get('target', 'N/A')}",
            f"Scan Time: {result.get('start_time', 'N/A')}",
            f"Duration: {result.get('duration', 0)}s",
            f"Open Ports: {len(result.get('port_data', {}).get('open_ports', []))}",
            f"AI Services: {len([s for s in result.get('port_data', {}).get('services', []) if s.get('detected')])}",
        ]
        for line in info:
            self.cell(0, 8, line, 0, 1, "C")

    def add_findings_summary(self, result: Dict):
        """Add findings summary page."""
        self.add_page()
        self.set_font("Helvetica", "B", 14)
        self.cell(0, 10, "Findings Summary", 0, 1, "L")
        self.ln(5)

        summary = result.get("summary", {})
        self.set_font("Helvetica", "", 11)

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

    def add_finding_detail(self, finding: Dict, index: int):
        """Add detailed finding page."""
        self.add_page()

        # Header
        severity = finding.get("severity", "info").upper()
        title = finding.get("title_en", finding.get("title_zh", "Unknown"))

        self.set_font("Helvetica", "B", 12)
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
        self.set_font("Helvetica", "B", 10)
        self.cell(30, 8, severity, 0, 0, "L", fill=True)
        self.set_text_color(0, 0, 0)
        self.ln(5)

        # Service info
        self.set_font("Helvetica", "", 10)
        self.cell(0, 6, f"Service: {finding.get('service', 'N/A')}:{finding.get('port', 'N/A')}", 0, 1, "L")
        self.ln(3)

        # Description
        self.set_font("Helvetica", "B", 10)
        self.cell(0, 6, "Description:", 0, 1, "L")
        self.set_font("Helvetica", "", 9)
        desc = finding.get("description_en", finding.get("description_zh", ""))
        self.multi_cell(0, 5, desc)
        self.ln(3)

        # Evidence
        self.set_font("Helvetica", "B", 10)
        self.cell(0, 6, "Evidence:", 0, 1, "L")
        self.set_font("Courier", "", 8)
        evidence = finding.get("evidence", "")
        self.multi_cell(0, 4, evidence)
        self.ln(3)

        # Recommendation
        self.set_font("Helvetica", "B", 10)
        self.cell(0, 6, "Recommendation:", 0, 1, "L")
        self.set_font("Helvetica", "", 9)
        rec = finding.get("recommendation_en", finding.get("recommendation_zh", ""))
        self.multi_cell(0, 5, rec)
        self.ln(3)

        # Remediation script
        remediation = finding.get("remediation", "")
        if remediation:
            self.set_font("Helvetica", "B", 10)
            self.cell(0, 6, "Remediation Command:", 0, 1, "L")
            self.set_font("Courier", "", 8)
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
