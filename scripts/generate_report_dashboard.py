#!/usr/bin/env python3
"""
Generate HTML dashboard for test reports.

Creates tests/reports/index.html with links to latest coverage, pytest,
E2E, and metrics reports.
"""

import json
import sys
from pathlib import Path
from datetime import datetime


def find_latest_report(report_dir: Path, pattern: str) -> Path | None:
    """Find the most recent report matching the pattern."""
    if not report_dir.exists():
        return None
    
    reports = list(report_dir.glob(pattern))
    if not reports:
        return None
    
    # Sort by modification time
    reports.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return reports[0]


def load_latest_metrics(metrics_dir: Path) -> dict | None:
    """Load the most recent metrics JSON file."""
    if not metrics_dir.exists():
        return None
    
    metrics_files = sorted(metrics_dir.glob("metrics-*.json"), reverse=True)
    if not metrics_files:
        return None
    
    try:
        with open(metrics_files[0], 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Warning: Failed to load metrics: {e}")
        return None


def generate_dashboard(reports_dir: Path):
    """Generate the HTML dashboard."""
    # Find latest reports
    coverage_fast = reports_dir / "coverage" / "fast-ci" / "index.html"
    coverage_nightly = reports_dir / "coverage" / "nightly" / "index.html"
    coverage_full = reports_dir / "coverage" / "full" / "index.html"
    
    pytest_fast = reports_dir / "pytest" / "fast-ci.html"
    pytest_nightly = reports_dir / "pytest" / "nightly.html"
    pytest_full = reports_dir / "pytest" / "full.html"
    
    # Load latest metrics
    metrics = load_latest_metrics(reports_dir / "metrics")
    
    # Generate HTML
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Gap-Hunter-2 Test Reports Dashboard</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        
        header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        
        header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        
        header p {{
            font-size: 1.1em;
            opacity: 0.9;
        }}
        
        .content {{
            padding: 40px;
        }}
        
        .metrics-summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }}
        
        .metric-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 25px;
            border-radius: 8px;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        
        .metric-card h3 {{
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 10px;
            opacity: 0.9;
        }}
        
        .metric-card .value {{
            font-size: 2.5em;
            font-weight: bold;
        }}
        
        .section {{
            margin-bottom: 40px;
        }}
        
        .section h2 {{
            font-size: 1.8em;
            margin-bottom: 20px;
            color: #667eea;
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
        }}
        
        .report-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
        }}
        
        .report-card {{
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            padding: 20px;
            transition: all 0.3s ease;
        }}
        
        .report-card:hover {{
            border-color: #667eea;
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2);
            transform: translateY(-2px);
        }}
        
        .report-card h3 {{
            font-size: 1.3em;
            margin-bottom: 10px;
            color: #333;
        }}
        
        .report-card p {{
            color: #666;
            margin-bottom: 15px;
        }}
        
        .report-card a {{
            display: inline-block;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 10px 20px;
            border-radius: 5px;
            text-decoration: none;
            transition: opacity 0.3s ease;
        }}
        
        .report-card a:hover {{
            opacity: 0.9;
        }}
        
        .report-card.unavailable {{
            opacity: 0.5;
        }}
        
        .report-card.unavailable a {{
            background: #ccc;
            cursor: not-allowed;
            pointer-events: none;
        }}
        
        footer {{
            background: #f5f5f5;
            padding: 20px;
            text-align: center;
            color: #666;
            font-size: 0.9em;
        }}
        
        .timestamp {{
            color: #999;
            font-size: 0.9em;
            margin-top: 10px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🧪 Test Reports Dashboard</h1>
            <p>Gap-Hunter-2 Research-Based Testing Framework</p>
        </header>
        
        <div class="content">
"""
    
    # Add metrics summary if available
    if metrics:
        html += """
            <div class="metrics-summary">
"""
        
        if 'coverage_percent' in metrics:
            html += f"""
                <div class="metric-card">
                    <h3>Coverage</h3>
                    <div class="value">{metrics['coverage_percent']:.1f}%</div>
                </div>
"""
        
        if 'total_tests' in metrics:
            html += f"""
                <div class="metric-card">
                    <h3>Total Tests</h3>
                    <div class="value">{metrics['total_tests']}</div>
                </div>
"""
        
        if 'passed' in metrics:
            html += f"""
                <div class="metric-card">
                    <h3>Passed</h3>
                    <div class="value">{metrics['passed']}</div>
                </div>
"""
        
        if 'failed' in metrics:
            html += f"""
                <div class="metric-card">
                    <h3>Failed</h3>
                    <div class="value">{metrics['failed']}</div>
                </div>
"""
        
        html += """
            </div>
"""
    
    # Coverage Reports Section
    html += """
            <div class="section">
                <h2>📊 Coverage Reports</h2>
                <div class="report-grid">
"""
    
    # Fast CI Coverage
    html += f"""
                    <div class="report-card{'unavailable' if not coverage_fast.exists() else ''}">
                        <h3>Fast CI Coverage</h3>
                        <p>Unit + Integration tests coverage</p>
                        <a href="coverage/fast-ci/index.html">View Report</a>
                    </div>
"""
    
    # Nightly Coverage
    html += f"""
                    <div class="report-card{' unavailable' if not coverage_nightly.exists() else ''}">
                        <h3>Nightly Coverage</h3>
                        <p>E2E + Adversarial tests coverage</p>
                        <a href="coverage/nightly/index.html">View Report</a>
                    </div>
"""
    
    # Full Coverage
    html += f"""
                    <div class="report-card{' unavailable' if not coverage_full.exists() else ''}">
                        <h3>Full Coverage</h3>
                        <p>Complete test suite coverage</p>
                        <a href="coverage/full/index.html">View Report</a>
                    </div>
"""
    
    html += """
                </div>
            </div>
"""
    
    # Pytest Reports Section
    html += """
            <div class="section">
                <h2>🧪 Pytest Reports</h2>
                <div class="report-grid">
"""
    
    # Fast CI Pytest
    html += f"""
                    <div class="report-card{' unavailable' if not pytest_fast.exists() else ''}">
                        <h3>Fast CI Tests</h3>
                        <p>Unit + Integration test results</p>
                        <a href="pytest/fast-ci.html">View Report</a>
                    </div>
"""
    
    # Nightly Pytest
    html += f"""
                    <div class="report-card{' unavailable' if not pytest_nightly.exists() else ''}">
                        <h3>Nightly Tests</h3>
                        <p>E2E + Adversarial test results</p>
                        <a href="pytest/nightly.html">View Report</a>
                    </div>
"""
    
    # Full Pytest
    html += f"""
                    <div class="report-card{' unavailable' if not pytest_full.exists() else ''}">
                        <h3>Full Test Suite</h3>
                        <p>Complete test results</p>
                        <a href="pytest/full.html">View Report</a>
                    </div>
"""
    
    html += """
                </div>
            </div>
"""
    
    # Metrics Section
    html += """
            <div class="section">
                <h2>📈 Metrics & Trends</h2>
                <div class="report-grid">
                    <div class="report-card">
                        <h3>Metrics History</h3>
                        <p>Historical test metrics data</p>
                        <a href="metrics/">View Metrics</a>
                    </div>
                    <div class="report-card">
                        <h3>Trend Charts</h3>
                        <p>Visual metric trends over time</p>
                        <a href="metrics/charts/">View Charts</a>
                    </div>
                </div>
            </div>
"""
    
    # Footer
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    html += f"""
        </div>
        
        <footer>
            <p>Generated by Gap-Hunter-2 Testing Framework</p>
            <p class="timestamp">Last updated: {timestamp}</p>
        </footer>
    </div>
</body>
</html>
"""
    
    # Write dashboard
    dashboard_path = reports_dir / "index.html"
    dashboard_path.write_text(html)
    print(f"Dashboard generated: {dashboard_path}")


def main():
    """Main entry point."""
    # Determine project root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    reports_dir = project_root / "tests" / "reports"
    
    print("="*60)
    print("Generating Test Reports Dashboard")
    print("="*60)
    
    # Ensure reports directory exists
    reports_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate dashboard
    generate_dashboard(reports_dir)
    
    print("="*60)
    print("Dashboard generation complete!")
    print(f"Open: {reports_dir / 'index.html'}")
    print("="*60)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
