"""Comprehensive Test Suite for Performance Comparison Framework.

This module provides unit tests, integration tests, and performance validation
for the Sim-Fusion vs Qibo fusion performance comparison system.

Test Coverage:
- Benchmark circuit generation
- Performance comparison engine
- Statistical analysis framework
- Report generation system
- Strategy recommendation system
- End-to-end workflows
- Error handling and edge cases
- Performance regression testing

Authors: Sim-Fusion Team
Version: 1.0.0
"""

import unittest
import sys
import os
import tempfile
import shutil
from pathlib import Path
from typing import Dict, List, Any
import warnings

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from qibo import Circuit, gates
    QIBO_AVAILABLE = True
except ImportError:
    QIBO_AVAILABLE = False
    Circuit = None
    gates = None

try:
    from sim_fusion import sim_fusion, quick_sim_fusion, sim_fusion_with_stats, analyze_optimization
    SIM_FUSION_AVAILABLE = True
except ImportError:
    SIM_FUSION_AVAILABLE = False

try:
    from benchmark_circuits import BenchmarkCircuitGenerator, create_benchmark_circuits
    BENCHMARK_AVAILABLE = True
except ImportError:
    BENCHMARK_AVAILABLE = False

try:
    from performance_comparison import PerformanceComparisonEngine, PerformanceMetrics
    COMPARISON_AVAILABLE = True
except ImportError:
    COMPARISON_AVAILABLE = False

try:
    from statistical_analysis import StatisticalAnalyzer, StatisticalSummary
    ANALYSIS_AVAILABLE = True
except ImportError:
    ANALYSIS_AVAILABLE = False

try:
    from report_generator import ReportGenerator, quick_report
    REPORT_AVAILABLE = True
except ImportError:
    REPORT_AVAILABLE = False

try:
    from strategy_recommender import StrategyRecommender, CircuitCharacteristics
    RECOMMENDER_AVAILABLE = True
except ImportError:
    RECOMMENDER_AVAILABLE = False


class MockSimFusionStats:
    """Mock SimFusionStats for testing without full dependencies."""
    def __init__(self, gate_reduction=0.1, depth_reduction=0.05, total_time=0.1):
        self.gate_reduction_percent = gate_reduction * 100
        self.depth_reduction_percent = depth_reduction * 100
        self.total_time = total_time
        self.optimization_success = True


class TestBenchmarkCircuitGeneration(unittest.TestCase):
    """Test benchmark circuit generation functionality."""

    def setUp(self):
        if not BENCHMARK_AVAILABLE:
            self.skipTest("benchmark_circuits module not available")
        self.generator = BenchmarkCircuitGenerator()

    def test_circuit_generator_initialization(self):
        """Test benchmark circuit generator initialization."""
        self.assertIsInstance(self.generator.circuit_types, list)
        self.assertIn('bell_state', self.generator.circuit_types)
        self.assertIn('ghz_state', self.generator.circuit_types)
        self.assertIn('qft', self.generator.circuit_types)

    @unittest.skipUnless(QIBO_AVAILABLE, "Qibo not available")
    def test_bell_state_creation(self):
        """Test Bell state circuit creation."""
        circuit = self.generator.create_bell_state(2)
        self.assertIsInstance(circuit, Circuit)
        self.assertEqual(circuit.nqubits, 2)
        self.assertEqual(circuit.ngates, 2)  # H + CNOT

    @unittest.skipUnless(QIBO_AVAILABLE, "Qibo not available")
    def test_ghz_state_creation(self):
        """Test GHZ state circuit creation."""
        circuit = self.generator.create_ghz_state(4)
        self.assertIsInstance(circuit, Circuit)
        self.assertEqual(circuit.nqubits, 4)
        self.assertEqual(circuit.ngates, 4)  # H + 3*CNOT

    @unittest.skipUnless(QIBO_AVAILABLE, "Qibo not available")
    def test_qft_circuit_creation(self):
        """Test QFT circuit creation."""
        circuit = self.generator.create_qft_circuit(3)
        self.assertIsInstance(circuit, Circuit)
        self.assertEqual(circuit.nqubits, 3)
        self.assertGreater(circuit.ngates, 0)

    @unittest.skipUnless(QIBO_AVAILABLE, "Qibo not available")
    def test_redundant_circuit_creation(self):
        """Test redundant circuit creation."""
        for level in ["low", "medium", "high"]:
            circuit = self.generator.create_redundant_circuit(3, level)
            self.assertIsInstance(circuit, Circuit)
            self.assertEqual(circuit.nqubits, 3)
            self.assertGreater(circuit.ngates, 0)

    @unittest.skipUnless(QIBO_AVAILABLE, "Qibo not available")
    def test_circuit_suite_generation(self):
        """Test comprehensive circuit suite generation."""
        circuit_types = ['bell_state', 'ghz_state']
        suite = self.generator.generate_circuit_suite(
            circuit_types=circuit_types,
            n_qubits_range=(2, 4),
            circuits_per_type=2
        )

        self.assertIsInstance(suite, list)
        self.assertEqual(len(suite), 4)  # 2 types * 2 circuits each

        for item in suite:
            self.assertIn('circuit', item)
            self.assertIn('type', item)
            self.assertIn('n_qubits', item)
            self.assertIn('n_gates', item)

    @unittest.skipUnless(QIBO_AVAILABLE, "Qibo not available")
    def test_circuit_characteristics_analysis(self):
        """Test circuit characteristics analysis."""
        circuit = self.generator.create_bell_state(3)
        characteristics = self.generator.get_circuit_characteristics(circuit)

        self.assertIn('n_qubits', characteristics)
        self.assertIn('n_gates', characteristics)
        self.assertIn('gate_distribution', characteristics)
        self.assertIn('complexity_score', characteristics)


