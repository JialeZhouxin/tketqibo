# Sim-Fusion Performance Comparison Framework User Guide

## Overview

The Sim-Fusion Performance Comparison Framework provides a comprehensive system for comparing quantum circuit optimization methods, specifically Sim-Fusion (TKET + Qibo fusion) versus Qibo's native fusion optimization.

### Key Features

- **Benchmark Circuit Generation**: Create diverse quantum circuits for testing
- **Performance Comparison Engine**: Compare optimization methods with statistical rigor
- **Statistical Analysis Framework**: Comprehensive statistical analysis with significance testing
- **Report Generation System**: Generate detailed reports in multiple formats
- **Strategy Recommendation System**: Get intelligent optimization method recommendations

## Installation

### Prerequisites

```bash
# Core dependencies
pip install qibo

# For Sim-Fusion functionality
pip install pytket pytket-qibo

# Optional dependencies for enhanced features
pip install numpy scipy matplotlib seaborn scikit-learn jinja2

# For development and testing
pip install pytest
```

### Quick Setup

```python
# Verify installation
import sim_fusion
from src.performance_comparison import PerformanceComparisonEngine

print("Sim-Fusion Performance Comparison Framework ready!")
```

## Quick Start

### Basic Usage

```python
from qibo import Circuit, gates
import sim_fusion

# Create a test circuit
circuit = Circuit(3)
circuit.add(gates.H(0))
circuit.add(gates.CNOT(0, 1))
circuit.add(gates.H(1))
circuit.add(gates.H(1))  # Redundant gate

# Quick optimization
optimized = sim_fusion.quick_sim_fusion(circuit)
print(f"Optimized: {circuit.ngates} -> {optimized.ngates} gates")

# With detailed statistics
optimized, stats = sim_fusion.sim_fusion_with_stats(circuit, verbose=True)
print(f"Gate reduction: {stats.gate_reduction_percent:.1f}%")
print(f"Optimization time: {stats.total_time:.3f}s")
```

### Performance Comparison

```python
from src.performance_comparison import PerformanceComparisonEngine

# Initialize comparison engine
engine = PerformanceComparisonEngine()

# Single circuit comparison
result = engine.compare_optimization_methods(circuit, iterations=3)
print(f"Winner: {result['winner']}")

# Batch comparison
circuits = [circuit1, circuit2, circuit3]
results = engine.run_batch_comparison(circuits, iterations=3)

# Analyze results
sim_fusion_wins = sum(1 for r in results if r['winner'] == 'sim_fusion')
print(f"Sim-Fusion wins: {sim_fusion_wins}/{len(results)}")
```

## Detailed Usage

### 1. Benchmark Circuit Generation

```python
from src.benchmark_circuits import BenchmarkCircuitGenerator

# Create circuit generator
generator = BenchmarkCircuitGenerator()

# Generate different circuit types
bell_state = generator.create_bell_state(2)
ghz_state = generator.create_ghz_state(4)
qft_circuit = generator.create_qft_circuit(3)
redundant_circuit = generator.create_redundant_circuit(3, "high")

# Generate comprehensive circuit suite
circuit_suite = generator.generate_circuit_suite(
    circuit_types=['bell_state', 'ghz_state', 'qft', 'redundant_operations'],
    n_qubits_range=(2, 6),
    circuits_per_type=3
)

print(f"Generated {len(circuit_suite)} circuits")
for item in circuit_suite:
    print(f"  {item['type']}: {item['n_qubits']} qubits, {item['n_gates']} gates")
```

#### Available Circuit Types

- **Bell State**: Entangled Bell states
- **GHZ State**: Greenberger–Horne–Zeilinger states
- **QFT**: Quantum Fourier Transform
- **QAOA**: Quantum Approximate Optimization Algorithm
- **VQE**: Variational Quantum Eigensolver
- **Random Clifford**: Random Clifford circuits
- **Random Rotation**: Random rotation gate circuits
- **Redundant Operations**: Circuits with known redundancies
- **Mixed Algorithm**: Combined algorithm patterns

### 2. Statistical Analysis

