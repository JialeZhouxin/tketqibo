"""
Quantum Algorithms Benchmark Framework

This module provides a comprehensive framework for benchmarking quantum algorithms
with different optimization strategies in the cross-framework optimizer.

Author: Claude AI Assistant
Date: 2025-12-19
"""

import sys
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import json
import warnings
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Dict, List, Any, Optional, Union, Tuple
from abc import ABC, abstractmethod
from enum import Enum

# Add project paths
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / 'src'))

# Import dependencies
try:
    from qibo import Circuit as QiboCircuit, gates
    QIBO_AVAILABLE = True
    print("Qibo is available")
except ImportError as e:
    QIBO_AVAILABLE = False
    QiboCircuit = None
    gates = None
    print(f"Qibo not available: {e}")

try:
    from qiskit import QuantumCircuit as QiskitCircuit
    from qiskit.circuit.library import QFT, TwoLocal, GroverOperator, PhaseEstimation
    from qiskit.algorithms import AmplificationProblem
    from qiskit.circuit.library import EfficientSU2
    QISKIT_AVAILABLE = True
    print("Qiskit is available")
except ImportError as e:
    QISKIT_AVAILABLE = False
    QiskitCircuit = None
    print(f"Qiskit not available: {e}")

try:
    from src.cross_framework_interface import optimize_circuit_with_stats, optimize_circuit
    INTERFACE_AVAILABLE = True
    print("Cross-framework interface is available")
except ImportError as e:
    INTERFACE_AVAILABLE = False
    print(f"Cross-framework interface not available: {e}")


class AlgorithmType(Enum):
    """Algorithm type categories."""
    VARIATIONAL = "variational"
    SEARCH = "search"
    TRANSFORM = "transform"
    APPLICATION = "application"


class OptimizationStrategy(Enum):
    """Available optimization strategies."""
    NONE = "none"
    QISKIT_ONLY = "qiskit_only"
    SIM_FUSION = "sim_fusion"
    HYBRID = "hybrid"


class ScaleSize(Enum):
    """Algorithm scale sizes."""
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"


@dataclass
class AlgorithmMetrics:
    """Metrics for a single algorithm test."""
    algorithm_name: str
    algorithm_type: str
    scale_size: str
    optimization_strategy: str
    optimization_level: int

    # Original circuit metrics
    original_gates: int
    original_depth: int
    original_qubits: int

    # Optimized circuit metrics
    optimized_gates: int
    optimized_depth: int

    # Performance metrics
    optimization_time: float
    conversion_time: float
    total_time: float
    memory_usage_mb: float

    # Efficiency metrics
    gate_reduction_percent: float
    depth_reduction_percent: float

    # Test metadata
    test_timestamp: str
    test_success: bool
    error_message: Optional[str] = None


