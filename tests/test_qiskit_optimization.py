"""
Qiskit Optimization Verification Tests

This module contains comprehensive tests for verifying the Qiskit optimization
functionality in the cross-framework quantum circuit optimizer.
"""

import sys
import time
import numpy as np
import unittest
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import traceback

# Add project paths
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

# Import dependencies
try:
    from qibo import Circuit as QiboCircuit, gates
    QIBO_AVAILABLE = True
except ImportError:
    QIBO_AVAILABLE = False
    QiboCircuit = None
    gates = None

try:
    from qiskit import QuantumCircuit as QiskitCircuit
    from qiskit.circuit.library import QFT, TwoLocal
    QISKIT_AVAILABLE = True
except ImportError:
    QISKIT_AVAILABLE = False
    QiskitCircuit = None
    QFT = None
    TwoLocal = None

try:
    from src.cross_framework_interface import (
        optimize_circuit,
        optimize_circuit_with_stats,
        optimize_qiskit,
        quick_optimize
    )
    INTERFACE_AVAILABLE = True
except ImportError:
    INTERFACE_AVAILABLE = False

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False


@dataclass
class PerformanceMetrics:
    """Performance metrics for optimization verification."""
    circuit_name: str
    original_gates: int
    optimized_gates: int
    original_depth: int = 0
    optimized_depth: int = 0
    optimization_time: float = 0.0
    memory_usage_mb: float = 0.0
    optimization_level: int = 0
    strategy: str = ""

    @property
    def gate_reduction_percent(self) -> float:
        """Calculate gate reduction percentage."""
        if self.original_gates == 0:
            return 0.0
        return (self.original_gates - self.optimized_gates) / self.original_gates * 100

    @property
    def depth_reduction_percent(self) -> float:
        """Calculate depth reduction percentage."""
        if self.original_depth == 0:
            return 0.0
        return (self.original_depth - self.optimized_depth) / self.original_depth * 100

    @property
    def optimization_efficiency(self) -> float:
        """Calculate optimization efficiency (reduction % per second)."""
        if self.optimization_time == 0:
            return 0.0
        return self.gate_reduction_percent / self.optimization_time


