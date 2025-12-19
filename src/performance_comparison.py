"""Performance Comparison Engine for Sim-Fusion vs Qibo Fusion.

This module provides comprehensive performance comparison between Sim-Fusion
and Qibo native fusion optimization strategies, including statistical analysis
and detailed metrics collection.
"""

import time
import gc
import sys
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
from typing import Dict, List, Optional, Any, Tuple
import numpy as np
from qibo import Circuit, gates

# Import Sim-Fusion components
try:
    from sim_fusion import sim_fusion, SimFusionStats
    SIM_FUSION_AVAILABLE = True
except ImportError:
    SIM_FUSION_AVAILABLE = False

# Import Qibo fusion capabilities
try:
    from qibo.models import Circuit
    QIBO_FUSION_AVAILABLE = True
except ImportError:
    QIBO_FUSION_AVAILABLE = False


class PerformanceMetrics:
    """Detailed performance metrics for optimization comparison."""

    def __init__(self,
                 method_name: str,
                 original_gates: int = 0,
                 original_depth: int = 0,
                 optimized_gates: int = 0,
                 optimized_depth: int = 0,
                 optimization_time: float = 0.0,
                 memory_usage_mb: float = 0.0,
                 success: bool = True,
                 error_message: Optional[str] = None):
        """Initialize performance metrics.

        Args:
            method_name: Name of the optimization method
            original_gates: Number of gates in original circuit
            original_depth: Depth of original circuit
            optimized_gates: Number of gates after optimization
            optimized_depth: Depth after optimization
            optimization_time: Time taken for optimization (seconds)
            memory_usage_mb: Peak memory usage during optimization (MB)
            success: Whether optimization was successful
            error_message: Error message if optimization failed
        """
        self.method_name = method_name
        self.original_gates = original_gates
        self.original_depth = original_depth
        self.optimized_gates = optimized_gates
        self.optimized_depth = optimized_depth
        self.optimization_time = optimization_time
        self.memory_usage_mb = memory_usage_mb
        self.success = success
        self.error_message = error_message

    @property
    def gate_reduction(self) -> int:
        """Gate reduction count."""
        return self.original_gates - self.optimized_gates

    @property
    def gate_reduction_percent(self) -> float:
        """Gate reduction percentage."""
        if self.original_gates == 0:
            return 0.0
        return (self.gate_reduction / self.original_gates) * 100.0

    @property
    def depth_reduction(self) -> int:
        """Depth reduction count."""
        return self.original_depth - self.optimized_depth

    @property
    def depth_reduction_percent(self) -> float:
        """Depth reduction percentage."""
        if self.original_depth == 0:
            return 0.0
        return (self.depth_reduction / self.original_depth) * 100.0

    @property
    def efficiency_score(self) -> float:
        """Optimization efficiency score (%/s)."""
        if self.optimization_time == 0:
            return 0.0
        avg_reduction = (self.gate_reduction_percent + self.depth_reduction_percent) / 2.0
        return avg_reduction / self.optimization_time

    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary."""
        return {
            'method_name': self.method_name,
            'original_gates': self.original_gates,
            'optimized_gates': self.optimized_gates,
            'gate_reduction': self.gate_reduction,
            'gate_reduction_percent': self.gate_reduction_percent,
            'original_depth': self.original_depth,
            'optimized_depth': self.optimized_depth,
            'depth_reduction': self.depth_reduction,
            'depth_reduction_percent': self.depth_reduction_percent,
            'optimization_time': self.optimization_time,
            'memory_usage_mb': self.memory_usage_mb,
            'efficiency_score': self.efficiency_score,
            'success': self.success,
            'error_message': self.error_message
        }


class MemoryMonitor:
    """Monitor memory usage during optimization."""

    def __init__(self):
        """Initialize memory monitor."""
        self.peak_memory = 0.0
        self.start_time = None
        self.psutil_available = PSUTIL_AVAILABLE
        if self.psutil_available:
            try:
                import os
                self.process = psutil.Process(os.getpid())
            except:
                self.psutil_available = False

    def start_monitoring(self):
        """Start monitoring memory usage."""
        self.start_time = time.time()
        self.peak_memory = 0.0

    def update_peak(self):
        """Update peak memory usage."""
        if self.psutil_available and hasattr(self, 'process'):
            try:
                current_memory = self.process.memory_info().rss / (1024 * 1024)  # MB
                self.peak_memory = max(self.peak_memory, current_memory)
            except:
                pass

    def stop_monitoring(self) -> float:
        """Stop monitoring and return peak memory usage."""
        if self.start_time is not None:
            duration = time.time() - self.start_time
            self.start_time = None
        return self.peak_memory


class PerformanceComparisonEngine:
    """Engine for comparing Sim-Fusion vs Qibo fusion performance."""

    def __init__(self):
        """Initialize the performance comparison engine."""
        self.memory_monitor = MemoryMonitor()
        self.results_history: List[Dict[str, Any]] = []

    def get_circuit_depth(self, circuit: Circuit) -> int:
        """Calculate circuit depth."""
        try:
            # Try to get depth if available
            if hasattr(circuit, 'depth'):
                return circuit.depth()
            else:
                # Calculate depth manually
                depth = 0
                qubit_levels = [0] * circuit.nqubits

                for gate in circuit.queue:
                    gate_qubits = list(gate.qubits)
                    max_level = max(qubit_levels[q] for q in gate_qubits)
                    for q in gate_qubits:
                        qubit_levels[q] = max_level + 1
                    depth = max(depth, max_level + 1)

                return depth
        except:
            # Fallback to simple gate count
            return circuit.ngates

    def optimize_with_sim_fusion(self, circuit: Circuit, verbose: bool = False) -> PerformanceMetrics:
        """Optimize circuit using Sim-Fusion.

        Args:
            circuit: Quantum circuit to optimize
            verbose: Whether to print verbose output

        Returns:
            Performance metrics for Sim-Fusion optimization
        """
        if not SIM_FUSION_AVAILABLE:
            return PerformanceMetrics(
                method_name="Sim-Fusion",
                original_gates=circuit.ngates,
                original_depth=self.get_circuit_depth(circuit),
                success=False,
                error_message="Sim-Fusion not available"
            )

        original_gates = circuit.ngates
        original_depth = self.get_circuit_depth(circuit)

        try:
            # Start memory monitoring
            self.memory_monitor.start_monitoring()

            # Perform optimization
            start_time = time.time()
            optimized_circuit, stats = sim_fusion(circuit, return_stats=True, verbose=verbose)
            optimization_time = time.time() - start_time

            # Stop memory monitoring
            peak_memory = self.memory_monitor.stop_monitoring()

            return PerformanceMetrics(
                method_name="Sim-Fusion",
                original_gates=original_gates,
                original_depth=original_depth,
                optimized_gates=optimized_circuit.ngates,
                optimized_depth=self.get_circuit_depth(optimized_circuit),
                optimization_time=optimization_time,
                memory_usage_mb=peak_memory,
                success=True
            )

        except Exception as e:
            self.memory_monitor.stop_monitoring()
            return PerformanceMetrics(
                method_name="Sim-Fusion",
                original_gates=original_gates,
                original_depth=original_depth,
                success=False,
                error_message=str(e)
            )

    def optimize_with_qibo_fusion(self, circuit: Circuit, verbose: bool = False) -> PerformanceMetrics:
        """Optimize circuit using Qibo native fusion.

        Args:
            circuit: Quantum circuit to optimize
            verbose: Whether to print verbose output

        Returns:
            Performance metrics for Qibo fusion optimization
        """
        if not QIBO_FUSION_AVAILABLE:
            return PerformanceMetrics(
                method_name="Qibo Fusion",
                original_gates=circuit.ngates,
                original_depth=self.get_circuit_depth(circuit),
                success=False,
                error_message="Qibo fusion not available"
            )

        original_gates = circuit.ngates
        original_depth = self.get_circuit_depth(circuit)

        try:
            # Start memory monitoring
            self.memory_monitor.start_monitoring()

            # Perform optimization
            start_time = time.time()
            optimized_circuit = circuit.fuse()
            optimization_time = time.time() - start_time

            # Stop memory monitoring
            peak_memory = self.memory_monitor.stop_monitoring()

            return PerformanceMetrics(
                method_name="Qibo Fusion",
                original_gates=original_gates,
                original_depth=original_depth,
                optimized_gates=optimized_circuit.ngates,
                optimized_depth=self.get_circuit_depth(optimized_circuit),
                optimization_time=optimization_time,
                memory_usage_mb=peak_memory,
                success=True
            )

        except Exception as e:
            self.memory_monitor.stop_monitoring()
            return PerformanceMetrics(
                method_name="Qibo Fusion",
                original_gates=original_gates,
                original_depth=original_depth,
                success=False,
                error_message=str(e)
            )

    def compare_optimization_methods(self, circuit: Circuit,
                                     verbose: bool = False,
                                     iterations: int = 3) -> Dict[str, Any]:
        """Compare Sim-Fusion vs Qibo fusion on a single circuit.

        Args:
            circuit: Quantum circuit to test
            verbose: Whether to print verbose output
            iterations: Number of iterations for statistical significance

        Returns:
            Comparison results dictionary
        """
        circuit_id = f"circuit_{circuit.nqubits}q_{circuit.ngates}g"

        # Store results for each method and iteration
        sim_fusion_metrics = []
        qibo_fusion_metrics = []

        # Run multiple iterations for statistical significance
        for iteration in range(iterations):
            if verbose:
                print(f"Iteration {iteration + 1}/{iterations}")

            # Test Sim-Fusion
            sim_metrics = self.optimize_with_sim_fusion(circuit.copy(), verbose)
            sim_fusion_metrics.append(sim_metrics)

            # Test Qibo Fusion
            qibo_metrics = self.optimize_with_qibo_fusion(circuit.copy(), verbose)
            qibo_fusion_metrics.append(qibo_metrics)

            # Force garbage collection
            gc.collect()

        # Calculate statistics
        comparison_result = {
            'circuit_id': circuit_id,
            'circuit_info': {
                'n_qubits': circuit.nqubits,
                'n_gates': circuit.ngates,
                'depth': self.get_circuit_depth(circuit)
            },
            'sim_fusion': self._calculate_statistics(sim_fusion_metrics),
            'qibo_fusion': self._calculate_statistics(qibo_fusion_metrics),
            'comparison': self._compare_methods(sim_fusion_metrics, qibo_fusion_metrics),
            'iterations': iterations
        }

        # Add to history
        self.results_history.append(comparison_result)

        return comparison_result

    def _calculate_statistics(self, metrics_list: List[PerformanceMetrics]) -> Dict[str, Any]:
        """Calculate statistics for a list of metrics."""
        if not metrics_list:
            return {
                'success_rate': 0.0,
                'error_messages': []
            }

        successful_metrics = [m for m in metrics_list if m.success]
        failed_metrics = [m for m in metrics_list if not m.success]

        if not successful_metrics:
            return {
                'success_rate': 0.0,
                'error_messages': [m.error_message for m in failed_metrics]
            }

        # Calculate statistics
        gate_reductions = [m.gate_reduction_percent for m in successful_metrics]
        depth_reductions = [m.depth_reduction_percent for m in successful_metrics]
        optimization_times = [m.optimization_time for m in successful_metrics]
        memory_usage = [m.memory_usage_mb for m in successful_metrics]
        efficiency_scores = [m.efficiency_score for m in successful_metrics]

        return {
            'success_rate': len(successful_metrics) / len(metrics_list),
            'error_messages': [m.error_message for m in failed_metrics],
            'gate_reduction_mean': np.mean(gate_reductions),
            'gate_reduction_std': np.std(gate_reductions),
            'gate_reduction_min': np.min(gate_reductions),
            'gate_reduction_max': np.max(gate_reductions),
            'depth_reduction_mean': np.mean(depth_reductions),
            'depth_reduction_std': np.std(depth_reductions),
            'optimization_time_mean': np.mean(optimization_times),
            'optimization_time_std': np.std(optimization_times),
            'memory_usage_mean': np.mean(memory_usage),
            'memory_usage_std': np.std(memory_usage),
            'efficiency_score_mean': np.mean(efficiency_scores),
            'efficiency_score_std': np.std(efficiency_scores)
        }

    def _compare_methods(self, sim_metrics: List[PerformanceMetrics],
                        qibo_metrics: List[PerformanceMetrics]) -> Dict[str, Any]:
        """Compare two optimization methods."""
        successful_sim = [m for m in sim_metrics if m.success]
        successful_qibo = [m for m in qibo_metrics if m.success]

        if not successful_sim or not successful_qibo:
            return {
                'winner': 'inconclusive',
                'reason': 'One or both methods failed'
            }

        sim_gate_reductions = [m.gate_reduction_percent for m in successful_sim]
        qibo_gate_reductions = [m.gate_reduction_percent for m in successful_qibo]

        sim_times = [m.optimization_time for m in successful_sim]
        qibo_times = [m.optimization_time for m in successful_qibo]

        sim_efficiency = [m.efficiency_score for m in successful_sim]
        qibo_efficiency = [m.efficiency_score for m in successful_qibo]

        # Calculate comparison metrics
        gate_reduction_diff = np.mean(sim_gate_reductions) - np.mean(qibo_gate_reductions)
        time_diff = np.mean(qibo_times) - np.mean(sim_times)  # Positive means Sim-Fusion is faster
        efficiency_diff = np.mean(sim_efficiency) - np.mean(qibo_efficiency)

        # Determine winner based on multiple factors
        sim_score = 0
        qibo_score = 0

        # Gate reduction (40% weight)
        if gate_reduction_diff > 5:
            sim_score += 2
        elif gate_reduction_diff < -5:
            qibo_score += 2
        else:
            sim_score += 1
            qibo_score += 1

        # Time (30% weight)
        if time_diff > 0.1:
            sim_score += 2
        elif time_diff < -0.1:
            qibo_score += 2
        else:
            sim_score += 1
            qibo_score += 1

        # Efficiency (30% weight)
        if efficiency_diff > 10:
            sim_score += 2
        elif efficiency_diff < -10:
            qibo_score += 2
        else:
            sim_score += 1
            qibo_score += 1

        winner = 'tie'
        if sim_score > qibo_score:
            winner = 'Sim-Fusion'
        elif qibo_score > sim_score:
            winner = 'Qibo Fusion'

        return {
            'winner': winner,
            'sim_fusion_score': sim_score,
            'qibo_fusion_score': qibo_score,
            'gate_reduction_difference': gate_reduction_diff,
            'time_difference': time_diff,
            'efficiency_difference': efficiency_diff,
            'detailed_comparison': {
                'sim_fusion_better_gate_reduction': gate_reduction_diff > 0,
                'sim_fusion_faster': time_diff > 0,
                'sim_fusion_more_efficient': efficiency_diff > 0
            }
        }

    def run_comprehensive_benchmark(self, circuits: List[Dict[str, Any]],
                                   verbose: bool = False,
                                   iterations: int = 3) -> Dict[str, Any]:
        """Run comprehensive performance benchmark on multiple circuits.

        Args:
            circuits: List of circuit dictionaries
            verbose: Whether to print verbose output
            iterations: Number of iterations per circuit

        Returns:
            Comprehensive benchmark results
        """
        if verbose:
            print(f"Starting comprehensive benchmark on {len(circuits)} circuits...")
            print(f"Using {iterations} iterations per circuit")

        all_results = []
        successful_comparisons = 0
        failed_comparisons = 0

        for i, circuit_info in enumerate(circuits):
            circuit = circuit_info['circuit']
            circuit_id = circuit_info.get('circuit_id', f'circuit_{i}')

            if verbose:
                print(f"\n[{i+1}/{len(circuits)}] Testing {circuit_id}...")
                print(f"   Type: {circuit_info.get('type', 'unknown')}")
                print(f"   Gates: {circuit.ngates}, Qubits: {circuit.nqubits}")

            try:
                comparison_result = self.compare_optimization_methods(
                    circuit, verbose=False, iterations=iterations
                )
                comparison_result['circuit_info'] = circuit_info
                all_results.append(comparison_result)
                successful_comparisons += 1

                if verbose:
                    winner = comparison_result['comparison']['winner']
                    print(f"   Winner: {winner}")

            except Exception as e:
                if verbose:
                    print(f"   Error: {e}")
                failed_comparisons += 1

        # Generate summary statistics
        summary = self._generate_summary_statistics(all_results)

        return {
            'summary': summary,
            'detailed_results': all_results,
            'successful_comparisons': successful_comparisons,
            'failed_comparisons': failed_comparisons,
            'total_circuits': len(circuits),
            'iterations_per_circuit': iterations
        }

    def _generate_summary_statistics(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate summary statistics from all comparison results."""
        if not results:
            return {
                'overall_winner': 'inconclusive',
                'circuit_count': 0,
                'error': 'No results available'
            }

        winners = [r['comparison']['winner'] for r in results]
        winner_counts = {w: winners.count(w) for w in set(winners)}

        overall_winner = max(winner_counts, key=winner_counts.get) if winner_counts else 'inconclusive'

        # Calculate average performance metrics
        sim_stats = []
        qibo_stats = []

        for result in results:
            if 'sim_fusion' in result and result['sim_fusion']['success_rate'] > 0:
                sim_stats.append(result['sim_fusion'])
            if 'qibo_fusion' in result and result['qibo_fusion']['success_rate'] > 0:
                qibo_stats.append(result['qibo_fusion'])

        avg_sim_gate_reduction = np.mean([s['gate_reduction_mean'] for s in sim_stats]) if sim_stats else 0
        avg_qibo_gate_reduction = np.mean([s['gate_reduction_mean'] for s in qibo_stats]) if qibo_stats else 0

        return {
            'overall_winner': overall_winner,
            'winner_distribution': winner_counts,
            'circuit_count': len(results),
            'average_sim_fusion_gate_reduction': avg_sim_gate_reduction,
            'average_qibo_fusion_gate_reduction': avg_qibo_gate_reduction,
            'performance_improvement': avg_sim_gate_reduction - avg_qibo_gate_reduction,
            'success_rate': len([r for r in results if 'sim_fusion' in r and r['sim_fusion']['success_rate'] > 0 and
                                       'qibo_fusion' in r and r['qibo_fusion']['success_rate'] > 0]) / len(results)
        }


# Convenience functions
def compare_single_circuit(circuit: Circuit,
                          iterations: int = 5,
                          verbose: bool = False) -> Dict[str, Any]:
    """Compare Sim-Fusion vs Qibo fusion on a single circuit.

    Args:
        circuit: Quantum circuit to compare
        iterations: Number of iterations for statistical significance
        verbose: Whether to print verbose output

    Returns:
        Comparison results dictionary
    """
    engine = PerformanceComparisonEngine()
    return engine.compare_optimization_methods(circuit, verbose=verbose, iterations=iterations)


def run_performance_benchmark(circuits: List[Dict[str, Any]],
                              iterations: int = 3,
                              verbose: bool = False) -> Dict[str, Any]:
    """Run performance benchmark on multiple circuits.

    Args:
        circuits: List of circuit dictionaries
        iterations: Number of iterations per circuit
        verbose: Whether to print verbose output

    Returns:
        Comprehensive benchmark results
    """
    engine = PerformanceComparisonEngine()
    return engine.run_comprehensive_benchmark(circuits, verbose=verbose, iterations=iterations)