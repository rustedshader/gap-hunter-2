#!/usr/bin/env python3
"""
Analyze test metrics and generate trend charts.

Loads metrics from tests/reports/metrics/, calculates rolling averages,
generates trend charts, and detects degradations.
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


def load_metrics(metrics_dir: Path) -> List[Dict[str, Any]]:
    """Load all metrics JSON files from the metrics directory."""
    metrics = []
    
    if not metrics_dir.exists():
        print(f"Metrics directory not found: {metrics_dir}")
        return metrics
    
    for metrics_file in sorted(metrics_dir.glob("metrics-*.json")):
        try:
            with open(metrics_file, 'r') as f:
                data = json.load(f)
                metrics.append(data)
        except Exception as e:
            print(f"Warning: Failed to load {metrics_file}: {e}")
    
    return metrics


def calculate_rolling_average(metrics: List[Dict[str, Any]], key: str, days: int = 7) -> List[float]:
    """Calculate rolling average for a metric over the specified number of days."""
    if not metrics:
        return []
    
    # Sort by timestamp
    sorted_metrics = sorted(metrics, key=lambda m: m.get('timestamp', ''))
    
    rolling_avgs = []
    for i, metric in enumerate(sorted_metrics):
        # Get metrics from the last N days
        current_time = datetime.fromisoformat(metric['timestamp'].replace('Z', '+00:00'))
        cutoff_time = current_time - timedelta(days=days)
        
        recent_values = []
        for j in range(max(0, i - 50), i + 1):  # Look back up to 50 entries
            if j < len(sorted_metrics):
                m = sorted_metrics[j]
                m_time = datetime.fromisoformat(m['timestamp'].replace('Z', '+00:00'))
                if m_time >= cutoff_time and key in m:
                    recent_values.append(float(m[key]))
        
        if recent_values:
            rolling_avgs.append(sum(recent_values) / len(recent_values))
        else:
            rolling_avgs.append(float(metric.get(key, 0)))
    
    return rolling_avgs


def detect_degradations(metrics: List[Dict[str, Any]], threshold: float = 0.05) -> List[Dict[str, Any]]:
    """Detect metrics that have degraded by more than the threshold (default 5%)."""
    degradations = []
    
    if len(metrics) < 2:
        return degradations
    
    # Sort by timestamp
    sorted_metrics = sorted(metrics, key=lambda m: m.get('timestamp', ''))
    
    # Compare latest metric with 7-day average
    latest = sorted_metrics[-1]
    
    for key in ['coverage_percent', 'f1_score', 'faithfulness_score', 'alignment_score']:
        if key not in latest:
            continue
        
        # Calculate 7-day average
        rolling_avg = calculate_rolling_average(sorted_metrics, key, days=7)
        if not rolling_avg or len(rolling_avg) < 2:
            continue
        
        current_value = float(latest[key])
        avg_value = rolling_avg[-2] if len(rolling_avg) >= 2 else rolling_avg[-1]
        
        # Calculate degradation percentage
        if avg_value > 0:
            degradation = (avg_value - current_value) / avg_value
            
            if degradation > threshold:
                degradations.append({
                    'metric': key,
                    'current': current_value,
                    'average': avg_value,
                    'degradation_percent': degradation * 100,
                    'timestamp': latest['timestamp']
                })
    
    return degradations


def generate_trend_chart(metrics: List[Dict[str, Any]], metric_key: str, output_path: Path, title: str):
    """Generate a trend chart for a specific metric."""
    if not metrics:
        print(f"No metrics to plot for {metric_key}")
        return
    
    # Sort by timestamp
    sorted_metrics = sorted(metrics, key=lambda m: m.get('timestamp', ''))
    
    # Extract timestamps and values
    timestamps = []
    values = []
    
    for metric in sorted_metrics:
        if metric_key in metric:
            try:
                ts = datetime.fromisoformat(metric['timestamp'].replace('Z', '+00:00'))
                timestamps.append(ts)
                values.append(float(metric[metric_key]))
            except Exception as e:
                print(f"Warning: Failed to parse metric: {e}")
    
    if not timestamps:
        print(f"No valid data for {metric_key}")
        return
    
    # Calculate rolling average
    rolling_avg = calculate_rolling_average(sorted_metrics, metric_key, days=7)
    
    # Create plot
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Plot actual values
    ax.plot(timestamps, values, marker='o', linestyle='-', linewidth=1, markersize=4, 
            label='Actual', alpha=0.7)
    
    # Plot rolling average
    if rolling_avg:
        ax.plot(timestamps, rolling_avg, linestyle='--', linewidth=2, 
                label='7-day Rolling Average', color='red')
    
    # Formatting
    ax.set_xlabel('Date')
    ax.set_ylabel(title)
    ax.set_title(f'{title} Over Time')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # Format x-axis dates
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=max(1, len(timestamps) // 10)))
    plt.xticks(rotation=45, ha='right')
    
    # Tight layout
    plt.tight_layout()
    
    # Save
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"Generated chart: {output_path}")


def main():
    """Main entry point."""
    # Determine project root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    metrics_dir = project_root / "tests" / "reports" / "metrics"
    charts_dir = metrics_dir / "charts"
    
    print("="*60)
    print("Test Metrics Analysis")
    print("="*60)
    
    # Load metrics
    print(f"\nLoading metrics from: {metrics_dir}")
    metrics = load_metrics(metrics_dir)
    
    if not metrics:
        print("No metrics found. Run tests first to generate metrics.")
        return 0
    
    print(f"Loaded {len(metrics)} metric entries")
    
    # Generate trend charts
    print("\nGenerating trend charts...")
    
    charts = [
        ('coverage_percent', 'Coverage (%)', 'coverage_trend.png'),
        ('f1_score', 'F1-Score', 'f1_score_trend.png'),
        ('faithfulness_score', 'Faithfulness Score', 'faithfulness_trend.png'),
        ('alignment_score', 'Alignment Score', 'alignment_trend.png'),
    ]
    
    for metric_key, title, filename in charts:
        # Check if any metrics have this key
        if any(metric_key in m for m in metrics):
            output_path = charts_dir / filename
            generate_trend_chart(metrics, metric_key, output_path, title)
        else:
            print(f"Skipping {metric_key} (no data)")
    
    # Detect degradations
    print("\nDetecting degradations...")
    degradations = detect_degradations(metrics, threshold=0.05)
    
    if degradations:
        print(f"\n⚠️  Found {len(degradations)} metric degradations:")
        for deg in degradations:
            print(f"  - {deg['metric']}: {deg['current']:.2f} "
                  f"(avg: {deg['average']:.2f}, "
                  f"degraded by {deg['degradation_percent']:.1f}%)")
        
        # Save degradations to file
        degradations_file = metrics_dir / "degradations.json"
        with open(degradations_file, 'w') as f:
            json.dump(degradations, f, indent=2)
        print(f"\nDegradations saved to: {degradations_file}")
        
        # Exit with error code if degradations found
        return 1
    else:
        print("\n✅ No significant degradations detected")
    
    print("\n" + "="*60)
    print("Analysis complete!")
    print(f"Charts saved to: {charts_dir}")
    print("="*60)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
