#!/usr/bin/env python3
"""
测试 optimization_level=0 时 Transpiler 的行为
"""

import sys
sys.path.insert(0, '.')

from qiskit import QuantumCircuit, transpile
from qiskit.quantum_info import Operator
from qibo import Circuit, gates
import numpy as np

print("=" * 70)
print("Transpiler Level 0 行为测试")
print("=" * 70)

# 创建原始电路
qc_original = QuantumCircuit(2)
qc_original.h(0)
qc_original.cx(0, 1)

print("\n[1] 原始电路")
print(f"  门数: {len(qc_original)}")
for i, instruction in enumerate(qc_original.data):
    gate = instruction.operation if hasattr(instruction, 'operation') else instruction[0]
    qubits = instruction.qubits if hasattr(instruction, 'qubits') else instruction[1]
    qubit_indices = [qc_original.qubits.index(q) for q in qubits]
    print(f"    [{i}] {gate.name} on qubits {qubit_indices}")

u_original = Operator(qc_original).data
print(f"\n原始酉矩阵:\n{u_original}")

# Transpile level 0
print("\n[2] Transpile (level=0)")
qc_transpiled = transpile(qc_original, optimization_level=0)
print(f"  门数: {len(qc_transpiled)}")
for i, instruction in enumerate(qc_transpiled.data):
    gate = instruction.operation if hasattr(instruction, 'operation') else instruction[0]
    qubits = instruction.qubits if hasattr(instruction, 'qubits') else instruction[1]
    qubit_indices = [qc_transpiled.qubits.index(q) for q in qubits]
    params = gate.params if hasattr(gate, 'params') else []
    if params:
        print(f"    [{i}] {gate.name}{params} on qubits {qubit_indices}")
    else:
        print(f"    [{i}] {gate.name} on qubits {qubit_indices}")

u_transpiled = Operator(qc_transpiled).data
print(f"\nTranspile 后酉矩阵:\n{u_transpiled}")

diff = np.linalg.norm(u_original - u_transpiled, 'fro')
print(f"\nFrobenius 范数差异: {diff:.2e}")

# Transpile level 0 with basis_gates
print("\n[3] Transpile (level=0, basis_gates=['u3', 'cx'])")
qc_transpiled2 = transpile(qc_original, optimization_level=0, basis_gates=['u3', 'cx'])
print(f"  门数: {len(qc_transpiled2)}")
for i, instruction in enumerate(qc_transpiled2.data):
    gate = instruction.operation if hasattr(instruction, 'operation') else instruction[0]
    qubits = instruction.qubits if hasattr(instruction, 'qubits') else instruction[1]
    qubit_indices = [qc_transpiled2.qubits.index(q) for q in qubits]
    params = gate.params if hasattr(gate, 'params') else []
    if params:
        print(f"    [{i}] {gate.name}{params} on qubits {qubit_indices}")
    else:
        print(f"    [{i}] {gate.name} on qubits {qubit_indices}")

u_transpiled2 = Operator(qc_transpiled2).data
print(f"\nTranspile 后酉矩阵:\n{u_transpiled2}")

diff2 = np.linalg.norm(u_original - u_transpiled2, 'fro')
print(f"\nFrobenius 范数差异: {diff2:.2e}")

print("\n" + "=" * 70)
