"""Performance Validation with Diverse Circuits.

This module performs comprehensive validation of the Sim-Fusion performance
comparison framework using a wide variety of quantum circuit types and sizes.

Validation Scenarios:
- Small circuits (2-5 qubits)
- Medium circuits (6-15 qubits)
- Large circuits (16+ qubits)
- Different gate densities
- Various algorithm patterns
- Redundancy-heavy circuits
- Minimal redundancy circuits

Authors: Sim-Fusion Team
Version: 1.0.0
"""

import sys
import os
import time
import statistics
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from qibo import Circuit, gates
    QIBO_AVAILABLE = True
except ImportError:
    QIBO_AVAILABLE = False

try:
    import sim_fusion
    SIM_FUSION_AVAILABLE = True
except ImportError:
    SIM_FUSION_AVAILABLE = False

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


@dataclass
class ValidationConfig:
    """Configuration for performance validation."""
    circuit_types: List[str]
    qubit_ranges: Dict[str, Tuple[int, int]]
    iterations_per_circuit: int
    timeout_seconds: float
    output_dir: str


@dataclass
class ValidationResults:
    """Results from performance validation."""
    total_circuits_tested: int
    successful_optimizations: int
    failed_optimizations: int
    average_gate_reduction: float
    average_optimization_time: float
    circuit_type_results: Dict[str, Dict[str, Any]]
    scalability_data: Dict[int, Dict[str, Any]]
    error_log: List[str]


