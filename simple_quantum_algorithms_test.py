"""Simple Quantum Algorithms Performance Test.

This script tests the cross-framework optimizer on various quantum algorithms.
"""

import sys
import time
import numpy as np
from pathlib import Path

# Add project paths
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / 'src'))

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

try:
    from src.cross_framework_interface import (
        optimize_circuit,
        optimize_circuit_with_stats
    )
    INTERFACE_AVAILABLE = True
except ImportError:
    INTERFACE_AVAILABLE = False


class SimpleQuantumAlgorithmTest:
    """Simple quantum algorithm test class."""

    def __init__(self):
        """Initialize test."""
        self.results = {}

    def run_all_tests(self):
        """Run all algorithm tests."""
        print("Starting Quick Quantum Algorithm Performance Test")
        print("=" * 50)

        if not INTERFACE_AVAILABLE:
            print("ERROR: Cross-framework interface not available")
            return

        algorithms = [
            ("VQE", self.test_vqe),
            ("QAOA", self.test_qaoa),
            ("VQC", self.test_vqc),
            ("Grover", self.test_grover),
            ("Deutsch-Jozsa", self.test_deutsch_jozsa),
            ("Bernstein-Vazirani", self.test_bernstein_vazirani),
            ("QFT", self.test_qft),
            ("QPE", self.test_qpe),
            ("Shor", self.test_shor),
            ("HHL", self.test_hhl),
        ]

        for alg_name, test_func in algorithms:
            try:
                print(f"\nTesting {alg_name}")
                test_func()
            except Exception as e:
                print(f"ERROR: {alg_name} test failed: {e}")

        self.print_summary()

    def test_vqe(self):
        """Test VQE algorithm."""
        if not QIBO_AVAILABLE:
            print("  WARNING: Qibo not available, skipping")
            return

        # Simplified VQE circuit
        circuit = QiboCircuit(4)
        # Parameterized layer
        for i in range(4):
            circuit.add(gates.RY(np.random.uniform(0, 2*np.pi), i))
        # Entanglement layer
        for i in range(3):
            circuit.add(gates.CNOT(i, i+1))
        # Another parameterized layer
        for i in range(4):
            circuit.add(gates.RZ(np.random.uniform(0, 2*np.pi), i))

        self._test_optimization("VQE", circuit)

    def test_qaoa(self):
        """Test QAOA algorithm."""
        if not QIBO_AVAILABLE:
            print("  WARNING: Qibo not available, skipping")
            return

        n_qubits = 4
        n_layers = 2
        circuit = QiboCircuit(n_qubits)

        # Initial state
        for i in range(n_qubits):
            circuit.add(gates.H(i))

        # QAOA layers
        for layer in range(n_layers):
            # Problem Hamiltonian (simplified)
            for i in range(n_qubits-1):
                circuit.add(gates.CZ(i, i+1))
            # Mixing Hamiltonian
            for i in range(n_qubits):
                circuit.add(gates.RX(np.random.uniform(0, np.pi), i))

        self._test_optimization("QAOA", circuit)

    def test_vqc(self):
        """Test VQC algorithm."""
        if QISKIT_AVAILABLE:
            # Use Qiskit TwoLocal
            circuit = TwoLocal(3, ['ry', 'rz'], 'cx', reps=2)
            circuit = circuit.bind_parameters(np.random.uniform(-np.pi, np.pi, circuit.num_parameters))
            self._test_optimization("VQC", circuit)
        else:
            print("  WARNING: Qiskit not available, skipping")

    def test_grover(self):
        """Test Grover's algorithm."""
        if QIBO_AVAILABLE:
            n_qubits = 3
            circuit = QiboCircuit(n_qubits)
            # Initial superposition
            for i in range(n_qubits):
                circuit.add(gates.H(i))
            # Grover iteration (simplified)
            for i in range(n_qubits-1):
                circuit.add(gates.CNOT(i, i+1))
            # Oracle (simplified)
            circuit.add(gates.Z(0))
            # Diffusion operator (simplified)
            for i in range(n_qubits):
                circuit.add(gates.H(i))
                circuit.add(gates.X(i))

            self._test_optimization("Grover", circuit)
        else:
            print("  WARNING: Qibo not available, skipping")

    def test_deutsch_jozsa(self):
        """Test Deutsch-Jozsa algorithm."""
        if QIBO_AVAILABLE:
            circuit = QiboCircuit(3)
            # Initialization
            for i in range(3):
                circuit.add(gates.H(i))
            # Oracle (balanced function)
            circuit.add(gates.CNOT(0, 1))
            circuit.add(gates.CNOT(1, 2))
            # Hadamard
            for i in range(3):
                circuit.add(gates.H(i))

            self._test_optimization("Deutsch-Jozsa", circuit)
        else:
            print("  WARNING: Qibo not available, skipping")

    def test_bernstein_vazirani(self):
        """Test Bernstein-Vazirani algorithm."""
        if QIBO_AVAILABLE:
            circuit = QiboCircuit(3)
            # Initialization
            for i in range(3):
                circuit.add(gates.H(i))
            # Oracle for "101"
            circuit.add(gates.CNOT(0, 2))
            # Hadamard
            for i in range(3):
                circuit.add(gates.H(i))

            self._test_optimization("Bernstein-Vazirani", circuit)
        else:
            print("  WARNING: Qibo not available, skipping")

    def test_qft(self):
        """Test QFT algorithm."""
        if QISKIT_AVAILABLE:
            circuit = QFT(4, do_swaps=False)
            self._test_optimization("QFT", circuit)
        elif QIBO_AVAILABLE:
            # Manual QFT
            n_qubits = 3
            circuit = QiboCircuit(n_qubits)

            for target in range(n_qubits):
                circuit.add(gates.H(target))
                for control in range(target+1, n_qubits):
                    angle = np.pi / (2**(control-target))
                    circuit.add(gates.CU1(angle, control, target))

            self._test_optimization("QFT", circuit)
        else:
            print("  WARNING: Qiskit and Qibo not available, skipping")

    def test_qpe(self):
        """Test QPE algorithm."""
        if QIBO_AVAILABLE:
            # Simplified QPE
            circuit = QiboCircuit(4)
            n_estimation = 3
            # Initialize estimation register
            for i in range(n_estimation):
                circuit.add(gates.H(i))
            # Controlled U operations (simplified)
            phase = np.pi/4
            for i in range(n_estimation):
                for _ in range(2**i):
                    circuit.add(gates.CU1(phase, i, 3))

            self._test_optimization("QPE", circuit)
        else:
            print("  WARNING: Qibo not available, skipping")

    def test_shor(self):
        """Test Shor's algorithm (simplified)."""
        if QISKIT_AVAILABLE:
            # Simplified Shor's algorithm components
            circuit = QiskitCircuit(6)  # 4 counting + 2 work qubits

            # Initialize counting register
            for i in range(4):
                circuit.h(i)
            # Controlled modular exponentiation (simplified)
            for i in range(4):
                angle = 2*np.pi/15 * (2**i)  # 2^i mod 15
                circuit.cp(angle, i, 4)

            self._test_optimization("Shor", circuit)
        else:
            print("  WARNING: Qiskit not available, skipping")

    def test_hhl(self):
        """Test HHL algorithm (simplified)."""
        if QISKIT_AVAILABLE:
            # Simplified HHL components
            circuit = QiskitCircuit(4)
            # State preparation (simplified)
            circuit.h(0)
            circuit.cx(0, 1)
            # Quantum phase estimation (simplified)
            for i in range(1, 3):
                circuit.h(i)
                circuit.cp(np.pi/(2**i), 0, i)
            # Controlled rotation (simplified)
            circuit.ccx(1, 2, 3)
            # Decoding (simplified)
            circuit.h(1)
            circuit.h(2)

            self._test_optimization("HHL", circuit)
        else:
            print("  WARNING: Qiskit not available, skipping")

    def _test_optimization(self, alg_name: str, circuit):
        """Test circuit optimization."""
        try:
            # Get original gate count
            if QIBO_AVAILABLE and hasattr(circuit, 'ngates'):
                original_gates = circuit.ngates
                qasm_str = self._qibo_to_qasm(circuit)
            elif QISKIT_AVAILABLE and hasattr(circuit, 'num_qubits'):
                original_gates = len(circuit)
                qasm_str = circuit.qasm()
            else:
                original_gates = 0
                qasm_str = str(circuit)

            print(f"    Original circuit: {original_gates} gates")

            # Test different strategies
            strategies = ["none", "qiskit_only"]
            results = {}

            for strategy in strategies:
                try:
                    start_time = time.time()
                    optimized, stats = optimize_circuit_with_stats(
                        qasm_str,
                        strategy=strategy,
                        verbose=False
                    )
                    total_time = time.time() - start_time

                    reduction = original_gates - stats['optimized_gates']
                    print(f"    {strategy:12}: {original_gates:3}->{stats['optimized_gates']:3} gates "
                          f"({stats['gate_reduction_percent']:5.1f}%) "
                          f"time {total_time:.4f}s")

                    results[strategy] = {
                        'success': True,
                        'reduction_percent': stats['gate_reduction_percent']
                    }

                except Exception as e:
                    print(f"    {strategy:12}: ERROR - {str(e)[:30]}")
                    results[strategy] = {
                        'success': False,
                        'error': str(e)
                    }

            # Store results
            self.results[alg_name] = {
                'original_gates': original_gates,
                'results': results
            }

        except Exception as e:
            print(f"    ERROR: Test failed: {e}")

    def _qibo_to_qasm(self, circuit: QiboCircuit) -> str:
        """Convert Qibo circuit to QASM string."""
        n_qubits = circuit.nqubits
        qasm_lines = [
            f"OPENQASM 2.0;",
            f'include "qelib1.inc";',
            f"qreg q[{n_qubits}];"
        ]

        gate_map = {
            'H': 'h', 'X': 'x', 'Y': 'y', 'Z': 'z',
            'CNOT': 'cx', 'CZ': 'cz', 'SWAP': 'swap',
            'RX': 'rx', 'RY': 'ry', 'RZ': 'rz',
            'U1': 'u1', 'CU1': 'cu1'
        }

        for gate in circuit.queue:
            gate_name = gate.__class__.__name__
            qubits = gate.qubits

            if gate_name in gate_map:
                qasm_gate = gate_map[gate_name]

                if gate_name in ['H', 'X', 'Y', 'Z', 'S', 'T']:
                    qasm_lines.append(f"{qasm_gate} q[{qubits[0]}];")
                elif gate_name in ['CNOT', 'CZ', 'SWAP']:
                    qasm_lines.append(f"{qasm_gate} q[{qubits[0]}], q[{qubits[1]}];")
                elif gate_name in ['RX', 'RY', 'RZ']:
                    if hasattr(gate, 'theta'):
                        qasm_lines.append(f"{qasm_gate}({gate.theta:.6f}) q[{qubits[0]}];")
                elif gate_name == 'U1':
                    if hasattr(gate, 'phi'):
                        qasm_lines.append(f"u1({gate.phi:.6f}) q[{qubits[0]}];")
                elif gate_name == 'CU1':
                    if hasattr(gate, 'phi'):
                        qasm_lines.append(f"cu1({gate.phi:.6f}) q[{qubits[0]}], q[{qubits[1]}];")

        return "\n".join(qasm_lines)

    def print_summary(self):
        """Print summary report."""
        print("\n" + "=" * 60)
        print("Quick Test Summary Report")
        print("=" * 60)

        if not self.results:
            print("No test results")
            return

        # Statistics for each strategy
        strategies = ["none", "qiskit_only"]
        total_original_gates = sum(r['original_gates'] for r in self.results.values())

        print(f"\nOverall Statistics:")
        print(f"Tested algorithms: {len(self.results)}")
        print(f"Total original gates: {total_original_gates}")

        for strategy in strategies:
            success_count = 0
            total_reduction = 0

            for alg_name, result in self.results.items():
                if strategy in result['results'] and result['results'][strategy]['success']:
                    success_count += 1
                    total_reduction += result['results'][strategy]['reduction_percent']

            success_rate = success_count / len(self.results) * 100
            avg_reduction = total_reduction / len(self.results) if self.results else 0

            print(f"\n{strategy:12}:")
            print(f"  Success rate: {success_rate:.1f}% ({success_count}/{len(self.results)})")
            print(f"  Avg gate reduction: {avg_reduction:.1f}%")

        # Find best optimization
        best_reduction = 0
        best_algorithm = ""
        best_strategy = ""

        for alg_name, result in self.results.items():
            for strategy, stats in result['results'].items():
                if stats['success'] and stats['reduction_percent'] > best_reduction:
                    best_reduction = stats['reduction_percent']
                    best_algorithm = alg_name
                    best_strategy = strategy

        if best_algorithm:
            print(f"\nBest Optimization:")
            print(f"  Algorithm: {best_algorithm}")
            print(f"  Strategy: {best_strategy}")
            print(f"  Gate reduction: {best_reduction:.1f}%")

        print(f"\nRecommendations:")
        print(f"  - Use 'qiskit_only' for good performance on most circuits")
        print(f"  - Use 'none' for format conversion only")
        print(f"  - Consider circuit-specific optimization strategies")


def main():
    """Main function."""
    test_suite = SimpleQuantumAlgorithmTest()
    test_suite.run_all_tests()


if __name__ == "__main__":
    main()