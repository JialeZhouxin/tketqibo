"""Comprehensive Performance Comparison Demo.

This script demonstrates the complete usage of the Sim-Fusion vs Qibo fusion
performance comparison framework with real quantum circuits.

Usage:
    python examples/performance_comparison_demo.py [--quick] [--full] [--reports]

Options:
    --quick   Run a quick demo with minimal circuits
    --full    Run comprehensive demo with many circuit types
    --reports Generate detailed reports
"""

import sys
import os
import argparse
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from qibo import Circuit, gates
    QIBO_AVAILABLE = True
except ImportError:
    QIBO_AVAILABLE = False
    print("Warning: Qibo not available. Some features will be limited.")

try:
    import sim_fusion
    SIM_FUSION_AVAILABLE = True
except ImportError:
    SIM_FUSION_AVAILABLE = False
    print("Warning: Sim-Fusion not available.")

try:
    from src.benchmark_circuits import BenchmarkCircuitGenerator
    BENCHMARK_AVAILABLE = True
except ImportError:
    BENCHMARK_AVAILABLE = False

try:
    from src.performance_comparison import PerformanceComparisonEngine
    COMPARISON_AVAILABLE = True
except ImportError:
    COMPARISON_AVAILABLE = False

try:
    from src.statistical_analysis import StatisticalAnalyzer
    ANALYSIS_AVAILABLE = True
except ImportError:
    ANALYSIS_AVAILABLE = False

try:
    from src.report_generator import ReportGenerator, ReportFormat
    REPORT_AVAILABLE = True
except ImportError:
    REPORT_AVAILABLE = False

try:
    from src.strategy_recommender import StrategyRecommender
    RECOMMENDER_AVAILABLE = True
except ImportError:
    RECOMMENDER_AVAILABLE = False


def create_demo_circuits():
    """Create demonstration circuits with varying characteristics."""
    if not BENCHMARK_AVAILABLE or not QIBO_AVAILABLE:
        print("Cannot create demo circuits without required dependencies.")
        return []

    generator = BenchmarkCircuitGenerator()

    circuits = []

    # Small Bell states
    circuits.append(generator.create_bell_state(2))
    circuits.append(generator.create_bell_state(3))

    # Medium GHZ states
    circuits.append(generator.create_ghz_state(4))
    circuits.append(generator.create_ghz_state(5))

    # QFT circuits
    circuits.append(generator.create_qft_circuit(3))
    circuits.append(generator.create_qft_circuit(4))

    # Redundant circuits (good for testing optimization)
    circuits.append(generator.create_redundant_circuit(3, "medium"))
    circuits.append(generator.create_redundant_circuit(4, "high"))

    # Random circuits
    circuits.append(generator.create_random_clifford_circuit(4, 15))
    circuits.append(generator.create_random_rotation_circuit(4, 20))

    # Mixed algorithm circuits
    circuits.append(generator.create_mixed_algorithm_circuit(5))

    return circuits


def create_custom_circuit():
    """Create a custom circuit with specific characteristics."""
    if not QIBO_AVAILABLE:
        return None

    # Create a circuit with known redundant operations
    circuit = Circuit(4)

    # Initial state preparation
    circuit.add(gates.H(0))
    circuit.add(gates.H(1))

    # Entanglement layer
    circuit.add(gates.CNOT(0, 1))
    circuit.add(gates.CNOT(1, 2))
    circuit.add(gates.CNOT(2, 3))

    # Add some redundant operations (should be optimized away)
    circuit.add(gates.X(0))
    circuit.add(gates.X(0))  # X*X = I
    circuit.add(gates.H(2))
    circuit.add(gates.H(2))  # H*H = I

    # Add some rotation gates
    circuit.add(gates.RX(0.5, 0))
    circuit.add(gates.RY(0.3, 1))
    circuit.add(gates.RZ(0.7, 2))

    # Final entanglement
    circuit.add(gates.CNOT(0, 3))
    circuit.add(gates.CNOT(1, 3))

    return circuit