class PerformanceMetrics:
    """Collects and manages performance metrics for benchmarking."""

    def __init__(self):
        self.metrics_list: List[AlgorithmMetrics] = []
        self.start_time = 0
        self.start_memory = 0

    def start_measurement(self):
        """Start measuring performance metrics."""
        self.start_time = time.time()
        self.start_memory = self._get_memory_usage()

    def record_circuit_metrics(self, circuit: Any, name: str) -> Dict[str, Any]:
        """Record basic circuit metrics."""
        if hasattr(circuit, 'ngates'):
            # Qibo circuit
            return {
                'gates': circuit.ngates,
                'depth': circuit.depth,
                'qubits': circuit.nqubits
            }
        elif hasattr(circuit, 'size'):
            # Qiskit circuit
            return {
                'gates': circuit.size(),
                'depth': circuit.depth(),
                'qubits': circuit.num_qubits
            }
        else:
            print(f"Warning: Unknown circuit type for {name}")
            return {'gates': 0, 'depth': 0, 'qubits': 0}

    def get_current_metrics(self) -> Dict[str, float]:
        """Get current performance metrics."""
        current_time = time.time()
        current_memory = self._get_memory_usage()

        return {
            'elapsed_time': current_time - self.start_time,
            'memory_usage': current_memory - self.start_memory
        }

    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB."""
        try:
            import psutil
            process = psutil.Process()
            return process.memory_info().rss / 1024 / 1024  # Convert to MB
        except ImportError:
            # Fallback: simple estimate
            return 0.0

    def add_metrics(self, metrics: AlgorithmMetrics):
        """Add metrics to the collection."""
        self.metrics_list.append(metrics)

    def calculate_efficiency_metrics(self, original_gates: int, optimized_gates: int,
                                    original_depth: int, optimized_depth: int) -> Tuple[float, float]:
        """Calculate efficiency metrics."""
        if original_gates > 0:
            gate_reduction = (1 - optimized_gates / original_gates) * 100
        else:
            gate_reduction = 0.0

        if original_depth > 0:
            depth_reduction = (1 - optimized_depth / original_depth) * 100
        else:
            depth_reduction = 0.0

        return gate_reduction, depth_reduction

    def to_dataframe(self) -> pd.DataFrame:
        """Convert metrics to pandas DataFrame."""
        if not self.metrics_list:
            return pd.DataFrame()

        data = [asdict(metrics) for metrics in self.metrics_list]
        return pd.DataFrame(data)

    def save_to_file(self, filepath: str):
        """Save metrics to file."""
        df = self.to_dataframe()
        df.to_csv(filepath, index=False)

    def load_from_file(self, filepath: str):
        """Load metrics from file."""
        df = pd.read_csv(filepath)
        self.metrics_list = df.to_dict('records')


class AlgorithmFactory:
    """Factory for creating standardized quantum algorithm instances."""

    @staticmethod
    def create_vqe(n_qubits: int, scale_size: ScaleSize = ScaleSize.SMALL) -> QiskitCircuit:
        """Create VQE (Variational Quantum Eigensolver) circuit."""
        if not QISKIT_AVAILABLE:
            raise ImportError("Qiskit is required for VQE algorithm")

        # VQE ansatz parameters
        if scale_size == ScaleSize.SMALL:
            repetitions = 2
        elif scale_size == ScaleSize.MEDIUM:
            repetitions = 3
        else:  # LARGE
            repetitions = 4

        # Create hardware-efficient ansatz
        ansatz = TwoLocal(n_qubits, ['ry', 'rz'], 'cz', reps=repetitions)
        return ansatz

    @staticmethod
    def create_qaoa(n_qubits: int, scale_size: ScaleSize = ScaleSize.SMALL) -> QiskitCircuit:
        """Create QAOA (Quantum Approximate Optimization Algorithm) circuit."""
        if not QISKIT_AVAILABLE:
            raise ImportError("Qiskit is required for QAOA algorithm")

        # QAOA parameters
        if scale_size == ScaleSize.SMALL:
            p = 1  # Number of QAOA layers
        elif scale_size == ScaleSize.MEDIUM:
            p = 2
        else:  # LARGE
            p = 3

        # Create QAOA circuit for MaxCut problem
        from qiskit.circuit.library import QAOAAnsatz
        cost_operator = None  # Simplified for benchmarking

        ansatz = QAOAAnsatz(cost_operator, reps=p)
        return ansatz

    @staticmethod
    def create_vqc(n_qubits: int, scale_size: ScaleSize = ScaleSize.SMALL) -> QiskitCircuit:
        """Create VQC (Variational Quantum Classifier) circuit."""
        if not QISKIT_AVAILABLE:
            raise ImportError("Qiskit is required for VQC algorithm")

        # VQC parameters
        if scale_size == ScaleSize.SMALL:
            repetitions = 1
        elif scale_size == ScaleSize.MEDIUM:
            repetitions = 2
        else:  # LARGE
            repetitions = 3

        # Create VQC circuit (similar to VQE but for classification)
        ansatz = EfficientSU2(n_qubits, entanglement='full', reps=repetitions)
        return ansatz

    @staticmethod
    def create_grover(n_qubits: int, scale_size: ScaleSize = ScaleSize.SMALL) -> QiskitCircuit:
        """Create Grover's algorithm circuit."""
        if not QISKIT_AVAILABLE:
            raise ImportError("Qiskit is required for Grover algorithm")

        # Create oracle (simplified: marking state |11...1⟩)
        oracle = QuantumCircuit(n_qubits)
        oracle.cz(0, 1) if n_qubits >= 2 else None
        oracle = oracle.to_gate()

        # Create Grover operator
        if n_qubits <= 2:
            iterations = 1
        elif n_qubits <= 5:
            iterations = 2
        else:
            iterations = 3

        grover_op = GroverOperator(oracle, iterations=iterations)

        # Create initial state (uniform superposition)
        qc = QuantumCircuit(n_qubits)
        qc.h(range(n_qubits))
        qc.append(grover_op, range(n_qubits))

        return qc

    @staticmethod
    def create_deutsch_jozsa(n_qubits: int, scale_size: ScaleSize = ScaleSize.SMALL) -> QiskitCircuit:
        """Create Deutsch-Jozsa algorithm circuit."""
        if not QISKIT_AVAILABLE:
            raise ImportError("Qiskit is required for Deutsch-Jozsa algorithm")

        # Ensure n_qubits is odd for balanced function
        if n_qubits % 2 == 0:
            n_qubits += 1

        qc = QuantumCircuit(n_qubits, 1)

        # Initial state
        qc.h(range(n_qubits))
        qc.h(n_qubits-1)

        # Oracle (balanced function - simplified implementation)
        qc.cx(0, n_qubits-1)

        # Hadamard transform
        qc.h(range(n_qubits))

        return qc

    @staticmethod
    def create_bernstein_vazirani(n_qubits: int, scale_size: ScaleSize = ScaleSize.SMALL) -> QiskitCircuit:
        """Create Bernstein-Vazirani algorithm circuit."""
        if not QISKIT_AVAILABLE:
            raise ImportError("Qiskit is required for Bernstein-Vazirani algorithm")

        # Hidden string (simplified: all ones)
        hidden_string = "1" * n_qubits

        qc = QuantumCircuit(n_qubits, n_qubits)

        # Initial state
        qc.h(range(n_qubits))

        # Oracle for hidden string
        for i, bit in enumerate(hidden_string):
            if bit == '1':
                qc.cx(i, i)

        # Hadamard transform
        qc.h(range(n_qubits))

        return qc

    @staticmethod
    def create_qft(n_qubits: int, scale_size: ScaleSize = ScaleSize.SMALL) -> QiskitCircuit:
        """Create Quantum Fourier Transform circuit."""
        if not QISKIT_AVAILABLE:
            raise ImportError("Qiskit is required for QFT algorithm")

        # Create QFT circuit
        qc = QuantumCircuit(n_qubits)
        qft = QFT(n_qubits).to_gate()
        qc.append(qft, range(n_qubits))

        return qc

    @staticmethod
    def create_qpe(n_qubits: int, scale_size: ScaleSize = ScaleSize.SMALL) -> QiskitCircuit:
        """Create Quantum Phase Estimation circuit."""
        if not QISKIT_AVAILABLE:
            raise ImportError("Qiskit is required for QPE algorithm")

        # Simplified QPE implementation
        eigenvalue_qubits = n_qubits // 2
        ancilla_qubits = n_qubits - eigenvalue_qubits

        qc = QuantumCircuit(n_qubits, ancilla_qubits)

        # Initial state preparation (simplified)
        qc.h(range(ancilla_qubits))
        qc.x(eigenvalue_qubits)

        # Controlled-U operations (simplified)
        for i in range(ancilla_qubits):
            for _ in range(2**i):
                qc.cp(np.pi/4, ancilla_qubits-i-1, eigenvalue_qubits)

        # Inverse QFT
        inverse_qft = QFT(ancilla_qubits).inverse().to_gate()
        qc.append(inverse_qft, range(ancilla_qubits))

        return qc

    @staticmethod
    def create_shor(n_qubits: int, scale_size: ScaleSize = ScaleSize.SMALL) -> QiskitCircuit:
        """Create small-scale Shor's algorithm circuit (modular exponentiation part)."""
        if not QISKIT_AVAILABLE:
            raise ImportError("Qiskit is required for Shor algorithm")

        # Simplified modular multiplication circuit
        work_qubits = n_qubits // 2
        qc = QuantumCircuit(n_qubits)

        # Initial superposition
        qc.h(range(work_qubits))

        # Modular multiplication (simplified)
        for i in range(work_qubits):
            qc.ccx(i, work_qubits + i, work_qubits + i + 1)

        return qc

    @staticmethod
    def create_hhl(n_qubits: int, scale_size: ScaleSize = ScaleSize.SMALL) -> QiskitCircuit:
        """Create HHL (Harrow-Hassidim-Lloyd) algorithm circuit (simplified)."""
        if not QISKIT_AVAILABLE:
            raise ImportError("Qiskit is required for HHL algorithm")

        # Simplified HHL implementation (quantum phase estimation part)
        matrix_size = int(np.sqrt(n_qubits))

        qc = QuantumCircuit(n_qubits)

        # Initial state preparation
        qc.h(range(matrix_size))

        # Controlled rotations (simplified)
        for i in range(matrix_size):
            angle = np.pi / (2**i)
            qc.cu3(angle, 0, 0, i, i + matrix_size)

        # Quantum inverse operation (simplified)
        for i in range(matrix_size):
            qc.swap(i, n_qubits - 1 - i)

        return qc


