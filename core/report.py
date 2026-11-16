"""
AI Shield - PDF Report Generator (commercial bilingual report).

Section layout follows the commercial deliverable contract:

1. Assessment overview (cover)
2. Customer & engagement ID
3. Authorized target scope
4. Assessment timestamp & AI Shield version
5. Executive summary
6. Risk findings (severity, evidence, remediation)
7. Coverage & limitations
8. Retest status

Chinese is the default language; English uses the same underlying schema.
"""
import os
from typing import Dict

from fpdf import FPDF


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


_LABELS = {
    "zh": {
        "title": "AI Shield 安全扫描报告",
        "subtitle": "AI 服务安全评估报告",
        "grade": "安全评级",
        "risk_score": "风险评分",
        "overview": "一、评估概览",
        "customer_section": "二、客户与委托信息",
        "scope_section": "三、授权评估范围",
        "time_section": "四、评估时间与工具版本",
        "exec_section": "五、执行摘要",
        "findings_section": "六、风险发现",
        "coverage_section": "七、覆盖范围与局限性",
        "retest_section": "八、复测状态",
        "assessment_id": "评估编号",
        "assessment_type": "评估类型",
        "tool_version": "AI Shield 版本",
        "target": "评估目标",
        "start_time": "评估开始时间",
        "end_time": "评估结束时间",
        "duration": "评估耗时",
        "ports_scanned": "扫描端口",
        "open_ports": "开放端口",
        "customer": "客户名称",
        "engagement_id": "委托编号",
        "authorized_scope": "授权范围说明",
        "scope_default": "仅限对上述目标与端口执行只读安全评估。",
        "out_of_scope_note": (
            "范围外声明：未经书面授权，不对任何其他主机、端口或域名执行测试。"
        ),
        "non_destructive_note": (
            "本次评估为只读检测，不执行破坏性测试、不修改配置、"
            "不下载或删除模型数据。"
        ),
        "severity_counts": "发现数量",
        "critical": "严重",
        "high": "高危",
        "medium": "中危",
        "low": "低危",
        "info": "提示",
        "grade_reasons": "评级依据",
        "no_findings": "未发现确认的安全问题。",
        "finding_number": "发现",
        "confidence": "置信度",
        "service_label": "服务",
        "description": "描述",
        "evidence": "证据",
        "remediation": "修复建议",
        "coverage_status": "覆盖状态",
        "coverage_counts": "检查项统计",
        "coverage_full": "完整",
        "coverage_partial": "部分",
        "coverage_none": "无",
        "limitations": "局限性说明",
        "limitation_notes": (
            "1. 本次评估为只读检测，不向模型发送生成请求，"
            "提示词注入与数据泄露等生成类风险未被探测。\n"
            "2. 状态为未确认（unknown）或错误（error）的检查项不代表安全。\n"
            "3. 报告仅反映评估时段内的观察结果，不构成长期安全保证。"
        ),
        "notes_label": "评估备注",
        "retest_status": "复测状态",
        "retest_labels": {
            "not_retested": "未复测",
            "retested_pass": "已复测（通过）",
            "retested_fail": "已复测（仍存在问题）",
            "partial": "部分复测",
            "scheduled": "已安排复测",
            "not_applicable": "不适用",
        },
        "retest_note": "如需复测，请以新的委托编号重新发起授权评估。",
        "not_provided": "未提供",
    },
    "en": {
        "title": "AI Shield Security Report",
        "subtitle": "AI Service Security Assessment",
        "grade": "Grade",
        "risk_score": "Risk Score",
        "overview": "1. Assessment Overview",
        "customer_section": "2. Customer & Engagement",
        "scope_section": "3. Authorized Target Scope",
        "time_section": "4. Assessment Timestamp & Version",
        "exec_section": "5. Executive Summary",
        "findings_section": "6. Risk Findings",
        "coverage_section": "7. Coverage & Limitations",
        "retest_section": "8. Retest Status",
        "assessment_id": "Assessment ID",
        "assessment_type": "Assessment Type",
        "tool_version": "AI Shield Version",
        "target": "Target",
        "start_time": "Assessment Started",
        "end_time": "Assessment Finished",
        "duration": "Duration",
        "ports_scanned": "Ports Scanned",
        "open_ports": "Open Ports",
        "customer": "Customer",
        "engagement_id": "Engagement ID",
        "authorized_scope": "Authorized Scope",
        "scope_default": (
            "Only the targets and ports listed above are authorized for "
            "read-only security assessment."
        ),
        "out_of_scope_note": (
            "Out of scope: without written authorization, no other hosts, "
            "ports or domains are tested."
        ),
        "non_destructive_note": (
            "This assessment is read-only: no destructive tests, no "
            "configuration changes, no model download or deletion."
        ),
        "severity_counts": "Findings",
        "critical": "Critical",
        "high": "High",
        "medium": "Medium",
        "low": "Low",
        "info": "Info",
        "grade_reasons": "Why this grade",
        "no_findings": "No confirmed security findings.",
        "finding_number": "Finding",
        "confidence": "Confidence",
        "service_label": "Service",
        "description": "Description",
        "evidence": "Evidence",
        "remediation": "Remediation",
        "coverage_status": "Coverage Status",
        "coverage_counts": "Check Counts",
        "coverage_full": "Full",
        "coverage_partial": "Partial",
        "coverage_none": "None",
        "limitations": "Limitations",
        "limitation_notes": (
            "1. This is a read-only assessment; no generation requests are "
            "sent, so generation-based risks such as prompt injection and "
            "data leakage are not probed.\n"
            "2. Unknown or errored check items do not mean secure.\n"
            "3. This report reflects observations at assessment time only "
            "and is not a long-term security guarantee."
        ),
        "notes_label": "Assessment Notes",
        "retest_status": "Retest Status",
        "retest_labels": {
            "not_retested": "Not retested",
            "retested_pass": "Retested (passed)",
            "retested_fail": "Retested (issues remain)",
            "partial": "Partially retested",
            "scheduled": "Retest scheduled",
            "not_applicable": "Not applicable",
        },
        "retest_note": (
            "For a retest, start a new authorized assessment with a new "
            "engagement ID."
        ),
        "not_provided": "Not provided",
    },
}

