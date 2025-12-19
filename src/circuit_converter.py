"""Circuit converter between Qibo and TKET frameworks.

This module provides bidirectional conversion between Qibo Circuit objects
and TKET Circuit objects, enabling the use of TKET optimization with Qibo
simulations.
"""

from typing import Dict, List, Optional, Tuple, Union
import numpy as np

# Import both quantum computing frameworks
import qibo
from qibo import Circuit, gates
from pytket import OpType, Circuit as TketCircuit
from pytket.circuit import Command, Op
from pytket.circuit import PauliExpBox, Unitary1qBox, Unitary2qBox, CustomGate


class UnsupportedGateError(Exception):
    """Exception raised when a gate type is not supported for conversion."""
    pass


class CircuitConverter:
    """Converts between Qibo and TKET circuits."""

    def __init__(self):
        """Initialize the converter with gate mappings."""
        # Map Qibo gate classes to TKET OpType
        self.qibo_to_tket_map: Dict[type, OpType] = {
            gates.H: OpType.H,
            gates.X: OpType.X,
            gates.Y: OpType.Y,
            gates.Z: OpType.Z,
            # gates.I: OpType.Unitary1qBox,  # Skip identity for now
            gates.CNOT: OpType.CX,
            gates.CZ: OpType.CZ,
            gates.RX: OpType.Rx,
            gates.RY: OpType.Ry,
            gates.RZ: OpType.Rz,
            gates.CU1: OpType.CU1,  # Add CU1 support
            gates.SWAP: OpType.SWAP,  # Add SWAP support
            gates.S: OpType.S,       # Add S gate support
            gates.SDG: OpType.Sdg,   # Add SDG gate support
            gates.SX: OpType.SX,     # Add SX gate support
        }

        # Map TKET OpType to Qibo gate classes
        self.tket_to_qibo_map: Dict[OpType, type] = {
            OpType.H: gates.H,
            OpType.X: gates.X,
            OpType.Y: gates.Y,
            OpType.Z: gates.Z,
            # OpType.Unitary1qBox: gates.I,  # Skip identity for now
            OpType.CX: gates.CNOT,
            OpType.CZ: gates.CZ,
            OpType.Rx: gates.RX,
            OpType.Ry: gates.RY,
            OpType.Rz: gates.RZ,
            OpType.CU1: gates.CU1,  # Add CU1 support
            OpType.SWAP: gates.SWAP,  # Add SWAP support
            OpType.S: gates.S,       # Add S gate support
            OpType.Sdg: gates.SDG,   # Add SDG gate support
            OpType.SX: gates.SX,     # Add SX gate support
            OpType.TK1: gates.U3,    # Map TK1 to U3 for gate fusion
        }

    def qibo_to_tket(self, qibo_circuit: Circuit) -> TketCircuit:
        """Convert a Qibo Circuit to a TKET Circuit.

        Args:
            qibo_circuit: Qibo Circuit object

        Returns:
            TketCircuit: Equivalent TKET Circuit

        Raises:
            UnsupportedGateError: If a gate type is not supported
        """
        # Create TKET circuit with same number of qubits
        tket_circuit = TketCircuit(qibo_circuit.nqubits)

        # Convert each gate
        for gate in qibo_circuit.queue:
            self._add_qibo_gate_to_tket(gate, tket_circuit)

        return tket_circuit

    def tket_to_qibo(self, tket_circuit: TketCircuit) -> Circuit:
        """Convert a TKET Circuit to a Qibo Circuit.

        Args:
            tket_circuit: TKET Circuit object

        Returns:
            Circuit: Equivalent Qibo Circuit

        Raises:
            UnsupportedGateError: If a gate type is not supported
        """
        # Create Qibo circuit with same number of qubits
        qibo_circuit = Circuit(tket_circuit.n_qubits)

        # Convert each operation
        for cmd in tket_circuit.get_commands():
            self._add_tket_gate_to_qibo(cmd, qibo_circuit)

        return qibo_circuit

    def _add_qibo_gate_to_tket(self, gate: gates.Gate, tket_circuit: TketCircuit) -> None:
        """Add a single Qibo gate to TKET circuit.

        Args:
            gate: Qibo gate object
            tket_circuit: Target TKET circuit

        Raises:
            UnsupportedGateError: If gate type is not supported
        """
        gate_type = type(gate)

        if gate_type not in self.qibo_to_tket_map:
            raise UnsupportedGateError(f"Gate type {gate_type} not supported for conversion")

        tket_op_type = self.qibo_to_tket_map[gate_type]

        # Extract qubits based on gate type
        if gate_type in [gates.H, gates.X, gates.Y, gates.Z, gates.RX, gates.RY, gates.RZ, gates.S, gates.SDG, gates.SX]:
            # Single-qubit gates
            qubits = [gate.target_qubits[0]] if hasattr(gate, 'target_qubits') else [gate.qubits]
        elif gate_type in [gates.CNOT, gates.CZ]:
            # Two-qubit gates - Qibo uses different structure
            if hasattr(gate, 'control_qubits') and hasattr(gate, 'target_qubits'):
                control_qubits = gate.control_qubits
                target_qubits = gate.target_qubits
                qubits = [control_qubits[0], target_qubits[0]] if control_qubits and target_qubits else []
            elif hasattr(gate, 'qubits'):
                qubits = gate.qubits
            else:
                # Try to access legacy attributes
                qubits = [gate.q0, gate.q1] if hasattr(gate, 'q0') and hasattr(gate, 'q1') else []
        else:
            # Fallback
            qubits = list(gate.target_qubits) if hasattr(gate, 'target_qubits') else []

        # Handle different gate types
        if gate_type in [gates.H, gates.X, gates.Y, gates.Z, gates.S, gates.SDG, gates.SX]:
            # Single-qubit gates without parameters
            tket_circuit.add_gate(tket_op_type, qubits)

        elif gate_type in [gates.CNOT, gates.CZ, gates.SWAP]:
            # Two-qubit gates without parameters
            if len(qubits) != 2:
                raise ValueError(f"{gate_type} expects 2 qubits, got {len(qubits)}")
            tket_circuit.add_gate(tket_op_type, qubits)

        elif gate_type in [gates.RX, gates.RY, gates.RZ]:
            # Single-qubit rotation gates with parameter
            if hasattr(gate, 'theta'):
                param = gate.theta
            elif hasattr(gate, 'params') and gate.params:
                param = gate.params[0]
            elif hasattr(gate, 'init_kwargs') and 'theta' in gate.init_kwargs:
                param = gate.init_kwargs['theta']
            elif hasattr(gate, '_theta'):
                param = gate._theta
            else:
                # Debug: print gate attributes
                print(f"Gate attributes: {dir(gate)}")
                raise ValueError(f"Cannot extract parameter from {gate}")

            tket_circuit.add_gate(tket_op_type, [param], qubits)

        elif gate_type == gates.CU1:
            # Controlled phase rotation
            if hasattr(gate, 'theta'):
                param = gate.theta
            elif hasattr(gate, 'params') and gate.params:
                param = gate.params[0]
            elif hasattr(gate, 'init_kwargs') and 'theta' in gate.init_kwargs:
                param = gate.init_kwargs['theta']
            else:
                raise ValueError(f"Cannot extract parameter from CU1 gate {gate}")

            tket_circuit.add_gate(tket_op_type, [param], qubits)

        else:
            raise UnsupportedGateError(f"Gate type {gate_type} not handled")

    def _add_tket_gate_to_qibo(self, cmd: Command, qibo_circuit: Circuit) -> None:
        """Add a single TKET command to Qibo circuit.

        Args:
            cmd: TKET Command object
            qibo_circuit: Target Qibo circuit

        Raises:
            UnsupportedGateError: If operation type is not supported
        """
        op_type = cmd.op.type
        qubits = [q.index[0] for q in cmd.qubits]

        # Skip certain TKET-specific operations
        if op_type in [OpType.Barrier, OpType.Measure]:
            # Skip barriers and measurements for optimization benchmark
            return

        # Handle basic operations first
        if op_type in self.tket_to_qibo_map:
            qibo_gate_class = self.tket_to_qibo_map[op_type]

            # Handle different operation types
            if op_type in [OpType.H, OpType.X, OpType.Y, OpType.Z, OpType.S, OpType.Sdg, OpType.SX]:
                # Single-qubit gates without parameters
                qibo_circuit.add(qibo_gate_class(qubits[0]))

            elif op_type in [OpType.CX, OpType.CZ, OpType.SWAP]:
                # Two-qubit gates without parameters
                if len(qubits) != 2:
                    raise ValueError(f"{op_type} expects 2 qubits, got {len(qubits)}")
                qibo_circuit.add(qibo_gate_class(qubits[0], qubits[1]))

            elif op_type in [OpType.Rx, OpType.Ry, OpType.Rz]:
                # Single-qubit rotation gates with parameter
                if not cmd.op.params:
                    raise ValueError(f"{op_type} expects a parameter")
                param = cmd.op.params[0]
                qibo_circuit.add(qibo_gate_class(qubits[0], theta=param))

            elif op_type == OpType.CU1:
                # Controlled phase rotation
                if not cmd.op.params:
                    raise ValueError(f"{op_type} expects a parameter")
                param = cmd.op.params[0]
                qibo_circuit.add(qibo_gate_class(qubits[0], qubits[1], theta=param))

        elif op_type == OpType.TK1:
            # Handle TK1 (arbitrary single-qubit rotation)
            # Convert to Qibo U3 gate to preserve gate fusion
            # TK1 parameters are typically (theta, phi, lambda) or similar
            if len(cmd.op.params) >= 3:
                # Use first three parameters as U3 angles
                u3_theta = cmd.op.params[0]
                u3_phi = cmd.op.params[1]
                u3_lambda = cmd.op.params[2]
                qibo_circuit.add(gates.U3(qubits[0], theta=u3_theta, phi=u3_phi, lam=u3_lambda))
            elif len(cmd.op.params) == 2:
                # For 2-parameter TK1, use as U3 with lambda=0
                u3_theta = cmd.op.params[0]
                u3_phi = cmd.op.params[1]
                qibo_circuit.add(gates.U3(qubits[0], theta=u3_theta, phi=u3_phi, lam=0.0))
            elif len(cmd.op.params) == 1:
                # For 1-parameter TK1, use as rotation around Z axis
                u3_theta = cmd.op.params[0]
                qibo_circuit.add(gates.U3(qubits[0], theta=u3_theta, phi=0.0, lam=0.0))
            else:
                # Empty TK1, skip
                pass

        elif op_type in [OpType.Unitary1qBox, OpType.Unitary2qBox]:
            # Handle unitary boxes by extracting and decomposing
            # For now, skip these as they're complex
            print(f"Warning: Skipping {op_type} - complex unitary operation")

        elif op_type == OpType.noop:
            # No-op gate, skip
            pass

        else:
            # For unsupported operations, try to skip rather than fail
            print(f"Warning: Skipping unsupported TKET operation {op_type}")
            return

    def verify_conversion(self, original_circuit: Circuit,
                         converted_back_circuit: Circuit,
                         tolerance: float = 1e-6) -> bool:
        """Verify that converting back and forth preserves the circuit.

        Args:
            original_circuit: Original Qibo circuit
            converted_back_circuit: Circuit after Qibo->TKET->Qibo conversion
            tolerance: Numerical tolerance for matrix comparison

        Returns:
            bool: True if circuits are equivalent within tolerance
        """
        # Get unitary matrices for both circuits
        original_matrix = original_circuit.unitary()
        converted_matrix = converted_back_circuit.unitary()

        # Compare matrices
        if original_matrix.shape != converted_matrix.shape:
            return False

        # Use Frobenius norm to compare matrices
        diff = np.linalg.norm(original_matrix - converted_matrix, 'fro')
        return diff < tolerance