def demo_basic_optimization():
    """Demonstrate basic Sim-Fusion optimization."""
    print("\n" + "="*60)
    print("BASIC SIM-FUSION OPTIMIZATION DEMO")
    print("="*60)

    if not SIM_FUSION_AVAILABLE or not QIBO_AVAILABLE:
        print("Cannot run demo: Required dependencies not available.")
        return

    # Create a simple test circuit
    circuit = create_custom_circuit()
    if circuit is None:
        return

    print(f"Original circuit:")
    print(f"  Qubits: {circuit.nqubits}")
    print(f"  Gates: {circuit.ngates}")
    try:
        print(f"  Depth: {circuit.depth()}")
    except:
        print(f"  Depth: N/A")

    # Run Sim-Fusion optimization
    print(f"\nRunning Sim-Fusion optimization...")
    start_time = time.time()

    optimized = sim_fusion.quick_sim_fusion(circuit)

    optimization_time = time.time() - start_time

    print(f"Optimization completed in {optimization_time:.3f} seconds")
    print(f"Optimized circuit:")
    print(f"  Qubits: {optimized.nqubits}")
    print(f"  Gates: {optimized.ngates}")
    try:
        print(f"  Depth: {optimized.depth()}")
    except:
        print(f"  Depth: N/A")

    # Calculate improvements
    gate_reduction = circuit.ngates - optimized.ngates
    gate_reduction_percent = (gate_reduction / circuit.ngates) * 100

    print(f"\nOptimization Results:")
    print(f"  Gate reduction: {gate_reduction} gates ({gate_reduction_percent:.1f}%)")
    print(f"  Optimization time: {optimization_time:.3f} seconds")

    # Run with detailed statistics
    print(f"\nRunning with detailed statistics...")
    optimized, stats = sim_fusion.sim_fusion_with_stats(circuit, verbose=False)

    print(f"Detailed Statistics:")
    print(f"  Gate reduction: {stats.gate_reduction_percent:.1f}%")
    print(f"  Optimization efficiency: {stats.efficiency_score:.1f}%/s")
    print(f"  Overall improvement score: {stats.overall_improvement_score:.1f}/100")
    print(f"  Optimization type: {stats.optimization_type}")


def demo_performance_comparison(circuits, iterations=3):
    """Demonstrate performance comparison between methods."""
    print("\n" + "="*60)
    print("PERFORMANCE COMPARISON DEMO")
    print("="*60)

    if not COMPARISON_AVAILABLE or not SIM_FUSION_AVAILABLE or not QIBO_AVAILABLE:
        print("Cannot run demo: Required dependencies not available.")
        return None

    if not circuits:
        print("No circuits provided for comparison.")
        return None

    # Limit circuits for demo
    demo_circuits = circuits[:min(5, len(circuits))]
    print(f"Testing on {len(demo_circuits)} circuits with {iterations} iterations each")

    # Initialize comparison engine
    engine = PerformanceComparisonEngine()

    # Run batch comparison
    start_time = time.time()
    results = engine.run_batch_comparison(demo_circuits, iterations=iterations)
    total_time = time.time() - start_time

    print(f"\nComparison completed in {total_time:.2f} seconds")

    # Analyze results
    sim_fusion_wins = sum(1 for r in results if r['winner'] == 'sim_fusion')
    qibo_fusion_wins = sum(1 for r in results if r['winner'] == 'qibo_fusion')
    ties = sum(1 for r in results if r['winner'] == 'tie')

    print(f"\nWin Summary:")
    print(f"  Sim-Fusion wins: {sim_fusion_wins}")
    print(f"  Qibo Fusion wins: {qibo_fusion_wins}")
    print(f"  Ties: {ties}")

    # Calculate average improvements
    sim_improvements = [r['sim_fusion_metrics'].gate_reduction_percent for r in results if r['sim_fusion_metrics']]
    qibo_improvements = [r['qibo_fusion_metrics'].gate_reduction_percent for r in results if r['qibo_fusion_metrics']]

    if sim_improvements and qibo_improvements:
        avg_sim_improvement = sum(sim_improvements) / len(sim_improvements)
        avg_qibo_improvement = sum(qibo_improvements) / len(qibo_improvements)

        print(f"\nAverage Gate Reduction:")
        print(f"  Sim-Fusion: {avg_sim_improvement:.1f}%")
        print(f"  Qibo Fusion: {avg_qibo_improvement:.1f}%")

        # Calculate average optimization times
        sim_times = [r['sim_fusion_metrics'].optimization_time for r in results if r['sim_fusion_metrics']]
        qibo_times = [r['qibo_fusion_metrics'].optimization_time for r in results if r['qibo_fusion_metrics']]

        if sim_times and qibo_times:
            avg_sim_time = sum(sim_times) / len(sim_times)
            avg_qibo_time = sum(qibo_times) / len(qibo_times)

            print(f"\nAverage Optimization Time:")
            print(f"  Sim-Fusion: {avg_sim_time:.3f} seconds")
            print(f"  Qibo Fusion: {avg_qibo_time:.3f} seconds")

    return results


