#!/usr/bin/env python3
"""
AI Shield - Local AI Security Scanner.

Entry point for both CLI and Web modes.
"""
import argparse
import asyncio
import json
import os
import sys

# Ensure project root is in path.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core import __version__


def cmd_web(args):
    import uvicorn
    from web.server import app, assert_safe_bind

    try:
        assert_safe_bind(args.host)
    except RuntimeError as exc:
        print(f"❌ {exc}")
        sys.exit(1)

    print(
        f"""
    ╔═══════════════════════════════════════╗
    ║       🛡️  AI Shield v0.1.0-rc.1      ║
    ║     Local AI Security Scanner         ║
    ╠═══════════════════════════════════════╣
    ║  Web UI:  http://{args.host}:{args.port}
    ║  Press Ctrl+C to stop                 ║
    ╚═══════════════════════════════════════╝
    """
    )
    uvicorn.run(app, host=args.host, port=args.port, log_level="info")


def _parse_ports(raw):
    if not raw:
        return None
    return [int(p.strip()) for p in raw.split(",") if p.strip()]


def _parse_checks(raw):
    if not raw or raw == "all":
        return None
    return [c.strip() for c in raw.split(",") if c.strip()]


def _gate(findings, threshold, coverage_status=None):
    """Return ``(exit_code, message)`` for the fail gate.

    Exit code 0 = pass (no confirmed finding at/above threshold), 1 = fail.
    Only ``confirmed`` findings count; unknown/error/coverage never become a
    clean pass.
    """
    from core.rating import SEVERITY_ORDER, confirmed_findings_above, fail_gate_triggered

    threshold = threshold or "critical"
    if fail_gate_triggered(findings, threshold):
        above = confirmed_findings_above(findings, threshold)
        sevs = sorted(
            {f.get("severity", "info") for f in above},
            key=lambda s: -SEVERITY_ORDER.get(s, 0),
        )
        return 1, (
            f"🛡️  Fail gate: FAILED — {len(above)} confirmed finding(s) "
            f"at or above '{threshold}' ({', '.join(sevs)})"
        )
    note = ""
    if coverage_status and coverage_status != "full":
        note = f" (coverage={coverage_status}; no findings is NOT a security guarantee)"
    return 0, f"🛡️  Fail gate: PASS — no confirmed finding at or above '{threshold}'{note}"


def _print_diff(diff):
    summary = diff.get("summary", {})
    print("📊 Diff vs baseline:")
    for status in ("new", "fixed", "persistent", "changed", "unknown"):
        if summary.get(status):
            print(f"   {status}: {summary[status]}")
    if diff.get("version_note"):
        print(f"   ⚠️  {diff['version_note']}")
    for e in diff.get("entries", []):
        sev = e.get("severity", "info").upper()
        cid = e.get("check_id", "")
        svc = e.get("service", "")
        port = e.get("port", "")
        line = f"   [{e['status']:>10}] [{sev:>8}] {cid} ({svc}:{port})"
        if e.get("reason"):
            line += f" — {e['reason']}"
        print(line)


def _compute_gate(args, result, diff):
    """Compute the exit code from absolute and/or incremental gates."""
    from core.baseline import new_confirmed_above
    from core.rating import SEVERITY_ORDER

    codes = []
    fail_on = getattr(args, "fail_on", None)
    fail_on_new = getattr(args, "fail_on_new", None)

    if fail_on:
        code, msg = _gate(
            result.get("findings", []), fail_on, result.get("coverage_status")
        )
        print(msg)
        codes.append(code)

    if fail_on_new:
        if diff is None:
            print("⚠️  --fail-on-new requires --baseline; incremental gate not applied")
        else:
            above = new_confirmed_above(diff.get("entries", []), fail_on_new)
            if above:
                sevs = sorted(
                    {e.get("severity", "info") for e in above},
                    key=lambda s: -SEVERITY_ORDER.get(s, 0),
                )
                print(
                    f"🛡️  New-finding gate: FAILED — {len(above)} new confirmed "
                    f"finding(s) at or above '{fail_on_new}' ({', '.join(sevs)})"
                )
                codes.append(1)
            else:
                incomplete = any(
                    e.get("status") == "unknown" for e in diff.get("entries", [])
                )
                note = (
                    " (comparison incomplete; absence of new findings is not a guarantee)"
                    if incomplete
                    else ""
                )
                print(
                    f"🛡️  New-finding gate: PASS — no new confirmed finding at or "
                    f"above '{fail_on_new}'{note}"
                )
                codes.append(0)

    if not fail_on and not fail_on_new:
        code, msg = _gate(
            result.get("findings", []), "critical", result.get("coverage_status")
        )
        print(msg)
        codes.append(code)

    return 1 if 1 in codes else 0


