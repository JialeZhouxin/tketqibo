"""Benchmark Circuit Generator for Performance Comparison.

This module provides functions to generate various types of quantum circuits
for testing Sim-Fusion vs Qibo fusion performance, including Bell states,
GHZ states, QFT, QAOA, VQE, and circuits with redundant operations.
"""

from typing import List, Optional, Dict, Any, Tuple
import numpy as np
from qibo import Circuit, gates


class BenchmarkCircuitGenerator:
    """Generator for diverse quantum circuit benchmarks."""

    def __init__(self):
        """Initialize the circuit generator."""
        self.circuit_types = [
            'bell_state',
            'ghz_state',
            'qft',
            'qaoa',
            'vqe',
            'random_clifford',
            'random_rotation',
            'redundant_operations',
            'mixed_algorithm'
        ]

    def create_bell_state(self, n_qubits: int = 2) -> Circuit:
        """Create a Bell state circuit.

        Args:
            n_qubits: Number of qubits (default 2)

        Returns:
            Bell state circuit
        """
        circuit = Circuit(n_qubits)
        circuit.add(gates.H(0))

        # Create Bell state with multiple CNOTs if more qubits
        for i in range(1, n_qubits):
            circuit.add(gates.CNOT(0, i))

        return circuit

    def create_ghz_state(self, n_qubits: int = 3) -> Circuit:
        """Create a GHZ state circuit.

        Args:
            n_qubits: Number of qubits

        Returns:
            GHZ state circuit
        """
        circuit = Circuit(n_qubits)
        circuit.add(gates.H(0))

        for i in range(1, n_qubits):
            circuit.add(gates.CNOT(0, i))

        return circuit

    def create_qft_circuit(self, n_qubits: int = 4) -> Circuit:
        """Create a Quantum Fourier Transform circuit.

        Args:
            n_qubits: Number of qubits

        Returns:
            QFT circuit
        """
        circuit = Circuit(n_qubits)

        # QFT algorithm
        for j in range(n_qubits):
            circuit.add(gates.H(j))
            for k in range(j + 1, n_qubits):
                angle = np.pi / (2 ** (k - j))
                circuit.add(gates.CU1(angle, j, k))

        # Reverse qubit order
        for j in range(n_qubits // 2):
            circuit.add(gates.SWAP(j, n_qubits - 1 - j))

        return circuit

    def create_qaoa_circuit(self, n_qubits: int = 4, depth: int = 2) -> Circuit:
        """Create a QAOA circuit.

        Args:
            n_qubits: Number of qubits
            depth: QAOA depth (number of layers)

        Returns:
            QAOA circuit
        """
        circuit = Circuit(n_qubits)

        # Initial state
        for i in range(n_qubits):
            circuit.add(gates.H(i))

        # QAOA layers
        for layer in range(depth):
            # Problem unitary (ZZ interactions)
            for i in range(n_qubits):
                for j in range(i + 1, n_qubits):
                    if np.random.random() < 0.3:  # Random connectivity
                        gamma = np.random.uniform(0, np.pi)
                        circuit.add(gates.CZ(i, j))
                        circuit.add(gates.RZ(gamma, i))
                        circuit.add(gates.RZ(gamma, j))

            # Mixer unitary (X rotations)
            for i in range(n_qubits):
                beta = np.random.uniform(0, np.pi)
                circuit.add(gates.RX(beta, i))

        return circuit

    def create_vqe_ansatz(self, n_qubits: int = 4, depth: int = 3) -> Circuit:
        """Create a VQE ansatz circuit.

        Args:
            n_qubits: Number of qubits
            depth: Ansatz depth

        Returns:
            VQE ansatz circuit
        """
        circuit = Circuit(n_qubits)

        # Hardware-efficient ansatz
        for layer in range(depth):
            # Entangling layer
            for i in range(0, n_qubits - 1, 2):
                circuit.add(gates.CNOT(i, i + 1))

            if n_qubits % 2 == 0:
                for i in range(1, n_qubits - 1, 2):
                    circuit.add(gates.CNOT(i, i + 1))
            else:
                for i in range(1, n_qubits, 2):
                    circuit.add(gates.CNOT(i, (i + 1) % n_qubits))

            # Parameterized single-qubit rotations
            for i in range(n_qubits):
                theta = np.random.uniform(0, 2 * np.pi)
                circuit.add(gates.RY(theta, i))

                if np.random.random() < 0.5:
                    phi = np.random.uniform(0, 2 * np.pi)
                    circuit.add(gates.RZ(phi, i))

        return circuit

    def create_random_clifford_circuit(self, n_qubits: int = 5, n_gates: int = 20) -> Circuit:
        """Create a random Clifford circuit.

        Args:
            n_qubits: Number of qubits
            n_gates: Number of random gates

        Returns:
            Random Clifford circuit
        """
        circuit = Circuit(n_qubits)

        clifford_gates = [gates.H, gates.X, gates.Y, gates.Z, gates.S, gates.SDG]
        two_qubit_gates = [gates.CNOT, gates.CZ]

        for _ in range(n_gates):
            if np.random.random() < 0.7:  # 70% single-qubit gates
                gate_type = np.random.choice(clifford_gates)
                qubit = np.random.randint(0, n_qubits)
                circuit.add(gate_type(qubit))
            else:  # 30% two-qubit gates
                gate_type = np.random.choice(two_qubit_gates)
                qubit1 = np.random.randint(0, n_qubits)
                qubit2 = np.random.randint(0, n_qubits)
                while qubit2 == qubit1:
                    qubit2 = np.random.randint(0, n_qubits)
                circuit.add(gate_type(qubit1, qubit2))

        return circuit

    def create_random_rotation_circuit(self, n_qubits: int = 5, n_gates: int = 20) -> Circuit:
        """Create a random circuit with rotation gates.

        Args:
            n_qubits: Number of qubits
            n_gates: Number of random gates

        Returns:
            Random rotation circuit
        """
        circuit = Circuit(n_qubits)

        rotation_gates = [gates.RX, gates.RY, gates.RZ]
        two_qubit_gates = [gates.CNOT, gates.CZ]

        for _ in range(n_gates):
            if np.random.random() < 0.6:  # 60% single-qubit rotation gates
                gate_type = np.random.choice(rotation_gates)
                qubit = np.random.randint(0, n_qubits)
                angle = np.random.uniform(0, 2 * np.pi)
                circuit.add(gate_type(angle, qubit))
            else:  # 40% two-qubit gates
                gate_type = np.random.choice(two_qubit_gates)
                qubit1 = np.random.randint(0, n_qubits)
                qubit2 = np.random.randint(0, n_qubits)
                while qubit2 == qubit1:
                    qubit2 = np.random.randint(0, n_qubits)
                circuit.add(gate_type(qubit1, qubit2))

        return circuit

    def create_redundant_circuit(self, n_qubits: int = 3, redundancy_level: str = "medium") -> Circuit:
        """Create a circuit with redundant operations for optimization testing.

        Args:
            n_qubits: Number of qubits
            redundancy_level: "low", "medium", or "high"

        Returns:
            Circuit with redundant operations
        """
        circuit = Circuit(n_qubits)

        # Base circuit
        circuit.add(gates.H(0))
        circuit.add(gates.CNOT(0, 1))
        circuit.add(gates.CNOT(1, 2))

        if redundancy_level == "low":
            # Few redundant operations
            circuit.add(gates.X(0))
            circuit.add(gates.X(0))  # X*X = I

        elif redundancy_level == "medium":
            # Moderate redundant operations
            circuit.add(gates.H(1))
            circuit.add(gates.H(1))  # H*H = I
            circuit.add(gates.Z(2))
            circuit.add(gates.Z(2))  # Z*Z = I

        elif redundancy_level == "high":
            # Many redundant operations
            for i in range(n_qubits):
                # Add multiple pairs of redundant gates
                circuit.add(gates.X(i))
                circuit.add(gates.X(i))
                circuit.add(gates.H(i))
                circuit.add(gates.H(i))
                circuit.add(gates.Y(i))
                circuit.add(gates.Y(i))

        return circuit

    def create_mixed_algorithm_circuit(self, n_qubits: int = 4) -> Circuit:
        """Create a circuit combining multiple algorithm patterns.

        Args:
            n_qubits: Number of qubits

        Returns:
            Mixed algorithm circuit
        """
        circuit = Circuit(n_qubits)

        # Start with some Clifford operations
        circuit.add(gates.H(0))
        circuit.add(gates.CNOT(0, 1))

        # Add rotation gates
        for i in range(2):
            for j in range(n_qubits):
                angle = np.random.uniform(0, np.pi)
                if j % 2 == 0:
                    circuit.add(gates.RX(angle, j))
                else:
                    circuit.add(gates.RY(angle, j))

        # Add entanglement
        for i in range(0, n_qubits - 1, 2):
            circuit.add(gates.CNOT(i, i + 1))

        # Add some redundant operations
        circuit.add(gates.H(0))
        circuit.add(gates.H(0))
        circuit.add(gates.Z(2))
        circuit.add(gates.Z(2))

        # Final Clifford layer
        for i in range(n_qubits):
            if np.random.random() < 0.5:
                circuit.add(gates.S(i))

        return circuit

    def generate_circuit_suite(self, circuit_types: Optional[List[str]] = None,
                             n_qubits_range: Tuple[int, int] = (2, 8),
                             circuits_per_type: int = 3) -> List[Dict[str, Any]]:
        """Generate a comprehensive suite of benchmark circuits.

        Args:
            circuit_types: Types of circuits to generate (None for all types)
            n_qubits_range: Range of qubit numbers (min, max)
            circuits_per_type: Number of circuits per type

        Returns:
            List of circuit metadata and circuits
        """
        if circuit_types is None:
            circuit_types = self.circuit_types

        circuit_suite = []

        for circuit_type in circuit_types:
            for i in range(circuits_per_type):
                # Vary the number of qubits
                n_qubits = np.random.randint(n_qubits_range[0], n_qubits_range[1] + 1)

                if circuit_type == 'bell_state':
                    circuit = self.create_bell_state(n_qubits)
                    description = f"Bell state with {n_qubits} qubits"

                elif circuit_type == 'ghz_state':
                    circuit = self.create_ghz_state(n_qubits)
                    description = f"GHZ state with {n_qubits} qubits"

                elif circuit_type == 'qft':
                    circuit = self.create_qft_circuit(n_qubits)
                    description = f"QFT with {n_qubits} qubits"

                elif circuit_type == 'qaoa':
                    depth = np.random.randint(1, 4)
                    circuit = self.create_qaoa_circuit(n_qubits, depth)
                    description = f"QAOA with {n_qubits} qubits, depth {depth}"

                elif circuit_type == 'vqe':
                    depth = np.random.randint(2, 5)
                    circuit = self.create_vqe_ansatz(n_qubits, depth)
                    description = f"VQE ansatz with {n_qubits} qubits, depth {depth}"

                elif circuit_type == 'random_clifford':
                    n_gates = np.random.randint(10, 30)
                    circuit = self.create_random_clifford_circuit(n_qubits, n_gates)
                    description = f"Random Clifford with {n_qubits} qubits, {n_gates} gates"

                elif circuit_type == 'random_rotation':
                    n_gates = np.random.randint(15, 35)
                    circuit = self.create_random_rotation_circuit(n_qubits, n_gates)
                    description = f"Random rotation with {n_qubits} qubits, {n_gates} gates"

                elif circuit_type == 'redundant_operations':
                    redundancy_level = np.random.choice(["low", "medium", "high"])
                    circuit = self.create_redundant_circuit(n_qubits, redundancy_level)
                    description = f"Redundant operations with {n_qubits} qubits, {redundancy_level} redundancy"

                elif circuit_type == 'mixed_algorithm':
                    circuit = self.create_mixed_algorithm_circuit(n_qubits)
                    description = f"Mixed algorithm pattern with {n_qubits} qubits"

                circuit_suite.append({
                    'circuit': circuit,
                    'type': circuit_type,
                    'description': description,
                    'n_qubits': n_qubits,
                    'n_gates': circuit.ngates,
                    'circuit_id': f"{circuit_type}_{i}_{n_qubits}q"
                })

        return circuit_suite

    def get_circuit_characteristics(self, circuit: Circuit) -> Dict[str, Any]:
        """Analyze circuit characteristics.

        Args:
            circuit: Quantum circuit to analyze

        Returns:
            Dictionary of circuit characteristics
        """
        # Count gate types
        gate_counts = {}
        for gate in circuit.queue:
            gate_name = gate.__class__.__name__
            gate_counts[gate_name] = gate_counts.get(gate_name, 0) + 1

        # Determine circuit complexity
        single_qubit_gates = sum(1 for gate in circuit.queue if gate.qubits == (0,))
        two_qubit_gates = circuit.ngates - single_qubit_gates

        complexity_score = circuit.ngates + 2 * two_qubit_gates  # Weight two-qubit gates more

        return {
            'n_qubits': circuit.nqubits,
            'n_gates': circuit.ngates,
            'gate_distribution': gate_counts,
            'single_qubit_gates': single_qubit_gates,
            'two_qubit_gates': two_qubit_gates,
            'complexity_score': complexity_score,
            'has_rotation_gates': any('R' in name for name in gate_counts.keys()),
            'has_clifford_gates': any(name in ['H', 'X', 'Y', 'Z', 'S', 'SDG', 'CNOT', 'CZ']
                                 for name in gate_counts.keys()),
            'entanglement_density': two_qubit_gates / max(circuit.ngates, 1)
        }


# Convenience functions for direct usage
def create_benchmark_circuits(circuit_types: Optional[List[str]] = None,
                             n_circuits: int = 20,
                             n_qubits_range: Tuple[int, int] = (2, 8)) -> List[Dict[str, Any]]:
    """Create a set of benchmark circuits for testing.

    Args:
        circuit_types: Types of circuits to generate
        n_circuits: Total number of circuits to generate
        n_qubits_range: Range of qubit numbers

    Returns:
        List of circuit metadata and circuits
    """
    generator = BenchmarkCircuitGenerator()

    # Calculate circuits per type
    if circuit_types is None:
        circuit_types = generator.circuit_types
    circuits_per_type = max(1, n_circuits // len(circuit_types))

    return generator.generate_circuit_suite(
        circuit_types=circuit_types,
        n_qubits_range=n_qubits_range,
        circuits_per_type=circuits_per_type
    )