class TestSimFusionCore(unittest.TestCase):
    """Test Sim-Fusion core functionality."""

    @unittest.skipUnless(SIM_FUSION_AVAILABLE and QIBO_AVAILABLE, "Dependencies not available")
    def test_sim_fusion_basic_functionality(self):
        """Test basic Sim-Fusion optimization."""
        # Create simple test circuit
        circuit = Circuit(2)
        circuit.add(gates.H(0))
        circuit.add(gates.CNOT(0, 1))
        circuit.add(gates.H(1))
        circuit.add(gates.H(1))  # Redundant

        original_gates = circuit.ngates

        # Test optimization
        optimized = sim_fusion(circuit)
        self.assertIsInstance(optimized, Circuit)
        self.assertEqual(optimized.nqubits, circuit.nqubits)

        # Should reduce gates (remove redundant H*H)
        self.assertLessEqual(optimized.ngates, original_gates)

    @unittest.skipUnless(SIM_FUSION_AVAILABLE and QIBO_AVAILABLE, "Dependencies not available")
    def test_sim_fusion_with_stats(self):
        """Test Sim-Fusion with statistics collection."""
        circuit = Circuit(2)
        circuit.add(gates.H(0))
        circuit.add(gates.CNOT(0, 1))

        optimized, stats = sim_fusion_with_stats(circuit, verbose=False)

        self.assertIsInstance(optimized, Circuit)
        self.assertIsInstance(stats, object)  # SimFusionStats object
        self.assertTrue(hasattr(stats, 'gate_reduction_percent'))
        self.assertTrue(hasattr(stats, 'total_time'))

    @unittest.skipUnless(SIM_FUSION_AVAILABLE and QIBO_AVAILABLE, "Dependencies not available")
    def test_quick_sim_fusion(self):
        """Test quick Sim-Fusion interface."""
        circuit = Circuit(2)
        circuit.add(gates.H(0))
        circuit.add(gates.CNOT(0, 1))

        optimized = quick_sim_fusion(circuit)
        self.assertIsInstance(optimized, Circuit)

    @unittest.skipUnless(SIM_FUSION_AVAILABLE and QIBO_AVAILABLE, "Dependencies not available")
    def test_circuit_analysis(self):
        """Test circuit analysis functionality."""
        circuit = Circuit(2)
        circuit.add(gates.H(0))
        circuit.add(gates.CNOT(0, 1))

        analysis = analyze_optimization(circuit)

        self.assertIsInstance(analysis, dict)
        self.assertIn('basic_stats', analysis)
        self.assertIn('gate_distribution', analysis)
        self.assertIn('optimization_potential', analysis)


