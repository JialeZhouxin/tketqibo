"""Quantum Circuit Generators for Benchmarking.

This module provides implementations of various quantum algorithms and ansatz
used for benchmarking quantum circuit optimization and simulation.
"""

from typing import List, Optional, Tuple
import numpy as np
import math

from qibo import Circuit, gates


def generate_qft_circuit(n_qubits: int, inverse: bool = False) -> Circuit:
    """Generate a Quantum Fourier Transform circuit.

    Args:
        n_qubits: Number of qubits
        inverse: Whether to generate inverse QFT

    Returns:
        Qibo Circuit implementing QFT or inverse QFT
    """
    circuit = Circuit(n_qubits)

    if inverse:
        # Inverse QFT - apply gates in reverse order with negative angles
        for j in reversed(range(n_qubits)):
            # Apply Hadamard
            circuit.add(gates.H(j))

            # Apply controlled phase rotations
            for k in reversed(range(j)):
                angle = -2 * np.pi / (2 ** (j - k + 1))
                circuit.add(gates.CU1(k, j, theta=angle))

            # Swap qubits (required for inverse QFT)
            for k in range(n_qubits // 2):
                if j == k and j < n_qubits // 2:
                    # Swap only once per pair
                    circuit.add(gates.SWAP(j, n_qubits - 1 - j))
    else:
        # Standard QFT
        for j in range(n_qubits):
            # Apply Hadamard
            circuit.add(gates.H(j))

            # Apply controlled phase rotations
            for k in range(j):
                angle = 2 * np.pi / (2 ** (j - k + 1))
                circuit.add(gates.CU1(k, j, theta=angle))

        # Swap qubits at the end
        for j in range(n_qubits // 2):
            circuit.add(gates.SWAP(j, n_qubits - 1 - j))

    return circuit


def generate_hea_circuit(n_qubits: int, layers: int, entanglement: str = "circular") -> Circuit:
    """Generate a Hardware-Efficient Ansatz circuit.

    Args:
        n_qubits: Number of qubits
        layers: Number of variational layers
        entanglement: Entanglement pattern ('linear', 'circular', 'full')

    Returns:
        Qibo Circuit implementing HEA
    """
    circuit = Circuit(n_qubits)

    for layer in range(layers):
        # Parameterized single-qubit rotations
        for q in range(n_qubits):
            # Random parameters for each rotation
            theta_ry = np.random.uniform(0, 2 * np.pi)
            theta_rz = np.random.uniform(0, 2 * np.pi)

            circuit.add(gates.RY(q, theta=theta_ry))
            circuit.add(gates.RZ(q, theta=theta_rz))

        # Entangling layer
        if entanglement == "linear":
            # Linear entanglement: (0,1), (1,2), (2,3), ...
            for q in range(n_qubits - 1):
                circuit.add(gates.CZ(q, q + 1))

        elif entanglement == "circular":
            # Circular entanglement: (0,1), (1,2), ..., (n-2,n-1), (n-1,0)
            for q in range(n_qubits):
                next_q = (q + 1) % n_qubits
                circuit.add(gates.CZ(q, next_q))

        elif entanglement == "full":
            # Full entanglement: all-to-all connectivity
            for q in range(n_qubits):
                for r in range(q + 1, n_qubits):
                    circuit.add(gates.CZ(q, r))

    return circuit


def generate_random_clifford_circuit(n_qubits: int, depth: int,
                                    include_measurements: bool = False) -> Circuit:
    """Generate a random Clifford circuit for stress testing.

    Args:
        n_qubits: Number of qubits
        depth: Circuit depth (number of layers)
        include_measurements: Whether to add measurement gates

    Returns:
        Qibo Circuit with random Clifford gates
    """
    circuit = Circuit(n_qubits)

    # Define Clifford gate set
    single_qubit_gates = [gates.H, gates.S, gates.SDG, gates.X, gates.Y, gates.Z]
    two_qubit_gates = [gates.CNOT, gates.CZ]

    for layer in range(depth):
        # Random single-qubit gates on each qubit
        for q in range(n_qubits):
            gate_type = np.random.choice(single_qubit_gates)
            if gate_type in [gates.S, gates.SDG]:
                circuit.add(gate_type(q))
            else:
                circuit.add(gate_type(q))

        # Random two-qubit gates
        n_two_qubit = np.random.randint(0, n_qubits)
        for _ in range(n_two_qubit):
            # Pick two random qubits
            q1, q2 = np.random.choice(n_qubits, size=2, replace=False)
            gate_type = np.random.choice(two_qubit_gates)

            if gate_type == gates.CNOT:
                circuit.add(gates.CNOT(q1, q2))
            else:  # CZ
                circuit.add(gates.CZ(q1, q2))

    # Add measurements if requested
    if include_measurements:
        for q in range(n_qubits):
            circuit.add(gates.M(q))

    return circuit


def generate_vqe_ansatz(n_qubits: int, layers: int, problem_type: str = "maxcut") -> Circuit:
    """Generate a VQE-style ansatz.

    Args:
        n_qubits: Number of qubits
        layers: Number of variational layers
        problem_type: Type of problem ('maxcut', 'ising')

    Returns:
        Qibo Circuit implementing VQE ansatz
    """
    circuit = Circuit(n_qubits)

    # Initial state preparation
    if problem_type == "maxcut":
        # Start with equal superposition
        for q in range(n_qubits):
            circuit.add(gates.H(q))
    else:  # Ising
        # Start with |0...0>
        pass

    for layer in range(layers):
        # Problem unitary
        if problem_type == "maxcut":
            # Max-Cut problem Hamiltonian (ZZ interactions)
            for i in range(n_qubits):
                for j in range(i + 1, n_qubits):
                    # Problem parameter (in real VQE, this would be optimized)
                    gamma = np.random.uniform(0, np.pi)
                    circuit.add(gates.CNOT(i, j))
                    circuit.add(gates.RZ(j, 2 * gamma))
                    circuit.add(gates.CNOT(i, j))

        elif problem_type == "ising":
            # Transverse field Ising model
            for i in range(n_qubits):
                gamma = np.random.uniform(0, np.pi)
                circuit.add(gates.RZ(i, gamma))

            # Add ZZ interactions if more than 1 qubit
            for i in range(n_qubits - 1):
                gamma = np.random.uniform(0, np.pi)
                circuit.add(gates.CNOT(i, i + 1))
                circuit.add(gates.RZ(i + 1, 2 * gamma))
                circuit.add(gates.CNOT(i, i + 1))

        # Mixer unitary (X rotations)
        beta = np.random.uniform(0, np.pi)
        for q in range(n_qubits):
            circuit.add(gates.RX(q, beta))

    return circuit


def generate_qaoa_circuit(n_qubits: int, layers: int, problem_type: str = "maxcut") -> Circuit:
    """Generate a QAOA circuit.

    Args:
        n_qubits: Number of qubits
        layers: Number of QAOA layers (p)
        problem_type: Type of optimization problem

    Returns:
        Qibo Circuit implementing QAOA
    """
    circuit = Circuit(n_qubits)

    # Initial state preparation
    for q in range(n_qubits):
        circuit.add(gates.H(q))

    for layer in range(layers):
        # Problem unitary
        if problem_type == "maxcut":
            # Max-Cut on complete graph
            for i in range(n_qubits):
                for j in range(i + 1, n_qubits):
                    gamma = np.pi / (2 * layers)  # Simple schedule
                    circuit.add(gates.CNOT(i, j))
                    circuit.add(gates.RZ(j, 2 * gamma))
                    circuit.add(gates.CNOT(i, j))

        # Mixer unitary
        beta = np.pi / (2 * layers)  # Simple schedule
        for q in range(n_qubits):
            circuit.add(gates.RX(q, beta))

    return circuit


def generate_ghz_state(n_qubits: int) -> Circuit:
    """Generate a GHZ state preparation circuit.

    Args:
        n_qubits: Number of qubits

    Returns:
        Qibo Circuit that prepares GHZ state
    """
    circuit = Circuit(n_qubits)

    # Start with superposition on first qubit
    circuit.add(gates.H(0))

    # Create entanglement with all other qubits
    for q in range(1, n_qubits):
        circuit.add(gates.CNOT(0, q))

    return circuit


def generate_random_parameterized_circuit(n_qubits: int, depth: int,
                                         parameter_distribution: str = "uniform") -> Circuit:
    """Generate a random parameterized circuit.

    Args:
        n_qubits: Number of qubits
        depth: Circuit depth
        parameter_distribution: How to distribute parameters ('uniform', 'normal', 'fixed')

    Returns:
        Qibo Circuit with random parameterized gates
    """
    circuit = Circuit(n_qubits)

    # Parameter generation function
    if parameter_distribution == "uniform":
        get_param = lambda: np.random.uniform(0, 2 * np.pi)
    elif parameter_distribution == "normal":
        get_param = lambda: np.abs(np.random.normal(0, np.pi/4))
    else:  # fixed
        get_param = lambda: np.pi / 4

    for layer in range(depth):
        # Random single-qubit rotations
        for q in range(n_qubits):
            # Choose rotation axis randomly
            axis = np.random.choice(['X', 'Y', 'Z'])
            param = get_param()

            if axis == 'X':
                circuit.add(gates.RX(q, theta=param))
            elif axis == 'Y':
                circuit.add(gates.RY(q, theta=param))
            else:  # Z
                circuit.add(gates.RZ(q, theta=param))

        # Random entangling gates
        n_entanglers = np.random.randint(1, n_qubits)
        for _ in range(n_entanglers):
            q1, q2 = np.random.choice(n_qubits, size=2, replace=False)
            circuit.add(gates.CNOT(q1, q2))

    return circuit


# Utility functions
def count_gates_by_type(circuit: Circuit) -> dict:
    """Count gates by type in a circuit."""
    gate_counts = {}
    for gate in circuit.queue:
        gate_type = gate.__class__.__name__
        gate_counts[gate_type] = gate_counts.get(gate_type, 0) + 1
    return gate_counts


def estimate_circuit_depth(circuit: Circuit) -> int:
    """Estimate the depth of a circuit."""
    depth = 0
    active_qubits = set()

    for gate in circuit.queue:
        try:
            if hasattr(gate, 'target_qubits'):
                qubits = set(gate.target_qubits)
            elif hasattr(gate, 'qubits'):
                qubits = set(gate.qubits)
            elif hasattr(gate, 'control_qubits') and hasattr(gate, 'target_qubits'):
                qubits = set(gate.control_qubits) | set(gate.target_qubits)
            else:
                qubits = set()

            if qubits.isdisjoint(active_qubits):
                active_qubits.update(qubits)
            else:
                depth += 1
                active_qubits = qubits
        except:
            depth += 1
            active_qubits = set()

    if active_qubits:
        depth += 1

    return depth