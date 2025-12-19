"""Performance Optimizer for Comparison Framework.

This module provides optimization utilities to improve the efficiency and scalability
of the Sim-Fusion performance comparison framework.

Optimization Features:
- Parallel processing support
- Result caching system
- Memory usage optimization
- Batch processing optimization
- Adaptive iteration management
- Progress tracking and monitoring

Authors: Sim-Fusion Team
Version: 1.0.0
"""

import time
import threading
import hashlib
import pickle
from typing import Dict, List, Any, Optional, Callable, Tuple
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
import warnings
from pathlib import Path

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False


@dataclass
class OptimizationConfig:
    """Configuration for performance optimization."""
    enable_parallel_processing: bool = True
    max_workers: int = 4
    enable_caching: bool = True
    cache_size_limit: int = 1000
    enable_memory_monitoring: bool = True
    memory_limit_mb: float = 1024.0  # 1GB
    enable_adaptive_iterations: bool = True
    min_iterations: int = 2
    max_iterations: int = 10
    target_precision: float = 0.01
    enable_progress_tracking: bool = True


@dataclass
class OptimizationMetrics:
    """Metrics for optimization performance."""
    total_time_saved: float
    cache_hit_rate: float
    parallel_efficiency: float
    memory_usage_peak: float
    circuits_optimized: int
    average_speedup: float


class ResultCache:
    """Thread-safe result caching system."""

    def __init__(self, max_size: int = 1000):
        """Initialize the cache.

        Args:
            max_size: Maximum number of cached results
        """
        self.max_size = max_size
        self.cache = {}
        self.access_times = {}
        self.lock = threading.RLock()
        self.hits = 0
        self.misses = 0

    def _generate_key(self, circuit_data: Any, method_config: Dict[str, Any]) -> str:
        """Generate cache key from circuit and configuration."""
        # Create a hashable representation
        circuit_repr = str(circuit_data.ngates if hasattr(circuit_data, 'ngates') else circuit_data)
        config_repr = str(sorted(method_config.items()))
        combined = f"{circuit_repr}_{config_repr}"

        # Generate hash
        return hashlib.md5(combined.encode()).hexdigest()

    def get(self, circuit_data: Any, method_config: Dict[str, Any]) -> Optional[Any]:
        """Get cached result."""
        key = self._generate_key(circuit_data, method_config)

        with self.lock:
            if key in self.cache:
                self.access_times[key] = time.time()
                self.hits += 1
                return self.cache[key]
            else:
                self.misses += 1
                return None

    def put(self, circuit_data: Any, method_config: Dict[str, Any], result: Any):
        """Cache result."""
        key = self._generate_key(circuit_data, method_config)

        with self.lock:
            # Remove oldest if cache is full
            if len(self.cache) >= self.max_size:
                oldest_key = min(self.access_times.items(), key=lambda x: x[1])[0]
                del self.cache[oldest_key]
                del self.access_times[oldest_key]

            self.cache[key] = result
            self.access_times[key] = time.time()

    def get_hit_rate(self) -> float:
        """Get cache hit rate."""
        with self.lock:
            total = self.hits + self.misses
            return self.hits / max(total, 1)

    def clear(self):
        """Clear all cached results."""
        with self.lock:
            self.cache.clear()
            self.access_times.clear()
            self.hits = 0
            self.misses = 0


class MemoryMonitor:
    """Memory usage monitoring."""

    def __init__(self, limit_mb: float = 1024.0):
        """Initialize memory monitor.

        Args:
            limit_mb: Memory limit in MB
        """
        self.limit_mb = limit_mb
        self.peak_usage = 0.0
        self.monitoring = False
        self.monitor_thread = None

    def start_monitoring(self):
        """Start memory monitoring."""
        if not PSUTIL_AVAILABLE:
            warnings.warn("psutil not available, memory monitoring disabled")
            return

        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_memory, daemon=True)
        self.monitor_thread.start()

    def stop_monitoring(self):
        """Stop memory monitoring."""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1.0)

    def _monitor_memory(self):
        """Monitor memory usage in background."""
        process = psutil.Process()

        while self.monitoring:
            try:
                memory_mb = process.memory_info().rss / 1024 / 1024
                self.peak_usage = max(self.peak_usage, memory_mb)

                if memory_mb > self.limit_mb:
                    warnings.warn(f"Memory usage ({memory_mb:.1f} MB) exceeds limit ({self.limit_mb:.1f} MB)")

                time.sleep(1.0)  # Check every second

            except (psutil.NoSuchProcess, psutil.AccessDenied):
                break