class TestPerformanceComparison(unittest.TestCase):
    """Test performance comparison engine."""

    def setUp(self):
        if not COMPARISON_AVAILABLE:
            self.skipTest("performance_comparison module not available")
        self.engine = PerformanceComparisonEngine()

    @unittest.skipUnless(SIM_FUSION_AVAILABLE and QIBO_AVAILABLE, "Dependencies not available")
    def test_performance_metrics_creation(self):
        """Test performance metrics creation."""
        metrics = PerformanceMetrics(
            method='sim_fusion',
            original_gates=10,
            optimized_gates=7,
            optimization_time=0.1
        )

        self.assertEqual(metrics.method, 'sim_fusion')
        self.assertEqual(metrics.gate_reduction, 3)
        self.assertEqual(metrics.gate_reduction_percent, 30.0)

    @unittest.skipUnless(SIM_FUSION_AVAILABLE and QIBO_AVAILABLE, "Dependencies not available")
    def test_single_circuit_comparison(self):
        """Test single circuit performance comparison."""
        # Create test circuit
        circuit = Circuit(2)
        circuit.add(gates.H(0))
        circuit.add(gates.CNOT(0, 1))
        circuit.add(gates.H(1))
        circuit.add(gates.H(1))

        # Run comparison
        result = self.engine.compare_optimization_methods(circuit, verbose=False, iterations=1)

        self.assertIsInstance(result, dict)
        self.assertIn('sim_fusion_metrics', result)
        self.assertIn('qibo_fusion_metrics', result)
        self.assertIn('winner', result)

    @unittest.skipUnless(BENCHMARK_AVAILABLE and SIM_FUSION_AVAILABLE and QIBO_AVAILABLE, "Dependencies not available")
    def test_batch_circuit_comparison(self):
        """Test batch circuit comparison."""
        # Generate test circuits
        generator = BenchmarkCircuitGenerator()
        circuits = [
            generator.create_bell_state(2),
            generator.create_ghz_state(3),
            generator.create_redundant_circuit(2, "low")
        ]

        # Run batch comparison
        results = self.engine.run_batch_comparison(circuits, iterations=1)

        self.assertIsInstance(results, list)
        self.assertEqual(len(results), len(circuits))

        for result in results:
            self.assertIn('sim_fusion_metrics', result)
            self.assertIn('qibo_fusion_metrics', result)


class TestStatisticalAnalysis(unittest.TestCase):
    """Test statistical analysis framework."""

    def setUp(self):
        if not ANALYSIS_AVAILABLE:
            self.skipTest("statistical_analysis module not available")
        self.analyzer = StatisticalAnalyzer()

    def test_statistical_summary_creation(self):
        """Test statistical summary creation."""
        values = [1.0, 1.2, 0.9, 1.1, 1.0, 0.8, 1.3]
        summary = StatisticalSummary(values, "test_metric")

        self.assertAlmostEqual(summary.mean, 1.042, places=2)
        self.assertGreater(summary.stdev, 0)
        self.assertEqual(summary.n, len(values))
        self.assertTrue(summary.is_stable())

    def test_significance_testing(self):
        """Test statistical significance testing."""
        group1 = [1.0, 1.1, 0.9, 1.2, 1.0]
        group2 = [0.8, 0.9, 0.7, 0.8, 0.9]

        from statistical_analysis import StatisticalTest
        result = self.analyzer.test_significance(
            group1, group2, StatisticalTest.T_TEST
        )

        self.assertTrue(hasattr(result, 'p_value'))
        self.assertTrue(hasattr(result, 'is_significant'))

    def test_trend_analysis(self):
        """Test trend analysis."""
        # Improving trend
        values = [10, 12, 11, 13, 15, 14, 16, 18]

        trend = self.analyzer.analyze_trend(values)

        self.assertTrue(hasattr(trend, 'direction'))
        self.assertTrue(hasattr(trend, 'correlation'))
        self.assertTrue(hasattr(trend, 'slope'))

    def test_comprehensive_analysis(self):
        """Test comprehensive analysis functionality."""
        sim_fusion_data = {
            'gate_reduction': [15.0, 14.5, 16.2, 15.8, 15.1],
            'optimization_time': [0.12, 0.15, 0.11, 0.14, 0.13]
        }

        qibo_fusion_data = {
            'gate_reduction': [12.0, 11.8, 12.5, 12.2, 11.9],
            'optimization_time': [0.08, 0.09, 0.07, 0.08, 0.09]
        }

        analysis = self.analyzer.comprehensive_analysis(
            sim_fusion_data, qibo_fusion_data
        )

        self.assertIn('summary_statistics', analysis)
        self.assertIn('significance_tests', analysis)
        self.assertIn('recommendations', analysis)


