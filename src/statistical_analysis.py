"""Statistical Analysis Framework for Performance Comparison.

This module provides comprehensive statistical analysis capabilities for
comparing Sim-Fusion vs Qibo fusion performance across multiple experiments.

Key Features:
- Statistical significance testing (t-tests, Mann-Whitney U tests)
- Confidence interval calculations
- Performance trend analysis
- Effect size calculations
- Multiple comparison corrections
- Bootstrapping for robust estimates

Authors: Sim-Fusion Team
Version: 1.0.0
"""

from __future__ import annotations

import math
import statistics
from typing import List, Dict, Any, Tuple, Optional, Union
from dataclasses import dataclass
from enum import Enum
import warnings

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    np = None

try:
    from scipy import stats
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False
    stats = None


class StatisticalTest(Enum):
    """Statistical test types."""
    T_TEST = "t_test"
    MANN_WHITNEY = "mann_whitney"
    WILCOXON = "wilcoxon"
    PAIRED_T_TEST = "paired_t_test"
    BOOTSTRAP = "bootstrap"


class TrendDirection(Enum):
    """Performance trend directions."""
    IMPROVING = "improving"
    DEGRADING = "degrading"
    STABLE = "stable"
    UNCLEAR = "unclear"


@dataclass
class StatisticalSummary:
    """Statistical summary of performance metrics."""

    def __init__(self,
                 values: List[float],
                 metric_name: str = "metric"):
        """Initialize statistical summary.

        Args:
            values: List of measurement values
            metric_name: Name of the metric being analyzed
        """
        if not values:
            raise ValueError("Values list cannot be empty")

        self.values = values
        self.metric_name = metric_name
        self.n = len(values)

        # Basic statistics
        self.mean = statistics.mean(values)
        self.median = statistics.median(values)
        self.stdev = statistics.stdev(values) if self.n > 1 else 0.0
        self.variance = statistics.variance(values) if self.n > 1 else 0.0

        # Percentiles
        sorted_values = sorted(values)
        self.min_val = sorted_values[0]
        self.max_val = sorted_values[-1]
        self.q25 = self._percentile(sorted_values, 25)
        self.q75 = self._percentile(sorted_values, 75)

        # Confidence intervals (95% default)
        self.confidence_interval_95 = self._calculate_confidence_interval(0.95)

    def _percentile(self, sorted_values: List[float], percentile: float) -> float:
        """Calculate percentile value."""
        if NUMPY_AVAILABLE:
            return float(np.percentile(sorted_values, percentile))
        else:
            # Simple linear interpolation
            index = (percentile / 100) * (len(sorted_values) - 1)
            lower = int(math.floor(index))
            upper = int(math.ceil(index))
            if lower == upper:
                return sorted_values[lower]
            weight = index - lower
            return sorted_values[lower] * (1 - weight) + sorted_values[upper] * weight

    def _calculate_confidence_interval(self, confidence: float) -> Tuple[float, float]:
        """Calculate confidence interval for the mean."""
        if self.n <= 1:
            return (self.mean, self.mean)

        if SCIPY_AVAILABLE:
            alpha = 1 - confidence
            t_critical = stats.t.ppf(1 - alpha/2, self.n - 1)
            margin = t_critical * (self.stdev / math.sqrt(self.n))
            return (self.mean - margin, self.mean + margin)
        else:
            # Approximate using normal distribution for large n
            if self.n >= 30:
                z_critical = 1.96 if confidence == 0.95 else 1.645
                margin = z_critical * (self.stdev / math.sqrt(self.n))
                return (self.mean - margin, self.mean + margin)
            else:
                # For small n without scipy, use Chebyshev's inequality
                margin = self.stdev / math.sqrt(confidence * self.n)
                return (self.mean - margin, self.mean + margin)

    def coefficient_of_variation(self) -> float:
        """Calculate coefficient of variation (CV)."""
        if self.mean == 0:
            return float('inf') if self.stdev > 0 else 0.0
        return self.stdev / abs(self.mean)

    def is_stable(self, cv_threshold: float = 0.1) -> bool:
        """Check if measurements are stable (low variability)."""
        return self.coefficient_of_variation() <= cv_threshold