class ProgressTracker:
    """Progress tracking for long-running optimizations."""

    def __init__(self, total_items: int = 0):
        """Initialize progress tracker.

        Args:
            total_items: Total number of items to process
        """
        self.total_items = total_items
        self.completed_items = 0
        self.start_time = time.time()
        self.lock = threading.Lock()

    def update(self, completed: int = 1):
        """Update progress.

        Args:
            completed: Number of items completed in this update
        """
        with self.lock:
            self.completed_items += completed

    def get_progress(self) -> Dict[str, Any]:
        """Get current progress information."""
        with self.lock:
            elapsed = time.time() - self.start_time

            if self.total_items > 0:
                progress_percent = (self.completed_items / self.total_items) * 100
                items_per_second = self.completed_items / max(elapsed, 0.001)
                eta_seconds = (self.total_items - self.completed_items) / max(items_per_second, 0.001)
            else:
                progress_percent = 0
                items_per_second = 0
                eta_seconds = 0

            return {
                'completed': self.completed_items,
                'total': self.total_items,
                'progress_percent': progress_percent,
                'elapsed_time': elapsed,
                'items_per_second': items_per_second,
                'eta_seconds': eta_seconds
            }


class AdaptiveIterationManager:
    """Manages adaptive number of iterations based on convergence."""

    def __init__(self, min_iterations: int = 2, max_iterations: int = 10,
                 target_precision: float = 0.01):
        """Initialize adaptive iteration manager.

        Args:
            min_iterations: Minimum number of iterations
            max_iterations: Maximum number of iterations
            target_precision: Target precision for convergence
        """
        self.min_iterations = min_iterations
        self.max_iterations = max_iterations
        self.target_precision = target_precision

    def determine_iterations(self, current_iteration: int, recent_results: List[float]) -> bool:
        """Determine if more iterations are needed.

        Args:
            current_iteration: Current iteration number
            recent_results: Results from recent iterations

        Returns:
            True if more iterations should be performed
        """
        # Must do minimum iterations
        if current_iteration < self.min_iterations:
            return True

        # Stop if reached maximum
        if current_iteration >= self.max_iterations:
            return False

        # Check convergence if we have enough results
        if len(recent_results) >= 3:
            # Calculate variance of recent results
            if NUMPY_AVAILABLE:
                variance = np.var(recent_results)
            else:
                mean_val = sum(recent_results) / len(recent_results)
                variance = sum((x - mean_val) ** 2 for x in recent_results) / len(recent_results)

            # Stop if converged
            if variance < self.target_precision:
                return False

        return True


