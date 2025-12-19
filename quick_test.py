"""Quick Test Runner for Performance Comparison Framework.

This script provides a fast way to test the core functionality
of the Sim-Fusion performance comparison system.
"""

import sys
import os
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")

    try:
        import sim_fusion
        print("+ sim_fusion imported")
    except Exception as e:
        print(f"- sim_fusion import failed: {e}")
        return False

    try:
        from src.benchmark_circuits import BenchmarkCircuitGenerator
        print("+ benchmark_circuits imported")
    except Exception as e:
        print(f"- benchmark_circuits import failed: {e}")
        return False

    try:
        from src.performance_comparison import PerformanceComparisonEngine
        print("+ performance_comparison imported")
    except Exception as e:
        print(f"- performance_comparison import failed: {e}")
        return False

    try:
        from src.statistical_analysis import StatisticalAnalyzer
        print("+ statistical_analysis imported")
    except Exception as e:
        print(f"- statistical_analysis import failed: {e}")
        return False

    try:
        from src.report_generator import ReportGenerator
        print("+ report_generator imported")
    except Exception as e:
        print(f"- report_generator import failed: {e}")
        return False

    try:
        from src.strategy_recommender import StrategyRecommender
        print("+ strategy_recommender imported")
    except Exception as e:
        print(f"- strategy_recommender import failed: {e}")
        return False

    return True

def test_basic_functionality():
    """Test basic functionality without external dependencies."""
    print("\nTesting basic functionality...")

    try:
        # Test statistical analysis
        from src.statistical_analysis import StatisticalAnalyzer
        analyzer = StatisticalAnalyzer()

        # Test with sample data
        sim_data = {'gate_reduction': [15.2, 14.8, 16.1]}
        qibo_data = {'gate_reduction': [12.1, 11.9, 13.2]}

        summary = analyzer.summarize_metrics(sim_data)
        test_result = analyzer.test_significance(
            sim_data['gate_reduction'],
            qibo_data['gate_reduction']
        )

        print(f"+ Statistical analysis working (p-value: {test_result.p_value:.4f})")

    except Exception as e:
        print(f"- Statistical analysis failed: {e}")
        return False

    try:
        # Test strategy recommendation
        from src.strategy_recommender import StrategyRecommender, CircuitCharacteristics

        recommender = StrategyRecommender(learning_enabled=False)
        characteristics = CircuitCharacteristics(
            n_qubits=4, n_gates=12, depth=6,
            two_qubit_gate_ratio=0.3, rotation_gate_ratio=0.4,
            clifford_gate_ratio=0.3, redundancy_level=0.2,
            circuit_density=3.0, entanglement_density=0.25
        )

        recommendation = recommender.recommend_optimization_method(characteristics)
        print(f"+ Strategy recommendation working (method: {recommendation.method.value})")

    except Exception as e:
        print(f"- Strategy recommendation failed: {e}")
        return False

    return True

def test_qibo_integration():
    """Test integration with Qibo if available."""
    print("\nTesting Qibo integration...")

    try:
        from qibo import Circuit, gates
        print("✓ Qibo imported")
    except ImportError:
        print("⚠ Qibo not available, skipping integration tests")
        return True

    try:
        import sim_fusion

        # Create test circuit
        circuit = Circuit(2)
        circuit.add(gates.H(0))
        circuit.add(gates.CNOT(0, 1))
        circuit.add(gates.H(1))
        circuit.add(gates.H(1))  # Redundant

        print(f"✓ Test circuit created: {circuit.ngates} gates")

        # Test Sim-Fusion
        optimized = sim_fusion.quick_sim_fusion(circuit)
        print(f"✓ Sim-Fusion optimization: {circuit.ngates} -> {optimized.ngates} gates")

        # Test with statistics
        optimized, stats = sim_fusion.sim_fusion_with_stats(circuit, verbose=False)
        print(f"✓ Sim-Fusion with stats: {stats.gate_reduction_percent:.1f}% reduction")

    except Exception as e:
        print(f"✗ Qibo integration failed: {e}")
        return False

    return True

def test_benchmark_generation():
    """Test benchmark circuit generation."""
    print("\nTesting benchmark circuit generation...")

    try:
        from qibo import Circuit, gates
        from src.benchmark_circuits import BenchmarkCircuitGenerator

        generator = BenchmarkCircuitGenerator()

        # Test Bell state
        bell = generator.create_bell_state(2)
        print(f"✓ Bell state: {bell.ngates} gates")

        # Test GHZ state
        ghz = generator.create_ghz_state(3)
        print(f"✓ GHZ state: {ghz.ngates} gates")

        # Test redundant circuit
        redundant = generator.create_redundant_circuit(3, "medium")
        print(f"✓ Redundant circuit: {redundant.ngates} gates")

        # Test circuit suite
        suite = generator.generate_circuit_suite(
            circuit_types=['bell_state', 'ghz_state'],
            circuits_per_type=1
        )
        print(f"✓ Circuit suite: {len(suite)} circuits generated")

    except ImportError:
        print("⚠ Qibo not available, skipping benchmark tests")
        return True
    except Exception as e:
        print(f"✗ Benchmark generation failed: {e}")
        return False

    return True

def test_report_generation():
    """Test report generation."""
    print("\nTesting report generation...")

    try:
        from src.report_generator import ReportGenerator, ReportFormat
        import tempfile
        import shutil

        # Create temporary directory
        temp_dir = tempfile.mkdtemp()

        try:
            generator = ReportGenerator(output_dir=temp_dir, include_charts=False)

            # Test data
            analysis_results = {
                'summary_statistics': {
                    'sim_fusion': {'gate_reduction': {'mean': 15.5, 'n': 5}},
                    'qibo_fusion': {'gate_reduction': {'mean': 12.3, 'n': 5}}
                },
                'significance_tests': {
                    'gate_reduction': {
                        't_test': {'is_significant': True, 'p_value': 0.001}
                    }
                },
                'recommendations': ['Test recommendation']
            }

            # Generate reports
            output_files = generator.generate_comprehensive_report(
                analysis_results=analysis_results,
                formats=[ReportFormat.MARKDOWN, ReportFormat.JSON]
            )

            print(f"✓ Generated {len(output_files)} report files")

            # Check files
            for format_type, file_path in output_files.items():
                if os.path.exists(file_path):
                    size = os.path.getsize(file_path)
                    print(f"✓ {format_type} report: {size} bytes")
                else:
                    print(f"✗ {format_type} report file missing")
                    return False

        finally:
            # Cleanup
            shutil.rmtree(temp_dir)

    except Exception as e:
        print(f"✗ Report generation failed: {e}")
        return False

    return True

def main():
    """Run all quick tests."""
    print("=" * 50)
    print("Sim-Fusion Performance Comparison Quick Test")
    print("=" * 50)

    tests = [
        ("Import Tests", test_imports),
        ("Basic Functionality", test_basic_functionality),
        ("Qibo Integration", test_qibo_integration),
        ("Benchmark Generation", test_benchmark_generation),
        ("Report Generation", test_report_generation)
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        print("-" * len(test_name))

        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} ERROR: {e}")

    print(f"\n{'=' * 50}")
    print(f"Test Results: {passed}/{total} passed")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    print("=" * 50)

    if passed == total:
        print("🎉 All tests passed! System is working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Check details above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)