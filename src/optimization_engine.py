"""TKET Optimization Engine.

This module provides hardware-agnostic optimization for quantum circuits
using TKET's optimization passes, focusing on reducing gate count and depth
for improved simulation performance.
"""

from typing import Dict, List, Optional, Tuple
import time

from pytket import Circuit as TketCircuit, OpType
from pytket.passes import (
    SequencePass,
    CommuteThroughMultis,
    RemoveRedundancies,
    FullPeepholeOptimise,
    SimplifyInitial,
    EulerAngleReduction,
    SquashTK1,
    CliffordSimp,
)
from pytket.transform import Transform

from circuit_converter import CircuitConverter
from qibo import Circuit as QiboCircuit


class OptimizationResult:
    """Result of circuit optimization."""

    def __init__(self,
                 original_circuit: QiboCircuit,
                 optimized_circuit: QiboCircuit,
                 compile_time: float,
                 original_gates: int,
                 optimized_gates: int,
                 original_depth: int,
                 optimized_depth: int,
                 strategy: str = "unknown"):
        """Initialize optimization result.

        Args:
            original_circuit: Original Qibo circuit
            optimized_circuit: Optimized Qibo circuit
            compile_time: Time taken for optimization (seconds)
            original_gates: Number of gates in original circuit
            optimized_gates: Number of gates in optimized circuit
            original_depth: Depth of original circuit
            optimized_depth: Depth of optimized circuit
            strategy: Optimization strategy used
        """
        self.original_circuit = original_circuit
        self.optimized_circuit = optimized_circuit
        self.compile_time = compile_time
        self.strategy = strategy

        # Statistics
        self.original_gates = original_gates
        self.optimized_gates = optimized_gates
        self.original_depth = original_depth
        self.optimized_depth = optimized_depth

        # Computed metrics
        self.gate_reduction = original_gates - optimized_gates
        self.gate_reduction_percent = (self.gate_reduction / original_gates * 100) if original_gates > 0 else 0
        self.depth_reduction = original_depth - optimized_depth
        self.depth_reduction_percent = (self.depth_reduction / original_depth * 100) if original_depth > 0 else 0

    def summary(self) -> str:
        """Return a summary string of the optimization results."""
        return (f"Optimization completed in {self.compile_time:.4f}s\n"
                f"Gates: {self.original_gates} → {self.optimized_gates} "
                f"({self.gate_reduction_percent:.1f}% reduction)\n"
                f"Depth: {self.original_depth} → {self.optimized_depth} "
                f"({self.depth_reduction_percent:.1f}% reduction)")

    def __str__(self) -> str:
        return self.summary()


