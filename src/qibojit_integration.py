"""QiboJIT Integration Module.

This module provides high-performance quantum circuit execution using QiboJIT
when available, with automatic fallback to standard Qibo.
"""

import time
from typing import Optional, Tuple, Union
import warnings

try:
    from qibojit import Circuit as JITCircuit
    from qibo import Circuit as QiboCircuit
    QIBOJIT_AVAILABLE = True
except ImportError:
    from qibo import Circuit as QiboCircuit
    QIBOJIT_AVAILABLE = False
    warnings.warn("QiboJIT not available. Using standard Qibo execution.")


class QiboJITExecutor:
    """Executor that automatically uses QiboJIT when beneficial."""

    def __init__(self, jit_threshold_qubits: int = 15, jit_threshold_depth: int = 50):
        """Initialize QiboJIT executor.

        Args:
            jit_threshold_qubits: Minimum qubits for JIT acceleration
            jit_threshold_depth: Minimum circuit depth for JIT acceleration
        """
        self.jit_threshold_qubits = jit_threshold_qubits
        self.jit_threshold_depth = jit_threshold_depth
        self.use_jit = QIBOJIT_AVAILABLE

    def should_use_jit(self, circuit: QiboCircuit) -> bool:
        """Determine if JIT should be used for this circuit.

        Args:
            circuit: Qibo circuit to evaluate

        Returns:
            True if JIT should be used, False otherwise
        """
        if not self.use_jit:
            return False

        # Check if circuit meets JIT thresholds
        n_qubits = circuit.nqubits
        depth = len(circuit.queue)

        return (n_qubits >= self.jit_threshold_qubits or
                depth >= self.jit_threshold_depth)

    def execute_circuit(self, circuit: QiboCircuit, nshots: int = 1000) -> Tuple:
        """Execute a circuit with automatic JIT selection.

        Args:
            circuit: Qibo circuit to execute
            nshots: Number of measurement shots

        Returns:
            Execution results
        """
        if self.should_use_jit(circuit):
            return self._execute_with_jit(circuit, nshots)
        else:
            return self._execute_with_qibo(circuit, nshots)

    def _execute_with_jit(self, circuit: QiboCircuit, nshots: int) -> Tuple:
        """Execute circuit using QiboJIT.

        Args:
            circuit: Qibo circuit to execute
            nshots: Number of measurement shots

        Returns:
            Execution results
        """
        try:
            # Convert Qibo circuit to JIT circuit
            jit_circuit = JITCircuit.from_qibo(circuit)

            # Execute with JIT
            if hasattr(jit_circuit, 'nshots'):
                return jit_circuit(nshots=nshots)
            else:
                return jit_circuit()

        except Exception as e:
            warnings.warn(f"QiboJIT execution failed: {e}. Falling back to Qibo.")
            return self._execute_with_qibo(circuit, nshots)

    def _execute_with_qibo(self, circuit: QiboCircuit, nshots: int) -> Tuple:
        """Execute circuit using standard Qibo.

        Args:
            circuit: Qibo circuit to execute
            nshots: Number of measurement shots

        Returns:
            Execution results
        """
        if hasattr(circuit, 'nshots'):
            return circuit(nshots=nshots)
        else:
            return circuit()

    def measure_execution_time(self, circuit: QiboCircuit, nshots: int = 1000,
                               warmup_runs: int = 1) -> dict:
        """Measure execution time with automatic JIT selection.

        Args:
            circuit: Qibo circuit to benchmark
            nshots: Number of measurement shots
            warmup_runs: Number of warmup runs before timing

        Returns:
            Dictionary with timing information
        """
        using_jit = self.should_use_jit(circuit)

        # Warmup runs
        for _ in range(warmup_runs):
            self.execute_circuit(circuit, nshots)

        # Measure execution time
        start_time = time.perf_counter()
        result = self.execute_circuit(circuit, nshots)
        end_time = time.perf_counter()

        execution_time = end_time - start_time

        return {
            'execution_time': execution_time,
            'using_jit': using_jit,
            'result': result,
            'n_qubits': circuit.nqubits,
            'circuit_depth': len(circuit.queue),
            'nshots': nshots
        }

    def benchmark_jit_vs_qibo(self, circuit: QiboCircuit, nshots: int = 1000,
                              repetitions: int = 5) -> dict:
        """Benchmark JIT vs standard Qibo execution.

        Args:
            circuit: Qibo circuit to benchmark
            nshots: Number of measurement shots
            repetitions: Number of repetitions for timing

        Returns:
            Benchmark results comparing JIT and Qibo performance
        """
        if not QIBOJIT_AVAILABLE:
            return {
                'error': 'QiboJIT not available',
                'qibo_time': None,
                'jit_time': None,
                'speedup': None
            }

        # Benchmark standard Qibo
        qibo_times = []
        for _ in range(repetitions):
            start_time = time.perf_counter()
            self._execute_with_qibo(circuit, nshots)
            end_time = time.perf_counter()
            qibo_times.append(end_time - start_time)

        # Benchmark JIT (if applicable)
        jit_times = []
        if self.should_use_jit(circuit):
            for _ in range(repetitions):
                start_time = time.perf_counter()
                self._execute_with_jit(circuit, nshots)
                end_time = time.perf_counter()
                jit_times.append(end_time - start_time)
        else:
            jit_times = None

        # Calculate statistics
        avg_qibo_time = sum(qibo_times) / len(qibo_times)
        std_qibo_time = (sum((t - avg_qibo_time) ** 2 for t in qibo_times) / len(qibo_times)) ** 0.5

        if jit_times:
            avg_jit_time = sum(jit_times) / len(jit_times)
            std_jit_time = (sum((t - avg_jit_time) ** 2 for t in jit_times) / len(jit_times)) ** 0.5
            speedup = avg_qibo_time / avg_jit_time
        else:
            avg_jit_time = None
            std_jit_time = None
            speedup = None

        return {
            'circuit_info': {
                'n_qubits': circuit.nqubits,
                'circuit_depth': len(circuit.queue),
                'should_use_jit': self.should_use_jit(circuit)
            },
            'qibo_time': {
                'average': avg_qibo_time,
                'std': std_qibo_time,
                'times': qibo_times
            },
            'jit_time': {
                'average': avg_jit_time,
                'std': std_jit_time,
                'times': jit_times
            } if jit_times else None,
            'speedup': speedup,
            'nshots': nshots,
            'repetitions': repetitions
        }