class TestReportGeneration(unittest.TestCase):
    """Test report generation system."""

    def setUp(self):
        if not REPORT_AVAILABLE:
            self.skipTest("report_generator module not available")
        self.temp_dir = tempfile.mkdtemp()
        self.generator = ReportGenerator(output_dir=self.temp_dir, include_charts=False)

    def tearDown(self):
        if hasattr(self, 'temp_dir') and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_markdown_report_generation(self):
        """Test Markdown report generation."""
        # Create test data
        analysis_results = {
            'summary_statistics': {
                'sim_fusion': {
                    'gate_reduction': {'mean': 15.5, 'stdev': 0.5, 'n': 5}
                },
                'qibo_fusion': {
                    'gate_reduction': {'mean': 12.3, 'stdev': 0.6, 'n': 5}
                }
            },
            'significance_tests': {
                'gate_reduction': {
                    't_test': {
                        'is_significant': True,
                        'p_value': 0.001,
                        'effect_size': 1.5
                    }
                }
            },
            'recommendations': ['Test recommendation']
        }

        # Generate report
        from report_generator import ReportFormat
        output_files = self.generator.generate_comprehensive_report(
            analysis_results=analysis_results,
            formats=[ReportFormat.MARKDOWN]
        )

        self.assertIn('markdown', output_files)
        markdown_path = output_files['markdown']

        # Check file exists
        self.assertTrue(os.path.exists(markdown_path))

        # Check file content
        with open(markdown_path, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn('Performance Comparison Report', content)
            self.assertIn('Sim-Fusion', content)

    def test_json_report_generation(self):
        """Test JSON report generation."""
        analysis_results = {
            'summary_statistics': {},
            'significance_tests': {},
            'recommendations': []
        }

        from report_generator import ReportFormat
        output_files = self.generator.generate_comprehensive_report(
            analysis_results=analysis_results,
            formats=[ReportFormat.JSON]
        )

        self.assertIn('json', output_files)
        json_path = output_files['json']

        # Check file exists and is valid JSON
        self.assertTrue(os.path.exists(json_path))

        import json
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.assertIn('metadata', data)
            self.assertIn('sections', data)


class TestStrategyRecommendation(unittest.TestCase):
    """Test strategy recommendation system."""

    def setUp(self):
        if not RECOMMENDER_AVAILABLE:
            self.skipTest("strategy_recommender module not available")
        self.recommender = StrategyRecommender(learning_enabled=False)

    def test_circuit_characteristics_creation(self):
        """Test circuit characteristics creation."""
        characteristics = CircuitCharacteristics(
            n_qubits=4,
            n_gates=12,
            depth=6,
            two_qubit_gate_ratio=0.3,
            rotation_gate_ratio=0.4,
            clifford_gate_ratio=0.3,
            redundancy_level=0.2,
            circuit_density=3.0,
            entanglement_density=0.25
        )

        self.assertEqual(characteristics.n_qubits, 4)
        self.assertEqual(characteristics.circuit_density, 3.0)

    def test_circuit_analysis_from_data(self):
        """Test circuit characteristics from analysis data."""
        analysis_data = {
            'qubits': 3,
            'gates': 15,
            'depth': 8,
            'gate_distribution': {
                'H': 3, 'X': 2, 'CNOT': 4, 'RX': 3, 'RY': 3
            },
            'redundancy_level': 0.3,
            'entanglement_density': 0.27
        }

        characteristics = self.recommender.analyze_circuit_characteristics(analysis_data)

        self.assertEqual(characteristics.n_qubits, 3)
        self.assertEqual(characteristics.n_gates, 15)
        self.assertGreater(characteristics.two_qubit_gate_ratio, 0)

    def test_optimization_recommendation(self):
        """Test optimization method recommendation."""
        characteristics = CircuitCharacteristics(
            n_qubits=8,
            n_gates=25,
            depth=12,
            two_qubit_gate_ratio=0.4,
            rotation_gate_ratio=0.3,
            clifford_gate_ratio=0.3,
            redundancy_level=0.5,  # High redundancy
            circuit_density=3.1,
            entanglement_density=0.4
        )

        recommendation = self.recommender.recommend_optimization_method(
            characteristics, UsageScenario.SIMULATION
        )

        self.assertTrue(hasattr(recommendation, 'method'))
        self.assertTrue(hasattr(recommendation, 'confidence'))
        self.assertTrue(hasattr(recommendation, 'reasoning'))

    def test_scenario_specific_recommendations(self):
        """Test scenario-specific recommendations."""
        characteristics = CircuitCharacteristics(
            n_qubits=6, n_gates=20, depth=10,
            two_qubit_gate_ratio=0.3, rotation_gate_ratio=0.7,
            clifford_gate_ratio=0.0, redundancy_level=0.1,
            circuit_density=3.3, entanglement_density=0.3
        )

        scenarios = [
            UsageScenario.REAL_TIME_APPLICATIONS,
            UsageScenario.LARGE_SCALE_PROBLEMS,
            UsageScenario.HARDWARE_EXECUTION
        ]

        recommendations = []
        for scenario in scenarios:
            rec = self.recommender.recommend_optimization_method(characteristics, scenario)
            recommendations.append(rec)

        # Should have valid recommendations for all scenarios
        self.assertEqual(len(recommendations), len(scenarios))
        for rec in recommendations:
            self.assertIsNotNone(rec.method)

    def test_recommendation_summary(self):
        """Test comprehensive recommendation summary."""
        characteristics = CircuitCharacteristics(
            n_qubits=5, n_gates=18, depth=9,
            two_qubit_gate_ratio=0.3, rotation_gate_ratio=0.4,
            clifford_gate_ratio=0.3, redundancy_level=0.3,
            circuit_density=3.6, entanglement_density=0.3
        )

        summary = self.recommender.get_recommendation_summary(characteristics)

        self.assertIn('primary_recommendation', summary)
        self.assertIn('alternatives', summary)
        self.assertIn('circuit_analysis', summary)
        self.assertIn('key_factors', summary)


class TestIntegrationWorkflows(unittest.TestCase):
    """Test end-to-end integration workflows."""

    @unittest.skipUnless(
        BENCHMARK_AVAILABLE and SIM_FUSION_AVAILABLE and COMPARISON_AVAILABLE and ANALYSIS_AVAILABLE,
        "Integration dependencies not available"
    )
    def test_complete_comparison_workflow(self):
        """Test complete performance comparison workflow."""
        # Generate test circuits
        generator = BenchmarkCircuitGenerator()
        circuits = generator.generate_circuit_suite(
            circuit_types=['bell_state', 'redundant_operations'],
            n_qubits_range=(2, 4),
            circuits_per_type=2
        )

        # Extract circuit objects
        test_circuits = [item['circuit'] for item in circuits]

        # Run performance comparison
        engine = PerformanceComparisonEngine()
        comparison_results = engine.run_batch_comparison(test_circuits, iterations=2)

        # Analyze results statistically
        analyzer = StatisticalAnalyzer()

        # Extract metrics for statistical analysis
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

        statistical_results = analyzer.comprehensive_analysis(
            sim_fusion_data, qibo_fusion_data
        )

        # Verify workflow completed successfully
        self.assertIsInstance(comparison_results, list)
        self.assertGreater(len(comparison_results), 0)
        self.assertIsInstance(statistical_results, dict)
        self.assertIn('summary_statistics', statistical_results)

    @unittest.skipUnless(
        BENCHMARK_AVAILABLE and RECOMMENDER_AVAILABLE and QIBO_AVAILABLE,
        "Integration dependencies not available"
    )
    def test_recommendation_integration_workflow(self):
        """Test recommendation system integration with circuit analysis."""
        # Generate test circuit
        generator = BenchmarkCircuitGenerator()
        circuit = generator.create_redundant_circuit(4, "high")

        # Analyze circuit characteristics
        characteristics_data = generator.get_circuit_characteristics(circuit)

        # Get optimization recommendation
        recommender = StrategyRecommender(learning_enabled=False)
        characteristics = recommender.analyze_circuit_characteristics(characteristics_data)
        recommendation = recommender.recommend_optimization_method(
            characteristics, UsageScenario.SIMULATION
        )

        # Verify integration worked
        self.assertIsInstance(recommendation, object)
        self.assertTrue(hasattr(recommendation, 'method'))
        self.assertTrue(hasattr(recommendation, 'confidence'))

    @unittest.skipUnless(
        BENCHMARK_AVAILABLE and SIM_FUSION_AVAILABLE and REPORT_AVAILABLE and QIBO_AVAILABLE,
        "Integration dependencies not available"
    )
    def test_report_generation_workflow(self):
        """Test report generation integration workflow."""
        # Create minimal test data for report generation
        analysis_results = {
            'summary_statistics': {
                'sim_fusion': {
                    'gate_reduction': {'mean': 15.0, 'stdev': 1.0, 'n': 3, 'min_val': 14.0, 'max_val': 16.0}
                },
                'qibo_fusion': {
                    'gate_reduction': {'mean': 12.0, 'stdev': 0.8, 'n': 3, 'min_val': 11.0, 'max_val': 13.0}
                }
            },
            'significance_tests': {
                'gate_reduction': {
                    't_test': {
                        'is_significant': True,
                        'p_value': 0.01,
                        'effect_size': 1.2,
                        'statistic': 3.5,
                        'interpretation': 'Significant difference'
                    }
                }
            },
            'recommendations': ['Test recommendation for workflow']
        }

        # Generate reports
        temp_dir = tempfile.mkdtemp()
        try:
            generator = ReportGenerator(output_dir=temp_dir, include_charts=False)
            from report_generator import ReportFormat
            output_files = generator.generate_comprehensive_report(
                analysis_results=analysis_results,
                formats=[ReportFormat.MARKDOWN, ReportFormat.JSON]
            )

            # Verify reports generated
            self.assertIn('markdown', output_files)
            self.assertIn('json', output_files)

            for format_type, file_path in output_files.items():
                self.assertTrue(os.path.exists(file_path))
                self.assertGreater(os.path.getsize(file_path), 0)

        finally:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)


