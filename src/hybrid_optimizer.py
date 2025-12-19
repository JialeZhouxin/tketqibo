"""Hybrid Quantum Circuit Optimizer.

This module provides a unified interface for optimizing Qibo circuits
using a hybrid strategy combining TKET preprocessing and Qibo fusion.
"""

from typing import Dict, Optional, Tuple, Union
import time

from qibo import Circuit, gates
from optimization_engine import TketOptimizer


class HybridOptimizationStats:
    """Statistics for hybrid optimization process."""

    def __init__(self,
                 original_gates: int,
                 original_depth: int,
                 optimized_gates: int,
                 optimized_depth: int,
                 tket_compile_time: float,
                 fusion_time: float,
                 total_time: float):
        """Initialize optimization statistics.

        Args:
            original_gates: Number of gates in original circuit
            original_depth: Depth of original circuit
            optimized_gates: Number of gates after TKET optimization
            optimized_depth: Depth after TKET optimization
            tket_compile_time: Time taken for TKET compilation
            fusion_time: Time taken for Qibo fusion
            total_time: Total optimization time
        """
        self.original_gates = original_gates
        self.original_depth = original_depth
        self.optimized_gates = optimized_gates
        self.optimized_depth = optimized_depth
        self.tket_compile_time = tket_compile_time
        self.fusion_time = fusion_time
        self.total_time = total_time

        # Computed metrics
        self.gate_reduction = original_gates - optimized_gates
        self.gate_reduction_percent = (self.gate_reduction / original_gates * 100) if original_gates > 0 else 0
        self.depth_reduction = original_depth - optimized_depth
        self.depth_reduction_percent = (self.depth_reduction / original_depth * 100) if original_depth > 0 else 0

    def to_dict(self) -> Dict:
        """Convert statistics to dictionary."""
        return {
            'original_gates': self.original_gates,
            'optimized_gates': self.optimized_gates,
            'gate_reduction': self.gate_reduction,
            'gate_reduction_percent': self.gate_reduction_percent,
            'original_depth': self.original_depth,
            'optimized_depth': self.optimized_depth,
            'depth_reduction': self.depth_reduction,
            'depth_reduction_percent': self.depth_reduction_percent,
            'tket_compile_time': self.tket_compile_time,
            'fusion_time': self.fusion_time,
            'total_time': self.total_time
        }

    def summary(self) -> str:
        """Return a formatted summary string."""
        return (f"Hybrid Optimization Summary:\n"
                f"  Gates: {self.original_gates} → {self.optimized_gates} "
                f"({self.gate_reduction_percent:+.1f}%)\n"
                f"  Depth: {self.original_depth} → {self.optimized_depth} "
                f"({self.depth_reduction_percent:+.1f}%)\n"
                f"  TKET compile: {self.tket_compile_time:.4f}s\n"
                f"  Qibo fusion: {self.fusion_time:.4f}s\n"
                f"  Total time: {self.total_time:.4f}s")


class HybridOptimizer:
    """Hybrid quantum circuit optimizer combining TKET and Qibo fusion."""

    def __init__(self, strategy: str = "simulation"):
        """Initialize the hybrid optimizer.

        Args:
            strategy: TKET optimization strategy ('base', 'light', 'aggressive', 'sim-fusion', 'hardware', 'simulation')
        """
        self.tket_optimizer = TketOptimizer(strategy=strategy)

    def validate_circuit(self, circuit: Circuit) -> None:
        """Validate input circuit.

        Args:
            circuit: Qibo circuit to validate

        Raises:
            ValueError: If circuit is invalid or contains unsupported gates
        """
        if not isinstance(circuit, Circuit):
            raise ValueError(f"Input must be a Qibo Circuit, got {type(circuit)}")

        if circuit.nqubits == 0:
            raise ValueError("Circuit must have at least one qubit")

        if len(circuit.queue) == 0:
            raise ValueError("Circuit must contain at least one gate")

        # Check for supported gate types
        supported_gates = {
            gates.H, gates.X, gates.Y, gates.Z,
            gates.CNOT, gates.CZ, gates.SWAP,
            gates.RX, gates.RY, gates.RZ,
            gates.CU1, gates.U3, gates.SX
        }

        unsupported_gates = []
        for gate in circuit.queue:
            gate_type = type(gate)
            if gate_type not in supported_gates:
                unsupported_gates.append(gate_type.__name__)

        if unsupported_gates:
            unique_unsupported = list(set(unsupported_gates))
            raise ValueError(f"Circuit contains unsupported gate types: {unique_unsupported}")

    def _calculate_depth(self, circuit: Circuit) -> int:
        """Calculate the depth of a Qibo circuit.

        Args:
            circuit: Qibo circuit

        Returns:
            Circuit depth
        """
        if not circuit.queue:
            return 0

        depth = 0
        used_qubits = set()

        for gate in circuit.queue:
            try:
                if hasattr(gate, 'target_qubits'):
                    gate_qubits = set(gate.target_qubits)
                elif hasattr(gate, 'control_qubits') and hasattr(gate, 'target_qubits'):
                    gate_qubits = set(gate.control_qubits) | set(gate.target_qubits)
                elif hasattr(gate, 'qubits'):
                    gate_qubits = set(gate.qubits)
                else:
                    gate_qubits = set()

                if gate_qubits.isdisjoint(used_qubits):
                    used_qubits.update(gate_qubits)
                else:
                    depth += 1
                    used_qubits = gate_qubits
            except:
                depth += 1
                used_qubits = set()

        if used_qubits:
            depth += 1

        return depth