```python
from src.statistical_analysis import StatisticalAnalyzer

# Initialize analyzer
analyzer = StatisticalAnalyzer(significance_level=0.05)

# Prepare performance data
sim_fusion_data = {
    'gate_reduction': [15.2, 14.8, 16.1, 15.9, 15.5],
    'optimization_time': [0.12, 0.15, 0.11, 0.14, 0.13],
    'efficiency_score': [120.5, 115.2, 125.8, 118.9, 122.1]
}

qibo_fusion_data = {
    'gate_reduction': [12.1, 11.9, 13.2, 12.8, 12.5],
    'optimization_time': [0.08, 0.09, 0.07, 0.08, 0.09],
}

# Generate statistical summaries
sim_summary = analyzer.summarize_metrics(sim_fusion_data)
for metric, summary in sim_summary.items():
    print(f"{metric}: mean={summary.mean:.3f}, std={summary.stdev:.3f}")

# Perform significance testing
test_result = analyzer.test_significance(
    sim_fusion_data['gate_reduction'],
    qibo_fusion_data['gate_reduction']
)
print(f"Significant difference: {test_result.is_significant}")
print(f"P-value: {test_result.p_value:.6f}")

# Trend analysis
trend = analyzer.analyze_trend(sim_fusion_data['gate_reduction'])
print(f"Trend: {trend.direction.value} (correlation: {trend.correlation:.3f})")

# Comprehensive analysis
comprehensive = analyzer.comprehensive_analysis(sim_fusion_data, qibo_fusion_data)
print("Recommendations:")
for rec in comprehensive['recommendations']:
    print(f"  - {rec}")
```

#### Statistical Methods

- **Descriptive Statistics**: Mean, standard deviation, percentiles, confidence intervals
- **Significance Testing**: T-tests, Mann-Whitney U tests, paired tests
- **Effect Size Calculation**: Cohen's d, rank-biserial correlation
- **Trend Analysis**: Linear regression, correlation analysis
- **Bootstrap Methods**: Resampling for robust estimates

### 3. Report Generation

```python
from src.report_generator import ReportGenerator, ReportFormat

# Initialize report generator
generator = ReportGenerator(
    output_dir="performance_reports",
    include_charts=True  # Requires matplotlib
)

# Generate comprehensive reports
output_files = generator.generate_comprehensive_report(
    analysis_results=comprehensive_analysis_data,
    circuit_metadata={
        'circuit_types': ['bell_state', 'ghz_state', 'qft'],
        'qubit_range': (2, 6),
        'iterations': 3
    },
    formats=[ReportFormat.MARKDOWN, ReportFormat.JSON, ReportFormat.HTML]
)

print("Generated reports:")
for format_type, file_path in output_files.items():
    print(f"  {format_type}: {file_path}")

# Quick report generation
from src.report_generator import quick_report
quick_files = quick_report(
    analysis_results,
    output_dir="quick_reports",
    formats=['markdown', 'json']
)
```

#### Report Formats

- **Markdown**: Human-readable reports with tables and charts
- **JSON**: Machine-readable structured data
- **CSV**: Tabular data for spreadsheet analysis
- **HTML**: Interactive web reports (optional)

### 4. Strategy Recommendations

```python
from src.strategy_recommender import StrategyRecommender, UsageScenario

# Initialize recommender
recommender = StrategyRecommender(
    learning_enabled=True,
    historical_data_path="performance_history.json"  # Optional
)

# Analyze circuit characteristics
circuit_characteristics = {
    'qubits': 4,
    'gates': 20,
    'depth': 12,
    'gate_distribution': {
        'H': 3, 'X': 2, 'CNOT': 6, 'RX': 4, 'RY': 3, 'RZ': 2
    },
    'redundancy_level': 0.3,
    'entanglement_density': 0.3
}

characteristics = recommender.analyze_circuit_characteristics(circuit_characteristics)

# Get recommendation for different scenarios
scenarios = [
    UsageScenario.SIMULATION,
    UsageScenario.REAL_TIME_APPLICATIONS,
    UsageScenario.LARGE_SCALE_PROBLEMS,
    UsageScenario.HARDWARE_EXECUTION
]

for scenario in scenarios:
    recommendation = recommender.recommend_optimization_method(
        characteristics, scenario
    )
    print(f"{scenario.value}: {recommendation.method.value}")
    print(f"  Confidence: {recommendation.confidence.value}")
    print(f"  Reasoning: {recommendation.reasoning}")

# Comprehensive recommendation summary
summary = recommender.get_recommendation_summary(characteristics, UsageScenario.SIMULATION)
print(f"Primary recommendation: {summary['primary_recommendation']['method']}")
print(f"Key factors: {summary['key_factors']}")
```

#### Usage Scenarios

- **Simulation**: General quantum circuit simulation
- **Hardware Execution**: Optimization for actual quantum hardware
- **Repeated Optimization**: Multiple similar optimizations
- **Large Scale Problems**: Large quantum circuits (>20 qubits)
- **Real Time Applications**: Time-critical optimizations
- **Research Exploration**: Experimental quantum algorithm development

## Advanced Usage

### Custom Performance Metrics