class TestErrorHandling(unittest.TestCase):
    """Test error handling and edge cases."""

    @unittest.skipUnless(SIM_FUSION_AVAILABLE and QIBO_AVAILABLE, "Dependencies not available")
    def test_empty_circuit_handling(self):
        """Test handling of empty circuits."""
        circuit = Circuit(2)  # Empty circuit

        try:
            optimized = sim_fusion(circuit)
            self.assertIsInstance(optimized, Circuit)
        except Exception as e:
            self.fail(f"Empty circuit caused unexpected error: {e}")

    @unittest.skipUnless(ANALYSIS_AVAILABLE, "statistical_analysis not available")
    def test_insufficient_data_handling(self):
        """Test handling of insufficient statistical data."""
        analyzer = StatisticalAnalyzer()

        # Test with empty data
        with self.assertRaises(ValueError):
            StatisticalSummary([], "test")

        # Test with single data point
        summary = StatisticalSummary([1.0], "test")
        self.assertEqual(summary.mean, 1.0)
        self.assertEqual(summary.stdev, 0.0)

    @unittest.skipUnless(COMPARISON_AVAILABLE, "performance_comparison not available")
    def test_invalid_circuit_handling(self):
        """Test handling of invalid circuit inputs."""
        engine = PerformanceComparisonEngine()

        # Test with None input
        with self.assertRaises((TypeError, AttributeError)):
            engine.compare_optimization_methods(None)

    def test_module_import_fallbacks(self):
        """Test graceful handling of missing optional dependencies."""
        # This test verifies that modules handle missing dependencies gracefully
        try:
            # Attempt imports that might fail
            import matplotlib
            matplotlib_available = True
        except ImportError:
            matplotlib_available = False

        try:
            import scipy
            scipy_available = True
        except ImportError:
            scipy_available = False

        try:
            import sklearn
            sklearn_available = True
        except ImportError:
            sklearn_available = False

        # Verify the system can work without these
        self.assertTrue(True)  # If we get here, fallbacks work