def demo_statistical_analysis(results):
    """Demonstrate statistical analysis of performance data."""
    print("\n" + "="*60)
    print("STATISTICAL ANALYSIS DEMO")
    print("="*60)

    if not ANALYSIS_AVAILABLE or not results:
        print("Cannot run demo: Required dependencies or data not available.")
        return None

    # Extract performance data
    sim_fusion_data = {
        'gate_reduction': [r['sim_fusion_metrics'].gate_reduction_percent
                         for r in results if r['sim_fusion_metrics']],
        'optimization_time': [r['sim_fusion_metrics'].optimization_time
                            for r in results if r['sim_fusion_metrics']],
        'efficiency_score': [getattr(r['sim_fusion_metrics'], 'efficiency_score', 0)
                           for r in results if r['sim_fusion_metrics']]
    }

    qibo_fusion_data = {
        'gate_reduction': [r['qibo_fusion_metrics'].gate_reduction_percent
                         for r in results if r['qibo_fusion_metrics']],
        'optimization_time': [r['qibo_fusion_metrics'].optimization_time
                            for r in results if r['qibo_fusion_metrics']]
    }

    # Initialize analyzer
    analyzer = StatisticalAnalyzer()

    # Generate statistical summaries
    print("Generating statistical summaries...")
    sim_summary = analyzer.summarize_metrics(sim_fusion_data)
    qibo_summary = analyzer.summarize_metrics(qibo_fusion_data)

    print(f"\nSim-Fusion Summary Statistics:")
    for metric, summary in sim_summary.items():
        print(f"  {metric}:")
        print(f"    Mean: {summary.mean:.3f}")
        print(f"    Std Dev: {summary.stdev:.3f}")
        print(f"    Range: [{summary.min_val:.3f}, {summary.max_val:.3f}]")
        print(f"    CV: {summary.coefficient_of_variation():.3f}")

    print(f"\nQibo Fusion Summary Statistics:")
    for metric, summary in qibo_summary.items():
        print(f"  {metric}:")
        print(f"    Mean: {summary.mean:.3f}")
        print(f"    Std Dev: {summary.stdev:.3f}")
        print(f"    Range: [{summary.min_val:.3f}, {summary.max_val:.3f}]")
        print(f"    CV: {summary.coefficient_of_variation():.3f}")

    # Run significance tests
    print(f"\nSignificance Testing:")
    common_metrics = set(sim_fusion_data.keys()) & set(qibo_fusion_data.keys())

    for metric in common_metrics:
        if len(sim_fusion_data[metric]) >= 3 and len(qibo_fusion_data[metric]) >= 3:
            test_result = analyzer.test_significance(
                sim_fusion_data[metric], qibo_fusion_data[metric]
            )
            print(f"  {metric}:")
            print(f"    Significant difference: {test_result.is_significant}")
            print(f"    P-value: {test_result.p_value:.6f}")
            print(f"    Effect size: {test_result.effect_size:.3f}")

    # Comprehensive analysis
    print(f"\nRunning comprehensive analysis...")
    comprehensive = analyzer.comprehensive_analysis(sim_fusion_data, qibo_fusion_data)

    print(f"Recommendations:")
    for i, rec in enumerate(comprehensive['recommendations'], 1):
        print(f"  {i}. {rec}")

    return comprehensive


