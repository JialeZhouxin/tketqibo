"""Report Generation System for Performance Comparison.

This module provides comprehensive report generation capabilities for the
Sim-Fusion vs Qibo fusion performance comparison framework.

Key Features:
- Multiple output formats (JSON, CSV, Markdown, HTML)
- Visual chart generation (performance comparisons, trend analysis)
- Template-based report customization
- Executive summary and detailed analysis sections
- Automated insights and recommendations extraction
- Export functionality for further analysis

Dependencies:
- Optional: matplotlib, seaborn (for visualization)
- Optional: jinja2 (for HTML template rendering)

Authors: Sim-Fusion Team
Version: 1.0.0
"""

from __future__ import annotations

import json
import csv
import math
import statistics
from typing import Dict, List, Any, Optional, Union, TextIO
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from enum import Enum
import os

try:
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    plt = None

try:
    import seaborn as sns
    SEABORN_AVAILABLE = True
except ImportError:
    SEABORN_AVAILABLE = False
    sns = None

try:
    from jinja2 import Template, Environment, FileSystemLoader
    JINJA2_AVAILABLE = True
except ImportError:
    JINJA2_AVAILABLE = False
    Template = None


class ReportFormat(Enum):
    """Supported report formats."""
    JSON = "json"
    CSV = "csv"
    MARKDOWN = "markdown"
    HTML = "html"
    EXCEL = "excel"