def cmd_scan(args):
    from core.baseline import (
        BaselineError,
        build_baseline,
        compare_baseline,
        load_baseline,
        save_baseline,
    )
    from core.report import generate_pdf_report
    from core.scanner import Scanner

    target = args.target
    ports = _parse_ports(args.ports)
    checks = _parse_checks(args.checks)

    scanner = Scanner()

    if "/" in target:
        if any(
            getattr(args, k, None)
            for k in ("baseline", "baseline_out", "fail_on_new", "diff_json")
        ):
            print("❌ Baseline comparison is only supported for single-target scans, not subnets.")
            return 2
        print(f"\n🛡️  AI Shield - Subnet Scan: {target}\n")
        try:
            results = asyncio.run(
                scanner.run_subnet_scan(
                    target, ports, checks, allow_private=args.allow_private
                )
            )
        except ValueError as exc:
            print(f"❌ 目标被拒绝: {exc}")
            return 2
        except Exception as exc:
            print(f"❌ 扫描失败: {type(exc).__name__}")
            return 2

        total_critical = sum(r.get("summary", {}).get("critical", 0) for r in results if "summary" in r)
        print(f"{'=' * 50}")
        print(f"  Targets: {len(results)}")
        print(f"  Critical: {total_critical}")
        print(f"{'=' * 50}\n")
        for r in results:
            if "error" in r:
                print(f"  ❌ {r['target']}: {r['error']}")
            else:
                grade = r.get("grade", "N/A")
                findings = len(r.get("findings", []))
                print(f"  {r['target']}: Grade {grade}, {findings} findings")

        if args.output:
            with open(args.output, "w", encoding="utf-8") as fp:
                json.dump(results, fp, ensure_ascii=False, indent=2)
            print(f"\n📄 Report saved to {args.output}")

        all_findings = []
        for r in results:
            if "findings" in r:
                all_findings.extend(r["findings"])
        exit_code, msg = _gate(all_findings, getattr(args, "fail_on", None))
        print(msg)
        return exit_code

    print(f"\n🛡️  AI Shield - Scanning {target}...\n")
    try:
        result = asyncio.run(
            scanner.run_scan(target, ports, checks, allow_private=args.allow_private)
        )
    except ValueError as exc:
        print(f"❌ 目标被拒绝: {exc}")
        return 2
    except Exception as exc:
        print(f"❌ 扫描失败: {type(exc).__name__}")
        return 2

    print(f"{'=' * 50}")
    print(f"  Grade: {result['grade']}  |  Risk Score: {result['risk_score']}/100")
    print(f"  Coverage: {result.get('coverage_status', 'none')}")
    print(f"  Duration: {result['duration']}s")
    print(f"{'=' * 50}\n")

    for reason in result.get("grade_reasons", []):
        print(f"  📋 {reason}")
    for note in result.get("notes", []):
        print(f"  ℹ️  {note}")
    print()

    cr = result.get("check_results", {})
    if cr:
        statuses = ", ".join(f"{k}={v}" for k, v in sorted(cr.items()))
        print(f"  ✅ Check status: {statuses}\n")

    pd = result.get("port_data", {})
    print(f"📡 Open Ports: {len(pd.get('open_ports', []))}")
    for svc in pd.get("services", []):
        detected = "✅" if svc.get("detected") else ""
        ver = f" v{svc['version']}" if svc.get("version") else ""
        print(f"   {svc['port']:>5}/tcp  {svc['service']}{ver} {detected}")
    print()

    findings = result.get("findings", [])
    s = result.get("summary", {})
    print(f"🐛 Findings: {len(findings)}")
    print(
        f"   Critical: {s.get('critical', 0)}  High: {s.get('high', 0)}  "
        f"Medium: {s.get('medium', 0)}  Low: {s.get('low', 0)}\n"
    )

    for f in findings:
        sev = f["severity"].upper()
        title = f.get("title_en", f.get("title_zh", ""))
        conf = f.get("confidence", "confirmed")
        print(f"   [{sev:>8}] ({conf}) {title}")
        print(f"            {f.get('service', '')}:{f.get('port', '')}")
        if f.get("evidence"):
            for line in f["evidence"].split("\n")[:3]:
                print(f"            → {line}")
        if f.get("recommendation_en"):
            print(f"            🔧 Fix: {f['recommendation_en'].split(chr(10))[0]}")
        print()

    if args.output:
        if args.output.endswith(".pdf"):
            generate_pdf_report(result, args.output)
            print(f"📄 PDF report saved to {args.output}")
        else:
            with open(args.output, "w", encoding="utf-8") as fp:
                json.dump(result, fp, ensure_ascii=False, indent=2)
            print(f"📄 Report saved to {args.output}")

    print()

    diff = None
    try:
        if getattr(args, "baseline_out", None):
            save_baseline(build_baseline(result), args.baseline_out)
            print(f"📌 Baseline saved to {args.baseline_out}")

        if getattr(args, "baseline", None):
            baseline = load_baseline(args.baseline)
            diff = compare_baseline(baseline, result)
            _print_diff(diff)
            if getattr(args, "diff_json", None):
                with open(args.diff_json, "w", encoding="utf-8") as fp:
                    json.dump(diff, fp, ensure_ascii=False, indent=2)
                print(f"📄 Diff report saved to {args.diff_json}")
    except BaselineError as exc:
        print(f"❌ Baseline error: {exc}")
        return 2

    return _compute_gate(args, result, diff)