```python
from src.performance_comparison import PerformanceMetrics

# Create custom metrics
custom_metrics = PerformanceMetrics(
    method='sim_fusion',
    original_gates=20,
    optimized_gates=15,
    optimization_time=0.1,
    memory_usage=50.0,
    circuit_size_kb=10.5
)

print(f"Custom efficiency: {custom_metrics.efficiency_score:.1f}")
```

### Extending the Framework

```python
# Custom optimization method
class CustomOptimizer:
    def __init__(self):
        self.name = "custom_method"

    def optimize(self, circuit):
        # Your custom optimization logic
        return optimized_circuit

# Integrate with comparison engine
def compare_with_custom(engine, circuit, custom_optimizer):
    # Run standard comparison
    standard_result = engine.compare_optimization_methods(circuit)

    # Add custom method
    custom_start = time.time()
    custom_optimized = custom_optimizer.optimize(circuit)
    custom_time = time.time() - custom_start

    # Compare custom method
    custom_metrics = PerformanceMetrics(
        method='custom',
        original_gates=circuit.ngates,
        optimized_gates=custom_optimized.ngates,
        optimization_time=custom_time
    )

    return standard_result, custom_metrics
```

### Batch Processing

```python
import concurrent.futures
from src.performance_comparison import PerformanceComparisonEngine

def process_circuit_batch(circuits, max_workers=4):
    """Process multiple circuits in parallel."""
    engine = PerformanceComparisonEngine()

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(engine.compare_optimization_methods, circuit, iterations=3)
            for circuit in circuits
        ]

        results = []
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            results.append(result)

    return results

# Usage
circuits = [circuit1, circuit2, circuit3, circuit4]
batch_results = process_circuit_batch(circuits)
```

## Best Practices

### 1. Circuit Selection

- **Diverse Circuit Types**: Use various circuit types for comprehensive testing
- **Appropriate Size**: Test circuits of different sizes (2-20+ qubits)
- **Realistic Complexity**: Use circuits that represent actual use cases
- **Known Characteristics**: Include circuits with known optimization opportunities

### 2. Statistical Rigor

- **Multiple Iterations**: Run each comparison multiple times (3-5+ iterations)
- **Consistent Conditions**: Ensure consistent testing environment
- **Significance Testing**: Use statistical tests to validate results
- **Effect Size**: Consider practical significance, not just statistical significance

### 3. Performance Optimization

- **Memory Management**: Monitor memory usage for large circuits
- **Parallel Processing**: Use batch processing for multiple circuits
- **Result Caching**: Cache results to avoid redundant computations
- **Profiling**: Profile performance bottlenecks

### 4. Result Interpretation

- **Context Matters**: Consider circuit characteristics when interpreting results
- **Multiple Metrics**: Look at multiple performance metrics, not just gate count
- **Practical Trade-offs**: Consider optimization time vs. quality trade-offs
- **Scenario-Specific**: Different scenarios may require different optimization strategies

## Troubleshooting

### Common Issues

#### 1. Import Errors

```python
# Ensure proper path setup
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
```

#### 2. Memory Issues

```python
# For large circuits, monitor memory usage
import psutil
import os

process = psutil.Process(os.getpid())
print(f"Memory usage: {process.memory_info().rss / 1024 / 1024:.1f} MB")
```

#### 3. Performance Issues

```python
# Use fallback options for faster execution
from src.performance_comparison import PerformanceComparisonEngine

engine = PerformanceComparisonEngine(
    enable_memory_monitoring=False,  # Disable for speed
    cache_results=True  # Enable caching
)
```

#### 4. Statistical Issues

```python
# Handle insufficient data gracefully
analyzer = StatisticalAnalyzer(min_sample_size=3)

# Check data before analysis
if len(data) >= analyzer.min_sample_size:
    result = analyzer.test_significance(group1, group2)
else:
    print("Insufficient data for statistical analysis")
```

### Debug Mode

```python
# Enable verbose output for debugging
import sim_fusion

optimized, stats = sim_fusion.sim_fusion_with_stats(circuit, verbose=True)

# Performance comparison with debugging
engine = PerformanceComparisonEngine()
result = engine.compare_optimization_methods(circuit, verbose=True, iterations=1)
```

## Integration Examples

### Jupyter Notebook Workflow

