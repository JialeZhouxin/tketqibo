"""Fixed Quantum Algorithms Performance Test.

This script tests the cross-framework optimizer on various quantum algorithms
with proper error handling and fallbacks.
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
    print("Qibo is available")
except ImportError as e:
    QIBO_AVAILABLE = False
    QiboCircuit = None
    gates = None
    print(f"Qibo not available: {e}")

try:
    from qiskit import QuantumCircuit as QiskitCircuit
    from qiskit.circuit.library import QFT, TwoLocal
    QISKIT_AVAILABLE = True
    print("Qiskit is available")
except ImportError as e:
    QISKIT_AVAILABLE = False
    QiskitCircuit = None
    print(f"Qiskit not available: {e}")

try:
    from src.cross_framework_interface import (
        optimize_circuit,
        optimize_circuit_with_stats
    )
    INTERFACE_AVAILABLE = True
    print("Cross-framework interface is available")
except ImportError as e:
    INTERFACE_AVAILABLE = False
    print(f"Cross-framework interface not available: {e}")


class FixedQuantumAlgorithmTest:
    """Fixed quantum algorithm test class."""

    def __init__(self):
        """Initialize test."""
        self.results = {}

    def run_all_tests(self):
        """Run all algorithm tests."""
        print("Fixed Quantum Algorithm Performance Test")
        print("=" * 50)

        if not INTERFACE_AVAILABLE:
            print("ERROR: Cross-framework interface not available")
            return

        # Test only algorithms that work with available frameworks
        algorithms = []

        if QIBO_AVAILABLE:
            algorithms.extend([
                ("Simple Grover", self.test_simple_grover),
                ("Simple QFT", self.test_simple_qft),
                ("Bell State", self.test_bell_state),
                ("GHZ State", self.test_ghz_state),
                ("Random Circuit", self.test_random_circuit),
            ])

        if QISKIT_AVAILABLE:
            algorithms.extend([
                ("Qiskit VQC", self.test_qiskit_vqc),
                ("Qiskit QFT", self.test_qiskit_qft),
            ])

        print(f"Testing {len(algorithms)} algorithms")
        print(f"Qibo available: {QIBO_AVAILABLE}")
        print(f"Qiskit available: {QISKIT_AVAILABLE}")

        for alg_name, test_func in algorithms:
            try:
                print(f"\nTesting {alg_name}")
                test_func()
            except Exception as e:
                print(f"ERROR: {alg_name} test failed: {e}")
                import traceback
                traceback.print_exc()

        self.print_summary()

    def test_simple_grover(self):
        """Test simple Grover's algorithm."""
        if not QIBO_AVAILABLE:
            return

        n_qubits = 3
        circuit = QiboCircuit(n_qubits)
        # Initial superposition
        for i in range(n_qubits):
            circuit.add(gates.H(i))
        # Simple oracle (mark |000>)
        circuit.add(gates.Z(0))
        # Diffusion operator
        for i in range(n_qubits):
            circuit.add(gates.H(i))
            circuit.add(gates.X(i))
        if n_qubits > 1:
            circuit.add(gates.CNOT(0, n_qubits - 1))
        for i in range(n_qubits):
            circuit.add(gates.X(i))
            circuit.add(gates.H(i))

        self._test_optimization("Simple Grover", circuit)

    def test_simple_qft(self):
        """Test simple QFT algorithm."""
        if not QIBO_AVAILABLE:
            return

        n_qubits = 3
        circuit = QiboCircuit(n_qubits)

        # Simple QFT implementation
        circuit.add(gates.H(0))
        circuit.add(gates.CU1(np.pi/2, 1, 0))
        circuit.add(gates.H(1))
        circuit.add(gates.CU1(np.pi/4, 2, 0))
        circuit.add(gates.CU1(np.pi/2, 2, 1))
        circuit.add(gates.H(2))

        self._test_optimization("Simple QFT", circuit)

    def test_bell_state(self):
        """Test Bell state creation."""
        if not QIBO_AVAILABLE:
            return

        circuit = QiboCircuit(2)
        circuit.add(gates.H(0))
        circuit.add(gates.CNOT(0, 1))

        self._test_optimization("Bell State", circuit)

    def test_ghz_state(self):
        """Test GHZ state creation."""
        if not QIBO_AVAILABLE:
            return

        circuit = QiboCircuit(3)
        circuit.add(gates.H(0))
        circuit.add(gates.CNOT(0, 1))
        circuit.add(gates.CNOT(0, 2))

        self._test_optimization("GHZ State", circuit)

    def test_random_circuit(self):
        """Test random circuit."""
        if not QIBO_AVAILABLE:
            return

        np.random.seed(42)
        n_qubits = 3
        n_gates = 8
        circuit = QiboCircuit(n_qubits)

        for _ in range(n_gates):
            gate_type = np.random.choice(['H', 'X', 'Y', 'Z', 'RX', 'RY', 'RZ', 'CNOT'])
            if gate_type in ['H', 'X', 'Y', 'Z']:
                qubit = np.random.randint(0, n_qubits)
                if gate_type == 'H':
                    circuit.add(gates.H(qubit))
                elif gate_type == 'X':
                    circuit.add(gates.X(qubit))
                elif gate_type == 'Y':
                    circuit.add(gates.Y(qubit))
                elif gate_type == 'Z':
                    circuit.add(gates.Z(qubit))
            elif gate_type in ['RX', 'RY', 'RZ']:
                qubit = np.random.randint(0, n_qubits)
                angle = np.random.uniform(0, 2*np.pi)
                if gate_type == 'RX':
                    circuit.add(gates.RX(angle, qubit))
                elif gate_type == 'RY':
                    circuit.add(gates.RY(angle, qubit))
                elif gate_type == 'RZ':
                    circuit.add(gates.RZ(angle, qubit))
            elif gate_type == 'CNOT' and n_qubits >= 2:
                control = np.random.randint(0, n_qubits-1)
                target = np.random.randint(control+1, n_qubits)
                circuit.add(gates.CNOT(control, target))

        self._test_optimization("Random Circuit", circuit)

    def test_qiskit_vqc(self):
        """Test Qiskit VQC."""
        if not QISKIT_AVAILABLE:
            return

        try:
            circuit = TwoLocal(3, ['ry', 'rz'], 'cx', reps=2, entanglement='linear')
            # Use default parameters
            self._test_optimization("Qiskit VQC", circuit)
        except Exception as e:
            print(f"    WARNING: Qiskit VQC creation failed: {e}")

    def test_qiskit_qft(self):
        """Test Qiskit QFT."""
        if not QISKIT_AVAILABLE:
            return

        try:
            circuit = QFT(3, do_swaps=False)
            self._test_optimization("Qiskit QFT", circuit)
        except Exception as e:
            print(f"    WARNING: Qiskit QFT creation failed: {e}")

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
                qasm_str = ""

            print(f"    Original circuit: {original_gates} gates")

            if not qasm_str:
                print(f"    WARNING: Empty QASM string, skipping optimization test")
                return

            # Test only available strategies
            strategies = []
            if QIBO_AVAILABLE:
                strategies.append("sim_fusion")
            if QISKIT_AVAILABLE:
                strategies.append("qiskit_only")

            if not strategies:
                print(f"    WARNING: No optimization strategies available")
                return

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
                        'reduction_percent': stats['gate_reduction_percent'],
                        'optimized_gates': stats['optimized_gates']
                    }

                except Exception as e:
                    print(f"    {strategy:12}: ERROR - {str(e)[:50]}")
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
            import traceback
            traceback.print_exc()

    def _qibo_to_qasm(self, circuit: QiboCircuit) -> str:
        """Convert Qibo circuit to QASM string."""
        try:
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

        except Exception as e:
            print(f"ERROR in QASM conversion: {e}")
            return ""

    def print_summary(self):
        """Print summary report."""
        print("\n" + "=" * 60)
        print("Fixed Test Summary Report")
        print("=" * 60)

        if not self.results:
            print("No test results")
            return

        # Statistics
        strategies = []
        if QIBO_AVAILABLE:
            strategies.append("sim_fusion")
        if QISKIT_AVAILABLE:
            strategies.append("qiskit_only")

        total_original_gates = sum(r['original_gates'] for r in self.results.values())
        successful_tests = len([r for r in self.results.values() if any(res.get('success', False) for res in r['results'].values())])

        print(f"\nOverall Statistics:")
        print(f"Tested algorithms: {len(self.results)}")
        print(f"Successful tests: {successful_tests}")
        print(f"Total original gates: {total_original_gates}")

        for strategy in strategies:
            success_count = 0
            total_reduction = 0
            total_optimized = 0

            for alg_name, result in self.results.items():
                if strategy in result['results'] and result['results'][strategy]['success']:
                    success_count += 1
                    total_reduction += result['results'][strategy]['reduction_percent']
                    total_optimized += result['results'][strategy]['optimized_gates']

            success_rate = success_count / len(self.results) * 100 if self.results else 0
            avg_reduction = total_reduction / len(self.results) if self.results else 0

            print(f"\n{strategy:12}:")
            print(f"  Success rate: {success_rate:.1f}% ({success_count}/{len(self.results)})")
            print(f"  Avg gate reduction: {avg_reduction:.1f}%")
            if success_count > 0:
                print(f"  Avg optimized gates: {total_optimized/success_count:.1f}")

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

        print(f"\nAvailable Frameworks:")
        print(f"  Qibo: {QIBO_AVAILABLE}")
        print(f"  Qiskit: {QISKIT_AVAILABLE}")

        print(f"\nRecommendations:")
        if QISKIT_AVAILABLE:
            print(f"  - Use 'qiskit_only' for robust optimization")
        if QIBO_AVAILABLE:
            print(f"  - Use 'sim_fusion' for Qibo-specific optimization")
        if not (QISKIT_AVAILABLE or QIBO_AVAILABLE):
            print(f"  - Install either Qiskit or Qibo for optimization")


def main():
    """Main function."""
    test_suite = FixedQuantumAlgorithmTest()
    test_suite.run_all_tests()


if __name__ == "__main__":
    main()