class TketOptimizer:
    """TKET-based optimizer for quantum circuits with multiple optimization strategies."""

    def __init__(self, strategy: str = "simulation"):
        """Initialize the optimizer with optimization passes.

        Args:
            strategy: Optimization strategy ('base', 'light', 'aggressive', 'sim-fusion', 'hardware', 'simulation')
        """
        self.converter = CircuitConverter()
        self.strategy = strategy

        # Define optimization profiles
        self.optimization_profiles = self._create_optimization_profiles()

        # Get the optimization pass for the selected strategy
        self.optimization_pass = self.optimization_profiles.get(strategy, self.optimization_profiles["simulation"])

        # Statistics tracking
        self.optimizations_performed = 0
        self.total_gates_reduced = 0

    def _create_optimization_profiles(self) -> Dict[str, SequencePass]:
        """Create different optimization profiles for various use cases."""

        profiles = {
            # Base: Minimal optimization (just identity removal)
            "base": SequencePass([
                RemoveRedundancies(),        # Only remove identities and clear redundancies
            ]),

            # Light: Basic cleanup with minimal overhead
            "light": SequencePass([
                RemoveRedundancies(),        # Remove redundant gates and identities
                CommuteThroughMultis(),      # Move multi-qubit gates through commutation
                RemoveRedundancies(),        # Final cleanup after commutation
            ]),

            # Aggressive: Full optimization pipeline
            "aggressive": SequencePass([
                CommuteThroughMultis(),      # Move multi-qubit gates through commutation
                RemoveRedundancies(),        # Remove redundant gates and identities
                CliffordSimp(),              # Simplify Clifford gate sequences
                FullPeepholeOptimise(),      # Full peephole optimization (decomposes gates)
                RemoveRedundancies(),        # Final cleanup
            ]),

            # Sim-Fusion: Optimized for Qibo simulator performance
            "sim-fusion": SequencePass([
                RemoveRedundancies(),        # Initial cleanup
                CommuteThroughMultis(),      # Allow gate reordering to find cancellations
                CliffordSimp(),              # Simplify Clifford gate sequences
                FullPeepholeOptimise(),      # Full peephole optimization
                SquashTK1(),                 # Merge single-qubit gates into TK1 form
                RemoveRedundancies(),        # Final cleanup
            ]),

            # Sim-Tuned: Pure simulation-focused optimization
            "sim-tuned": SequencePass([
                RemoveRedundancies(),        # Quick cleanup
                EulerAngleReduction(         # Optimize rotation chains for simulation
                    OpType.Rz, OpType.Rx, strict=False
                ),
                EulerAngleReduction(         # Optimize reverse rotation chains
                    OpType.Rx, OpType.Rz, strict=False
                ),
                SquashTK1(),                 # Maximize gate fusion for simulator
                CommuteThroughMultis(),      # Final commutation for fusion
                RemoveRedundancies(),        # Final cleanup
            ]),

            # Hardware: Legacy hardware optimization (for backward compatibility)
            "hardware": SequencePass([
                CommuteThroughMultis(),      # Move multi-qubit gates through commutation
                SimplifyInitial(),           # Simplify initial state
                RemoveRedundancies(),        # Remove redundant gates and identities
                CliffordSimp(),              # Simplify Clifford gate sequences
                FullPeepholeOptimise(),      # Full peephole optimization (decomposes gates)
            ]),

            # Simulation: Legacy simulation optimization (for backward compatibility)
            "simulation": SequencePass([
                CommuteThroughMultis(),      # Allow gate reordering to find cancellations
                SimplifyInitial(),           # Simplify initial state
                RemoveRedundancies(),        # Remove redundant gates and identities
                CliffordSimp(),              # Simplify Clifford gate sequences
                EulerAngleReduction(
                    OpType.Rz, OpType.Rx, strict=False
                ),                             # Squash Rz-Rx chains (helps with HEA)
                EulerAngleReduction(
                    OpType.Rx, OpType.Rz, strict=False
                ),                             # Squash Rx-Rz chains
                SquashTK1(),                   # Merge single-qubit gates into TK1 form
            ]),
        }

        return profiles

    def optimize_circuit(self, qibo_circuit: QiboCircuit, strategy: Optional[str] = None) -> OptimizationResult:
        """Optimize a Qibo circuit using TKET passes.

        Args:
            qibo_circuit: Input Qibo circuit
            strategy: Optimization strategy ('base', 'light', 'aggressive', 'sim-fusion', 'hardware', 'simulation', defaults to self.strategy)

        Returns:
            OptimizationResult: Results of the optimization
        """
        # Use provided strategy or default
        if strategy is None:
            strategy = self.strategy

        if strategy not in self.optimization_profiles:
            available = list(self.optimization_profiles.keys())
            raise ValueError(f"Invalid optimization strategy: {strategy}. Available: {available}")

        # Get initial statistics
        original_gates = len(qibo_circuit.queue)
        original_depth = self._calculate_depth(qibo_circuit)

        # Start timing
        start_time = time.perf_counter()

        # Convert to TKET
        tket_circuit = self.converter.qibo_to_tket(qibo_circuit)

        # Apply optimization based on strategy
        optimization_pass = self.optimization_profiles[strategy]
        optimization_pass.apply(tket_circuit)

        # Convert back to Qibo
        optimized_qibo_circuit = self.converter.tket_to_qibo(tket_circuit)

        # End timing
        end_time = time.perf_counter()
        compile_time = end_time - start_time

        # Get optimized statistics
        optimized_gates = len(optimized_qibo_circuit.queue)
        optimized_depth = self._calculate_depth(optimized_qibo_circuit)

        # Update statistics
        self.optimizations_performed += 1
        self.total_gates_reduced += (original_gates - optimized_gates)

        # Return result
        return OptimizationResult(
            original_circuit=qibo_circuit,
            optimized_circuit=optimized_qibo_circuit,
            compile_time=compile_time,
            original_gates=original_gates,
            optimized_gates=optimized_gates,
            original_depth=original_depth,
            optimized_depth=optimized_depth,
            strategy=strategy
        )

    def _calculate_depth(self, circuit: QiboCircuit) -> int:
        """Calculate the depth of a Qibo circuit.

        Args:
            circuit: Qibo circuit

        Returns:
            int: Circuit depth
        """
        if not circuit.queue:
            return 0

        # Simple depth calculation: count parallel gate layers
        depth = 0
        used_qubits = set()

        for gate in circuit.queue:
            # Get qubits this gate acts on
            gate_qubits = self._get_gate_qubits(gate)

            # Check if this gate can be executed in parallel with previous gates
            if gate_qubits.isdisjoint(used_qubits):
                # Parallel - continue current layer
                used_qubits.update(gate_qubits)
            else:
                # Sequential - start new layer
                depth += 1
                used_qubits = gate_qubits

        # Add final layer if there are pending gates
        if used_qubits:
            depth += 1

        return depth

    def _get_gate_qubits(self, gate) -> set:
        """Get the set of qubits a gate acts on."""
        try:
            if hasattr(gate, 'target_qubits'):
                return set(gate.target_qubits)
            elif hasattr(gate, 'control_qubits') and hasattr(gate, 'target_qubits'):
                return set(gate.control_qubits) | set(gate.target_qubits)
            elif hasattr(gate, 'qubits'):
                return set(gate.qubits)
            else:
                return set()
        except:
            return set()

    def get_statistics(self) -> Dict[str, int]:
        """Get optimizer statistics.

        Returns:
            Dict containing optimization statistics
        """
        return {
            'optimizations_performed': self.optimizations_performed,
            'total_gates_reduced': self.total_gates_reduced,
            'average_gates_reduced': (
                self.total_gates_reduced / self.optimizations_performed
                if self.optimizations_performed > 0 else 0
            )
        }

    def reset_statistics(self) -> None:
        """Reset optimizer statistics."""
        self.optimizations_performed = 0
        self.total_gates_reduced = 0