def create_optimized_executor(jit_threshold_qubits: int = 15,
                              jit_threshold_depth: int = 50) -> QiboJITExecutor:
    """Create an optimized QiboJIT executor.

    Args:
        jit_threshold_qubits: Minimum qubits for JIT acceleration
        jit_threshold_depth: Minimum circuit depth for JIT acceleration

    Returns:
        Configured QiboJITExecutor instance
    """
    return QiboJITExecutor(
        jit_threshold_qubits=jit_threshold_qubits,
        jit_threshold_depth=jit_threshold_depth
    )


# Global executor instance
_default_executor = None


def get_default_executor() -> QiboJITExecutor:
    """Get the default QiboJIT executor instance.

    Returns:
        Default QiboJITExecutor
    """
    global _default_executor
    if _default_executor is None:
        _default_executor = create_optimized_executor()
    return _default_executor


def execute_circuit_optimized(circuit, nshots: int = 1000) -> Tuple:
    """Execute a circuit using the optimized executor.

    Args:
        circuit: Qibo circuit to execute
        nshots: Number of measurement shots

    Returns:
        Execution results
    """
    executor = get_default_executor()
    return executor.execute_circuit(circuit, nshots)


def benchmark_circuit_performance(circuit, nshots: int = 1000,
                                 repetitions: int = 5) -> dict:
    """Benchmark circuit performance with optimal executor.

    Args:
        circuit: Qibo circuit to benchmark
        nshots: Number of measurement shots
        repetitions: Number of repetitions

    Returns:
        Performance benchmark results
    """
    executor = get_default_executor()
    return executor.measure_execution_time(circuit, nshots, warmup_runs=1)