class PerformanceOptimizer:
    """Main performance optimization system."""

    def __init__(self, config: Optional[OptimizationConfig] = None):
        """Initialize performance optimizer.

        Args:
            config: Optimization configuration
        """
        self.config = config or OptimizationConfig()

        # Initialize components
        self.cache = ResultCache(self.config.cache_size_limit) if self.config.enable_caching else None
        self.memory_monitor = MemoryMonitor(self.config.memory_limit_mb) if self.config.enable_memory_monitoring else None
        self.progress_tracker = None
        self.iteration_manager = AdaptiveIterationManager(
            self.config.min_iterations,
            self.config.max_iterations,
            self.config.target_precision
        ) if self.config.enable_adaptive_iterations else None

        # Metrics
        self.metrics = OptimizationMetrics(
            total_time_saved=0.0,
            cache_hit_rate=0.0,
            parallel_efficiency=0.0,
            memory_usage_peak=0.0,
            circuits_optimized=0,
            average_speedup=0.0
        )

    def optimize_batch_processing(self, circuits: List[Any],
                                optimization_func: Callable,
                                **kwargs) -> List[Any]:
        """Optimize batch processing of circuits.

        Args:
            circuits: List of circuits to optimize
            optimization_func: Function to call for each circuit
            **kwargs: Additional arguments for optimization function

        Returns:
            List of optimization results
        """
        if not self.config.enable_parallel_processing or len(circuits) == 1:
            return self._process_sequential(circuits, optimization_func, **kwargs)

        return self._process_parallel(circuits, optimization_func, **kwargs)

    def _process_sequential(self, circuits: List[Any],
                           optimization_func: Callable,
                           **kwargs) -> List[Any]:
        """Process circuits sequentially."""
        results = []
        start_time = time.time()

        if self.config.enable_progress_tracking:
            self.progress_tracker = ProgressTracker(len(circuits))

        try:
            if self.memory_monitor:
                self.memory_monitor.start_monitoring()

            for circuit in circuits:
                result = self._optimize_single_circuit(circuit, optimization_func, **kwargs)
                results.append(result)

                if self.progress_tracker:
                    self.progress_tracker.update()

        finally:
            if self.memory_monitor:
                self.memory_monitor.stop_monitoring()
                self.metrics.memory_usage_peak = self.memory_monitor.peak_usage

        total_time = time.time() - start_time
        self.metrics.circuits_optimized += len(circuits)

        return results

    def _process_parallel(self, circuits: List[Any],
                         optimization_func: Callable,
                         **kwargs) -> List[Any]:
        """Process circuits in parallel."""
        results = [None] * len(circuits)
        start_time = time.time()

        if self.config.enable_progress_tracking:
            self.progress_tracker = ProgressTracker(len(circuits))

        try:
            if self.memory_monitor:
                self.memory_monitor.start_monitoring()

            max_workers = min(self.config.max_workers, len(circuits))

            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                # Submit all tasks
                future_to_index = {
                    executor.submit(self._optimize_single_circuit, circuit, optimization_func, **kwargs): i
                    for i, circuit in enumerate(circuits)
                }

                # Collect results
                completed = 0
                for future in as_completed(future_to_index):
                    index = future_to_index[future]
                    try:
                        results[index] = future.result()
                        completed += 1

                        if self.progress_tracker:
                            self.progress_tracker.update()

                    except Exception as e:
                        results[index] = {'error': str(e)}
                        warnings.warn(f"Error processing circuit {index}: {e}")

        finally:
            if self.memory_monitor:
                self.memory_monitor.stop_monitoring()
                self.metrics.memory_usage_peak = self.memory_monitor.peak_usage

        total_time = time.time() - start_time
        self.metrics.circuits_optimized += len(circuits)

        # Calculate parallel efficiency
        if self.cache:
            self.metrics.cache_hit_rate = self.cache.get_hit_rate()

        return results

    def _optimize_single_circuit(self, circuit: Any,
                               optimization_func: Callable,
                               **kwargs) -> Any:
        """Optimize a single circuit with caching."""
        # Check cache first
        if self.cache:
            method_config = {k: v for k, v in kwargs.items() if k != 'circuit'}
            cached_result = self.cache.get(circuit, method_config)
            if cached_result is not None:
                return cached_result

        # Perform optimization
        result = optimization_func(circuit, **kwargs)

        # Cache result
        if self.cache and result is not None:
            method_config = {k: v for k, v in kwargs.items() if k != 'circuit'}
            self.cache.put(circuit, method_config, result)

        return result

    def adaptive_comparison(self, circuit: Any, comparison_func: Callable, **kwargs) -> Any:
        """Perform adaptive comparison with convergence detection."""
        if not self.config.enable_adaptive_iterations:
            return comparison_func(circuit, **kwargs)

        iterations = kwargs.get('iterations', 3)
        recent_results = []

        for iteration in range(1, self.config.max_iterations + 1):
            kwargs['iterations'] = 1  # Do one iteration at a time
            result = comparison_func(circuit, **kwargs)

            # Extract key metric (e.g., gate reduction)
            if hasattr(result, 'gate_reduction_percent'):
                metric = result.gate_reduction_percent
            elif isinstance(result, dict) and 'gate_reduction_percent' in result:
                metric = result['gate_reduction_percent']
            else:
                # If we can't extract a metric, use default iterations
                if iteration >= iterations:
                    break
                continue

            recent_results.append(metric)

            # Check if more iterations are needed
            if not self.iteration_manager.determine_iterations(iteration, recent_results[-3:]):
                break

        return result

    def get_progress_info(self) -> Optional[Dict[str, Any]]:
        """Get current progress information."""
        if self.progress_tracker:
            return self.progress_tracker.get_progress()
        return None

    def get_optimization_metrics(self) -> OptimizationMetrics:
        """Get optimization performance metrics."""
        if self.cache:
            self.metrics.cache_hit_rate = self.cache.get_hit_rate()

        return self.metrics

    def clear_cache(self):
        """Clear result cache."""
        if self.cache:
            self.cache.clear()

    def reset_metrics(self):
        """Reset optimization metrics."""
        self.metrics = OptimizationMetrics(
            total_time_saved=0.0,
            cache_hit_rate=0.0,
            parallel_efficiency=0.0,
            memory_usage_peak=0.0,
            circuits_optimized=0,
            average_speedup=0.0
        )