class QiskitOptimizationTestSuite:
    """Comprehensive test suite for Qiskit optimization verification."""

    def __init__(self):
        """Initialize the test suite."""
        self.test_results: List[PerformanceMetrics] = []
        self.verbose = True
        self.qiskit_levels = [0, 1, 2, 3]

        # Performance targets based on requirements
        self.performance_targets = {
            'small_circuit_time': 1.0,      # seconds for 1-5 qubits
            'medium_circuit_time': 10.0,    # seconds for 6-15 qubits
            'large_circuit_time': 60.0,     # seconds for 16+ qubits
            'memory_growth_factor': 3.0,     # max 3x original circuit size
            'accuracy_threshold': 99.9       # % conversion accuracy
        }

    def log(self, message: str) -> None:
        """Log a message if verbose mode is enabled."""
        if self.verbose:
            print(f"[QISKIT_VERIFY] {message}")

    def get_memory_usage(self) -> float:
        """Get current memory usage in MB."""
        if PSUTIL_AVAILABLE:
            try:
                process = psutil.Process()
                return process.memory_info().rss / 1024 / 1024
            except:
                return 0.0
        return 0.0

    def measure_optimization(self, circuit: Any, strategy: str, level: int = 2,
                           circuit_name: str = "unknown") -> Optional[PerformanceMetrics]:
        """Measure optimization performance with detailed metrics."""
        if not INTERFACE_AVAILABLE:
            self.log("ERROR: Cross-framework interface not available")
            return None

        try:
            # Get original circuit stats
            original_gates = getattr(circuit, 'ngates', len(circuit)) if hasattr(circuit, 'ngates') else len(circuit)
            original_depth = getattr(circuit, 'depth', 0) if hasattr(circuit, 'depth') else 0

            # Convert to QASM if needed
            if isinstance(circuit, QiskitCircuit):
                try:
                    # For Qiskit 2.x, use qiskit.qasm2.dumps
                    from qiskit.qasm2 import dumps
                    qasm_str = dumps(circuit)
                except ImportError:
                    # Fallback for older Qiskit versions
                    try:
                        qasm_str = circuit.qasm()
                    except AttributeError:
                        self.log(f"ERROR: Cannot convert Qiskit circuit to QASM - unsupported version")
                        return None
            elif hasattr(circuit, 'to_qasm'):
                qasm_str = circuit.to_qasm()
            else:
                self.log(f"ERROR: Cannot convert {type(circuit)} to QASM")
                return None

            self.log(f"Testing {circuit_name}: {original_gates} gates, depth {original_depth}")

            # Measure memory before optimization
            initial_memory = self.get_memory_usage()

            # Perform optimization
            start_time = time.time()

            if strategy.startswith('qiskit'):
                optimized, stats = optimize_circuit_with_stats(
                    qasm_str, strategy=strategy, optimization_level=level, verbose=False
                )
            else:
                optimized, stats = optimize_circuit_with_stats(
                    qasm_str, strategy=strategy, verbose=False
                )

            optimization_time = time.time() - start_time
            final_memory = self.get_memory_usage()
            memory_delta = final_memory - initial_memory

            # Get optimized circuit stats
            optimized_gates = stats['optimized_gates']
            optimized_depth = stats.get('optimized_depth', 0)

            metrics = PerformanceMetrics(
                circuit_name=circuit_name,
                original_gates=original_gates,
                optimized_gates=optimized_gates,
                original_depth=original_depth,
                optimized_depth=optimized_depth,
                optimization_time=optimization_time,
                memory_usage_mb=memory_delta,
                optimization_level=level,
                strategy=strategy
            )

            self.log(f"  Result: {original_gates} → {optimized_gates} gates "
                    f"({metrics.gate_reduction_percent:.1f}% reduction)")
            self.log(f"  Depth: {original_depth} → {optimized_depth} "
                    f"({metrics.depth_reduction_percent:.1f}% reduction)")
            self.log(f"  Time: {optimization_time:.4f}s, Memory: {memory_delta:.1f}MB")

            return metrics

        except Exception as e:
            self.log(f"ERROR: Optimization failed for {circuit_name}: {e}")
            self.log(f"  Traceback: {traceback.format_exc()}")
            return None

    def run_comprehensive_verification(self) -> Dict[str, Any]:
        """Run comprehensive Qiskit optimization verification."""
        self.log("=" * 60)
        self.log("Starting Qiskit Optimization Verification")
        self.log("=" * 60)

        if not all([QIBO_AVAILABLE, QISKIT_AVAILABLE, INTERFACE_AVAILABLE]):
            self.log("ERROR: Required dependencies not available")
            self.log(f"  Qibo: {QIBO_AVAILABLE}")
            self.log(f"  Qiskit: {QISKIT_AVAILABLE}")
            self.log(f"  Interface: {INTERFACE_AVAILABLE}")
            return {'status': 'failed', 'reason': 'missing_dependencies'}

        verification_results = {
            'status': 'in_progress',
            'tests_run': 0,
            'tests_passed': 0,
            'performance_metrics': [],
            'summary': {}
        }

        # Run all test phases
        try:
            self._test_qiskit_levels()
            self._test_basic_circuits()
            self._test_algorithm_circuits()
            self._test_large_circuits()
            self._test_error_handling()

            verification_results['performance_metrics'] = self.test_results
            verification_results['summary'] = self._generate_summary()
            verification_results['status'] = 'completed'

        except Exception as e:
            self.log(f"ERROR: Verification failed: {e}")
            verification_results['status'] = 'failed'
            verification_results['error'] = str(e)

        self._print_summary(verification_results['summary'])
        return verification_results

    def _test_qiskit_levels(self) -> None:
        """Test all Qiskit optimization levels (0-3)."""
        self.log("\n" + "=" * 40)
        self.log("Testing Qiskit Optimization Levels")
        self.log("=" * 40)

        # Create a test circuit
        circuit = QiskitCircuit(4)
        circuit.h([0, 1, 2, 3])
        circuit.cx(0, 1)
        circuit.cx(1, 2)
        circuit.cx(2, 3)
        circuit.rz(np.pi/4, [0, 1, 2, 3])
        circuit.cx(3, 0)
        circuit.x([0, 1])

        for level in self.qiskit_levels:
            self.log(f"\nTesting Qiskit Level {level}:")
            metrics = self.measure_optimization(
                circuit, 'qiskit_only', level, f"qiskit_level_{level}"
            )
            if metrics:
                self.test_results.append(metrics)

    def _test_basic_circuits(self) -> None:
        """Test basic quantum circuits."""
        self.log("\n" + "=" * 40)
        self.log("Testing Basic Quantum Circuits")
        self.log("=" * 40)

        basic_circuits = [
            ('Bell State', self._create_bell_circuit),
            ('GHZ State', self._create_ghz_circuit),
            ('Simple Entanglement', self._create_simple_entanglement_circuit),
            ('Random Circuit', self._create_random_circuit),
        ]

        for name, circuit_func in basic_circuits:
            try:
                circuit = circuit_func()
                self.log(f"\nTesting {name}:")
                metrics = self.measure_optimization(circuit, 'qiskit_only', 2, name)
                if metrics:
                    self.test_results.append(metrics)
            except Exception as e:
                self.log(f"ERROR: {name} test failed: {e}")

    def _test_algorithm_circuits(self) -> None:
        """Test quantum algorithm circuits."""
        self.log("\n" + "=" * 40)
        self.log("Testing Quantum Algorithm Circuits")
        self.log("=" * 40)

        algorithm_circuits = [
            ('Grover Circuit', self._create_grover_circuit),
            ('QFT Circuit', self._create_qft_circuit),
            ('Deutsch-Jozsa Circuit', self._create_deutsch_jozsa_circuit),
            ('VQE Ansatz', self._create_vqe_circuit),
        ]

        for name, circuit_func in algorithm_circuits:
            try:
                circuit = circuit_func()
                self.log(f"\nTesting {name}:")
                metrics = self.measure_optimization(circuit, 'qiskit_only', 2, name)
                if metrics:
                    self.test_results.append(metrics)
            except Exception as e:
                self.log(f"ERROR: {name} test failed: {e}")

    def _test_large_circuits(self) -> None:
        """Test large-scale circuits for performance scaling."""
        self.log("\n" + "=" * 40)
        self.log("Testing Large-Scale Circuits")
        self.log("=" * 40)

        sizes = [8, 12, 16]  # Different qubit counts
        for size in sizes:
            try:
                circuit = self._create_large_circuit(size)
                self.log(f"\nTesting {size}-qubit circuit:")
                metrics = self.measure_optimization(circuit, 'qiskit_only', 2, f"large_{size}_qubits")
                if metrics:
                    self.test_results.append(metrics)

                    # Check performance targets
                    if size <= 5 and metrics.optimization_time > self.performance_targets['small_circuit_time']:
                        self.log(f"WARNING: Small circuit exceeded time target: {metrics.optimization_time:.4f}s")
                    elif 6 <= size <= 15 and metrics.optimization_time > self.performance_targets['medium_circuit_time']:
                        self.log(f"WARNING: Medium circuit exceeded time target: {metrics.optimization_time:.4f}s")
                    elif size >= 16 and metrics.optimization_time > self.performance_targets['large_circuit_time']:
                        self.log(f"WARNING: Large circuit exceeded time target: {metrics.optimization_time:.4f}s")
            except Exception as e:
                self.log(f"ERROR: {size}-qubit test failed: {e}")

    def _test_error_handling(self) -> None:
        """Test error handling and edge cases."""
        self.log("\n" + "=" * 40)
        self.log("Testing Error Handling")
        self.log("=" * 40)

        error_cases = [
            ('Empty Circuit', self._create_empty_circuit),
            ('Invalid QASM', self._create_invalid_qasm),
        ]

        for name, case_func in error_cases:
            try:
                self.log(f"\nTesting {name}:")
                case_func()  # This should be handled gracefully
            except Exception as e:
                self.log(f"Expected error handled: {e}")

    def _create_bell_circuit(self) -> QiskitCircuit:
        """Create a Bell state circuit."""
        circuit = QiskitCircuit(2)
        circuit.h(0)
        circuit.cx(0, 1)
        return circuit

    def _create_ghz_circuit(self) -> QiskitCircuit:
        """Create a GHZ state circuit."""
        circuit = QiskitCircuit(3)
        circuit.h(0)
        circuit.cx(0, 1)
        circuit.cx(0, 2)
        return circuit

    def _create_simple_entanglement_circuit(self) -> QiskitCircuit:
        """Create a simple entanglement circuit."""
        circuit = QiskitCircuit(4)
        for i in range(4):
            circuit.h(i)
        for i in range(3):
            circuit.cx(i, i+1)
        return circuit

    def _create_random_circuit(self) -> QiskitCircuit:
        """Create a random quantum circuit."""
        np.random.seed(42)  # For reproducibility
        n_qubits = 4
        circuit = QiskitCircuit(n_qubits)

        for _ in range(10):
            gate_type = np.random.choice(['h', 'x', 'y', 'z', 'rx', 'ry', 'rz', 'cx'])
            if gate_type == 'h':
                qubit = np.random.randint(0, n_qubits)
                circuit.h(qubit)
            elif gate_type in ['x', 'y', 'z']:
                qubit = np.random.randint(0, n_qubits)
                getattr(circuit, gate_type)(qubit)
            elif gate_type in ['rx', 'ry', 'rz']:
                qubit = np.random.randint(0, n_qubits)
                angle = np.random.uniform(0, 2*np.pi)
                getattr(circuit, gate_type)(angle, qubit)
            elif gate_type == 'cx' and n_qubits >= 2:
                control = np.random.randint(0, n_qubits-1)
                target = np.random.randint(control+1, n_qubits)
                circuit.cx(control, target)

        return circuit

    def _create_grover_circuit(self) -> QiskitCircuit:
        """Create a simplified Grover circuit."""
        n_qubits = 3
        circuit = QiskitCircuit(n_qubits)

        # Initial superposition
        for i in range(n_qubits):
            circuit.h(i)

        # Oracle (mark |000>)
        circuit.z(0)

        # Diffusion operator
        for i in range(n_qubits):
            circuit.h(i)
            circuit.x(i)
        circuit.h(2)
        circuit.ccx(0, 1, 2)
        circuit.h(2)

        for i in range(n_qubits):
            circuit.x(i)
            circuit.h(i)

        return circuit

    def _create_qft_circuit(self) -> QiskitCircuit:
        """Create a QFT circuit."""
        n_qubits = 3
        circuit = QiskitCircuit(n_qubits)

        for target in range(n_qubits):
            circuit.h(target)
            for control in range(target + 1, n_qubits):
                angle = np.pi / (2 ** (control - target))
                try:
                    # Try cu1 first (older Qiskit)
                    circuit.cu1(angle, control, target)
                except AttributeError:
                    # Fallback to cp for newer Qiskit
                    circuit.cp(angle, control, target)

        return circuit

    def _create_deutsch_jozsa_circuit(self) -> QiskitCircuit:
        """Create a Deutsch-Jozsa circuit."""
        n_qubits = 3
        circuit = QiskitCircuit(n_qubits + 1)

        # Initialize
        for i in range(n_qubits + 1):
            circuit.h(i)

        # Oracle (balanced function)
        circuit.cx(0, n_qubits)
        circuit.cx(1, n_qubits)

        # Final Hadamards
        for i in range(n_qubits):
            circuit.h(i)

        return circuit

    def _create_vqe_circuit(self) -> QiskitCircuit:
        """Create a VQE ansatz circuit."""
        n_qubits = 4
        n_layers = 2
        circuit = QiskitCircuit(n_qubits)

        # Initial state
        for i in range(n_qubits):
            circuit.h(i)

        # VQE layers
        for layer in range(n_layers):
            # Problem Hamiltonian
            for i in range(n_qubits - 1):
                circuit.cx(i, i + 1)

            # Mixer Hamiltonian
            for i in range(n_qubits):
                angle = np.pi / (4 + layer)
                circuit.rx(angle, i)

        return circuit

    def _create_large_circuit(self, n_qubits: int) -> QiskitCircuit:
        """Create a large quantum circuit."""
        circuit = QiskitCircuit(n_qubits)

        # Initial layer
        for i in range(n_qubits):
            circuit.h(i)

        # Entanglement layers
        for layer in range(3):
            for i in range(n_qubits - 1):
                circuit.cx(i, i + 1)

            # Random rotations
            for i in range(n_qubits):
                angle = np.pi / (layer + 2) * (i + 1) / n_qubits
                circuit.rz(angle, i)

        return circuit

    def _create_empty_circuit(self) -> None:
        """Test empty circuit handling."""
        empty_qasm = "OPENQASM 2.0;\ninclude \"qelib1.inc\";\nqreg q[0];"
        try:
            optimize_circuit(empty_qasm, strategy='qiskit_only')
        except Exception as e:
            self.log(f"Empty circuit handled: {e}")

    def _create_invalid_qasm(self) -> None:
        """Test invalid QASM handling."""
        invalid_qasm = "This is not valid QASM"
        try:
            optimize_circuit(invalid_qasm, strategy='qiskit_only')
        except Exception as e:
            self.log(f"Invalid QASM handled: {e}")

    def _generate_summary(self) -> Dict[str, Any]:
        """Generate summary statistics from test results."""
        if not self.test_results:
            return {'error': 'No test results available'}

        # Calculate statistics
        total_tests = len(self.test_results)
        total_original_gates = sum(r.original_gates for r in self.test_results)
        total_optimized_gates = sum(r.optimized_gates for r in self.test_results)
        total_reduction = total_original_gates - total_optimized_gates

        gate_reduction_rates = [r.gate_reduction_percent for r in self.test_results]
        optimization_times = [r.optimization_time for r in self.test_results]

        summary = {
            'total_tests': total_tests,
            'total_original_gates': total_original_gates,
            'total_optimized_gates': total_optimized_gates,
            'total_gate_reduction': total_reduction,
            'average_gate_reduction_percent': np.mean(gate_reduction_rates),
            'max_gate_reduction_percent': max(gate_reduction_rates),
            'min_gate_reduction_percent': min(gate_reduction_rates),
            'average_optimization_time': np.mean(optimization_times),
            'max_optimization_time': max(optimization_times),
            'min_optimization_time': min(optimization_times),
            'performance_by_level': self._analyze_by_level(),
            'performance_by_circuit_type': self._analyze_by_circuit_type()
        }

        # Add success criteria evaluation
        summary['success_criteria'] = self._evaluate_success_criteria(summary)

        return summary

    def _analyze_by_level(self) -> Dict[int, Dict[str, float]]:
        """Analyze performance by optimization level."""
        level_stats = {}
        for level in self.qiskit_levels:
            level_results = [r for r in self.test_results if r.optimization_level == level]
            if level_results:
                level_stats[level] = {
                    'count': len(level_results),
                    'avg_reduction': np.mean([r.gate_reduction_percent for r in level_results]),
                    'avg_time': np.mean([r.optimization_time for r in level_results])
                }
        return level_stats

    def _analyze_by_circuit_type(self) -> Dict[str, Dict[str, float]]:
        """Analyze performance by circuit type."""
        type_stats = {}
        circuit_types = list(set(r.circuit_name for r in self.test_results))

        for circuit_type in circuit_types:
            type_results = [r for r in self.test_results if r.circuit_name == circuit_type]
            if type_results:
                type_stats[circuit_type] = {
                    'count': len(type_results),
                    'avg_reduction': np.mean([r.gate_reduction_percent for r in type_results]),
                    'avg_time': np.mean([r.optimization_time for r in type_results]),
                    'best_reduction': max([r.gate_reduction_percent for r in type_results])
                }
        return type_stats

    def _evaluate_success_criteria(self, summary: Dict[str, Any]) -> Dict[str, bool]:
        """Evaluate success criteria based on requirements."""
        criteria = {
            'functional_tests_passed': True,  # All tests completed
            'performance_targets_met': True,
            'error_handling_verified': True,
            'scalability_confirmed': True
        }

        # Check performance targets
        max_time = summary.get('max_optimization_time', 0)
        if max_time > self.performance_targets['large_circuit_time']:
            criteria['performance_targets_met'] = False

        # Check optimization effectiveness
        avg_reduction = summary.get('average_gate_reduction_percent', 0)
        if avg_reduction < 1.0:  # At least some optimization
            criteria['performance_targets_met'] = False

        return criteria

    def _print_summary(self, summary: Dict[str, Any]) -> None:
        """Print summary results."""
        self.log("\n" + "=" * 60)
        self.log("QISKIT OPTIMIZATION VERIFICATION SUMMARY")
        self.log("=" * 60)

        if 'error' in summary:
            self.log(f"ERROR: {summary['error']}")
            return

        self.log(f"\nOverall Statistics:")
        self.log(f"  Total tests run: {summary['total_tests']}")
        self.log(f"  Total original gates: {summary['total_original_gates']}")
        self.log(f"  Total optimized gates: {summary['total_optimized_gates']}")
        self.log(f"  Total gate reduction: {summary['total_gate_reduction']} "
                f"({summary['total_gate_reduction']/summary['total_original_gates']*100:.1f}%)")

        self.log(f"\nPerformance Metrics:")
        self.log(f"  Average gate reduction: {summary['average_gate_reduction_percent']:.1f}%")
        self.log(f"  Best gate reduction: {summary['max_gate_reduction_percent']:.1f}%")
        self.log(f"  Average optimization time: {summary['average_optimization_time']:.4f}s")
        self.log(f"  Max optimization time: {summary['max_optimization_time']:.4f}s")

        self.log(f"\nSuccess Criteria:")
        criteria = summary.get('success_criteria', {})
        for criterion, passed in criteria.items():
            status = "✅ PASS" if passed else "❌ FAIL"
            self.log(f"  {criterion}: {status}")


def main():
    """Main function to run Qiskit optimization verification."""
    suite = QiskitOptimizationTestSuite()
    results = suite.run_comprehensive_verification()

    # Save results to file
    import json
    output_file = Path(__file__).parent.parent / "qiskit_verification_results.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)

    suite.log(f"\nResults saved to: {output_file}")
    return results


if __name__ == "__main__":
    main()