def demo_strategy_recommendation(circuits):
    """Demonstrate strategy recommendation system."""
    print("\n" + "="*60)
    print("STRATEGY RECOMMENDATION DEMO")
    print("="*60)

    if not RECOMMENDER_AVAILABLE or not BENCHMARK_AVAILABLE:
        print("Cannot run demo: Required dependencies not available.")
        return

    if not circuits:
        print("No circuits provided for recommendation.")
        return

    # Initialize recommender
    recommender = StrategyRecommender(learning_enabled=False)

    # Analyze different circuit types
    generator = BenchmarkCircuitGenerator()

    test_cases = [
        ("Small Bell State", generator.create_bell_state(2)),
        ("Medium Redundant Circuit", generator.create_redundant_circuit(4, "high")),
        ("Large Random Circuit", generator.create_random_clifford_circuit(6, 25)),
        ("Rotation-Heavy Circuit", generator.create_random_rotation_circuit(5, 20))
    ]

    from src.strategy_recommender import UsageScenario

    scenarios = [
        UsageScenario.SIMULATION,
        UsageScenario.REAL_TIME_APPLICATIONS,
        UsageScenario.LARGE_SCALE_PROBLEMS,
        UsageScenario.HARDWARE_EXECUTION
    ]

    for circuit_name, circuit in test_cases[:3]:  # Limit demo size
        print(f"\nAnalyzing {circuit_name}:")

        # Get circuit characteristics
        characteristics_data = generator.get_circuit_characteristics(circuit)
        characteristics = recommender.analyze_circuit_characteristics(characteristics_data)

        print(f"  Circuit characteristics:")
        print(f"    Qubits: {characteristics.n_qubits}")
        print(f"    Gates: {characteristics.n_gates}")
        print(f"    Two-qubit gate ratio: {characteristics.two_qubit_gate_ratio:.2f}")
        print(f"    Redundancy level: {characteristics.redundancy_level:.2f}")

        # Get recommendations for different scenarios
        for scenario in scenarios[:2]:  # Limit scenarios for demo
            recommendation = recommender.recommend_optimization_method(
                characteristics, scenario
            )
            print(f"    {scenario.value.title()}: {recommendation.method.value} "
                  f"(confidence: {recommendation.confidence.value})")