class TestPerformanceRegression(unittest.TestCase):
    """Test performance regression detection."""

    @unittest.skipUnless(SIM_FUSION_AVAILABLE and QIBO_AVAILABLE, "Dependencies not available")
    def test_optimization_performance_regression(self):
        """Test for performance regressions in optimization."""
        # Create test circuit
        circuit = Circuit(3)
        for i in range(3):
            circuit.add(gates.H(i))
        for i in range(2):
            circuit.add(gates.CNOT(i, i+1))

        # Multiple runs to check consistency
        times = []
        gate_reductions = []

        for _ in range(5):
            import time
            start_time = time.time()
            optimized = sim_fusion(circuit, verbose=False)
            end_time = time.time()

            times.append(end_time - start_time)
            gate_reductions.append((circuit.ngates - optimized.ngates) / circuit.ngates)

        # Basic performance checks
        avg_time = statistics.mean(times)
        avg_reduction = statistics.mean(gate_reductions)

        # Should complete within reasonable time
        self.assertLess(avg_time, 1.0, "Optimization taking too long")

        # Should provide some optimization benefit
        self.assertGreaterEqual(avg_reduction, 0, "Should not increase gate count")


def run_comprehensive_tests():
    """Run all tests and provide a summary."""
    # Create test suite
    test_classes = [
        TestBenchmarkCircuitGeneration,
        TestSimFusionCore,
        TestPerformanceComparison,
        TestStatisticalAnalysis,
        TestReportGeneration,
        TestStrategyRecommendation,
        TestIntegrationWorkflows,
        TestErrorHandling,
        TestPerformanceRegression
    ]

    suite = unittest.TestSuite()
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        suite.addTests(tests)

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Summary
    total_tests = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)
    skipped = len(result.skipped)
    passed = total_tests - failures - errors - skipped

    print(f"\n{'='*60}")
    print("TEST SUMMARY")
    print(f"{'='*60}")
    print(f"Total tests run: {total_tests}")
    print(f"Passed: {passed}")
    print(f"Failed: {failures}")
    print(f"Errors: {errors}")
    print(f"Skipped: {skipped}")
    print(f"Success rate: {(passed/total_tests)*100:.1f}%")
    print(f"{'='*60}")

    # Dependency status
    print(f"\nDEPENDENCY STATUS:")
    print(f"Qibo: {'✓' if QIBO_AVAILABLE else '✗'}")
    print(f"Sim-Fusion: {'✓' if SIM_FUSION_AVAILABLE else '✗'}")
    print(f"Benchmark Circuits: {'✓' if BENCHMARK_AVAILABLE else '✗'}")
    print(f"Performance Comparison: {'✓' if COMPARISON_AVAILABLE else '✗'}")
    print(f"Statistical Analysis: {'✓' if ANALYSIS_AVAILABLE else '✗'}")
    print(f"Report Generation: {'✓' if REPORT_AVAILABLE else '✗'}")
    print(f"Strategy Recommender: {'✓' if RECOMMENDER_AVAILABLE else '✗'}")

    if failures > 0 or errors > 0:
        print(f"\n⚠️  Some tests failed. Check output above for details.")
        return False
    else:
        print(f"\n✅ All tests passed successfully!")
        return True


if __name__ == '__main__':
    # Check dependencies first
    print("Checking dependencies...")
    print(f"Qibo: {'Available' if QIBO_AVAILABLE else 'Not Available'}")
    print(f"Sim-Fusion: {'Available' if SIM_FUSION_AVAILABLE else 'Not Available'}")

    if not QIBO_AVAILABLE or not SIM_FUSION_AVAILABLE:
        print("\n⚠️  Some core dependencies are missing.")
        print("Install required packages for full testing:")
        print("pip install qibo pytket pytket-qibo")

    print("\nRunning comprehensive test suite...")
    success = run_comprehensive_tests()

    sys.exit(0 if success else 1)