def cmd_refresh(args):
    """Fetch vulnerability intelligence from NVD + EPSS + CISA KEV."""
    from core.config import settings
    from core.intel import refresh_advisories

    print("🔄 Fetching vulnerability intelligence (NVD + EPSS + CISA KEV)...")
    result = asyncio.run(
        refresh_advisories(nvd_api_key=settings.nvd_api_key or args.api_key)
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("saved") else 1


def main():
    parser = argparse.ArgumentParser(
        description="AI Shield - Local AI Security Scanner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s web                          Start web UI on port 8899
  %(prog)s scan 127.0.0.1               Scan localhost for AI services
  %(prog)s scan 192.168.1.100 --ports 11434,8000
  %(prog)s scan 192.168.1.0/24 --allow-private
  %(prog)s scan 10.0.0.1 -o report.json
  %(prog)s scan 10.0.0.1 -o report.pdf
  %(prog)s refresh-intel                 Update NVD/EPSS/KEV cache
        """,
    )
    parser.add_argument("--version", action="version", version=__version__)

    subparsers = parser.add_subparsers(dest="command")

    web_parser = subparsers.add_parser("web", help="Start web UI")
    web_parser.add_argument("--host", default="127.0.0.1")
    web_parser.add_argument("--port", type=int, default=8899)

    scan_parser = subparsers.add_parser("scan", help="Run CLI scan")
    scan_parser.add_argument("target", help="Target IP, hostname, or CIDR")
    scan_parser.add_argument("--ports", help="Comma-separated ports")
    scan_parser.add_argument("--checks", default="all", help="Comma-separated checks or 'all'")
    scan_parser.add_argument("--allow-private", action="store_true",
                             help="Allow scanning private/LAN targets")
    scan_parser.add_argument("--fail-on", choices=["critical", "high", "medium", "low"],
                             help="Exit non-zero when a confirmed finding reaches this severity (default: critical)")
    scan_parser.add_argument("--baseline", help="Compare against a previous baseline JSON")
    scan_parser.add_argument("--baseline-out", help="Write a new baseline JSON after scanning")
    scan_parser.add_argument("--diff-json", help="Write the diff report to this JSON path (requires --baseline)")
    scan_parser.add_argument("--fail-on-new", choices=["critical", "high", "medium", "low"],
                             help="Exit non-zero when a NEW confirmed finding reaches this severity (requires --baseline)")
    scan_parser.add_argument("-o", "--output", help="Save report (.json or .pdf)")

    refresh_parser = subparsers.add_parser("refresh-intel", help="Fetch vulnerability intelligence")
    refresh_parser.add_argument("--api-key", help="NVD API key (overrides AI_SHIELD_NVD_API_KEY)")

    args = parser.parse_args()

    if args.command == "web":
        cmd_web(args)
    elif args.command == "scan":
        sys.exit(cmd_scan(args))
    elif args.command == "refresh-intel":
        sys.exit(cmd_refresh(args))
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
