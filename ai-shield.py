#!/usr/bin/env python3
"""
AI Shield - Local AI Security Scanner
Entry point for both CLI and Web modes.

Usage:
    python ai-shield.py web [--port 8899] [--host 0.0.0.0]
    python ai-shield.py scan <target> [--ports 11434,8000,8080] [--checks all]
"""
import sys
import os
import argparse
import asyncio
import json

# Ensure project root is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def cmd_web(args):
    """Start the web UI server."""
    import uvicorn
    from web.server import app

    print(f"""
    ╔═══════════════════════════════════════╗
    ║          🛡️  AI Shield v1.0.0         ║
    ║     Local AI Security Scanner         ║
    ╠═══════════════════════════════════════╣
    ║  Web UI:  http://{args.host}:{args.port}        
    ║  Press Ctrl+C to stop                 ║
    ╚═══════════════════════════════════════╝
    """)

    uvicorn.run(app, host=args.host, port=args.port, log_level="info")


def cmd_scan(args):
    """Run a CLI scan."""
    from core.scanner import Scanner
    from core.report import generate_pdf_report

    target = args.target
    ports = None
    if args.ports:
        ports = [int(p.strip()) for p in args.ports.split(",")]

    checks = None
    if args.checks and args.checks != "all":
        checks = [c.strip() for c in args.checks.split(",")]

    # Check if subnet scan
    is_subnet = "/" in target

    if is_subnet:
        print(f"\n🛡️  AI Shield - Subnet Scan: {target}\n")
        scanner = Scanner()
        results = asyncio.run(scanner.run_subnet_scan(target, ports, checks))

        # Summary
        total_findings = sum(len(r.get("findings", [])) for r in results if "findings" in r)
        critical = sum(r.get("summary", {}).get("critical", 0) for r in results if "summary" in r)
        print(f"{'='*50}")
        print(f"  Targets: {len(results)}")
        print(f"  Total Findings: {total_findings}")
        print(f"  Critical: {critical}")
        print(f"{'='*50}\n")

        for r in results:
            if "error" in r:
                print(f"  ❌ {r['target']}: {r['error']}")
            else:
                grade = r.get("grade", "N/A")
                findings = len(r.get("findings", []))
                print(f"  {r['target']}: Grade {grade}, {findings} findings")

        # Export combined report if requested
        if args.output:
            with open(args.output, "w") as fp:
                json.dump(results, fp, ensure_ascii=False, indent=2)
            print(f"\n📄 Report saved to {args.output}")

        return 0 if critical == 0 else 1
    else:
        print(f"\n🛡️  AI Shield - Scanning {target}...\n")
        scanner = Scanner()
        result = asyncio.run(scanner.run_scan(target, ports, checks))

        # Print results
        print(f"{'='*50}")
        print(f"  Grade: {result['grade']}  |  Risk Score: {result['risk_score']}/100")
        print(f"  Duration: {result['duration']}s")
        print(f"{'='*50}\n")

        # Port summary
        pd = result.get("port_data", {})
        print(f"📡 Open Ports: {len(pd.get('open_ports', []))}")
        for svc in pd.get("services", []):
            detected = "✅" if svc.get("detected") else ""
            ver = f" v{svc['version']}" if svc.get("version") else ""
            print(f"   {svc['port']:>5}/tcp  {svc['service']}{ver} {detected}")
        print()

        # Findings
        findings = result.get("findings", [])
        s = result.get("summary", {})
        print(f"🐛 Findings: {len(findings)}")
        print(f"   Critical: {s.get('critical',0)}  High: {s.get('high',0)}  Medium: {s.get('medium',0)}  Low: {s.get('low',0)}\n")

        for f in findings:
            sev = f["severity"].upper()
            title = f.get("title_en", f.get("title_zh", ""))
            print(f"   [{sev:>8}] {title}")
            print(f"            {f.get('service','')}:{f.get('port','')}")
            if f.get("evidence"):
                for line in f["evidence"].split("\n")[:3]:
                    print(f"            → {line}")
            if f.get("remediation"):
                print(f"            🔧 Fix: {f['remediation'].split(chr(10))[0]}")
            print()

        # Save report
        if args.output:
            if args.output.endswith(".pdf"):
                generate_pdf_report(result, args.output)
                print(f"📄 PDF report saved to {args.output}")
            else:
                with open(args.output, "w") as fp:
                    json.dump(result, fp, ensure_ascii=False, indent=2)
                print(f"📄 Report saved to {args.output}")

        print()
        return 0 if s.get("critical", 0) == 0 else 1


def main():
    parser = argparse.ArgumentParser(
        description="AI Shield - Local AI Security Scanner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s web                          Start web UI on port 8899
  %(prog)s web --port 9000              Start web UI on port 9000
  %(prog)s scan 127.0.0.1               Scan localhost for AI services
  %(prog)s scan 192.168.1.100 --ports 11434,8000
  %(prog)s scan 10.0.0.1 -o report.json
  %(prog)s scan 192.168.1.0/24          Subnet scan
  %(prog)s scan 10.0.0.1 -o report.pdf  PDF report
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Web command
    web_parser = subparsers.add_parser("web", help="Start web UI")
    web_parser.add_argument("--host", default="127.0.0.1", help="Bind address (default: 127.0.0.1)")
    web_parser.add_argument("--port", type=int, default=8899, help="Port (default: 8899)")

    # Scan command
    scan_parser = subparsers.add_parser("scan", help="Run CLI scan")
    scan_parser.add_argument("target", help="Target IP, hostname, or CIDR (e.g. 192.168.1.0/24)")
    scan_parser.add_argument("--ports", help="Comma-separated ports (default: AI service ports)")
    scan_parser.add_argument("--checks", default="all", help="Comma-separated checks or 'all'")
    scan_parser.add_argument("-o", "--output", help="Save report to file (.json or .pdf)")

    args = parser.parse_args()

    if args.command == "web":
        cmd_web(args)
    elif args.command == "scan":
        sys.exit(cmd_scan(args))
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