_SEVERITY_COLORS = {
    "critical": (220, 38, 38),
    "high": (234, 88, 12),
    "medium": (217, 119, 6),
    "low": (101, 163, 13),
    "info": (37, 99, 235),
}


class PDFReport(FPDF):
    """Generate PDF security report."""

    def __init__(self, lang: str = "zh"):
        super().__init__()
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
        # Without any Unicode-capable font only ASCII is renderable: the
        # report silently falls back to English labels.
        if self._latin_font_path is None and self._cjk_font_path is None:
            lang = "en"
        self.lang = lang if lang in _LABELS else "zh"
        self._t = _LABELS[self.lang]

    def _tt(self, key: str) -> str:
        return self._t.get(key, key)

    def _font(self, style: str = ""):
        if self._latin_font_path:
            return "LatSans", style
        return "Helvetica", style

    def _mono_font(self, style: str = ""):
        if self._latin_font_path:
            return "LatSans", style
        return "Courier", style

    def header(self):
        self.set_font(*self._font("B"), 14)
        self.cell(0, 10, self._tt("title"), 0, 1, "C")
        self.ln(3)

    def footer(self):
        self.set_y(-15)
        self.set_font(*self._font("I"), 8)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", 0, 0, "C")

    def _section(self, title: str):
        self.ln(3)
        self.set_font(*self._font("B"), 13)
        self.cell(0, 9, title, 0, 1, "L")
        self.set_draw_color(120, 120, 120)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.ln(3)

    def _kv(self, label: str, value: str):
        self.set_x(self.l_margin)
        self.set_font(*self._font("B"), 10)
        self.cell(42, 6, label, 0, 0, "L")
        self.set_font(*self._font(), 10)
        self.multi_cell(0, 6, value or self._tt("not_provided"))
        self.set_x(self.l_margin)

    def _severity_color(self, severity: str):
        return _SEVERITY_COLORS.get(str(severity).lower(), (0, 0, 0))

    def _cover(self, result: Dict):
        self.add_page()
        self.ln(25)
        self.set_font(*self._font("B"), 24)
        self.cell(0, 14, "AI Shield", 0, 1, "C")
        self.set_font(*self._font(), 13)
        self.cell(0, 9, self._tt("subtitle"), 0, 1, "C")
        self.cell(0, 8, str(result.get("assessment_type", "")), 0, 1, "C")
        self.ln(14)

        grade = result.get("grade", "N/A")
        score = result.get("risk_score", 0)
        self.set_font(*self._font("B"), 44)
        r, g, b = self._severity_color(grade)
        self.set_text_color(r, g, b)
        self.cell(0, 18, f"{self._tt('grade')}: {grade}", 0, 1, "C")
        self.set_text_color(0, 0, 0)
        self.set_font(*self._font(), 12)
        self.cell(0, 9, f"{self._tt('risk_score')}: {score}/100", 0, 1, "C")
        self.ln(14)

        self.set_font(*self._font(), 10)
        for line in (
            f"{self._tt('target')}: {result.get('target', 'N/A')}",
            f"{self._tt('assessment_id')}: {result.get('id', 'N/A')}",
            f"{self._tt('engagement_id')}: "
            f"{result.get('engagement_id') or self._tt('not_provided')}",
            f"{self._tt('start_time')}: {result.get('start_time', 'N/A')}",
        ):
            self.cell(0, 8, line, 0, 1, "C")

    def _overview(self, result: Dict):
        self._section(self._tt("overview"))
        pd = result.get("port_data", {})
        self._kv(self._tt("assessment_id"), str(result.get("id", "N/A")))
        self._kv(self._tt("assessment_type"), str(result.get("assessment_type", "")))
        self._kv(self._tt("tool_version"), str(result.get("tool_version", "N/A")))
        self._kv(self._tt("target"), str(result.get("target", "N/A")))
        ports = ", ".join(str(p) for p in pd.get("open_ports", []))
        self._kv(self._tt("ports_scanned"),
                 ports or str(pd.get("total_scanned", 0)))
        self._kv(self._tt("open_ports"), ports or "-")

    def _customer_section(self, result: Dict):
        self._section(self._tt("customer_section"))
        self._kv(self._tt("customer"), str(result.get("customer", "")))
        self._kv(self._tt("engagement_id"), str(result.get("engagement_id", "")))

    def _scope_section(self, result: Dict):
        self._section(self._tt("scope_section"))
        scope = str(result.get("authorized_scope", ""))
        self._kv(self._tt("target"), str(result.get("target", "N/A")))
        self._kv(self._tt("authorized_scope"), scope or self._tt("scope_default"))
        self.set_font(*self._font(), 9)
        self.multi_cell(0, 5, self._tt("out_of_scope_note"))
        self.ln(2)
        self.multi_cell(0, 5, self._tt("non_destructive_note"))

    def _time_section(self, result: Dict):
        self._section(self._tt("time_section"))
        self._kv(self._tt("start_time"), str(result.get("start_time", "N/A")))
        self._kv(self._tt("end_time"), str(result.get("end_time", "N/A")))
        self._kv(self._tt("duration"), f"{result.get('duration', 0)}s")
        self._kv(self._tt("tool_version"), str(result.get("tool_version", "N/A")))

    def _exec_summary(self, result: Dict):
        self._section(self._tt("exec_section"))
        grade = result.get("grade", "N/A")
        score = result.get("risk_score", 0)
        self.set_font(*self._font("B"), 14)
        self.cell(0, 8, f"{self._tt('grade')}: {grade}  "
                        f"{self._tt('risk_score')}: {score}/100", 0, 1, "L")
        self.ln(2)

        self.set_font(*self._font("B"), 10)
        self.cell(0, 7, self._tt("severity_counts"), 0, 1, "L")
        summary = result.get("summary", {})
        self.set_font(*self._font(), 10)
        for severity in ("critical", "high", "medium", "low", "info"):
            count = summary.get(severity, 0)
            r, g, b = self._severity_color(severity)
            self.set_text_color(r, g, b)
            self.cell(0, 6, f"  {self._tt(severity)}: {count}", 0, 1, "L")
        self.set_text_color(0, 0, 0)

        reasons = result.get("grade_reasons", [])
        self.ln(2)
        self.set_font(*self._font("B"), 10)
        self.cell(0, 7, self._tt("grade_reasons"), 0, 1, "L")
        self.set_font(*self._font(), 9)
        for reason in reasons:
            self.set_x(self.l_margin)
            self.multi_cell(0, 5, f"- {reason}")

    def _finding_block(self, finding: Dict, index: int):
        severity = str(finding.get("severity", "info")).upper()
        if self.lang == "zh":
            title = finding.get("title_zh", "")
        else:
            title = finding.get("title_en", "")
        if not title:
            title = finding.get("title_en", "") or finding.get("title_zh", "")
        self.ln(3)
        self.set_font(*self._font("B"), 11)
        self.cell(0, 7, f"{self._tt('finding_number')} #{index + 1}: {title}", 0, 1, "L")

        r, g, b = _SEVERITY_COLORS.get(severity.lower(), (128, 128, 128))
        self.set_fill_color(r, g, b)
        self.set_text_color(255, 255, 255)
        self.set_font(*self._font("B"), 9)
        self.cell(28, 7, severity, 0, 0, "L", fill=True)
        self.set_text_color(0, 0, 0)
        self.set_font(*self._font(), 9)
        self.cell(0, 7, f" {self._tt('confidence')}: "
                        f"{finding.get('confidence', 'confirmed')}", 0, 1, "L")
        self.ln(1)
        self._kv(self._tt("service_label"),
                 f"{finding.get('service', 'N/A')}:{finding.get('port', 'N/A')}")
        if self.lang == "zh":
            desc = finding.get("description_zh", "")
        else:
            desc = finding.get("description_en", "")
        if not desc:
            desc = finding.get("description_en", "") or finding.get("description_zh", "")
        self.set_font(*self._font("B"), 10)
        self.cell(0, 6, self._tt("description"), 0, 1, "L")
        self.set_font(*self._font(), 9)
        self.multi_cell(0, 5, desc or "-")
        self.ln(1)

        self.set_font(*self._font("B"), 10)
        self.cell(0, 6, self._tt("evidence"), 0, 1, "L")
        self.set_font(*self._mono_font(), 8)
        self.set_fill_color(245, 245, 245)
        self.multi_cell(0, 4, finding.get("evidence", "") or "-", fill=True)
        self.ln(1)

        if self.lang == "zh":
            rec = finding.get("recommendation_zh", "")
        else:
            rec = finding.get("recommendation_en", "")
        if not rec:
            rec = finding.get("recommendation_en", "") or finding.get("recommendation_zh", "")
        self.set_font(*self._font("B"), 10)
        self.cell(0, 6, self._tt("remediation"), 0, 1, "L")
        self.set_font(*self._font(), 9)
        self.multi_cell(0, 5, rec or "-")
        remediation = finding.get("remediation", "")
        if remediation:
            self.set_font(*self._mono_font(), 8)
            self.set_fill_color(240, 240, 240)
            self.multi_cell(0, 5, remediation, fill=True)

    def _coverage_section(self, result: Dict):
        self._section(self._tt("coverage_section"))
        status = str(result.get("coverage_status", "none"))
        self._kv(self._tt("coverage_status"), self._tt(f"coverage_{status}"))
        cov = result.get("coverage", {})
        counts = ", ".join(f"{k}={v}" for k, v in cov.items())
        self._kv(self._tt("coverage_counts"), counts or "-")
        notes = result.get("notes", [])
        if notes:
            self._kv(self._tt("notes_label"), "\n".join(str(n) for n in notes))
        self.ln(2)
        self.set_font(*self._font("B"), 10)
        self.cell(0, 6, self._tt("limitations"), 0, 1, "L")
        self.set_font(*self._font(), 9)
        self.multi_cell(0, 5, self._tt("limitation_notes"))

    def _retest_section(self, result: Dict):
        self._section(self._tt("retest_section"))
        status = str(result.get("retest_status", "not_retested"))
        labels = self._t.get("retest_labels", {})
        fallback = _LABELS["zh"]["retest_labels"].get(status, status)
        self._kv(self._tt("retest_status"), labels.get(status, fallback))
        self.set_font(*self._font(), 9)
        self.multi_cell(0, 5, self._tt("retest_note"))

    def generate(self, result: Dict, output_path: str):
        """Generate complete PDF report."""
        self.alias_nb_pages()

        self._cover(result)
        self.add_page()
        self._overview(result)
        self._customer_section(result)
        self._scope_section(result)
        self._time_section(result)
        self._exec_summary(result)

        self.add_page()
        self._section(self._tt("findings_section"))
        findings = result.get("findings", [])
        if not findings:
            self.set_font(*self._font(), 10)
            self.multi_cell(0, 6, self._tt("no_findings"))
        for i, finding in enumerate(findings):
            self._finding_block(finding, i)

        self._coverage_section(result)
        self._retest_section(result)

        self.output(output_path)
        return output_path


def generate_pdf_report(result: Dict, output_path: str, lang: str = "zh") -> str:
    """Generate PDF report from scan result."""
    pdf = PDFReport(lang)
    return pdf.generate(result, output_path)