```python
# In a Jupyter notebook for interactive analysis
%matplotlib inline

import matplotlib.pyplot as plt
from src.performance_comparison import PerformanceComparisonEngine
from src.benchmark_circuits import BenchmarkCircuitGenerator

# Generate circuits
generator = BenchmarkCircuitGenerator()
circuits = generator.generate_circuit_suite(circuits_per_type=2)

# Run comparison
engine = PerformanceComparisonEngine()
results = engine.run_batch_comparison(circuits, iterations=3)

# Visualize results
sim_reductions = [r['sim_fusion_metrics'].gate_reduction_percent for r in results]
qibo_reductions = [r['qibo_fusion_metrics'].gate_reduction_percent for r in results]

plt.figure(figsize=(10, 6))
plt.scatter(sim_reductions, qibo_reductions)
plt.xlabel('Sim-Fusion Gate Reduction (%)')
plt.ylabel('Qibo Fusion Gate Reduction (%)')
plt.title('Optimization Method Comparison')
plt.plot([0, max(sim_reductions + qibo_reductions)],
         [0, max(sim_reductions + qibo_reductions)], 'r--')  # Diagonal
plt.show()
```

### Continuous Integration

```python
# CI testing script
def test_performance_regression():
    """Test for performance regressions."""
    generator = BenchmarkCircuitGenerator()
    test_circuits = [
        generator.create_bell_state(2),
        generator.create_redundant_circuit(3, "medium"),
        generator.create_qft_circuit(3)
    ]

    engine = PerformanceComparisonEngine()
    results = engine.run_batch_comparison(test_circuits, iterations=3)

    # Check for regressions
    sim_improvements = [r['sim_fusion_metrics'].gate_reduction_percent for r in results]
    avg_improvement = sum(sim_improvements) / len(sim_improvements)

    if avg_improvement < 10.0:  # Threshold
        raise AssertionError(f"Performance regression detected: {avg_improvement:.1f}%")

    print(f"Performance test passed: {avg_improvement:.1f}% average improvement")
```

## API Reference

### Core Functions

#### sim_fusion Module

- `sim_fusion(circuit, return_stats=False, verbose=False, fallback=True)`
- `quick_sim_fusion(circuit)`
- `sim_fusion_with_stats(circuit, verbose=True)`
- `analyze_optimization(circuit)`

#### PerformanceComparisonEngine

- `compare_optimization_methods(circuit, verbose=False, iterations=3)`
- `run_batch_comparison(circuits, iterations=3, parallel=False)`

#### StatisticalAnalyzer

- `summarize_metrics(data)`
- `test_significance(group1, group2, test_type=StatisticalTest.T_TEST)`
- `analyze_trend(values, x_values=None)`
- `comprehensive_analysis(sim_fusion_data, qibo_fusion_data)`

#### ReportGenerator

- `generate_comprehensive_report(analysis_results, formats=None)`
- `generate_summary_report(analysis_results, format='markdown')`

#### StrategyRecommender

- `recommend_optimization_method(characteristics, scenario, priorities=None)`
- `get_recommendation_summary(characteristics, scenario)`
- `update_historical_data(characteristics, method, performance_results)`

### Data Classes

#### PerformanceMetrics

- `method`: Optimization method name
- `original_gates`: Original gate count
- `optimized_gates`: Optimized gate count
- `gate_reduction`: Number of gates reduced
- `gate_reduction_percent`: Percentage of gates reduced
- `optimization_time`: Time taken for optimization
- `efficiency_score`: Optimization efficiency metric

#### SimFusionStats

- Enhanced statistics including memory usage, TKET steps completed, circuit size
- Various performance ratios and improvement scores
- Optimization type classification

#### Recommendation

- `method`: Recommended optimization method
- `confidence`: Confidence level (HIGH, MEDIUM, LOW, VERY_LOW)
- `reasoning`: Explanation for recommendation
- `expected_benefits`: List of expected benefits
- `potential_drawbacks`: List of potential drawbacks
- `performance_prediction`: Predicted performance metrics

## Contributing

### Development Setup

```bash
# Clone repository
git clone <repository_url>
cd tketqibo

# Install dependencies
pip install -r requirements.txt

# Run tests
python tests/test_performance_comparison.py

# Run quick test
python quick_test.py
```

### Adding New Features

1. **New Circuit Types**: Extend `BenchmarkCircuitGenerator`
2. **New Metrics**: Add to `PerformanceMetrics` class
3. **New Analysis Methods**: Extend `StatisticalAnalyzer`
4. **New Report Formats**: Extend `ReportGenerator`

### Code Style

- Follow PEP 8 style guidelines
- Use type hints where appropriate
- Include docstrings for all public functions
- Add unit tests for new features

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

- **Documentation**: Check this guide and API reference
- **Issues**: Report bugs on the project issue tracker
- **Discussions**: Use project discussions for questions
- **Examples**: See `examples/` directory for more usage examples

## Changelog

### Version 1.0.0

- Initial release of Sim-Fusion Performance Comparison Framework
- Benchmark circuit generation
- Performance comparison engine
- Statistical analysis framework
- Report generation system
- Strategy recommendation system
- Comprehensive test suite
- Documentation and examples