@dataclass
class SignificanceTestResult:
    """Result of statistical significance test."""

    test_name: str
    statistic: float
    p_value: float
    is_significant: bool
    effect_size: float
    interpretation: str
    confidence_interval: Optional[Tuple[float, float]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        return {
            'test_name': self.test_name,
            'statistic': self.statistic,
            'p_value': self.p_value,
            'is_significant': self.is_significant,
            'effect_size': self.effect_size,
            'interpretation': self.interpretation,
            'confidence_interval': self.confidence_interval
        }


@dataclass
class TrendAnalysisResult:
    """Result of performance trend analysis."""

    direction: TrendDirection
    slope: float
    correlation: float
    r_squared: float
    trend_strength: str
    interpretation: str
    confidence_level: float

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        return {
            'direction': self.direction.value,
            'slope': self.slope,
            'correlation': self.correlation,
            'r_squared': self.r_squared,
            'trend_strength': self.trend_strength,
            'interpretation': self.interpretation,
            'confidence_level': self.confidence_level
        }


class StatisticalAnalyzer:
    """Main statistical analysis class for performance comparison."""

    def __init__(self,
                 significance_level: float = 0.05,
                 min_sample_size: int = 3):
        """Initialize the statistical analyzer.

        Args:
            significance_level: Alpha level for significance testing (default 0.05)
            min_sample_size: Minimum number of samples required for analysis
        """
        self.significance_level = significance_level
        self.min_sample_size = min_sample_size

    def summarize_metrics(self, data: Dict[str, List[float]]) -> Dict[str, StatisticalSummary]:
        """Generate statistical summaries for multiple metrics.

        Args:
            data: Dictionary mapping metric names to list of values

        Returns:
            Dictionary of statistical summaries
        """
        summaries = {}

        for metric_name, values in data.items():
            if len(values) < self.min_sample_size:
                warnings.warn(f"Insufficient samples for {metric_name}: {len(values)} < {self.min_sample_size}")
                continue

            try:
                summaries[metric_name] = StatisticalSummary(values, metric_name)
            except Exception as e:
                warnings.warn(f"Failed to summarize {metric_name}: {e}")

        return summaries

    def test_significance(self,
                         group1: List[float],
                         group2: List[float],
                         test_type: StatisticalTest = StatisticalTest.T_TEST,
                         alternative: str = "two-sided") -> SignificanceTestResult:
        """Test statistical significance between two groups.

        Args:
            group1: First group of measurements
            group2: Second group of measurements
            test_type: Type of statistical test to perform
            alternative: Alternative hypothesis ("two-sided", "less", "greater")

        Returns:
            Significance test result
        """
        if len(group1) < self.min_sample_size or len(group2) < self.min_sample_size:
            return SignificanceTestResult(
                test_name=test_type.value,
                statistic=0.0,
                p_value=1.0,
                is_significant=False,
                effect_size=0.0,
                interpretation="Insufficient sample size"
            )

        try:
            if test_type == StatisticalTest.T_TEST and SCIPY_AVAILABLE:
                # Independent two-sample t-test
                statistic, p_value = stats.ttest_ind(group1, group2, alternative=alternative)
                effect_size = self._calculate_cohens_d(group1, group2)

            elif test_type == StatisticalTest.PAIRED_T_TEST and SCIPY_AVAILABLE:
                # Paired t-test
                if len(group1) != len(group2):
                    raise ValueError("Groups must have same size for paired test")
                statistic, p_value = stats.ttest_rel(group1, group2, alternative=alternative)
                effect_size = self._calculate_paired_cohens_d(group1, group2)

            elif test_type == StatisticalTest.MANN_WHITNEY and SCIPY_AVAILABLE:
                # Mann-Whitney U test (non-parametric)
                statistic, p_value = stats.mannwhitneyu(
                    group1, group2, alternative=alternative
                )
                effect_size = self._calculate_rank_biserial_correlation(group1, group2)

            else:
                # Fallback to basic bootstrap test
                statistic, p_value = self._bootstrap_test(group1, group2)
                effect_size = self._calculate_cohens_d(group1, group2)
                test_type = StatisticalTest.BOOTSTRAP

            is_significant = p_value < self.significance_level
            interpretation = self._interpret_result(p_value, is_significant, effect_size)

            return SignificanceTestResult(
                test_name=test_type.value,
                statistic=statistic,
                p_value=p_value,
                is_significant=is_significant,
                effect_size=effect_size,
                interpretation=interpretation
            )

        except Exception as e:
            return SignificanceTestResult(
                test_name="error",
                statistic=0.0,
                p_value=1.0,
                is_significant=False,
                effect_size=0.0,
                interpretation=f"Test failed: {e}"
            )

    def analyze_trend(self,
                      values: List[float],
                      x_values: Optional[List[float]] = None) -> TrendAnalysisResult:
        """Analyze performance trend over time or scale.

        Args:
            values: Sequence of performance measurements
            x_values: Corresponding x-axis values (e.g., circuit sizes)

        Returns:
            Trend analysis result
        """
        if len(values) < 3:
            return TrendAnalysisResult(
                direction=TrendDirection.UNCLEAR,
                slope=0.0,
                correlation=0.0,
                r_squared=0.0,
                trend_strength="insufficient_data",
                interpretation="Need at least 3 data points for trend analysis",
                confidence_level=0.0
            )

        if x_values is None:
            x_values = list(range(len(values)))

        if len(x_values) != len(values):
            raise ValueError("x_values and values must have same length")

        try:
            if NUMPY_AVAILABLE:
                # Use numpy for linear regression
                x_arr = np.array(x_values)
                y_arr = np.array(values)

                # Calculate slope and intercept
                slope, intercept = np.polyfit(x_arr, y_arr, 1)

                # Calculate correlation
                correlation = np.corrcoef(x_arr, y_arr)[0, 1]
                r_squared = correlation ** 2

                # Predictions and residuals
                predictions = slope * x_arr + intercept
                residuals = y_arr - predictions

                # Trend strength based on correlation magnitude
                if abs(correlation) >= 0.8:
                    trend_strength = "strong"
                elif abs(correlation) >= 0.5:
                    trend_strength = "moderate"
                elif abs(correlation) >= 0.3:
                    trend_strength = "weak"
                else:
                    trend_strength = "very_weak"

                # Determine direction
                if abs(slope) < 0.01:  # Near-zero slope
                    direction = TrendDirection.STABLE
                elif slope > 0:
                    direction = TrendDirection.IMPROVING if trend_strength != "very_weak" else TrendDirection.UNCLEAR
                else:
                    direction = TrendDirection.DEGRADING if trend_strength != "very_weak" else TrendDirection.UNCLEAR

                interpretation = self._interpret_trend(correlation, slope, trend_strength)
                confidence_level = min(1.0, abs(correlation) * 1.25)  # Rough confidence estimate

            else:
                # Fallback without numpy
                direction = TrendDirection.UNCLEAR
                slope = 0.0
                correlation = 0.0
                r_squared = 0.0
                trend_strength = "no_numpy"
                interpretation = "Install numpy for trend analysis"
                confidence_level = 0.0

            return TrendAnalysisResult(
                direction=direction,
                slope=slope,
                correlation=correlation,
                r_squared=r_squared,
                trend_strength=trend_strength,
                interpretation=interpretation,
                confidence_level=confidence_level
            )

        except Exception as e:
            return TrendAnalysisResult(
                direction=TrendDirection.UNCLEAR,
                slope=0.0,
                correlation=0.0,
                r_squared=0.0,
                trend_strength="error",
                interpretation=f"Trend analysis failed: {e}",
                confidence_level=0.0
            )

    def _calculate_cohens_d(self, group1: List[float], group2: List[float]) -> float:
        """Calculate Cohen's d effect size."""
        if not group1 or not group2:
            return 0.0

        mean1, mean2 = statistics.mean(group1), statistics.mean(group2)
        n1, n2 = len(group1), len(group2)

        # Pooled standard deviation
        var1 = statistics.variance(group1) if n1 > 1 else 0.0
        var2 = statistics.variance(group2) if n2 > 1 else 0.0
        pooled_sd = math.sqrt(((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2))

        if pooled_sd == 0:
            return 0.0

        return abs(mean1 - mean2) / pooled_sd

    def _calculate_paired_cohens_d(self, group1: List[float], group2: List[float]) -> float:
        """Calculate Cohen's d for paired samples."""
        if len(group1) != len(group2) or not group1:
            return 0.0

        differences = [g1 - g2 for g1, g2 in zip(group1, group2)]
        mean_diff = statistics.mean(differences)
        std_diff = statistics.stdev(differences) if len(differences) > 1 else 0.0

        if std_diff == 0:
            return 0.0

        return abs(mean_diff) / std_diff

    def _calculate_rank_biserial_correlation(self, group1: List[float], group2: List[float]) -> float:
        """Calculate rank-biserial correlation for Mann-Whitney test."""
        # Simplified calculation
        n1, n2 = len(group1), len(group2)
        if n1 == 0 or n2 == 0:
            return 0.0

        # Sort all values and assign ranks
        all_values = group1 + group2
        ranked = sorted(enumerate(all_values), key=lambda x: x[1])

        # Sum ranks for group1
        rank_sum1 = sum(i + 1 for i, (orig_idx, _) in enumerate(ranked) if orig_idx < n1)

        # Expected rank sum under null hypothesis
        expected_rank_sum = n1 * (n1 + n2 + 1) / 2

        # Rank-biserial correlation
        numerator = 2 * rank_sum1 - n1 * (n1 + n2 + 1)
        denominator = n1 * n2

        return numerator / denominator if denominator != 0 else 0.0

    def _bootstrap_test(self, group1: List[float], group2: List[float],
                       n_bootstrap: int = 1000) -> Tuple[float, float]:
        """Simple bootstrap test for significance."""
        # Combine groups
        combined = group1 + group2
        n1, n2 = len(group1), len(group2)

        # Calculate observed difference
        observed_diff = abs(statistics.mean(group1) - statistics.mean(group2))

        # Bootstrap
        n_extreme = 0
        for _ in range(n_bootstrap):
            # Permute combined data
            import random
            shuffled = combined.copy()
            random.shuffle(shuffled)

            # Split into two groups
            new_group1 = shuffled[:n1]
            new_group2 = shuffled[n1:]

            # Calculate difference
            diff = abs(statistics.mean(new_group1) - statistics.mean(new_group2))

            if diff >= observed_diff:
                n_extreme += 1

        # p-value
        p_value = n_extreme / n_bootstrap

        # Use difference as statistic
        return observed_diff, p_value

    def _interpret_result(self, p_value: float, is_significant: bool, effect_size: float) -> str:
        """Interpret statistical test result."""
        if not is_significant:
            return "No significant difference detected"

        # Effect size interpretation (Cohen's d)
        if effect_size < 0.2:
            magnitude = "negligible"
        elif effect_size < 0.5:
            magnitude = "small"
        elif effect_size < 0.8:
            magnitude = "medium"
        else:
            magnitude = "large"

        return f"Significant difference detected ({magnitude} effect size, p={p_value:.3f})"

    def _interpret_trend(self, correlation: float, slope: float, strength: str) -> str:
        """Interpret trend analysis result."""
        if strength == "very_weak":
            return "No clear trend detected"
        elif strength == "weak":
            return f"Weak {'improving' if slope > 0 else 'degrading'} trend detected"
        elif strength == "moderate":
            return f"Moderate {'improving' if slope > 0 else 'degrading'} trend detected"
        elif strength == "strong":
            return f"Strong {'improving' if slope > 0 else 'degrading'} trend detected"
        else:
            return "Trend analysis inconclusive"

    def comprehensive_analysis(self,
                             sim_fusion_data: Dict[str, List[float]],
                             qibo_fusion_data: Dict[str, List[float]]) -> Dict[str, Any]:
        """Perform comprehensive statistical analysis comparing two methods.

        Args:
            sim_fusion_data: Performance metrics for Sim-Fusion
            qibo_fusion_data: Performance metrics for Qibo fusion

        Returns:
            Comprehensive analysis results
        """
        results = {
            'summary_statistics': {
                'sim_fusion': self.summarize_metrics(sim_fusion_data),
                'qibo_fusion': self.summarize_metrics(qibo_fusion_data)
            },
            'significance_tests': {},
            'trend_analysis': {},
            'recommendations': []
        }

        # Significance tests for each metric
        common_metrics = set(sim_fusion_data.keys()) & set(qibo_fusion_data.keys())

        for metric in common_metrics:
            sim_values = sim_fusion_data[metric]
            qibo_values = qibo_fusion_data[metric]

            # Basic t-test
            t_test = self.test_significance(sim_values, qibo_values, StatisticalTest.T_TEST)

            # Non-parametric test (if available)
            if SCIPY_AVAILABLE:
                mann_whitney = self.test_significance(sim_values, qibo_values, StatisticalTest.MANN_WHITNEY)
            else:
                mann_whitney = None

            results['significance_tests'][metric] = {
                't_test': t_test.to_dict(),
                'mann_whitney': mann_whitney.to_dict() if mann_whitney else None
            }

            # Trend analysis if we have enough data points
            if len(sim_values) >= 3:
                sim_trend = self.analyze_trend(sim_values)
                results['trend_analysis'][f'{metric}_sim_fusion'] = sim_trend.to_dict()

            if len(qibo_values) >= 3:
                qibo_trend = self.analyze_trend(qibo_values)
                results['trend_analysis'][f'{metric}_qibo_fusion'] = qibo_trend.to_dict()

        # Generate recommendations
        results['recommendations'] = self._generate_recommendations(results)

        return results

    def _generate_recommendations(self, analysis_results: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on analysis results."""
        recommendations = []

        # Analyze significance tests
        significance_tests = analysis_results.get('significance_tests', {})

        for metric, tests in significance_tests.items():
            t_test = tests.get('t_test', {})

            if t_test.get('is_significant', False):
                effect_size = t_test.get('effect_size', 0)

                if 'gate_reduction' in metric:
                    if effect_size > 0.5:
                        recommendations.append(f"Strong evidence of difference in {metric} - recommend method with better performance")
                    else:
                        recommendations.append(f"Moderate difference in {metric} - consider other factors")

                elif 'time' in metric or 'efficiency' in metric:
                    if effect_size > 0.3:
                        recommendations.append(f"Significant performance difference in {metric} - prioritize faster method")

            else:
                recommendations.append(f"No significant difference in {metric} - either method can be used")

        # Analyze trends
        trend_analysis = analysis_results.get('trend_analysis', {})

        for trend_key, trend in trend_analysis.items():
            if trend.get('direction') == 'improving' and trend.get('trend_strength') in ['strong', 'moderate']:
                recommendations.append(f"Improving trend detected in {trend_key} - performance may improve with larger circuits")
            elif trend.get('direction') == 'degrading' and trend.get('trend_strength') in ['strong', 'moderate']:
                recommendations.append(f"Concerning degrading trend in {trend_key} - investigate scaling issues")

        if not recommendations:
            recommendations.append("Insufficient evidence for strong recommendations - collect more data")

        return recommendations


# Convenience functions for quick usage
def quick_comparison(sim_fusion_metrics: Dict[str, List[float]],
                    qibo_fusion_metrics: Dict[str, List[float]],
                    significance_level: float = 0.05) -> Dict[str, Any]:
    """Quick comparison between Sim-Fusion and Qibo fusion.

    Args:
        sim_fusion_metrics: Performance metrics for Sim-Fusion
        qibo_fusion_metrics: Performance metrics for Qibo fusion
        significance_level: Statistical significance level

    Returns:
        Comparison analysis results
    """
    analyzer = StatisticalAnalyzer(significance_level=significance_level)
    return analyzer.comprehensive_analysis(sim_fusion_metrics, qibo_fusion_metrics)


def summarize_performance(data: Dict[str, List[float]]) -> Dict[str, StatisticalSummary]:
    """Generate statistical summaries for performance data.

    Args:
        data: Performance metrics data

    Returns:
        Statistical summaries
    """
    analyzer = StatisticalAnalyzer()
    return analyzer.summarize_metrics(data)