@dataclass
class ReportSection:
    """Individual report section data."""

    title: str
    content: str
    data: Optional[Dict[str, Any]] = None
    charts: Optional[List[str]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        return asdict(self)


@dataclass
class PerformanceInsight:
    """Automated performance insight."""

    category: str
    insight: str
    severity: str  # "high", "medium", "low"
    recommendation: str
    supporting_data: Optional[Dict[str, Any]] = None


class ChartGenerator:
    """Chart generation utility for performance visualization."""

    def __init__(self, style: str = "default", figsize: tuple = (10, 6)):
        """Initialize chart generator.

        Args:
            style: Matplotlib style to use
            figsize: Default figure size (width, height)
        """
        self.style = style
        self.figsize = figsize

        if MATPLOTLIB_AVAILABLE:
            plt.style.use(style if style in plt.style.available else 'default')

        if SEABORN_AVAILABLE:
            sns.set_palette("husl")

    def create_performance_comparison_chart(self,
                                          data: Dict[str, List[float]],
                                          title: str = "Performance Comparison",
                                          output_path: Optional[str] = None) -> str:
        """Create bar chart comparing performance metrics.

        Args:
            data: Dictionary mapping metric names to lists of values
            title: Chart title
            output_path: Path to save chart (if None, returns base64 string)

        Returns:
            Path to saved chart or base64 string
        """
        if not MATPLOTLIB_AVAILABLE:
            return "matplotlib_not_available"

        fig, ax = plt.subplots(figsize=self.figsize)

        # Prepare data
        methods = list(data.keys())
        metrics = list(data[methods[0]].keys()) if methods else []

        # Create bar positions
        x = range(len(metrics))
        width = 0.8 / len(methods)

        # Plot bars for each method
        for i, method in enumerate(methods):
            values = [data[method].get(metric, 0) for metric in metrics]
            offset = (i - len(methods)/2 + 0.5) * width
            ax.bar([xi + offset for xi in x], values, width, label=method, alpha=0.8)

        # Customize chart
        ax.set_xlabel('Metrics')
        ax.set_ylabel('Values')
        ax.set_title(title)
        ax.set_xticks(x)
        ax.set_xticklabels(metrics, rotation=45, ha='right')
        ax.legend()
        ax.grid(True, alpha=0.3)

        plt.tight_layout()

        if output_path:
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close()
            return output_path
        else:
            # Return as base64 string
            import io
            import base64
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.getvalue()).decode()
            plt.close()
            return f"data:image/png;base64,{image_base64}"

    def create_trend_analysis_chart(self,
                                   x_values: List[float],
                                   y_values: List[float],
                                   title: str = "Performance Trend",
                                   x_label: str = "X",
                                   y_label: str = "Y",
                                   output_path: Optional[str] = None) -> str:
        """Create line chart for trend analysis.

        Args:
            x_values: X-axis values
            y_values: Y-axis values
            title: Chart title
            x_label: X-axis label
            y_label: Y-axis label
            output_path: Path to save chart

        Returns:
            Path to saved chart or base64 string
        """
        if not MATPLOTLIB_AVAILABLE:
            return "matplotlib_not_available"

        fig, ax = plt.subplots(figsize=self.figsize)

        # Plot trend line
        ax.plot(x_values, y_values, marker='o', linewidth=2, markersize=6)

        # Add trend line (linear regression)
        if len(x_values) > 1:
            import numpy as np
            z = np.polyfit(x_values, y_values, 1)
            p = np.poly1d(z)
            ax.plot(x_values, p(x_values), "--", alpha=0.7, label=f"Trend: y={z[0]:.2f}x+{z[1]:.2f}")

        # Customize chart
        ax.set_xlabel(x_label)
        ax.set_ylabel(y_label)
        ax.set_title(title)
        ax.grid(True, alpha=0.3)
        ax.legend()

        plt.tight_layout()

        if output_path:
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close()
            return output_path
        else:
            import io
            import base64
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.getvalue()).decode()
            plt.close()
            return f"data:image/png;base64,{image_base64}"

    def create_box_plot(self,
                       data: Dict[str, List[float]],
                       title: str = "Distribution Comparison",
                       output_path: Optional[str] = None) -> str:
        """Create box plot for distribution comparison.

        Args:
            data: Dictionary mapping method names to value lists
            title: Chart title
            output_path: Path to save chart

        Returns:
            Path to saved chart or base64 string
        """
        if not MATPLOTLIB_AVAILABLE:
            return "matplotlib_not_available"

        fig, ax = plt.subplots(figsize=self.figsize)

        # Prepare data
        methods = list(data.keys())
        values = [data[method] for method in methods]

        # Create box plot
        box_plot = ax.boxplot(values, labels=methods, patch_artist=True)

        # Color the boxes
        if SEABORN_AVAILABLE:
            colors = sns.color_palette("husl", len(methods))
        else:
            colors = plt.cm.Set3(range(len(methods)))

        for patch, color in zip(box_plot['boxes'], colors):
            patch.set_facecolor(color)
            patch.set_alpha(0.7)

        # Customize chart
        ax.set_title(title)
        ax.set_ylabel('Values')
        ax.grid(True, alpha=0.3)

        plt.tight_layout()

        if output_path:
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close()
            return output_path
        else:
            import io
            import base64
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.getvalue()).decode()
            plt.close()
            return f"data:image/png;base64,{image_base64}"