def create_optimized_performance_engine(config: Optional[OptimizationConfig] = None):
    """Create an optimized performance comparison engine.

    Args:
        config: Optimization configuration

    Returns:
        Optimized performance comparison engine
    """
    from performance_comparison import PerformanceComparisonEngine

    base_engine = PerformanceComparisonEngine()
    optimizer = PerformanceOptimizer(config)

    class OptimizedEngine:
        """Engine with performance optimizations."""

        def __init__(self, base_engine: PerformanceComparisonEngine, optimizer: PerformanceOptimizer):
            self.base_engine = base_engine
            self.optimizer = optimizer

        def compare_optimization_methods(self, circuit, iterations=3, **kwargs):
            """Compare methods with adaptive iterations."""
            if self.optimizer.config.enable_adaptive_iterations:
                return self.optimizer.adaptive_comparison(
                    circuit, self.base_engine.compare_optimization_methods,
                    iterations=iterations, **kwargs
                )
            else:
                return self.base_engine.compare_optimization_methods(circuit, iterations=iterations, **kwargs)

        def run_batch_comparison(self, circuits, iterations=3, **kwargs):
            """Run batch comparison with optimization."""

            def optimized_comparison(circuit):
                return self.compare_optimization_methods(circuit, iterations=iterations, **kwargs)

            return self.optimizer.optimize_batch_processing(
                circuits, optimized_comparison
            )

        def get_progress(self):
            """Get optimization progress."""
            return self.optimizer.get_progress_info()

        def get_metrics(self):
            """Get optimization metrics."""
            return self.optimizer.get_optimization_metrics()

        def clear_cache(self):
            """Clear optimization cache."""
            self.optimizer.clear_cache()

    return OptimizedEngine(base_engine, optimizer)


# Utility functions
def benchmark_optimization(circuits: List[Any],
                          baseline_func: Callable,
                          optimized_func: Callable,
                          iterations: int = 3) -> Dict[str, float]:
    """Benchmark optimization improvements.

    Args:
        circuits: List of circuits to test
        baseline_func: Baseline optimization function
        optimized_func: Optimized function
        iterations: Number of iterations for timing

    Returns:
        Benchmark results
    """
    print("Running benchmark...")

    # Benchmark baseline
    start_time = time.time()
    for _ in range(iterations):
        for circuit in circuits:
            baseline_func(circuit)
    baseline_time = time.time() - start_time

    # Benchmark optimized
    start_time = time.time()
    for _ in range(iterations):
        for circuit in circuits:
            optimized_func(circuit)
    optimized_time = time.time() - start_time

    speedup = baseline_time / max(optimized_time, 0.001)
    time_saved = baseline_time - optimized_time

    return {
        'baseline_time': baseline_time,
        'optimized_time': optimized_time,
        'speedup': speedup,
        'time_saved': time_saved,
        'time_saved_percent': (time_saved / baseline_time) * 100
    }


def auto_tune_configuration(circuits: List[Any]) -> OptimizationConfig:
    """Automatically tune optimization configuration based on system and workload.

    Args:
        circuits: Sample circuits for workload analysis

    Returns:
        Optimized configuration
    """
    config = OptimizationConfig()

    # Determine optimal worker count
    import os
    cpu_count = os.cpu_count() or 1

    # Consider circuit complexity and system resources
    if PSUTIL_AVAILABLE:
        available_memory_gb = psutil.virtual_memory().available / (1024**3)
        config.memory_limit_mb = min(available_memory_gb * 0.5, 2048)  # Use up to 50% of available memory

    # Adjust workers based on circuit size
    if circuits:
        avg_circuit_size = sum(c.ngates for c in circuits if hasattr(c, 'ngates')) / len(circuits)

        if avg_circuit_size > 50:
            # Large circuits: use fewer workers to avoid memory pressure
            config.max_workers = max(1, min(4, cpu_count // 2))
        else:
            # Small circuits: can use more workers
            config.max_workers = max(1, min(8, cpu_count))

    # Enable caching for repeated workloads
    config.enable_caching = len(circuits) > 10

    # Adaptive iterations for precision vs. speed trade-off
    config.enable_adaptive_iterations = len(circuits) > 5

    print(f"Auto-tuned configuration: {config.max_workers} workers, "
          f"cache: {config.enable_caching}, memory_limit: {config.memory_limit_mb:.0f} MB")

    return config