class QuantumAlgorithmBenchmark:
    """Main class for quantum algorithm benchmarking."""

    def __init__(self, verbose: bool = True):
        """Initialize the benchmark framework.

        Args:
            verbose: Whether to print detailed progress information
        """
        self.verbose = verbose
        self.metrics_collector = PerformanceMetrics()
        self.algorithm_factory = AlgorithmFactory()

        # Define algorithm specifications
        self.algorithms = {
            'VQE': {
                'type': AlgorithmType.VARIATIONAL,
                'factory_method': self.algorithm_factory.create_vqe,
                'qubits': [4, 8, 12]
            },
            'QAOA': {
                'type': AlgorithmType.SEARCH,
                'factory_method': self.algorithm_factory.create_qaoa,
                'qubits': [4, 8, 16]
            },
            'VQC': {
                'type': AlgorithmType.VARIATIONAL,
                'factory_method': self.algorithm_factory.create_vqc,
                'qubits': [4, 6, 8]
            },
            'Grover': {
                'type': AlgorithmType.SEARCH,
                'factory_method': self.algorithm_factory.create_grover,
                'qubits': [3, 5, 7]
            },
            'Deutsch-Jozsa': {
                'type': AlgorithmType.SEARCH,
                'factory_method': self.algorithm_factory.create_deutsch_jozsa,
                'qubits': [2, 4, 6]
            },
            'Bernstein-Vazirani': {
                'type': AlgorithmType.SEARCH,
                'factory_method': self.algorithm_factory.create_bernstein_vazirani,
                'qubits': [3, 5, 7]
            },
            'QFT': {
                'type': AlgorithmType.TRANSFORM,
                'factory_method': self.algorithm_factory.create_qft,
                'qubits': [4, 8, 16]
            },
            'QPE': {
                'type': AlgorithmType.TRANSFORM,
                'factory_method': self.algorithm_factory.create_qpe,
                'qubits': [4, 6, 8]
            },
            'Shor': {
                'type': AlgorithmType.APPLICATION,
                'factory_method': self.algorithm_factory.create_shor,
                'qubits': [4, 6, 8]
            },
            'HHL': {
                'type': AlgorithmType.APPLICATION,
                'factory_method': self.algorithm_factory.create_hhl,
                'qubits': [4, 9, 16]
            }
        }

        if self.verbose:
            print(f"Initialized benchmark with {len(self.algorithms)} algorithms")

    def create_algorithm_circuit(self, algorithm_name: str, n_qubits: int,
                                scale_size: ScaleSize = ScaleSize.SMALL) -> QiskitCircuit:
        """Create a quantum algorithm circuit.

        Args:
            algorithm_name: Name of the algorithm
            n_qubits: Number of qubits
            scale_size: Scale size (SMALL, MEDIUM, LARGE)

        Returns:
            Quantum circuit for the specified algorithm
        """
        if algorithm_name not in self.algorithms:
            raise ValueError(f"Unknown algorithm: {algorithm_name}")

        algorithm_info = self.algorithms[algorithm_name]
        factory_method = algorithm_info['factory_method']

        return factory_method(n_qubits, scale_size)

    def test_algorithm_optimization(self, algorithm_name: str, n_qubits: int,
                                   scale_size: ScaleSize, strategy: str,
                                   optimization_level: int = 2) -> AlgorithmMetrics:
        """Test optimization for a single algorithm.

        Args:
            algorithm_name: Name of the algorithm
            n_qubits: Number of qubits
            scale_size: Scale size
            strategy: Optimization strategy
            optimization_level: Optimization level (0-3)

        Returns:
            AlgorithmMetrics object with test results
        """
        test_timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

        try:
            # Create algorithm circuit
            self.metrics_collector.start_measurement()
            creation_start = time.time()

            circuit = self.create_algorithm_circuit(algorithm_name, n_qubits, scale_size)

            # Record original circuit metrics
            original_metrics = self.metrics_collector.record_circuit_metrics(
                circuit, f"{algorithm_name}_original"
            )

            # Test optimization
            if self.verbose:
                print(f"Testing {algorithm_name} ({scale_size.value}) with {strategy}")

            optimized_circuit, stats = optimize_circuit_with_stats(
                circuit,
                strategy=strategy,
                optimization_level=optimization_level
            )

            # Get performance metrics
            perf_metrics = self.metrics_collector.get_current_metrics()

            # Record optimized circuit metrics
            optimized_metrics = self.metrics_collector.record_circuit_metrics(
                optimized_circuit, f"{algorithm_name}_optimized"
            )

            # Calculate efficiency metrics
            gate_reduction, depth_reduction = self.metrics_collector.calculate_efficiency_metrics(
                original_metrics['gates'],
                optimized_metrics['gates'],
                original_metrics['depth'],
                optimized_metrics['depth']
            )

            # Create metrics object
            algorithm_metrics = AlgorithmMetrics(
                algorithm_name=algorithm_name,
                algorithm_type=self.algorithms[algorithm_name]['type'].value,
                scale_size=scale_size.value,
                optimization_strategy=strategy,
                optimization_level=optimization_level,

                original_gates=original_metrics['gates'],
                original_depth=original_metrics['depth'],
                original_qubits=original_metrics['qubits'],

                optimized_gates=optimized_metrics['gates'],
                optimized_depth=optimized_metrics['depth'],

                optimization_time=stats.get('optimization_time', 0),
                conversion_time=stats.get('conversion_time', 0),
                total_time=perf_metrics['elapsed_time'],
                memory_usage_mb=perf_metrics['memory_usage'],

                gate_reduction_percent=gate_reduction,
                depth_reduction_percent=depth_reduction,

                test_timestamp=test_timestamp,
                test_success=True
            )

            if self.verbose:
                print(f"  ✅ Gates: {original_metrics['gates']} → {optimized_metrics['gates']} ({gate_reduction:.1f}% reduction)")
                print(f"  ✅ Depth: {original_metrics['depth']} → {optimized_metrics['depth']} ({depth_reduction:.1f}% reduction)")
                print(f"  ✅ Time: {perf_metrics['elapsed_time']:.3f}s")

            return algorithm_metrics

        except Exception as e:
            if self.verbose:
                print(f"  ❌ Error: {str(e)}")

            # Create error metrics
            return AlgorithmMetrics(
                algorithm_name=algorithm_name,
                algorithm_type=self.algorithms[algorithm_name]['type'].value,
                scale_size=scale_size.value,
                optimization_strategy=strategy,
                optimization_level=optimization_level,

                original_gates=0,
                original_depth=0,
                original_qubits=n_qubits,

                optimized_gates=0,
                optimized_depth=0,

                optimization_time=0,
                conversion_time=0,
                total_time=0,
                memory_usage_mb=0,

                gate_reduction_percent=0,
                depth_reduction_percent=0,

                test_timestamp=test_timestamp,
                test_success=False,
                error_message=str(e)
            )

    def run_comprehensive_benchmark(self, algorithms: List[str] = None,
                                   strategies: List[str] = None,
                                   optimization_levels: List[int] = None) -> pd.DataFrame:
        """Run comprehensive benchmark tests.

        Args:
            algorithms: List of algorithm names to test (None for all)
            strategies: List of strategies to test (None for all)
            optimization_levels: List of optimization levels to test (None for all)

        Returns:
            DataFrame with all benchmark results
        """
        if algorithms is None:
            algorithms = list(self.algorithms.keys())

        if strategies is None:
            strategies = [s.value for s in OptimizationStrategy]

        if optimization_levels is None:
            optimization_levels = [0, 1, 2, 3]

        total_tests = len(algorithms) * len(strategies) * len(optimization_levels)

        if self.verbose:
            print(f"\n{'='*60}")
            print(f"Starting comprehensive benchmark")
            print(f"Algorithms: {len(algorithms)}")
            print(f"Strategies: {len(strategies)}")
            print(f"Optimization levels: {len(optimization_levels)}")
            print(f"Total tests: {total_tests}")
            print(f"{'='*60}")

        test_count = 0
        start_time = time.time()

        for algorithm_name in algorithms:
            for scale_size in [ScaleSize.SMALL, ScaleSize.MEDIUM, ScaleSize.LARGE]:
                # Determine appropriate number of qubits for this scale
                if scale_size == ScaleSize.SMALL:
                    qubits_idx = 0
                elif scale_size == ScaleSize.MEDIUM:
                    qubits_idx = 1 if len(self.algorithms[algorithm_name]['qubits']) > 1 else 0
                else:  # LARGE
                    qubits_idx = min(2, len(self.algorithms[algorithm_name]['qubits']) - 1)

                n_qubits = self.algorithms[algorithm_name]['qubits'][qubits_idx]

                for strategy in strategies:
                    for opt_level in optimization_levels:
                        test_count += 1

                        if self.verbose:
                            progress = (test_count / total_tests) * 100
                            print(f"[{progress:.1f}%] Test {test_count}/{total_tests}: {algorithm_name} ({scale_size.value}, {strategy}, L{opt_level})")

                        # Run single test
                        metrics = self.test_algorithm_optimization(
                            algorithm_name, n_qubits, scale_size, strategy, opt_level
                        )

                        # Store results
                        self.metrics_collector.add_metrics(metrics)

        total_time = time.time() - start_time

        if self.verbose:
            print(f"\n{'='*60}")
            print(f"Benchmark completed in {total_time:.2f} seconds")
            print(f"Successful tests: {sum(1 for m in self.metrics_collector.metrics_list if m.test_success)}")
            print(f"Failed tests: {sum(1 for m in self.metrics_collector.metrics_list if not m.test_success)}")
            print(f"{'='*60}")

        return self.metrics_collector.to_dataframe()

    def generate_summary_report(self, results_df: pd.DataFrame) -> str:
        """Generate a summary report of the benchmark results.

        Args:
            results_df: DataFrame with benchmark results

        Returns:
            Summary report as a string
        """
        successful_results = results_df[results_df['test_success'] == True]

        if len(successful_results) == 0:
            return "No successful tests to report."

        report = []
        report.append("# Quantum Algorithms Optimization Benchmark Report\n")

        # Overall statistics
        report.append("## Overall Statistics\n")
        report.append(f"- Total tests: {len(results_df)}")
        report.append(f"- Successful tests: {len(successful_results)}")
        report.append(f"- Success rate: {len(successful_results)/len(results_df)*100:.1f}%\n")

        # Algorithm type analysis
        report.append("## Performance by Algorithm Type\n")
        for algo_type in successful_results['algorithm_type'].unique():
            type_data = successful_results[successful_results['algorithm_type'] == algo_type]

            avg_gate_reduction = type_data['gate_reduction_percent'].mean()
            avg_depth_reduction = type_data['depth_reduction_percent'].mean()
            avg_time = type_data['total_time'].mean()

            report.append(f"### {algo_type.title()} Algorithms")
            report.append(f"- Average gate reduction: {avg_gate_reduction:.1f}%")
            report.append(f"- Average depth reduction: {avg_depth_reduction:.1f}%")
            report.append(f"- Average optimization time: {avg_time:.3f}s\n")

        # Best performing algorithms
        report.append("## Top Performing Algorithms\n")
        best_gate_reduction = successful_results.nlargest(5, 'gate_reduction_percent')
        report.append("### Best Gate Reduction:")
        for _, row in best_gate_reduction.iterrows():
            report.append(f"- {row['algorithm_name']} ({row['optimization_strategy']}): {row['gate_reduction_percent']:.1f}%")
        report.append("")

        # Strategy comparison
        report.append("## Optimization Strategy Comparison\n")
        strategy_stats = successful_results.groupby('optimization_strategy').agg({
            'gate_reduction_percent': 'mean',
            'depth_reduction_percent': 'mean',
            'total_time': 'mean'
        }).round(2)

        report.append("Average Performance by Strategy:")
        for strategy, stats in strategy_stats.iterrows():
            report.append(f"- **{strategy}**: Gate: {stats['gate_reduction_percent']:.1f}%, "
                      f"Depth: {stats['depth_reduction_percent']:.1f}%, "
                      f"Time: {stats['total_time']:.3f}s")
        report.append("")

        # Optimization level analysis
        report.append("## Optimization Level Analysis\n")
        level_stats = successful_results.groupby('optimization_level').agg({
            'gate_reduction_percent': ['mean', 'std'],
            'depth_reduction_percent': ['mean', 'std']
        }).round(2)

        report.append("Performance by Optimization Level:")
        for level, stats in level_stats.iterrows():
            report.append(f"- **Level {level}**: Gate: {stats[('gate_reduction_percent', 'mean')]:.1f}% ± "
                      f"{stats[('gate_reduction_percent', 'std')]:.1f}%, "
                      f"Depth: {stats[('depth_reduction_percent', 'mean')]:.1f}% ± "
                      f"{stats[('depth_reduction_percent', 'std')]:.1f}%")

        return "\n".join(report)