class ReportGenerator:
    """Main report generation class."""

    def __init__(self,
                 output_dir: str = "reports",
                 include_charts: bool = True):
        """Initialize report generator.

        Args:
            output_dir: Directory to save reports
            include_charts: Whether to include charts in reports
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.include_charts = include_charts

        if include_charts:
            self.chart_generator = ChartGenerator()

    def generate_comprehensive_report(self,
                                    analysis_results: Dict[str, Any],
                                    circuit_metadata: Optional[Dict[str, Any]] = None,
                                    formats: List[ReportFormat] = None) -> Dict[str, str]:
        """Generate comprehensive performance comparison report.

        Args:
            analysis_results: Results from statistical analysis
            circuit_metadata: Metadata about test circuits
            formats: List of report formats to generate

        Returns:
            Dictionary mapping format names to file paths
        """
        if formats is None:
            formats = [ReportFormat.MARKDOWN, ReportFormat.JSON]

        # Generate report sections
        sections = self._create_report_sections(analysis_results, circuit_metadata)

        # Generate insights
        insights = self._generate_insights(analysis_results)

        # Create report data structure
        report_data = {
            'metadata': self._create_metadata(),
            'sections': sections,
            'insights': insights,
            'charts': self._generate_charts(analysis_results) if self.include_charts else [],
            'summary': self._create_executive_summary(analysis_results, insights)
        }

        # Generate reports in different formats
        output_files = {}

        for format_type in formats:
            if format_type == ReportFormat.MARKDOWN:
                output_files['markdown'] = self._generate_markdown_report(report_data)
            elif format_type == ReportFormat.JSON:
                output_files['json'] = self._generate_json_report(report_data)
            elif format_type == ReportFormat.CSV:
                output_files['csv'] = self._generate_csv_report(analysis_results)
            elif format_type == ReportFormat.HTML:
                output_files['html'] = self._generate_html_report(report_data)

        return output_files

    def _create_report_sections(self,
                               analysis_results: Dict[str, Any],
                               circuit_metadata: Optional[Dict[str, Any]]) -> List[ReportSection]:
        """Create report sections from analysis results."""
        sections = []

        # Executive Summary Section
        sections.append(ReportSection(
            title="Executive Summary",
            content=self._create_executive_summary_content(analysis_results),
            data={"summary_type": "executive"}
        ))

        # Test Setup Section
        if circuit_metadata:
            sections.append(ReportSection(
                title="Test Setup and Circuit Information",
                content=self._create_setup_content(circuit_metadata),
                data=circuit_metadata
            ))

        # Statistical Summary Section
        summary_stats = analysis_results.get('summary_statistics', {})
        if summary_stats:
            sections.append(ReportSection(
                title="Statistical Summary",
                content=self._create_statistical_summary_content(summary_stats),
                data=summary_stats
            ))

        # Significance Testing Section
        significance_tests = analysis_results.get('significance_tests', {})
        if significance_tests:
            sections.append(ReportSection(
                title="Statistical Significance Testing",
                content=self._create_significance_content(significance_tests),
                data=significance_tests
            ))

        # Trend Analysis Section
        trend_analysis = analysis_results.get('trend_analysis', {})
        if trend_analysis:
            sections.append(ReportSection(
                title="Performance Trend Analysis",
                content=self._create_trend_content(trend_analysis),
                data=trend_analysis
            ))

        # Recommendations Section
        recommendations = analysis_results.get('recommendations', [])
        if recommendations:
            sections.append(ReportSection(
                title="Recommendations",
                content=self._create_recommendations_content(recommendations),
                data={"recommendations": recommendations}
            ))

        return sections

    def _create_metadata(self) -> Dict[str, Any]:
        """Create report metadata."""
        return {
            'generated_at': datetime.now().isoformat(),
            'generator': 'Sim-Fusion Report Generator',
            'version': '1.0.0',
            'analysis_type': 'performance_comparison',
            'methods_compared': ['Sim-Fusion', 'Qibo Fusion']
        }

    def _create_executive_summary(self,
                                 analysis_results: Dict[str, Any],
                                 insights: List[PerformanceInsight]) -> Dict[str, Any]:
        """Create executive summary."""
        # Count significant differences
        significance_tests = analysis_results.get('significance_tests', {})
        significant_metrics = []
        nonsignificant_metrics = []

        for metric, tests in significance_tests.items():
            t_test = tests.get('t_test', {})
            if t_test.get('is_significant', False):
                significant_metrics.append(metric)
            else:
                nonsignificant_metrics.append(metric)

        # Extract key insights
        high_priority_insights = [insight for insight in insights
                                if insight.severity == 'high']

        return {
            'significant_differences': len(significant_metrics),
            'total_metrics_tested': len(significance_tests),
            'high_priority_insights': len(high_priority_insights),
            'key_findings': [insight.insight for insight in high_priority_insights[:3]],
            'overall_assessment': self._get_overall_assessment(significance_tests)
        }

    def _generate_insights(self, analysis_results: Dict[str, Any]) -> List[PerformanceInsight]:
        """Generate automated insights from analysis results."""
        insights = []

        # Analyze significance tests
        significance_tests = analysis_results.get('significance_tests', {})

        for metric, tests in significance_tests.items():
            t_test = tests.get('t_test', {})

            if t_test.get('is_significant', False):
                effect_size = t_test.get('effect_size', 0)
                p_value = t_test.get('p_value', 1)

                if 'gate_reduction' in metric:
                    if effect_size > 0.8:
                        insights.append(PerformanceInsight(
                            category="Performance Optimization",
                            insight=f"Large effect size ({effect_size:.2f}) in {metric}",
                            severity="high",
                            recommendation=f"Strongly prefer the better performing method for {metric}",
                            supporting_data={"effect_size": effect_size, "p_value": p_value}
                        ))
                    elif effect_size > 0.5:
                        insights.append(PerformanceInsight(
                            category="Performance Optimization",
                            insight=f"Medium effect size ({effect_size:.2f}) in {metric}",
                            severity="medium",
                            recommendation=f"Consider method superiority for {metric}",
                            supporting_data={"effect_size": effect_size, "p_value": p_value}
                        ))

                elif 'time' in metric or 'efficiency' in metric:
                    if effect_size > 0.3:
                        insights.append(PerformanceInsight(
                            category="Performance Efficiency",
                            insight=f"Significant time/efficiency difference in {metric}",
                            severity="high",
                            recommendation=f"Prioritize faster method for time-critical applications",
                            supporting_data={"effect_size": effect_size, "p_value": p_value}
                        ))

        # Analyze trends
        trend_analysis = analysis_results.get('trend_analysis', {})

        for trend_key, trend in trend_analysis.items():
            direction = trend.get('direction')
            strength = trend.get('trend_strength')

            if direction == 'degrading' and strength in ['strong', 'moderate']:
                insights.append(PerformanceInsight(
                    category="Scalability",
                    insight=f"Performance degradation trend in {trend_key}",
                    severity="high",
                    recommendation="Investigate scaling bottlenecks and optimization strategies",
                    supporting_data=trend
                ))
            elif direction == 'improving' and strength in ['strong', 'moderate']:
                insights.append(PerformanceInsight(
                    category="Scalability",
                    insight=f"Performance improvement trend in {trend_key}",
                    severity="low",
                    recommendation="Method shows good scaling characteristics",
                    supporting_data=trend
                ))

        return insights

    def _generate_charts(self, analysis_results: Dict[str, Any]) -> List[str]:
        """Generate charts for the report."""
        if not self.include_charts:
            return []

        charts = []

        # Performance comparison chart
        summary_stats = analysis_results.get('summary_statistics', {})
        if summary_stats:
            # Extract means for comparison
            comparison_data = {}
            for method, metrics in summary_stats.items():
                comparison_data[method] = {
                    metric: summary.mean for metric, summary in metrics.items()
                    if isinstance(summary, object) and hasattr(summary, 'mean')
                }

            if comparison_data:
                chart_path = self.output_dir / "performance_comparison.png"
                chart_result = self.chart_generator.create_performance_comparison_chart(
                    comparison_data,
                    "Sim-Fusion vs Qibo Fusion Performance Comparison",
                    str(chart_path)
                )
                if chart_path.exists():
                    charts.append(str(chart_path))

        return charts

    def _generate_markdown_report(self, report_data: Dict[str, Any]) -> str:
        """Generate Markdown format report."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = self.output_dir / f"performance_report_{timestamp}.md"

        with open(output_path, 'w', encoding='utf-8') as f:
            # Header
            f.write("# Sim-Fusion vs Qibo Fusion Performance Comparison Report\n\n")
            f.write(f"**Generated:** {report_data['metadata']['generated_at']}\n\n")

            # Executive Summary
            summary = report_data.get('summary', {})
            f.write("## Executive Summary\n\n")
            f.write(f"- **Metrics with significant differences:** {summary.get('significant_differences', 0)}/{summary.get('total_metrics_tested', 0)}\n")
            f.write(f"- **High-priority insights:** {summary.get('high_priority_insights', 0)}\n")
            f.write(f"- **Overall assessment:** {summary.get('overall_assessment', 'Inconclusive')}\n\n")

            if summary.get('key_findings'):
                f.write("### Key Findings\n\n")
                for finding in summary['key_findings']:
                    f.write(f"- {finding}\n")
                f.write("\n")

            # Sections
            for section in report_data.get('sections', []):
                f.write(f"## {section.title}\n\n")
                f.write(f"{section.content}\n\n")

            # Insights
            insights = report_data.get('insights', [])
            if insights:
                f.write("## Automated Insights\n\n")
                for insight in insights:
                    severity_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(insight.severity, "ℹ️")
                    f.write(f"### {severity_icon} {insight.category}\n\n")
                    f.write(f"**Insight:** {insight.insight}\n\n")
                    f.write(f"**Recommendation:** {insight.recommendation}\n\n")
                    f.write("---\n\n")

            # Charts
            charts = report_data.get('charts', [])
            if charts:
                f.write("## Visualizations\n\n")
                for chart_path in charts:
                    chart_name = Path(chart_path).name
                    f.write(f"![{chart_name}]({chart_path})\n\n")

        return str(output_path)

    def _generate_json_report(self, report_data: Dict[str, Any]) -> str:
        """Generate JSON format report."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = self.output_dir / f"performance_report_{timestamp}.json"

        # Convert to serializable format
        serializable_data = self._make_json_serializable(report_data)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(serializable_data, f, indent=2, ensure_ascii=False)

        return str(output_path)

    def _make_json_serializable(self, data: Any) -> Any:
        """Convert data to JSON-serializable format."""
        if isinstance(data, dict):
            return {key: self._make_json_serializable(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [self._make_json_serializable(item) for item in data]
        elif hasattr(data, '__dict__'):
            # For custom objects, convert to dict with basic attributes
            result = {}
            for attr in dir(data):
                if not attr.startswith('_'):
                    value = getattr(data, attr)
                    if not callable(value):
                        try:
                            # Try to make it JSON serializable
                            json.dumps(value)  # Test serialization
                            result[attr] = value
                        except (TypeError, ValueError):
                            # For non-serializable attributes, convert to string
                            result[attr] = str(value)
            return result
        elif hasattr(data, 'to_dict'):
            return self._make_json_serializable(data.to_dict())
        elif hasattr(data, 'asdict'):
            return self._make_json_serializable(asdict(data))
        else:
            # For basic types that should be serializable
            try:
                json.dumps(data)
                return data
            except (TypeError, ValueError):
                return str(data)

    def _generate_csv_report(self, analysis_results: Dict[str, Any]) -> str:
        """Generate CSV format report with summary statistics."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = self.output_dir / f"performance_summary_{timestamp}.csv"

        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)

            # Header
            writer.writerow([
                'Method', 'Metric', 'Mean', 'StdDev', 'Min', 'Max', 'Q25', 'Q75',
                'Sample_Size', 'CV', 'Is_Stable'
            ])

            # Data
            summary_stats = analysis_results.get('summary_statistics', {})
            for method, metrics in summary_stats.items():
                for metric_name, summary in metrics.items():
                    if hasattr(summary, 'mean'):  # StatisticalSummary object
                        writer.writerow([
                            method,
                            metric_name,
                            f"{summary.mean:.6f}",
                            f"{summary.stdev:.6f}",
                            f"{summary.min_val:.6f}",
                            f"{summary.max_val:.6f}",
                            f"{summary.q25:.6f}",
                            f"{summary.q75:.6f}",
                            summary.n,
                            f"{summary.coefficient_of_variation():.4f}",
                            summary.is_stable()
                        ])

        return str(output_path)

    def _generate_html_report(self, report_data: Dict[str, Any]) -> str:
        """Generate HTML format report."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = self.output_dir / f"performance_report_{timestamp}.html"

        # Simple HTML template
        html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sim-Fusion Performance Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }
        .header { background-color: #f4f4f4; padding: 20px; border-radius: 5px; }
        .section { margin: 20px 0; }
        .insight { border-left: 4px solid #ccc; padding: 10px; margin: 10px 0; }
        .high { border-left-color: #d32f2f; }
        .medium { border-left-color: #f57c00; }
        .low { border-left-color: #388e3c; }
        table { border-collapse: collapse; width: 100%; margin: 10px 0; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
        .chart { text-align: center; margin: 20px 0; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Sim-Fusion vs Qibo Fusion Performance Comparison</h1>
        <p><strong>Generated:</strong> {generated_at}</p>
    </div>

    <div class="section">
        <h2>Executive Summary</h2>
        <p><strong>Significant differences:</strong> {significant_diff}/{total_metrics}</p>
        <p><strong>High-priority insights:</strong> {high_priority_insights}</p>
        <p><strong>Overall assessment:</strong> {overall_assessment}</p>
    </div>

    {sections_html}

    {insights_html}

    {charts_html}
</body>
</html>
        """

        # Build sections HTML
        sections_html = ""
        for section in report_data.get('sections', []):
            sections_html += f'<div class="section"><h2>{section.title}</h2>{section.content}</div>'

        # Build insights HTML
        insights_html = '<div class="section"><h2>Automated Insights</h2>'
        for insight in report_data.get('insights', []):
            insights_html += f'''
            <div class="insight {insight.severity}">
                <h3>{insight.category}</h3>
                <p><strong>Insight:</strong> {insight.insight}</p>
                <p><strong>Recommendation:</strong> {insight.recommendation}</p>
            </div>
            '''
        insights_html += '</div>'

        # Build charts HTML
        charts_html = '<div class="section"><h2>Visualizations</h2>'
        for chart_path in report_data.get('charts', []):
            chart_name = Path(chart_path).name
            charts_html += f'<div class="chart"><img src="{chart_name}" alt="{chart_name}"></div>'
        charts_html += '</div>'

        # Fill template
        summary = report_data.get('summary', {})
        html_content = html_template.format(
            generated_at=report_data['metadata']['generated_at'],
            significant_diff=summary.get('significant_differences', 0),
            total_metrics=summary.get('total_metrics_tested', 0),
            high_priority_insights=summary.get('high_priority_insights', 0),
            overall_assessment=summary.get('overall_assessment', 'Inconclusive'),
            sections_html=sections_html,
            insights_html=insights_html,
            charts_html=charts_html
        )

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        return str(output_path)

    def _create_executive_summary_content(self, analysis_results: Dict[str, Any]) -> str:
        """Create executive summary content."""
        significance_tests = analysis_results.get('significance_tests', {})

        significant_count = sum(1 for tests in significance_tests.values()
                              if tests.get('t_test', {}).get('is_significant', False))
        total_count = len(significance_tests)

        content = f"This report compares the performance of Sim-Fusion (TKET + Qibo fusion) "
        content += f"against Qibo's native fusion optimization across {total_count} metrics. "

        if significant_count > 0:
            content += f"Significant performance differences were detected in {significant_count} metrics. "
        else:
            content += "No significant performance differences were detected. "

        return content

    def _create_setup_content(self, circuit_metadata: Dict[str, Any]) -> str:
        """Create test setup content."""
        content = "## Circuit Information\n\n"

        if 'circuit_types' in circuit_metadata:
            content += "**Circuit Types Tested:**\n"
            for circuit_type in circuit_metadata['circuit_types']:
                content += f"- {circuit_type}\n"

        if 'qubit_range' in circuit_metadata:
            content += f"\n**Qubit Range:** {circuit_metadata['qubit_range']}\n"

        if 'iterations' in circuit_metadata:
            content += f"**Iterations per Test:** {circuit_metadata['iterations']}\n"

        return content

    def _create_statistical_summary_content(self, summary_stats: Dict[str, Any]) -> str:
        """Create statistical summary content."""
        content = ""

        for method, metrics in summary_stats.items():
            content += f"### {method.title()}\n\n"
            content += "| Metric | Mean | Std Dev | Min | Max | CV |\n"
            content += "|--------|------|---------|-----|-----|----|\n"

            for metric_name, summary in metrics.items():
                if hasattr(summary, 'mean'):
                    cv = summary.coefficient_of_variation()
                    content += f"| {metric_name} | {summary.mean:.3f} | {summary.stdev:.3f} | "
                    content += f"{summary.min_val:.3f} | {summary.max_val:.3f} | {cv:.3f} |\n"

            content += "\n"

        return content

    def _create_significance_content(self, significance_tests: Dict[str, Any]) -> str:
        """Create significance testing content."""
        content = "| Metric | Test | Statistic | P-value | Significant? | Effect Size |\n"
        content += "|--------|------|-----------|---------|--------------|-------------|\n"

        for metric, tests in significance_tests.items():
            t_test = tests.get('t_test', {})
            content += f"| {metric} | {t_test.get('test_name', 'N/A')} | "
            content += f"{t_test.get('statistic', 'N/A'):.4f} | "
            content += f"{t_test.get('p_value', 'N/A'):.6f} | "
            content += f"{'Yes' if t_test.get('is_significant', False) else 'No'} | "
            content += f"{t_test.get('effect_size', 0):.3f} |\n"

        return content

    def _create_trend_content(self, trend_analysis: Dict[str, Any]) -> str:
        """Create trend analysis content."""
        content = "| Metric | Direction | Strength | Correlation | Interpretation |\n"
        content += "|--------|-----------|----------|-------------|----------------|\n"

        for metric_key, trend in trend_analysis.items():
            content += f"| {metric_key} | {trend.get('direction', 'N/A')} | "
            content += f"{trend.get('trend_strength', 'N/A')} | "
            content += f"{trend.get('correlation', 0):.3f} | "
            content += f"{trend.get('interpretation', 'N/A')} |\n"

        return content

    def _create_recommendations_content(self, recommendations: List[str]) -> str:
        """Create recommendations content."""
        content = ""
        for i, rec in enumerate(recommendations, 1):
            content += f"{i}. {rec}\n"
        return content

    def _get_overall_assessment(self, significance_tests: Dict[str, Any]) -> str:
        """Get overall assessment based on significance tests."""
        if not significance_tests:
            return "Insufficient data for assessment"

        significant_count = sum(1 for tests in significance_tests.values()
                              if tests.get('t_test', {}).get('is_significant', False))
        total_count = len(significance_tests)

        if significant_count == 0:
            return "No significant differences detected"
        elif significant_count / total_count >= 0.7:
            return "Strong evidence of performance differences"
        elif significant_count / total_count >= 0.4:
            return "Moderate evidence of performance differences"
        else:
            return "Limited evidence of performance differences"


# Convenience functions for quick usage
def quick_report(analysis_results: Dict[str, Any],
                output_dir: str = "reports",
                formats: List[str] = None) -> Dict[str, str]:
    """Generate quick performance comparison report.

    Args:
        analysis_results: Results from statistical analysis
        output_dir: Directory to save reports
        formats: List of format names (e.g., ['markdown', 'json'])

    Returns:
        Dictionary mapping format names to file paths
    """
    if formats is None:
        formats = ['markdown', 'json']

    # Convert string format names to enum
    format_enums = []
    for fmt in formats:
        try:
            format_enums.append(ReportFormat(fmt))
        except ValueError:
            print(f"Warning: Unknown format '{fmt}', skipping...")

    generator = ReportGenerator(output_dir=output_dir)
    return generator.generate_comprehensive_report(
        analysis_results=analysis_results,
        formats=format_enums
    )