def optimize_qibo_circuit_hybrid(
    circuit: Circuit,
    return_stats: bool = False,
    verbose: bool = False,
    strategy: str = "simulation"
) -> Union[Circuit, Tuple[Circuit, HybridOptimizationStats]]:
    """Optimize a Qibo circuit using hybrid TKET + Qibo fusion strategy.

    This function applies a two-phase optimization:
    1. TKET preprocessing with specified strategy
    2. Qibo fusion (matrix-level optimization)

    Args:
        circuit: Input Qibo circuit to optimize
        return_stats: Whether to return optimization statistics
        verbose: Whether to print detailed optimization progress
        strategy: TKET optimization strategy ('base', 'light', 'aggressive', 'sim-fusion', 'hardware', 'simulation')

    Returns:
        Optimized Qibo circuit. If return_stats=True, returns tuple of
        (optimized_circuit, optimization_stats).

    Raises:
        ValueError: If input circuit is invalid or contains unsupported gates

    Example:
        >>> from algorithms import generate_hea_circuit
        >>> circuit = generate_hea_circuit(10, layers=3)
        >>> optimized = optimize_qibo_circuit_hybrid(circuit)
        >>> # Or with statistics
        >>> optimized, stats = optimize_qibo_circuit_hybrid(circuit, return_stats=True)
        >>> print(stats.summary())
    """
    # Initialize optimizer
    optimizer = HybridOptimizer(strategy=strategy)

    # Validate input
    optimizer.validate_circuit(circuit)

    # Get initial statistics
    original_gates = len(circuit.queue)
    original_depth = optimizer._calculate_depth(circuit)

    if verbose:
        print(f"Starting hybrid optimization...")
        print(f"Original circuit: {original_gates} gates, depth {original_depth}")

    # Start timing
    total_start_time = time.perf_counter()

    # Phase 1: TKET preprocessing (simulation mode)
    if verbose:
        print("\nPhase 1: TKET preprocessing (simulation mode)...")

    tket_start_time = time.perf_counter()

    try:
        tket_result = optimizer.tket_optimizer.optimize_circuit(circuit, strategy=strategy)
        tket_optimized_circuit = tket_result.optimized_circuit
        tket_compile_time = time.perf_counter() - tket_start_time

        if verbose:
            print(f"TKET optimization completed in {tket_compile_time:.4f}s")
            print(f"After TKET: {tket_result.optimized_gates} gates, depth {tket_result.optimized_depth}")
            print(f"Gate reduction: {tket_result.gate_reduction_percent:+.1f}%")
            print(f"Depth reduction: {tket_result.depth_reduction_percent:+.1f}%")

    except Exception as e:
        # Fallback: use original circuit if TKET fails
        if verbose:
            print(f"TKET optimization failed: {e}")
            print("Falling back to original circuit...")
        tket_optimized_circuit = circuit
        tket_compile_time = time.perf_counter() - tket_start_time

    optimized_gates = len(tket_optimized_circuit.queue)
    optimized_depth = optimizer._calculate_depth(tket_optimized_circuit)

    # Phase 2: Qibo fusion
    if verbose:
        print("\nPhase 2: Qibo fusion (matrix-level optimization)...")

    fusion_start_time = time.perf_counter()

    try:
        # Create a copy for fusion to avoid modifying the TKET result
        fused_circuit = Circuit(tket_optimized_circuit.nqubits)
        for gate in tket_optimized_circuit.queue:
            fused_circuit.add(gate)

        # Apply Qibo fusion
        final_circuit = fused_circuit.fuse()
        fusion_time = time.perf_counter() - fusion_start_time

        if verbose:
            print(f"Qibo fusion completed in {fusion_time:.4f}s")
            print(f"Final circuit ready for execution")

    except Exception as e:
        # Fallback: use TKET result if fusion fails
        if verbose:
            print(f"Qibo fusion failed: {e}")
            print("Using TKET-optimized circuit...")
        final_circuit = tket_optimized_circuit
        fusion_time = time.perf_counter() - fusion_start_time

    # Calculate total time
    total_time = time.perf_counter() - total_start_time

    # Create statistics
    stats = HybridOptimizationStats(
        original_gates=original_gates,
        original_depth=original_depth,
        optimized_gates=optimized_gates,
        optimized_depth=optimized_depth,
        tket_compile_time=tket_compile_time,
        fusion_time=fusion_time,
        total_time=total_time
    )

    if verbose:
        print(f"\n{'='*50}")
        print("Hybrid Optimization Complete!")
        print(stats.summary())
        print(f"{'='*50}")

    # Return results
    if return_stats:
        return final_circuit, stats
    else:
        return final_circuit