def demo_report_generation(analysis_results, comparison_results):
    """Demonstrate report generation."""
    print("\n" + "="*60)
    print("REPORT GENERATION DEMO")
    print("="*60)

    if not REPORT_AVAILABLE:
        print("Cannot run demo: Report generator not available.")
        return

    # Create demo directory for reports
    report_dir = Path("demo_reports")
    report_dir.mkdir(exist_ok=True)

    # Prepare data for reports
    if analysis_results:
        report_data = analysis_results
    elif comparison_results:
        # Create minimal analysis data from comparison results
        sim_fusion_data = {
            'gate_reduction': [r['sim_fusion_metrics'].gate_reduction_percent
                             for r in comparison_results if r['sim_fusion_metrics']],
            'optimization_time': [r['sim_fusion_metrics'].optimization_time
                                for r in comparison_results if r['sim_fusion_metrics']]
        }
        qibo_fusion_data = {
            'gate_reduction': [r['qibo_fusion_metrics'].gate_reduction_percent
                             for r in comparison_results if r['qibo_fusion_metrics']],
            'optimization_time': [r['qibo_fusion_metrics'].optimization_time
                                for r in comparison_results if r['qibo_fusion_metrics']]
        }

        if ANALYSIS_AVAILABLE:
            analyzer = StatisticalAnalyzer()
            report_data = analyzer.comprehensive_analysis(sim_fusion_data, qibo_fusion_data)
        else:
            # Create minimal report data
            report_data = {
                'summary_statistics': {},
                'significance_tests': {},
                'recommendations': ['Demo recommendation']
            }
    else:
        print("No data available for report generation.")
        return

    # Generate reports
    generator = ReportGenerator(output_dir=str(report_dir), include_charts=False)

    formats = [ReportFormat.MARKDOWN, ReportFormat.JSON]
    print(f"Generating reports in {formats} formats...")

    try:
        output_files = generator.generate_comprehensive_report(
            analysis_results=report_data,
            formats=formats
        )

        print(f"Reports generated successfully:")
        for format_type, file_path in output_files.items():
            if os.path.exists(file_path):
                size = os.path.getsize(file_path)
                print(f"  {format_type}: {file_path} ({size} bytes)")
            else:
                print(f"  {format_type}: Failed to generate")

    except Exception as e:
        print(f"Report generation failed: {e}")


def main():
    """Main demo function."""
    parser = argparse.ArgumentParser(description="Sim-Fusion Performance Comparison Demo")
    parser.add_argument("--quick", action="store_true", help="Run quick demo")
    parser.add_argument("--full", action="store_true", help="Run full comprehensive demo")
    parser.add_argument("--reports", action="store_true", help="Generate detailed reports")
    args = parser.parse_args()

    print("Sim-Fusion Performance Comparison Framework Demo")
    print("=" * 60)

    # Check dependencies
    print("Checking dependencies...")
    dependencies = {
        "Qibo": QIBO_AVAILABLE,
        "Sim-Fusion": SIM_FUSION_AVAILABLE,
        "Benchmark Circuits": BENCHMARK_AVAILABLE,
        "Performance Comparison": COMPARISON_AVAILABLE,
        "Statistical Analysis": ANALYSIS_AVAILABLE,
        "Report Generation": REPORT_AVAILABLE,
        "Strategy Recommender": RECOMMENDER_AVAILABLE
    }

    for dep, available in dependencies.items():
        status = "Available" if available else "Not Available"
        print(f"  {dep}: {status}")

    missing_deps = [name for name, available in dependencies.items() if not available]
    if missing_deps:
        print(f"\nWarning: Missing dependencies: {', '.join(missing_deps)}")
        print("Some features may be limited.")

    # Basic optimization demo (always run)
    demo_basic_optimization()

    # Create circuits for further demos
    circuits = create_demo_circuits()
    print(f"\nCreated {len(circuits)} demo circuits")

    # Performance comparison demo
    iterations = 1 if args.quick else 3
    comparison_results = demo_performance_comparison(circuits, iterations)

    # Statistical analysis demo
    analysis_results = None
    if comparison_results and ANALYSIS_AVAILABLE:
        analysis_results = demo_statistical_analysis(comparison_results)

    # Strategy recommendation demo
    if not args.quick:
        demo_strategy_recommendation(circuits)

    # Report generation demo
    if args.reports:
        demo_report_generation(analysis_results, comparison_results)

    print("\n" + "="*60)
    print("DEMO COMPLETED")
    print("="*60)

    if args.reports:
        print("Check the 'demo_reports' directory for generated reports.")

    print("\nTo learn more:")
    print("  - Read the user guide: docs/performance_comparison_guide.md")
    print("  - Check API documentation: docs/api_reference.md")
    print("  - Run comprehensive tests: python tests/test_performance_comparison.py")


if __name__ == "__main__":
    main()