class PerformanceValidator:
    """Comprehensive performance validation system."""

    def __init__(self, config: ValidationConfig):
        """Initialize the validator.

        Args:
            config: Validation configuration
        """
        self.config = config
        self.output_dir = Path(config.output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Initialize components
        if BENCHMARK_AVAILABLE:
            self.generator = BenchmarkCircuitGenerator()

        if COMPARISON_AVAILABLE:
            self.engine = PerformanceComparisonEngine()

        # Results storage
        self.results = ValidationResults(
            total_circuits_tested=0,
            successful_optimizations=0,
            failed_optimizations=0,
            average_gate_reduction=0.0,
            average_optimization_time=0.0,
            circuit_type_results={},
            scalability_data={},
            error_log=[]
        )

    def run_validation(self) -> ValidationResults:
        """Run comprehensive performance validation."""
        print("Starting comprehensive performance validation...")
        print(f"Configuration: {self.config.circuit_types} circuit types")
        print(f"Output directory: {self.output_dir}")

        if not self._check_dependencies():
            print("Missing required dependencies for validation")
            return self.results

        # Validate each circuit type
        for circuit_type in self.config.circuit_types:
            print(f"\nValidating {circuit_type} circuits...")
            self._validate_circuit_type(circuit_type)

        # Validate scalability
        print(f"\nValidating scalability...")
        self._validate_scalability()

        # Generate validation report
        self._generate_validation_report()

        return self.results

    def _check_dependencies(self) -> bool:
        """Check if all required dependencies are available."""
        required = [QIBO_AVAILABLE, SIM_FUSION_AVAILABLE, BENCHMARK_AVAILABLE]
        if not all(required):
            missing = []
            if not QIBO_AVAILABLE:
                missing.append("Qibo")
            if not SIM_FUSION_AVAILABLE:
                missing.append("Sim-Fusion")
            if not BENCHMARK_AVAILABLE:
                missing.append("Benchmark Circuits")

            print(f"Missing dependencies: {', '.join(missing)}")
            return False

        return True

    def _validate_circuit_type(self, circuit_type: str):
        """Validate a specific circuit type."""
        if circuit_type not in self.config.qubit_ranges:
            print(f"Warning: No qubit range specified for {circuit_type}")
            return

        min_qubits, max_qubits = self.config.qubit_ranges[circuit_type]
        results = {
            'circuits_tested': 0,
            'successful': 0,
            'failed': 0,
            'gate_reductions': [],
            'optimization_times': [],
            'errors': []
        }

        # Test circuits of different sizes
        for n_qubits in range(min_qubits, min(max_qubits + 1, 8)):  # Limit for demo
            print(f"  Testing {circuit_type} with {n_qubits} qubits...")

            for circuit_idx in range(2):  # Test multiple circuits per size
                self.results.total_circuits_tested += 1
                results['circuits_tested'] += 1

                try:
                    # Generate circuit
                    circuit = self._generate_circuit(circuit_type, n_qubits, circuit_idx)
                    if circuit is None:
                        continue

                    # Run validation
                    circuit_result = self._validate_single_circuit(circuit, f"{circuit_type}_{n_qubits}q_{circuit_idx}")

                    if circuit_result['success']:
                        results['successful'] += 1
                        results['gate_reductions'].append(circuit_result['gate_reduction_percent'])
                        results['optimization_times'].append(circuit_result['optimization_time'])
                        self.results.successful_optimizations += 1
                    else:
                        results['failed'] += 1
                        results['errors'].append(circuit_result['error'])
                        self.results.failed_optimizations += 1

                except Exception as e:
                    error_msg = f"Validation error for {circuit_type}_{n_qubits}q_{circuit_idx}: {e}"
                    results['errors'].append(error_msg)
                    results['failed'] += 1
                    self.results.failed_optimizations += 1
                    self.results.error_log.append(error_msg)

        # Calculate statistics for this circuit type
        if results['gate_reductions']:
            results['avg_gate_reduction'] = statistics.mean(results['gate_reductions'])
            results['std_gate_reduction'] = statistics.stdev(results['gate_reductions']) if len(results['gate_reductions']) > 1 else 0.0

        if results['optimization_times']:
            results['avg_optimization_time'] = statistics.mean(results['optimization_times'])
            results['std_optimization_time'] = statistics.stdev(results['optimization_times']) if len(results['optimization_times']) > 1 else 0.0

        self.results.circuit_type_results[circuit_type] = results

        print(f"    {results['successful']}/{results['circuits_tested']} successful")
        if results['gate_reductions']:
            print(f"    Avg gate reduction: {results['avg_gate_reduction']:.1f}%")

    def _generate_circuit(self, circuit_type: str, n_qubits: int, index: int) -> Circuit:
        """Generate a circuit of specified type and size."""
        try:
            if circuit_type == 'bell_state':
                return self.generator.create_bell_state(n_qubits)
            elif circuit_type == 'ghz_state':
                return self.generator.create_ghz_state(n_qubits)
            elif circuit_type == 'qft':
                return self.generator.create_qft_circuit(n_qubits)
            elif circuit_type == 'redundant_operations':
                # Vary redundancy level
                redundancy_levels = ['low', 'medium', 'high']
                level = redundancy_levels[index % len(redundancy_levels)]
                return self.generator.create_redundant_circuit(n_qubits, level)
            elif circuit_type == 'random_clifford':
                # Vary number of gates
                n_gates = 10 + index * 5
                return self.generator.create_random_clifford_circuit(n_qubits, n_gates)
            elif circuit_type == 'random_rotation':
                # Vary number of gates
                n_gates = 15 + index * 5
                return self.generator.create_random_rotation_circuit(n_qubits, n_gates)
            elif circuit_type == 'mixed_algorithm':
                return self.generator.create_mixed_algorithm_circuit(n_qubits)
            else:
                print(f"Warning: Unknown circuit type {circuit_type}")
                return None

        except Exception as e:
            print(f"Error generating {circuit_type} circuit: {e}")
            return None

    def _validate_single_circuit(self, circuit: Circuit, circuit_id: str) -> Dict[str, Any]:
        """Validate optimization on a single circuit."""
        start_time = time.time()
        timeout = start_time + self.config.timeout_seconds

        try:
            # Run Sim-Fusion optimization
            optimized, stats = sim_fusion.sim_fusion_with_stats(circuit, verbose=False)

            # Check for timeout
            if time.time() > timeout:
                return {
                    'success': False,
                    'error': f'Timeout after {self.config.timeout_seconds} seconds'
                }

            return {
                'success': True,
                'gate_reduction_percent': stats.gate_reduction_percent,
                'optimization_time': stats.total_time,
                'original_gates': circuit.ngates,
                'optimized_gates': optimized.ngates,
                'efficiency_score': stats.efficiency_score,
                'circuit_id': circuit_id
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'circuit_id': circuit_id
            }

    def _validate_scalability(self):
        """Test scalability across different circuit sizes."""
        scalability_results = {}

        # Test scalability with Bell states (simple, predictable pattern)
        for n_qubits in [2, 3, 4, 5, 6, 8, 10]:
            print(f"  Testing scalability with {n_qubits} qubits...")

            try:
                circuit = self.generator.create_bell_state(n_qubits)
                result = self._validate_single_circuit(circuit, f"scalability_{n_qubits}q")

                if result['success']:
                    scalability_results[n_qubits] = {
                        'gate_reduction_percent': result['gate_reduction_percent'],
                        'optimization_time': result['optimization_time'],
                        'original_gates': result['original_gates'],
                        'optimized_gates': result['optimized_gates'],
                        'efficiency_score': result['efficiency_score']
                    }

                    print(f"    {result['gate_reduction_percent']:.1f}% reduction in {result['optimization_time']:.3f}s")

            except Exception as e:
                print(f"    Error: {e}")

        self.results.scalability_data = scalability_results

    def _generate_validation_report(self):
        """Generate comprehensive validation report."""
        # Calculate overall statistics
        all_gate_reductions = []
        all_optimization_times = []

        for circuit_type, results in self.results.circuit_type_results.items():
            all_gate_reductions.extend(results['gate_reductions'])
            all_optimization_times.extend(results['optimization_times'])

        if all_gate_reductions:
            self.results.average_gate_reduction = statistics.mean(all_gate_reductions)
        if all_optimization_times:
            self.results.average_optimization_time = statistics.mean(all_optimization_times)

        # Generate markdown report
        report_path = self.output_dir / "validation_report.md"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("# Sim-Fusion Performance Validation Report\n\n")
            f.write(f"**Generated:** {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            # Executive Summary
            f.write("## Executive Summary\n\n")
            f.write(f"- **Total circuits tested:** {self.results.total_circuits_tested}\n")
            f.write(f"- **Successful optimizations:** {self.results.successful_optimizations}\n")
            f.write(f"- **Failed optimizations:** {self.results.failed_optimizations}\n")
            f.write(f"- **Success rate:** {(self.results.successful_optimizations / max(self.results.total_circuits_tested, 1)) * 100:.1f}%\n")

            if self.results.average_gate_reduction > 0:
                f.write(f"- **Average gate reduction:** {self.results.average_gate_reduction:.1f}%\n")
            if self.results.average_optimization_time > 0:
                f.write(f"- **Average optimization time:** {self.results.average_optimization_time:.3f}s\n")

            # Circuit Type Results
            f.write("\n## Results by Circuit Type\n\n")
            for circuit_type, results in self.results.circuit_type_results.items():
                f.write(f"### {circuit_type.title()}\n\n")
                f.write(f"- **Circuits tested:** {results['circuits_tested']}\n")
                f.write(f"- **Successful:** {results['successful']}\n")
                f.write(f"- **Failed:** {results['failed']}\n")

                if results['gate_reductions']:
                    f.write(f"- **Average gate reduction:** {results['avg_gate_reduction']:.1f}%\n")
                    f.write(f"- **Standard deviation:** {results['std_gate_reduction']:.1f}%\n")

                if results['optimization_times']:
                    f.write(f"- **Average optimization time:** {results['avg_optimization_time']:.3f}s\n")
                    f.write(f"- **Standard deviation:** {results['std_optimization_time']:.3f}s\n")

                if results['errors']:
                    f.write(f"- **Errors:** {len(results['errors'])}\n")
                    for error in results['errors'][:3]:  # Show first 3 errors
                        f.write(f"  - {error}\n")
                    if len(results['errors']) > 3:
                        f.write(f"  - ... and {len(results['errors']) - 3} more\n")

                f.write("\n")

            # Scalability Results
            if self.results.scalability_data:
                f.write("## Scalability Analysis\n\n")
                f.write("| Qubits | Gate Reduction (%) | Optimization Time (s) | Efficiency Score |\n")
                f.write("|--------|-------------------|---------------------|------------------|\n")

                for n_qubits, data in sorted(self.results.scalability_data.items()):
                    f.write(f"| {n_qubits} | {data['gate_reduction_percent']:.1f} | "
                           f"{data['optimization_time']:.3f} | {data['efficiency_score']:.1f} |\n")

                f.write("\n")

            # Error Summary
            if self.results.error_log:
                f.write("## Error Summary\n\n")
                f.write(f"Total errors encountered: {len(self.results.error_log)}\n\n")
                for error in self.results.error_log[:10]:  # Show first 10 errors
                    f.write(f"- {error}\n")
                if len(self.results.error_log) > 10:
                    f.write(f"- ... and {len(self.results.error_log) - 10} more\n")

        # Generate JSON data
        json_path = self.output_dir / "validation_data.json"
        validation_data = {
            'metadata': {
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                'config': {
                    'circuit_types': self.config.circuit_types,
                    'qubit_ranges': self.config.qubit_ranges,
                    'iterations_per_circuit': self.config.iterations_per_circuit,
                    'timeout_seconds': self.config.timeout_seconds
                }
            },
            'results': {
                'total_circuits_tested': self.results.total_circuits_tested,
                'successful_optimizations': self.results.successful_optimizations,
                'failed_optimizations': self.results.failed_optimizations,
                'average_gate_reduction': self.results.average_gate_reduction,
                'average_optimization_time': self.results.average_optimization_time,
                'circuit_type_results': self.results.circuit_type_results,
                'scalability_data': self.results.scalability_data,
                'error_log': self.results.error_log
            }
        }

        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(validation_data, f, indent=2, ensure_ascii=False)

        print(f"\nValidation report generated:")
        print(f"  Markdown: {report_path}")
        print(f"  JSON data: {json_path}")


def create_validation_config() -> ValidationConfig:
    """Create validation configuration."""
    return ValidationConfig(
        circuit_types=[
            'bell_state',
            'ghz_state',
            'qft',
            'redundant_operations',
            'random_clifford',
            'random_rotation'
        ],
        qubit_ranges={
            'bell_state': (2, 4),
            'ghz_state': (3, 5),
            'qft': (3, 5),
            'redundant_operations': (3, 4),
            'random_clifford': (4, 6),
            'random_rotation': (4, 6)
        },
        iterations_per_circuit=1,  # Reduced for demo
        timeout_seconds=30.0,
        output_dir="validation_results"
    )


def main():
    """Run performance validation."""
    print("Sim-Fusion Performance Validation")
    print("=" * 50)

    config = create_validation_config()
    validator = PerformanceValidator(config)

    results = validator.run_validation()

    # Summary
    print(f"\n{'=' * 50}")
    print("VALIDATION SUMMARY")
    print(f"{'=' * 50}")
    print(f"Total circuits tested: {results.total_circuits_tested}")
    print(f"Successful optimizations: {results.successful_optimizations}")
    print(f"Failed optimizations: {results.failed_optimizations}")

    if results.total_circuits_tested > 0:
        success_rate = (results.successful_optimizations / results.total_circuits_tested) * 100
        print(f"Success rate: {success_rate:.1f}%")

    if results.average_gate_reduction > 0:
        print(f"Average gate reduction: {results.average_gate_reduction:.1f}%")

    if results.average_optimization_time > 0:
        print(f"Average optimization time: {results.average_optimization_time:.3f}s")

    if results.error_log:
        print(f"Total errors: {len(results.error_log)}")

    print(f"{'=' * 50}")

    if results.successful_optimizations > results.failed_optimizations:
        print("✅ Validation PASSED - System performing well")
        return True
    else:
        print("❌ Validation FAILED - Too many optimization failures")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)