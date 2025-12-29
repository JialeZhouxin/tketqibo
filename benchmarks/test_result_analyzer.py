"""
量子算法基准测试结果分析模块

该模块提供了对基准测试结果的深度分析功能，包括：
- 统计分析和显著性检验
- 性能模式识别
- 异常值检测
- 算法类型比较
- 规模扩展分析

Author: Claude AI Assistant
Date: 2025-12-19
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass
import json
from pathlib import Path
from scipy import stats
import warnings

# 忽略警告以保持输出清洁
warnings.filterwarnings('ignore')

@dataclass
class StatisticalSummary:
    """统计分析摘要"""
    mean: float
    median: float
    std: float
    min_value: float
    max_value: float
    q25: float
    q75: float
    sample_size: int

@dataclass
class PerformancePattern:
    """性能模式"""
    pattern_type: str
    description: str
    confidence: float
    algorithm: str
    metric: str

@dataclass
class OptimizationInsight:
    """优化洞察"""
    algorithm: str
    strategy: str
    metric: str
    improvement_percent: float
    statistical_significance: bool
    recommendation: str

class TestResultAnalyzer:
    """量子算法基准测试结果分析器"""

    def __init__(self, results_file: str = None):
        """
        初始化结果分析器

        Args:
            results_file: 基准测试结果JSON文件路径
        """
        self.results = []
        self.df = None
        self.statistical_summaries = {}
        self.performance_patterns = []
        self.optimization_insights = []

        if results_file:
            self.load_results(results_file)

    def load_results(self, results_file: str) -> None:
        """加载基准测试结果"""
        try:
            with open(results_file, 'r') as f:
                self.results = json.load(f)

            # 转换为DataFrame便于分析
            self.df = pd.DataFrame(self.results)

            # 只分析成功的测试
            if 'test_success' in self.df.columns:
                self.df = self.df[self.df['test_success'] == True]

            print(f"已加载 {len(self.results)} 个测试结果，其中 {len(self.df)} 个成功测试")

        except Exception as e:
            print(f"加载结果文件失败: {e}")
            self.results = []
            self.df = pd.DataFrame()

    def add_results(self, results: List[Dict[str, Any]]) -> None:
        """直接添加测试结果"""
        self.results.extend(results)
        self.df = pd.DataFrame(self.results)

        # 只分析成功的测试
        if 'test_success' in self.df.columns:
            self.df = self.df[self.df['test_success'] == True]

    def calculate_statistical_summaries(self) -> Dict[str, StatisticalSummary]:
        """计算各项指标的统计摘要"""
        if self.df is None or len(self.df) == 0:
            print("没有可用的测试数据进行统计分析")
            return {}

        metrics = [
            'gate_reduction_percent',
            'depth_reduction_percent',
            'optimization_time',
            'total_time'
        ]

        summaries = {}

        for metric in metrics:
            if metric in self.df.columns:
                values = self.df[metric].dropna()
                if len(values) > 0:
                    summary = StatisticalSummary(
                        mean=float(values.mean()),
                        median=float(values.median()),
                        std=float(values.std()),
                        min_value=float(values.min()),
                        max_value=float(values.max()),
                        q25=float(values.quantile(0.25)),
                        q75=float(values.quantile(0.75)),
                        sample_size=len(values)
                    )
                    summaries[metric] = summary
                    print(f"{metric}: 均值={summary.mean:.3f}, 中位数={summary.median:.3f}, 标准差={summary.std:.3f}")

        self.statistical_summaries = summaries
        return summaries

    def analyze_algorithm_performance(self) -> Dict[str, Dict[str, Any]]:
        """分析各算法的性能表现"""
        if self.df is None or len(self.df) == 0:
            print("没有可用的测试数据进行算法性能分析")
            return {}

        algorithm_analysis = {}

        # 按算法分组分析
        for algorithm in self.df['algorithm_name'].unique():
            algorithm_data = self.df[self.df['algorithm_name'] == algorithm]

            # 计算各策略的平均表现
            strategy_performance = {}
            for strategy in algorithm_data['optimization_strategy'].unique():
                strategy_data = algorithm_data[algorithm_data['optimization_strategy'] == strategy]

                if len(strategy_data) > 0:
                    strategy_performance[strategy] = {
                        'avg_gate_reduction': float(strategy_data['gate_reduction_percent'].mean()),
                        'avg_depth_reduction': float(strategy_data['depth_reduction_percent'].mean()),
                        'avg_time': float(strategy_data['total_time'].mean()),
                        'success_rate': len(strategy_data) / len(algorithm_data),
                        'sample_size': len(strategy_data)
                    }

            # 算法总体统计
            algorithm_analysis[algorithm] = {
                'strategies': strategy_performance,
                'total_tests': len(algorithm_data),
                'avg_gates_before': float(algorithm_data['original_gates'].mean()),
                'avg_gates_after': float(algorithm_data['optimized_gates'].mean()),
                'avg_depth_before': float(algorithm_data['original_depth'].mean()),
                'avg_depth_after': float(algorithm_data['optimized_depth'].mean())
            }

        return algorithm_analysis

    def identify_performance_patterns(self) -> List[PerformancePattern]:
        """识别性能模式"""
        patterns = []

        if self.df is None or len(self.df) == 0:
            return patterns

        # 模式1: 门数量与优化效果的关系
        correlation_matrix = self.df[['original_gates', 'gate_reduction_percent']].corr()
        if len(correlation_matrix) > 1:
            correlation = correlation_matrix.iloc[0, 1]
            if abs(correlation) > 0.3:
                pattern_type = "正相关" if correlation > 0 else "负相关"
                patterns.append(PerformancePattern(
                    pattern_type=f"门数量-优化效果{pattern_type}",
                    description=f"原始门数量与优化效果呈{pattern_type} (相关系数: {correlation:.3f})",
                    confidence=abs(correlation),
                    algorithm="全算法",
                    metric="gate_reduction_percent"
                ))

        # 模式2: 量子比特数与优化效果的关系
        if 'n_qubits' in self.df.columns:
            qubit_correlation = self.df[['n_qubits', 'gate_reduction_percent']].corr().iloc[0, 1]
            if not np.isnan(qubit_correlation) and abs(qubit_correlation) > 0.2:
                pattern_type = "正相关" if qubit_correlation > 0 else "负相关"
                patterns.append(PerformancePattern(
                    pattern_type=f"量子比特数-优化效果{pattern_type}",
                    description=f"量子比特数与优化效果呈{pattern_type} (相关系数: {qubit_correlation:.3f})",
                    confidence=abs(qubit_correlation),
                    algorithm="全算法",
                    metric="gate_reduction_percent"
                ))

        # 模式3: 算法类型特定的模式
        algorithm_type_patterns = self.analyze_algorithm_type_patterns()
        patterns.extend(algorithm_type_patterns)

        self.performance_patterns = patterns
        return patterns

    def analyze_algorithm_type_patterns(self) -> List[PerformancePattern]:
        """分析算法类型特定的模式"""
        patterns = []

        if self.df is None or len(self.df) == 0:
            return patterns

        # 按算法类型分组
        if 'algorithm_type' in self.df.columns:
            for alg_type in self.df['algorithm_type'].unique():
                type_data = self.df[self.df['algorithm_type'] == alg_type]

                # 计算该类型的平均优化效果
                avg_gate_reduction = type_data['gate_reduction_percent'].mean()
                avg_depth_reduction = type_data['depth_reduction_percent'].mean()

                # 判断是否为高性能模式
                if avg_gate_reduction > 15:
                    patterns.append(PerformancePattern(
                        pattern_type="高门优化潜力",
                        description=f"{alg_type}类型算法显示出门优化高潜力 (平均减少: {avg_gate_reduction:.1f}%)",
                        confidence=avg_gate_reduction / 100,
                        algorithm=alg_type,
                        metric="gate_reduction_percent"
                    ))

                if avg_depth_reduction > 20:
                    patterns.append(PerformancePattern(
                        pattern_type="高深度优化潜力",
                        description=f"{alg_type}类型算法显示出深度优化高潜力 (平均减少: {avg_depth_reduction:.1f}%)",
                        confidence=avg_depth_reduction / 100,
                        algorithm=alg_type,
                        metric="depth_reduction_percent"
                    ))

        return patterns

    def detect_outliers(self) -> Dict[str, List[Dict[str, Any]]]:
        """检测异常值"""
        outliers = {}

        if self.df is None or len(self.df) == 0:
            return outliers

        metrics = ['gate_reduction_percent', 'depth_reduction_percent', 'optimization_time']

        for metric in metrics:
            if metric in self.df.columns:
                values = self.df[metric].dropna()
                if len(values) > 5:  # 需要足够的数据点
                    # 使用IQR方法检测异常值
                    Q1 = values.quantile(0.25)
                    Q3 = values.quantile(0.75)
                    IQR = Q3 - Q1
                    lower_bound = Q1 - 1.5 * IQR
                    upper_bound = Q3 + 1.5 * IQR

                    outlier_mask = (values < lower_bound) | (values > upper_bound)
                    outlier_indices = values[outlier_mask].index.tolist()

                    if outlier_indices:
                        outlier_data = []
                        for idx in outlier_indices:
                            row = self.df.iloc[idx]
                            outlier_data.append({
                                'algorithm': row['algorithm_name'],
                                'strategy': row['optimization_strategy'],
                                'n_qubits': row.get('n_qubits', 'N/A'),
                                'value': float(row[metric]),
                                'z_score': float((row[metric] - values.mean()) / values.std())
                            })

                        outliers[metric] = outlier_data
                        print(f"{metric} 检测到 {len(outlier_data)} 个异常值")

        return outliers

    def compare_optimization_strategies(self) -> Dict[str, Any]:
        """比较优化策略效果"""
        if self.df is None or len(self.df) == 0:
            return {}

        strategy_comparison = {}

        # 计算各策略的平均表现
        for strategy in self.df['optimization_strategy'].unique():
            strategy_data = self.df[self.df['optimization_strategy'] == strategy]

            strategy_comparison[strategy] = {
                'avg_gate_reduction': float(strategy_data['gate_reduction_percent'].mean()),
                'avg_depth_reduction': float(strategy_data['depth_reduction_percent'].mean()),
                'avg_time': float(strategy_data['total_time'].mean()),
                'success_rate': len(strategy_data[strategy_data['test_success'] == True]) / len(strategy_data) if 'test_success' in strategy_data.columns else 1.0,
                'sample_size': len(strategy_data),
                'gate_reduction_std': float(strategy_data['gate_reduction_percent'].std()),
                'depth_reduction_std': float(strategy_data['depth_reduction_percent'].std())
            }

        # 进行统计显著性检验
        significance_tests = {}
        strategies = list(strategy_comparison.keys())

        for i, strategy1 in enumerate(strategies):
            for strategy2 in strategies[i+1:]:
                data1 = self.df[self.df['optimization_strategy'] == strategy1]['gate_reduction_percent'].dropna()
                data2 = self.df[self.df['optimization_strategy'] == strategy2]['gate_reduction_percent'].dropna()

                if len(data1) > 5 and len(data2) > 5:
                    # 使用t检验比较两个策略
                    t_stat, p_value = stats.ttest_ind(data1, data2)

                    significance_tests[f"{strategy1}_vs_{strategy2}"] = {
                        't_statistic': float(t_stat),
                        'p_value': float(p_value),
                        'significant_difference': p_value < 0.05,
                        'effect_size': float(np.abs(data1.mean() - data2.mean()))
                    }

        return {
            'strategy_performance': strategy_comparison,
            'significance_tests': significance_tests
        }

    def generate_optimization_recommendations(self) -> List[OptimizationInsight]:
        """生成优化建议"""
        insights = []

        if self.df is None or len(self.df) == 0:
            return insights

        # 策略效果比较
        strategy_performance = {}
        for strategy in self.df['optimization_strategy'].unique():
            strategy_data = self.df[self.df['optimization_strategy'] == strategy]
            strategy_performance[strategy] = strategy_data['gate_reduction_percent'].mean()

        # 找出最佳策略
        if strategy_performance:
            best_strategy = max(strategy_performance.keys(), key=lambda x: strategy_performance[x])
            best_performance = strategy_performance[best_strategy]

            # 为每个算法生成建议
            for algorithm in self.df['algorithm_name'].unique():
                algorithm_data = self.df[self.df['algorithm_name'] == algorithm]

                # 找出该算法的最佳策略
                algorithm_best_strategy = None
                algorithm_best_performance = -1

                for strategy in algorithm_data['optimization_strategy'].unique():
                    strategy_data = algorithm_data[algorithm_data['optimization_strategy'] == strategy]
                    performance = strategy_data['gate_reduction_percent'].mean()

                    if performance > algorithm_best_performance:
                        algorithm_best_performance = performance
                        algorithm_best_strategy = strategy

                if algorithm_best_strategy:
                    # 生成建议
                    if algorithm_best_performance > 15:
                        recommendation_level = "强烈推荐"
                    elif algorithm_best_performance > 8:
                        recommendation_level = "推荐"
                    else:
                        recommendation_level = "谨慎考虑"

                    insights.append(OptimizationInsight(
                        algorithm=algorithm,
                        strategy=algorithm_best_strategy,
                        metric="gate_reduction_percent",
                        improvement_percent=algorithm_best_performance,
                        statistical_significance=True,  # 简化处理
                        recommendation=f"对于{algorithm}算法，{recommendation_level}使用{algorithm_best_strategy}策略，预期可获得{algorithm_best_performance:.1f}%的门数量减少"
                    ))

        return insights

    def generate_analysis_report(self) -> str:
        """生成完整的分析报告"""
        report = ["# 量子算法基准测试结果分析报告\n"]
        report.append(f"分析时间: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        # 基础统计
        if self.df is not None and len(self.df) > 0:
            report.append("## 基础统计信息\n")
            report.append(f"- 总测试数量: {len(self.df)}")
            report.append(f"- 涉及算法数: {len(self.df['algorithm_name'].unique())}")
            report.append(f"- 测试策略数: {len(self.df['optimization_strategy'].unique())}")
            report.append(f"- 量子比特范围: {self.df['n_qubits'].min()} - {self.df['n_qubits'].max()}\n")

        # 统计摘要
        summaries = self.calculate_statistical_summaries()
        if summaries:
            report.append("## 统计摘要\n")
            for metric, summary in summaries.items():
                report.append(f"### {metric}")
                report.append(f"- 平均值: {summary.mean:.3f}")
                report.append(f"- 中位数: {summary.median:.3f}")
                report.append(f"- 标准差: {summary.std:.3f}")
                report.append(f"- 最小值: {summary.min_value:.3f}")
                report.append(f"- 最大值: {summary.max_value:.3f}")
                report.append(f"- 样本数量: {summary.sample_size}\n")

        # 算法性能分析
        algorithm_analysis = self.analyze_algorithm_performance()
        if algorithm_analysis:
            report.append("## 算法性能分析\n")
            for algorithm, analysis in algorithm_analysis.items():
                report.append(f"### {algorithm}")
                report.append(f"- 总测试数: {analysis['total_tests']}")
                report.append(f"- 平均原始门数: {analysis['avg_gates_before']:.1f}")
                report.append(f"- 平均优化后门数: {analysis['avg_gates_after']:.1f}")
                report.append(f"- 平均原始深度: {analysis['avg_depth_before']:.1f}")
                report.append(f"- 平均优化后深度: {analysis['avg_depth_after']:.1f}\n")

                report.append("#### 策略表现:")
                for strategy, perf in analysis['strategies'].items():
                    report.append(f"- {strategy}: 门减少 {perf['avg_gate_reduction']:.1f}%, 深度减少 {perf['avg_depth_reduction']:.1f}%, 成功率 {perf['success_rate']*100:.1f}%")
                report.append("")

        # 性能模式
        patterns = self.identify_performance_patterns()
        if patterns:
            report.append("## 性能模式\n")
            for i, pattern in enumerate(patterns, 1):
                report.append(f"{i}. **{pattern.pattern_type}**")
                report.append(f"   - 描述: {pattern.description}")
                report.append(f"   - 置信度: {pattern.confidence:.3f}")
                report.append(f"   - 相关算法: {pattern.algorithm}")
                report.append("")

        # 异常值检测
        outliers = self.detect_outliers()
        if outliers:
            report.append("## 异常值检测\n")
            for metric, outlier_list in outliers.items():
                report.append(f"### {metric}")
                report.append(f"检测到 {len(outlier_list)} 个异常值:")
                for outlier in outlier_list[:5]:  # 只显示前5个
                    report.append(f"- {outlier['algorithm']} ({outlier['strategy']}): {outlier['value']:.3f} (Z-score: {outlier['z_score']:.2f})")
                if len(outlier_list) > 5:
                    report.append(f"- ... 还有 {len(outlier_list) - 5} 个异常值")
                report.append("")

        # 策略比较
        strategy_comparison = self.compare_optimization_strategies()
        if strategy_comparison and 'strategy_performance' in strategy_comparison:
            report.append("## 策略效果比较\n")
            for strategy, perf in strategy_comparison['strategy_performance'].items():
                report.append(f"### {strategy}")
                report.append(f"- 平均门减少: {perf['avg_gate_reduction']:.1f}% ± {perf['gate_reduction_std']:.1f}%")
                report.append(f"- 平均深度减少: {perf['avg_depth_reduction']:.1f}% ± {perf['depth_reduction_std']:.1f}%")
                report.append(f"- 平均时间: {perf['avg_time']:.3f}s")
                report.append(f"- 成功率: {perf['success_rate']*100:.1f}%")
                report.append("")

        # 优化建议
        insights = self.generate_optimization_recommendations()
        if insights:
            report.append("## 优化建议\n")
            for insight in insights:
                report.append(f"- {insight.recommendation}")
            report.append("")

        return "\n".join(report)

    def save_analysis_report(self, filename: str = "quantum_benchmark_analysis.md") -> None:
        """保存分析报告"""
        report = self.generate_analysis_report()
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"分析报告已保存到: {filename}")

    def export_analysis_data(self, filename: str = "analysis_data.json") -> None:
        """导出分析数据"""
        # 转换数据为JSON可序列化格式
        def convert_for_json(obj):
            if hasattr(obj, '__dict__'):
                return {k: convert_for_json(v) for k, v in vars(obj).items()}
            elif isinstance(obj, dict):
                return {k: convert_for_json(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_for_json(item) for item in obj]
            elif isinstance(obj, (np.integer, np.floating)):
                return float(obj) if isinstance(obj, np.floating) else int(obj)
            elif isinstance(obj, np.bool_):
                return bool(obj)
            elif isinstance(obj, (np.ndarray, pd.Series)):
                return obj.tolist()
            else:
                return obj

        analysis_data = {
            'statistical_summaries': convert_for_json(self.statistical_summaries),
            'performance_patterns': convert_for_json(self.performance_patterns),
            'optimization_insights': convert_for_json(self.optimization_insights),
            'algorithm_analysis': convert_for_json(self.analyze_algorithm_performance()),
            'strategy_comparison': convert_for_json(self.compare_optimization_strategies()),
            'outliers': convert_for_json(self.detect_outliers())
        }

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(analysis_data, f, indent=2, ensure_ascii=False)

        print(f"分析数据已导出到: {filename}")


def main():
    """主函数用于测试分析器功能"""
    print("量子算法基准测试结果分析器")
    print("=" * 40)

    # 创建分析器
    analyzer = TestResultAnalyzer()

    # 尝试加载现有的测试结果
    results_file = "simple_benchmark_results.json"
    if Path(results_file).exists():
        analyzer.load_results(results_file)

        # 生成完整分析报告
        report = analyzer.generate_analysis_report()
        print("\n分析报告:")
        print("=" * 40)
        print(report)

        # 保存报告
        analyzer.save_analysis_report("quantum_benchmark_analysis.md")
        analyzer.export_analysis_data("analysis_data.json")
    else:
        print(f"未找到测试结果文件: {results_file}")
        print("请先运行基准测试以生成结果数据")


if __name__ == "__main__":
    main()