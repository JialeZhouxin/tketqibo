"""
Bug Fix Regression Test for cross_framework_optimizer.py

This script reproduces the original bug and verifies that the fix resolves the issue.

Bug Description:
- The original code used nested elif statements that prevented QISKIT branch
  from being executed when QIBO_AVAILABLE was True.
- This caused Qiskit QuantumCircuit objects to be rejected.

Fix Applied:
- Flattened the elif structure to ensure each framework check is independent
- Reordered checks to prioritize QISKIT before QIBO (more specific)
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_qiskit_circuit_detection():
    """Test that Qiskit QuantumCircuit is correctly detected."""
    print("[Test 1] Qiskit Circuit Detection")
    print("-" * 60)

    from qiskit import QuantumCircuit
    from cross_framework_optimizer import (
        CircuitTypeDetector,
        CircuitType,
        QISKIT_AVAILABLE,
        QIBO_AVAILABLE
    )

    # Environment info
    print(f"Environment: QIBO_AVAILABLE={QIBO_AVAILABLE}, QISKIT_AVAILABLE={QISKIT_AVAILABLE}")

    # Create Qiskit circuit
    qc = QuantumCircuit(2)
    qc.h(0)
    qc.cx(0, 1)
    qc.x(1)

    print(f"Input: {type(qc)}")
    print(f"Class name: {qc.__class__.__name__}")

    # Detect
    detector = CircuitTypeDetector()
    result = detector.detect_circuit_type(qc)

    # Assert
    print(f"Detected type: {result}")
    assert result == CircuitType.QISKIT, f"Expected CircuitType.QISKIT, got {result}"
    print("[PASS] Qiskit circuit correctly detected")
    print()
    return True

def test_qibo_circuit_detection():
    """Test that Qibo Circuit is still correctly detected."""
    print("[Test 2] Qibo Circuit Detection")
    print("-" * 60)

    from qibo import Circuit, gates
    from cross_framework_optimizer import (
        CircuitTypeDetector,
        CircuitType,
        QIBO_AVAILABLE
    )

    if not QIBO_AVAILABLE:
        print("[SKIP] Qibo not available")
        print()
        return True

    # Create Qibo circuit
    qc = Circuit(2)
    qc.add(gates.H(0))
    qc.add(gates.CNOT(0, 1))
    qc.add(gates.X(1))

    print(f"Input: {type(qc)}")
    print(f"Class name: {qc.__class__.__name__}")
    print(f"Has ngates: {hasattr(qc, 'ngates')}")

    # Detect
    detector = CircuitTypeDetector()
    result = detector.detect_circuit_type(qc)

    # Assert
    print(f"Detected type: {result}")
    assert result == CircuitType.QIBO, f"Expected CircuitType.QIBO, got {result}"
    print("[PASS] Qibo circuit correctly detected")
    print()
    return True

def test_qasm_string_detection():
    """Test that QASM strings are still correctly detected."""
    print("[Test 3] QASM String Detection")
    print("-" * 60)

    from cross_framework_optimizer import (
        CircuitTypeDetector,
        CircuitType
    )

    # QASM string
    qasm = """OPENQASM 2.0;
include "qelib1.inc";
qreg q[2];
h q[0];
cx q[0],q[1];
"""

    print(f"Input type: {type(qasm)}")
    print(f"Input length: {len(qasm)} chars")

    # Detect
    detector = CircuitTypeDetector()
    result = detector.detect_circuit_type(qasm)

    # Assert
    print(f"Detected type: {result}")
    assert result == CircuitType.QASM, f"Expected CircuitType.QASM, got {result}"
    print("[PASS] QASM string correctly detected")
    print()
    return True

def test_optimize_qiskit_function():
    """Test the original failing scenario from the notebook."""
    print("[Test 4] optimize_qiskit Function Integration Test")
    print("-" * 60)

    from qiskit import QuantumCircuit
    from src.cross_framework_interface import optimize_qiskit

    # Create the same circuit from the notebook
    qc_qiskit = QuantumCircuit(2)
    qc_qiskit.h(0)
    qc_qiskit.cx(0, 1)
    qc_qiskit.h(0)  # Redundant H gate
    qc_qiskit.x(1)
    qc_qiskit.x(1)  # Redundant X gate

    print(f"Original circuit: {len(qc_qiskit)} gates, depth {qc_qiskit.depth()}")

    try:
        # This should work now
        optimized_qibo = optimize_qiskit(
            qc_qiskit,
            strategy="qiskit_only",
            optimization_level=2
        )

        # Qibo Circuit.depth is a property, not a method
        opt_depth = optimized_qibo.depth if callable(optimized_qibo.depth) else optimized_qibo.depth
        print(f"Optimized circuit: {optimized_qibo.ngates} gates, depth {opt_depth}")
        print("[PASS] optimize_qiskit function works correctly")
        print()
        return True
    except Exception as e:
        print(f"[FAIL] optimize_qiskit failed with error: {e}")
        print()
        return False

def test_unsupported_type():
    """Test that unsupported types are properly rejected."""
    print("[Test 5] Unsupported Type Rejection")
    print("-" * 60)

    from cross_framework_optimizer import (
        CircuitTypeDetector,
        UnsupportedCircuitError
    )

    # Unsupported type (random object)
    unsupported_obj = {"random": "object"}

    print(f"Input type: {type(unsupported_obj)}")

    # Detect
    detector = CircuitTypeDetector()
    try:
        result = detector.detect_circuit_type(unsupported_obj)
        print(f"[FAIL] Should have raised UnsupportedCircuitError, got {result}")
        print()
        return False
    except UnsupportedCircuitError as e:
        print(f"[PASS] Correctly raised UnsupportedCircuitError")
        print(f"      Error message: {e}")
        print()
        return True
    except Exception as e:
        print(f"[FAIL] Raised unexpected error: {e}")
        print()
        return False

def main():
    """Run all regression tests."""
    print("=" * 60)
    print("Bug Fix Regression Test Suite")
    print("=" * 60)
    print()
    print("Testing fix for cross_framework_optimizer.py")
    print("Bug: elif chain preventing QISKIT detection when QIBO_AVAILABLE=True")
    print("Fix: Flattened elif structure with precise matching")
    print()
    print("=" * 60)
    print()

    tests = [
        ("Qiskit Circuit Detection", test_qiskit_circuit_detection),
        ("Qibo Circuit Detection", test_qibo_circuit_detection),
        ("QASM String Detection", test_qasm_string_detection),
        ("optimize_qiskit Integration", test_optimize_qiskit_function),
        ("Unsupported Type Rejection", test_unsupported_type),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"[FAIL] {test_name} raised unexpected exception: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
            print()

    # Summary
    print("=" * 60)
    print("Test Summary")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} {test_name}")

    print()
    print(f"Total: {passed}/{total} tests passed")

    if passed == total:
        print()
        print("=" * 60)
        print("SUCCESS: All regression tests passed!")
        print("The bug fix is verified to work correctly.")
        print("=" * 60)
        return 0
    else:
        print()
        print("=" * 60)
        print(f"FAILURE: {total - passed} test(s) failed")
        print("=" * 60)
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