def main():
    """Main function to run the quantum algorithms benchmark."""
    print("Quantum Algorithms Benchmark Framework")
    print("=" * 50)

    if not (QIBO_AVAILABLE and QISKIT_AVAILABLE and INTERFACE_AVAILABLE):
        print("Error: Required dependencies not available")
        print("- Qibo:", QIBO_AVAILABLE)
        print("- Qiskit:", QISKIT_AVAILABLE)
        print("- Interface:", INTERFACE_AVAILABLE)
        return

    # Create benchmark instance
    benchmark = QuantumAlgorithmBenchmark(verbose=True)

    # Run comprehensive benchmark
    try:
        # Test all algorithms with all strategies
        results_df = benchmark.run_comprehensive_benchmark()

        # Save results
        results_df.to_csv('quantum_algorithms_benchmark_results.csv', index=False)

        # Generate summary report
        report = benchmark.generate_summary_report(results_df)

        # Save report
        with open('quantum_algorithms_benchmark_report.md', 'w') as f:
            f.write(report)

        print(f"\nResults saved to:")
        print(f"- Data: quantum_algorithms_benchmark_results.csv")
        print(f"- Report: quantum_algorithms_benchmark_report.md")

        # Show summary
        print("\n" + "="*50)
        print("Benchmark Summary:")
        print("="*50)
        print(report.split("## Overall Statistics")[1].split("##")[0].strip())

    except Exception as e:
        print(f"Error during benchmark execution: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()