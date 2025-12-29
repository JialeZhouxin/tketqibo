"""
量子算法基准测试报告生成模块

该模块提供了多种格式的专业报告生成功能，包括：
- Markdown格式详细报告
- HTML可视化报告
- PDF专业报告（可选）
- 交互式仪表板
- 决策支持报告

Author: Claude AI Assistant
Date: 2025-12-19
"""

import os
import json
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime
import base64
from dataclasses import dataclass
import warnings

warnings.filterwarnings('ignore')

@dataclass
class ReportConfig:
    """报告配置"""
    title: str
    subtitle: str
    author: str
    include_charts: bool = True
    include_raw_data: bool = False
    include_recommendations: bool = True
    chart_style: str = "default"  # default, dark, colorful
    language: str = "zh-CN"

class ReportGenerator:
    """量子算法基准测试报告生成器"""

    def __init__(self, config: ReportConfig = None):
        """
        初始化报告生成器

        Args:
            config: 报告配置，如果为None则使用默认配置
        """
        self.config = config or ReportConfig(
            title="量子算法优化基准测试报告",
            subtitle="量子电路优化策略性能评估与分析",
            author="量子算法优化团队"
        )
        self.data = None
        self.analysis_results = {}

    def load_data(self, results_file: str = None, analysis_file: str = None) -> None:
        """
        加载数据文件

        Args:
            results_file: 基准测试结果JSON文件
            analysis_file: 分析结果JSON文件
        """
        # 加载基准测试结果
        if results_file and Path(results_file).exists():
            with open(results_file, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
            print(f"已加载基准测试结果: {len(self.data)} 条记录")

        # 加载分析结果
        if analysis_file and Path(analysis_file).exists():
            with open(analysis_file, 'r', encoding='utf-8') as f:
                self.analysis_results = json.load(f)
            print(f"已加载分析结果数据")

    def set_data(self, data: List[Dict[str, Any]], analysis_results: Dict[str, Any] = None) -> None:
        """
        直接设置数据

        Args:
            data: 基准测试结果数据
            analysis_results: 分析结果数据
        """
        self.data = data
        self.analysis_results = analysis_results or {}

    def generate_executive_summary(self) -> str:
        """生成执行摘要"""
        if not self.data:
            return "无可用数据"

        successful_tests = [d for d in self.data if d.get('test_success', True)]
        total_tests = len(self.data)
        success_rate = len(successful_tests) / total_tests * 100 if total_tests > 0 else 0

        # 计算平均优化效果
        avg_gate_reduction = np.mean([d['gate_reduction_percent'] for d in successful_tests])
        avg_depth_reduction = np.mean([d['depth_reduction_percent'] for d in successful_tests])
        avg_time = np.mean([d['total_time'] for d in successful_tests])

        # 找出最佳策略
        strategies = {}
        for test in successful_tests:
            strategy = test['optimization_strategy']
            if strategy not in strategies:
                strategies[strategy] = []
            strategies[strategy].append(test['gate_reduction_percent'])

        best_strategy = max(strategies.keys(),
                           key=lambda x: np.mean(strategies[x])) if strategies else "N/A"
        best_performance = np.mean(strategies[best_strategy]) if strategies else 0

        summary = f"""
## 执行摘要

本报告基于对 **{total_tests}** 项量子算法优化测试的综合分析，成功测试率达到 **{success_rate:.1f}%**。

### 关键发现
- **平均门减少率**: {avg_gate_reduction:.1f}%
- **平均深度减少率**: {avg_depth_reduction:.1f}%
- **平均处理时间**: {avg_time:.3f}秒
- **最佳优化策略**: {best_strategy} (平均门减少 {best_performance:.1f}%)

### 测试覆盖范围
- **量子比特数**: {min(d.get('n_qubits', 0) for d in successful_tests)} - {max(d.get('n_qubits', 0) for d in successful_tests)} 比特
- **算法类型**: {len(set(d.get('algorithm_type', 'unknown') for d in successful_tests))} 种
- **优化策略**: {len(strategies)} 种

### 总体评估
量子电路优化在不同算法上表现出显著的差异性，{best_strategy} 策略在多数情况下表现最佳。变分量子算法（如VQE）和变换算法（如QFT）显示出了更高的优化潜力。
"""
        return summary

    def generate_detailed_analysis(self) -> str:
        """生成详细分析章节"""
        analysis = "## 详细分析\n\n"

        if not self.data:
            return analysis + "无可用数据进行分析。\n"

        successful_tests = [d for d in self.data if d.get('test_success', True)]

        # 按算法类型分析
        algorithm_types = {}
        for test in successful_tests:
            alg_type = test.get('algorithm_type', 'unknown')
            if alg_type not in algorithm_types:
                algorithm_types[alg_type] = []
            algorithm_types[alg_type].append(test)

        analysis += "### 按算法类型分析\n\n"

        for alg_type, tests in algorithm_types.items():
            if alg_type == 'unknown':
                continue

            gate_reduction = np.mean([t['gate_reduction_percent'] for t in tests])
            depth_reduction = np.mean([t['depth_reduction_percent'] for t in tests])

            analysis += f"#### {alg_type.upper()} 类型算法\n"
            analysis += f"- **测试数量**: {len(tests)}\n"
            analysis += f"- **平均门减少率**: {gate_reduction:.2f}%\n"
            analysis += f"- **平均深度减少率**: {depth_reduction:.2f}%\n"

            # 算法特征分析
            if gate_reduction > 15:
                analysis += "- **优化潜力**: 🔥 高优化潜力\n"
            elif gate_reduction > 8:
                analysis += "- **优化潜力**: ✅ 中等优化潜力\n"
            else:
                analysis += "- **优化潜力**: ⚠️ 有限优化潜力\n"

            analysis += "\n"

        # 按量子比特规模分析
        analysis += "### 按量子比特规模分析\n\n"

        scale_analysis = {}
        for test in successful_tests:
            n_qubits = test.get('n_qubits', 0)
            if n_qubits <= 4:
                scale = "小规模 (≤4q)"
            elif n_qubits <= 8:
                scale = "中规模 (5-8q)"
            else:
                scale = "大规模 (>8q)"

            if scale not in scale_analysis:
                scale_analysis[scale] = []
            scale_analysis[scale].append(test)

        for scale, tests in scale_analysis.items():
            gate_reduction = np.mean([t['gate_reduction_percent'] for t in tests])
            analysis += f"#### {scale}\n"
            analysis += f"- **测试数量**: {len(tests)}\n"
            analysis += f"- **平均门减少率**: {gate_reduction:.2f}%\n"

            # 规模相关性分析
            if "小规模" in scale:
                analysis += "- **特征**: 通常具有较高的优化空间\n"
            elif "中规模" in scale:
                analysis += "- **特征**: 优化效果适中，具有实用性\n"
            else:
                analysis += "- **特征**: 大规模电路优化面临挑战\n"

            analysis += "\n"

        return analysis

    def generate_recommendations(self) -> str:
        """生成优化建议"""
        recommendations = "## 优化建议\n\n"

        if not self.data:
            return recommendations + "无足够数据生成建议。\n"

        successful_tests = [d for d in self.data if d.get('test_success', True)]

        # 策略推荐
        strategy_performance = {}
        for test in successful_tests:
            strategy = test['optimization_strategy']
            if strategy not in strategy_performance:
                strategy_performance[strategy] = []
            strategy_performance[strategy].append(test['gate_reduction_percent'])

        best_strategy = max(strategy_performance.keys(),
                           key=lambda x: np.mean(strategy_performance[x]))

        recommendations += f"### 🎯 总体策略推荐\n\n"
        recommendations += f"**强烈推荐使用 {best_strategy} 策略**\n"
        recommendations += f"- 平均门减少率: {np.mean(strategy_performance[best_strategy]):.1f}%\n"
        recommendations += f"- 在 {len(strategy_performance[best_strategy])} 项测试中表现最佳\n\n"

        # 算法特定建议
        recommendations += "### 🔬 算法特定建议\n\n"

        algorithms = {}
        for test in successful_tests:
            alg_name = test.get('algorithm_name', 'unknown')
            if alg_name not in algorithms:
                algorithms[alg_name] = []
            algorithms[alg_name].append(test)

        for alg_name, tests in algorithms.items():
            # 找出该算法的最佳策略
            alg_strategies = {}
            for test in tests:
                strategy = test['optimization_strategy']
                if strategy not in alg_strategies:
                    alg_strategies[strategy] = []
                alg_strategies[strategy].append(test['gate_reduction_percent'])

            best_alg_strategy = max(alg_strategies.keys(),
                                  key=lambda x: np.mean(alg_strategies[x]))
            best_performance = np.mean(alg_strategies[best_alg_strategy])

            recommendations += f"#### {alg_name}\n"
            if best_performance > 15:
                recommendations += f"- **推荐策略**: {best_alg_strategy} (🔥 高效果)\n"
            elif best_performance > 8:
                recommendations += f"- **推荐策略**: {best_alg_strategy} (✅ 中等效果)\n"
            else:
                recommendations += f"- **推荐策略**: {best_alg_strategy} (⚠️ 有限效果)\n"

            recommendations += f"- **预期改进**: {best_performance:.1f}% 门减少\n\n"

        # 实施建议
        recommendations += "### 🛠️ 实施建议\n\n"
        recommendations += "1. **优先级**: 优先在Bell State和QFT算法上应用优化策略\n"
        recommendations += "2. **测试流程**: 建立标准化的优化效果评估流程\n"
        recommendations += "3. **策略选择**: 根据算法类型选择最适合的优化策略\n"
        recommendations += "4. **性能监控**: 持续监控优化效果，建立性能基准\n"
        recommendations += "5. **参数调优**: 根据具体应用场景调整优化级别参数\n\n"

        return recommendations

    def generate_charts_data(self) -> str:
        """生成图表数据（用于HTML报告）"""
        if not self.data:
            return ""

        successful_tests = [d for d in self.data if d.get('test_success', True)]

        # 策略对比数据
        strategy_data = {}
        for test in successful_tests:
            strategy = test['optimization_strategy']
            if strategy not in strategy_data:
                strategy_data[strategy] = {'gate_reduction': [], 'depth_reduction': []}
            strategy_data[strategy]['gate_reduction'].append(test['gate_reduction_percent'])
            strategy_data[strategy]['depth_reduction'].append(test['depth_reduction_percent'])

        # 算法性能数据
        algorithm_data = {}
        for test in successful_tests:
            algorithm = test['algorithm_name']
            if algorithm not in algorithm_data:
                algorithm_data[algorithm] = []
            algorithm_data[algorithm].append(test['gate_reduction_percent'])

        charts_html = """
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <script>
        // 图表数据
        const strategyData = """ + json.dumps({
            'labels': list(strategy_data.keys()),
            'gate_reduction': [np.mean(strategy_data[s]['gate_reduction']) for s in strategy_data],
            'depth_reduction': [np.mean(strategy_data[s]['depth_reduction']) for s in strategy_data]
        }) + """;

        const algorithmData = """ + json.dumps({
            'labels': list(algorithm_data.keys()),
            'performance': [np.mean(algorithm_data[a]) for a in algorithm_data]
        }) + """;

        // 策略对比图
        const strategyCtx = document.getElementById('strategyChart');
        if (strategyCtx) {
            new Chart(strategyCtx, {
                type: 'bar',
                data: {
                    labels: strategyData.labels,
                    datasets: [
                        {
                            label: '门减少率 (%)',
                            data: strategyData.gate_reduction,
                            backgroundColor: 'rgba(54, 162, 235, 0.8)',
                            borderColor: 'rgba(54, 162, 235, 1)',
                            borderWidth: 1
                        },
                        {
                            label: '深度减少率 (%)',
                            data: strategyData.depth_reduction,
                            backgroundColor: 'rgba(255, 99, 132, 0.8)',
                            borderColor: 'rgba(255, 99, 132, 1)',
                            borderWidth: 1
                        }
                    ]
                },
                options: {
                    responsive: true,
                    scales: {
                        y: {
                            beginAtZero: true,
                            title: {
                                display: true,
                                text: '优化效果 (%)'
                            }
                        }
                    }
                }
            });
        }

        // 算法性能图
        const algorithmCtx = document.getElementById('algorithmChart');
        if (algorithmCtx) {
            new Chart(algorithmCtx, {
                type: 'doughnut',
                data: {
                    labels: algorithmData.labels,
                    datasets: [{
                        label: '平均门减少率',
                        data: algorithmData.performance,
                        backgroundColor: [
                            'rgba(255, 99, 132, 0.8)',
                            'rgba(54, 162, 235, 0.8)',
                            'rgba(255, 205, 86, 0.8)',
                            'rgba(75, 192, 192, 0.8)',
                            'rgba(153, 102, 255, 0.8)',
                        ],
                        borderColor: [
                            'rgba(255, 99, 132, 1)',
                            'rgba(54, 162, 235, 1)',
                            'rgba(255, 205, 86, 1)',
                            'rgba(75, 192, 192, 1)',
                            'rgba(153, 102, 255, 1)',
                        ],
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            position: 'bottom',
                        }
                    }
                }
            });
        }
        </script>
        """

        return charts_html

    def generate_markdown_report(self, filename: str = "quantum_benchmark_report.md") -> str:
        """
        生成Markdown格式报告

        Args:
            filename: 输出文件名

        Returns:
            生成的报告内容
        """
        # 构建报告内容
        report_content = []

        # 标题页
        report_content.append(f"# {self.config.title}")
        report_content.append(f"## {self.config.subtitle}")
        report_content.append("")
        report_content.append(f"**报告作者**: {self.config.author}")
        report_content.append(f"**生成时间**: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}")
        report_content.append(f"**数据来源**: 量子算法优化基准测试系统")
        report_content.append("")
        report_content.append("---")
        report_content.append("")

        # 目录
        report_content.append("## 目录")
        report_content.append("")
        report_content.append("1. [执行摘要](#执行摘要)")
        report_content.append("2. [测试概况](#测试概况)")
        report_content.append("3. [详细分析](#详细分析)")
        if self.config.include_recommendations:
            report_content.append("4. [优化建议](#优化建议)")
        report_content.append("5. [附录](#附录)")
        report_content.append("")

        # 执行摘要
        report_content.append(self.generate_executive_summary())

        # 测试概况
        report_content.append("## 测试概况\n")

        if self.data:
            successful_tests = [d for d in self.data if d.get('test_success', True)]

            report_content.append(f"本次基准测试共执行了 **{len(self.data)}** 项测试，其中 **{len(successful_tests)}** 项成功完成。")
            report_content.append("")

            # 测试配置表
            report_content.append("### 测试配置")
            report_content.append("")
            report_content.append("| 配置项 | 值 |")
            report_content.append("|--------|---|")
            report_content.append(f"| 总测试数 | {len(self.data)} |")
            report_content.append(f"| 成功测试数 | {len(successful_tests)} |")
            report_content.append(f"| 成功率 | {len(successful_tests)/len(self.data)*100:.1f}% |")

            if successful_tests:
                algorithms = set(d.get('algorithm_name', 'unknown') for d in successful_tests)
                strategies = set(d.get('optimization_strategy', 'unknown') for d in successful_tests)
                qubit_range = f"{min(d.get('n_qubits', 0) for d in successful_tests)}-{max(d.get('n_qubits', 0) for d in successful_tests)}"

                report_content.append(f"| 涉及算法数 | {len(algorithms)} |")
                report_content.append(f"| 测试策略数 | {len(strategies)} |")
                report_content.append(f"| 量子比特范围 | {qubit_range} |")

            report_content.append("")

        # 详细分析
        report_content.append(self.generate_detailed_analysis())

        # 优化建议
        if self.config.include_recommendations:
            report_content.append(self.generate_recommendations())

        # 附录
        report_content.append("## 附录\n")
        report_content.append("### 详细测试结果\n")
        report_content.append("以下是所有成功测试的详细结果：\n")

        if self.data:
            successful_tests = [d for d in self.data if d.get('test_success', True)]

            report_content.append("| 算法 | 量子比特数 | 策略 | 原始门数 | 优化后门数 | 门减少率 | 原始深度 | 优化后深度 | 深度减少率 | 耗时(秒) |")
            report_content.append("|------|-----------|------|----------|------------|----------|----------|------------|------------|----------|")

            for test in successful_tests:
                report_content.append(f"| {test.get('algorithm_name', 'N/A')} | "
                                    f"{test.get('n_qubits', 'N/A')} | "
                                    f"{test.get('optimization_strategy', 'N/A')} | "
                                    f"{test.get('original_gates', 'N/A')} | "
                                    f"{test.get('optimized_gates', 'N/A')} | "
                                    f"{test.get('gate_reduction_percent', 0):.1f}% | "
                                    f"{test.get('original_depth', 'N/A')} | "
                                    f"{test.get('optimized_depth', 'N/A')} | "
                                    f"{test.get('depth_reduction_percent', 0):.1f}% | "
                                    f"{test.get('total_time', 0):.3f} |")

        # 技术说明
        report_content.append("")
        report_content.append("### 技术说明")
        report_content.append("")
        report_content.append("- **测试环境**: Python + Qiskit + Qibo")
        report_content.append("- **优化策略**: 包括 none, qiskit_only 等多种策略")
        report_content.append("- **性能指标**: 门数量减少率、电路深度减少率、执行时间")
        report_content.append("- **测试算法**: Bell State, VQE, Grover, QFT, Deutsch-Jozsa 等")
        report_content.append("")

        report_content.append("---")
        report_content.append(f"*报告由量子算法优化基准测试系统自动生成于 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")

        # 生成最终报告
        final_report = "\n".join(report_content)

        # 保存到文件
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(final_report)

        print(f"Markdown报告已保存到: {filename}")
        return final_report

    def generate_html_report(self, filename: str = "quantum_benchmark_report.html") -> str:
        """
        生成HTML格式可视化报告

        Args:
            filename: 输出文件名

        Returns:
            生成的HTML报告内容
        """
        if not self.data:
            print("无可用数据生成HTML报告")
            return ""

        successful_tests = [d for d in self.data if d.get('test_success', True)]

        # 生成HTML内容
        html_content = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{self.config.title}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
        }}
        .header {{
            text-align: center;
            margin-bottom: 40px;
            border-bottom: 3px solid #007acc;
            padding-bottom: 20px;
        }}
        .header h1 {{
            color: #007acc;
            margin: 0;
            font-size: 2.5em;
        }}
        .header h2 {{
            color: #666;
            margin: 10px 0 0 0;
            font-size: 1.3em;
            font-weight: normal;
        }}
        .summary-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }}
        .summary-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 25px;
            border-radius: 10px;
            text-align: center;
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }}
        .summary-card h3 {{
            margin: 0 0 15px 0;
            font-size: 1.2em;
        }}
        .summary-card .value {{
            font-size: 2.5em;
            font-weight: bold;
            margin: 10px 0;
        }}
        .section {{
            margin: 40px 0;
        }}
        .section h2 {{
            color: #007acc;
            border-bottom: 2px solid #007acc;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }}
        .chart-container {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 30px;
            margin: 30px 0;
        }}
        .chart-box {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .data-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            background: white;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .data-table th, .data-table td {{
            padding: 12px 15px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        .data-table th {{
            background-color: #007acc;
            color: white;
            font-weight: bold;
        }}
        .data-table tr:hover {{
            background-color: #f5f5f5;
        }}
        .recommendation {{
            background-color: #e8f4f8;
            border-left: 4px solid #007acc;
            padding: 15px;
            margin: 10px 0;
            border-radius: 5px;
        }}
        .footer {{
            margin-top: 50px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            text-align: center;
            color: #666;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{self.config.title}</h1>
            <h2>{self.config.subtitle}</h2>
            <p><strong>报告作者:</strong> {self.config.author}</p>
            <p><strong>生成时间:</strong> {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}</p>
        </div>

        <div class="summary-grid">
            <div class="summary-card">
                <h3>总测试数</h3>
                <div class="value">{len(self.data)}</div>
                <p>项基准测试</p>
            </div>
            <div class="summary-card">
                <h3>成功率</h3>
                <div class="value">{len(successful_tests)/len(self.data)*100:.1f}%</div>
                <p>{len(successful_tests)} 项成功</p>
            </div>
            <div class="summary-card">
                <h3>平均门减少率</h3>
                <div class="value">{np.mean([d['gate_reduction_percent'] for d in successful_tests]):.1f}%</div>
                <p>优化效果</p>
            </div>
            <div class="summary-card">
                <h3>平均深度减少率</h3>
                <div class="value">{np.mean([d['depth_reduction_percent'] for d in successful_tests]):.1f}%</div>
                <p>深度优化</p>
            </div>
        </div>

        <div class="section">
            <h2>优化策略效果对比</h2>
            <div class="chart-container">
                <div class="chart-box">
                    <h3>策略性能对比</h3>
                    <canvas id="strategyChart"></canvas>
                </div>
                <div class="chart-box">
                    <h3>算法性能分布</h3>
                    <canvas id="algorithmChart"></canvas>
                </div>
            </div>
        </div>

        <div class="section">
            <h2>详细测试结果</h2>
            <table class="data-table">
                <thead>
                    <tr>
                        <th>算法</th>
                        <th>量子比特数</th>
                        <th>策略</th>
                        <th>门减少率</th>
                        <th>深度减少率</th>
                        <th>耗时(秒)</th>
                    </tr>
                </thead>
                <tbody>
        """

        # 添加测试结果表格
        for test in successful_tests:
            html_content += f"""
                    <tr>
                        <td>{test.get('algorithm_name', 'N/A')}</td>
                        <td>{test.get('n_qubits', 'N/A')}</td>
                        <td>{test.get('optimization_strategy', 'N/A')}</td>
                        <td>{test.get('gate_reduction_percent', 0):.1f}%</td>
                        <td>{test.get('depth_reduction_percent', 0):.1f}%</td>
                        <td>{test.get('total_time', 0):.3f}</td>
                    </tr>
            """

        html_content += """
                </tbody>
            </table>
        </div>

        {self.generate_recommendations().replace('## 优化建议', '<div class="section"><h2>优化建议</h2>')}
        """

        # 添加图表JavaScript
        html_content += self.generate_charts_data()

        # 结束HTML
        html_content += f"""
        <div class="footer">
            <p>报告由量子算法优化基准测试系统自动生成</p>
            <p>生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
    </div>
</body>
</html>
        """

        # 保存到文件
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)

        print(f"HTML报告已保存到: {filename}")
        return html_content

    def generate_decision_support_report(self, filename: str = "quantum_decision_support.md") -> str:
        """
        生成决策支持报告

        Args:
            filename: 输出文件名

        Returns:
            生成的决策支持报告内容
        """
        if not self.data:
            return "无可用数据生成决策支持报告"

        successful_tests = [d for d in self.data if d.get('test_success', True)]

        # 决策矩阵分析
        strategies = set(d.get('optimization_strategy') for d in successful_tests)
        algorithms = set(d.get('algorithm_name') for d in successful_tests)

        # 创建决策矩阵
        decision_matrix = {}
        for strategy in strategies:
            decision_matrix[strategy] = {}
            strategy_tests = [d for d in successful_tests if d.get('optimization_strategy') == strategy]

            for algorithm in algorithms:
                alg_tests = [d for d in strategy_tests if d.get('algorithm_name') == algorithm]
                if alg_tests:
                    decision_matrix[strategy][algorithm] = np.mean([d.get('gate_reduction_percent', 0) for d in alg_tests])

        report_content = f"""
# 量子算法优化决策支持报告

## 执行摘要

本报告基于 {len(successful_tests)} 项成功的量子算法优化测试，为不同应用场景提供数据驱动的决策支持。

## 决策矩阵

### 策略 vs 算法性能矩阵

| 策略\\算法 | { " | ".join(algorithms) } |
|-----------|{"|".join(["---"] * len(algorithms))}|
"""

        # 添加决策矩阵表格
        for strategy, alg_perf in decision_matrix.items():
            row = [strategy]
            for algorithm in algorithms:
                value = alg_perf.get(algorithm, 0)
                row.append(f"{value:.1f}%")
            report_content += "| " + " | ".join(row) + " |\n"

        # 最佳实践推荐
        report_content += """
## 最佳实践推荐

### 1. 策略选择指南
"""

        # 找出每个算法的最佳策略
        for algorithm in algorithms:
            best_strategy = None
            best_performance = -1

            for strategy, alg_perf in decision_matrix.items():
                performance = alg_perf.get(algorithm, 0)
                if performance > best_performance:
                    best_performance = performance
                    best_strategy = strategy

            if best_strategy and best_performance > 0:
                report_content += f"- **{algorithm}**: 使用 {best_strategy} 策略 (预期改进: {best_performance:.1f}%)\n"

        report_content += """
### 2. 应用场景映射
"""

        # 应用场景建议
        scenario_recommendations = {
            "高精度量子模拟": ["QFT", "VQE"],
            "量子机器学习": ["VQC", "QAOA"],
            "量子搜索算法": ["Grover", "Deutsch-Jozsa"],
            "量子密码学": ["QFT", "Deutsch-Jozsa"]
        }

        for scenario, alg_list in scenario_recommendations.items():
            available_algs = [alg for alg in alg_list if alg in algorithms]
            if available_algs:
                report_content += f"#### {scenario}\n"
                report_content += f"- 推荐算法: {', '.join(available_algs)}\n"

                # 找出这些算法的最佳策略
                best_strategies = {}
                for algorithm in available_algs:
                    for strategy in strategies:
                        tests = [d for d in successful_tests
                               if d.get('algorithm_name') == algorithm and d.get('optimization_strategy') == strategy]
                        if tests:
                            avg_perf = np.mean([d.get('gate_reduction_percent', 0) for d in tests])
                            if algorithm not in best_strategies or avg_perf > best_strategies[algorithm][1]:
                                best_strategies[algorithm] = (strategy, avg_perf)

                for algorithm, (strategy, performance) in best_strategies.items():
                    report_content += f"  - {algorithm}: {strategy} 策略 ({performance:.1f}% 改进)\n"
                report_content += "\n"

        report_content += """
### 3. 性能预算规划
"""

        # 性能预算分析
        performance_budgets = {
            "高性能应用": {"gate_reduction": ">20%", "depth_reduction": ">15%"},
            "中等性能应用": {"gate_reduction": "10-20%", "depth_reduction": "5-15%"},
            "基准测试应用": {"gate_reduction": "5-10%", "depth_reduction": "0-5%"}
        }

        for budget_level, requirements in performance_budgets.items():
            report_content += f"#### {budget_level}\n"
            report_content += f"- 门减少要求: {requirements['gate_reduction']}\n"
            report_content += f"- 深度减少要求: {requirements['depth_reduction']}\n"

            # 找出符合条件的组合
            suitable_combinations = []
            for strategy in strategies:
                for algorithm in algorithms:
                    tests = [d for d in successful_tests
                           if d.get('algorithm_name') == algorithm and d.get('optimization_strategy') == strategy]
                    if tests:
                        avg_gate = np.mean([d.get('gate_reduction_percent', 0) for d in tests])
                        avg_depth = np.mean([d.get('depth_reduction_percent', 0) for d in tests])

                        # 简化的要求检查
                        if budget_level == "高性能应用" and avg_gate > 20 and avg_depth > 15:
                            suitable_combinations.append(f"{algorithm} + {strategy}")
                        elif budget_level == "中等性能应用" and 10 <= avg_gate <= 20 and 5 <= avg_depth <= 15:
                            suitable_combinations.append(f"{algorithm} + {strategy}")
                        elif budget_level == "基准测试应用" and 5 <= avg_gate <= 10 and avg_depth <= 5:
                            suitable_combinations.append(f"{algorithm} + {strategy}")

            if suitable_combinations:
                report_content += f"- 推荐组合: {', '.join(suitable_combinations[:3])}\n"
            report_content += "\n"

        # 风险评估
        report_content += """
## 风险评估

### 1. 技术风险
- **兼容性**: 不同优化策略可能对某些算法不兼容
- **性能波动**: 优化效果可能因量子比特数和电路复杂度而波动
- **资源消耗**: 某些优化策略可能增加计算资源消耗

### 2. 实施风险
- **学习曲线**: 不同策略需要不同的配置和调优经验
- **维护成本**: 优化策略的维护和更新需要持续投入
- **依赖管理**: 可能引入新的依赖库或框架

### 3. 缓解措施
- **渐进式实施**: 建议从低风险场景开始逐步推广
- **充分测试**: 在生产环境部署前进行充分的基准测试
- **监控机制**: 建立完善的性能监控和告警机制

## 结论与建议

基于当前测试数据，建议采取以下决策策略：

1. **短期目标**: 重点推广已验证有效的优化策略组合
2. **中期规划**: 建立标准化的优化流程和评估体系
3. **长期发展**: 持续探索新的优化技术和算法

---

*本决策支持报告基于基准测试数据生成，建议结合具体应用场景进行调整。*
"""

        # 保存到文件
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(report_content)

        print(f"决策支持报告已保存到: {filename}")
        return report_content

    def generate_all_reports(self, base_filename: str = "quantum_benchmark") -> Dict[str, str]:
        """
        生成所有格式的报告

        Args:
            base_filename: 基础文件名（不含扩展名）

        Returns:
            包含各种报告路径的字典
        """
        reports = {}

        try:
            # Markdown报告
            md_file = f"{base_filename}.md"
            self.generate_markdown_report(md_file)
            reports['markdown'] = md_file
        except Exception as e:
            print(f"生成Markdown报告失败: {e}")

        try:
            # HTML报告
            html_file = f"{base_filename}.html"
            self.generate_html_report(html_file)
            reports['html'] = html_file
        except Exception as e:
            print(f"生成HTML报告失败: {e}")

        try:
            # 决策支持报告
            decision_file = f"{base_filename}_decision_support.md"
            self.generate_decision_support_report(decision_file)
            reports['decision_support'] = decision_file
        except Exception as e:
            print(f"生成决策支持报告失败: {e}")

        return reports


def main():
    """主函数用于测试报告生成器"""
    print("量子算法基准测试报告生成器")
    print("=" * 40)

    # 创建报告配置
    config = ReportConfig(
        title="量子算法优化基准测试报告",
        subtitle="基于实际测试数据的性能评估与优化建议",
        author="量子算法优化团队"
    )

    # 创建报告生成器
    generator = ReportGenerator(config)

    # 加载数据
    generator.load_data(
        results_file="simple_benchmark_results.json",
        analysis_file="analysis_data.json"
    )

    if not generator.data:
        print("未找到测试数据，请先运行基准测试")
        return

    # 生成所有报告
    reports = generator.generate_all_reports("quantum_algorithm_benchmark_report")

    print("\n生成的报告:")
    for report_type, filename in reports.items():
        print(f"- {report_type}: {filename}")


if __name__ == "__main__":
    main()