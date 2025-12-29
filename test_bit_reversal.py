#!/usr/bin/env python3
"""
测试位逆序排列修复
"""

import sys
sys.path.insert(0, '.')

from qiskit import QuantumCircuit
from qiskit.quantum_info import Operator
from qibo import Circuit, gates
import numpy as np

print("=" * 70)
print("位逆序排列修复测试")
print("=" * 70)

# 测试 1: X(1) 门
print("\n[测试 1] X(1) 门")
qc_qiskit = QuantumCircuit(2)
qc_qiskit.x(1)

u_qiskit = Operator(qc_qiskit).data
print(f"Qiskit 酉矩阵:\n{u_qiskit}")

qc_qibo = Circuit(2)
qc_qibo.add(gates.X(1))
u_qibo = qc_qibo.unitary()
print(f"\nQibo 酉矩阵（原始）:\n{u_qibo}")

# 应用位逆序排列
n_qubits = 2
dim = 2 ** n_qubits
bit_reversal = []
for i in range(dim):
    reversed_bits = format(i, f'0{n_qubits}b')[::-1]
    reversed_idx = int(reversed_bits, 2)
    bit_reversal.append(reversed_idx)

print(f"\n位逆序排列: {bit_reversal}")
u_qibo_adjusted = u_qibo[np.ix_(bit_reversal, bit_reversal)]
print(f"Qibo 酉矩阵（调整后）:\n{u_qibo_adjusted}")

# 检查差异
diff = np.linalg.norm(u_qiskit - u_qibo_adjusted, 'fro')
print(f"\nFrobenius 范数差异: {diff:.2e}")
if diff < 1e-10:
    print("[OK] X(1) 门: 矩阵完全匹配!")
else:
    # 检查全局相位
    product = np.dot(u_qiskit.conj().T, u_qibo_adjusted)
    first_element = product[0, 0]
    if np.abs(first_element) > 1e-15:
        phase = first_element / np.abs(first_element)
        normalized_diff = np.linalg.norm(u_qiskit - phase * u_qibo_adjusted, 'fro')
        print(f"全局相位: {phase}")
        print(f"消除全局相位后的差异: {normalized_diff:.2e}")
        if normalized_diff < 1e-10:
            print("[OK] X(1) 门: 相差全局相位，矩阵匹配!")
        else:
            print("[FAIL] X(1) 门: 矩阵不匹配")
    else:
        print("[FAIL] X(1) 门: 矩阵不匹配")

# 测试 2: Bell 电路 (H(0) + CX(0,1))
print("\n" + "=" * 70)
print("\n[测试 2] Bell 电路 (H(0) + CX(0,1))")

qc_qiskit = QuantumCircuit(2)
qc_qiskit.h(0)
qc_qiskit.cx(0, 1)

u_qiskit = Operator(qc_qiskit).data
print(f"Qiskit 酉矩阵:\n{u_qiskit}")

qc_qibo = Circuit(2)
qc_qibo.add(gates.H(0))
qc_qibo.add(gates.CNOT(0, 1))
u_qibo = qc_qibo.unitary()

u_qibo_adjusted = u_qibo[np.ix_(bit_reversal, bit_reversal)]
print(f"\nQibo 酉矩阵（调整后）:\n{u_qibo_adjusted}")

# 检查差异
diff = np.linalg.norm(u_qiskit - u_qibo_adjusted, 'fro')
print(f"\nFrobenius 范数差异: {diff:.2e}")
if diff < 1e-10:
    print("[OK] Bell 电路: 矩阵完全匹配!")
else:
    # 检查全局相位
    product = np.dot(u_qiskit.conj().T, u_qibo_adjusted)
    first_element = product[0, 0]
    if np.abs(first_element) > 1e-15:
        phase = first_element / np.abs(first_element)
        normalized_diff = np.linalg.norm(u_qiskit - phase * u_qibo_adjusted, 'fro')
        print(f"全局相位: {phase}")
        print(f"消除全局相位后的差异: {normalized_diff:.2e}")
        if normalized_diff < 1e-10:
            print("[OK] Bell 电路: 相差全局相位，矩阵匹配!")
        else:
            print("[FAIL] Bell 电路: 矩阵不匹配")
    else:
        print("[FAIL] Bell 电路: 矩阵不匹配")

# 测试 3: 3 量子比特电路
print("\n" + "=" * 70)
print("\n[测试 3] 3 量子比特电路 (X(0) + X(2))")

qc_qiskit = QuantumCircuit(3)
qc_qiskit.x(0)
qc_qiskit.x(2)

u_qiskit = Operator(qc_qiskit).data

qc_qibo = Circuit(3)
qc_qibo.add(gates.X(0))
qc_qibo.add(gates.X(2))
u_qibo = qc_qibo.unitary()

# 3 量子比特的位逆序排列
n_qubits = 3
dim = 2 ** n_qubits
bit_reversal_3 = []
for i in range(dim):
    reversed_bits = format(i, f'0{n_qubits}b')[::-1]
    reversed_idx = int(reversed_bits, 2)
    bit_reversal_3.append(reversed_idx)

print(f"位逆序排列 (3 qubits): {bit_reversal_3}")
u_qibo_adjusted = u_qibo[np.ix_(bit_reversal_3, bit_reversal_3)]

# 检查差异
diff = np.linalg.norm(u_qiskit - u_qibo_adjusted, 'fro')
print(f"Frobenius 范数差异: {diff:.2e}")
if diff < 1e-10:
    print("[OK] 3 量子比特电路: 矩阵完全匹配!")
else:
    # 检查全局相位
    product = np.dot(u_qiskit.conj().T, u_qibo_adjusted)
    first_element = product[0, 0]
    if np.abs(first_element) > 1e-15:
        phase = first_element / np.abs(first_element)
        normalized_diff = np.linalg.norm(u_qiskit - phase * u_qibo_adjusted, 'fro')
        print(f"消除全局相位后的差异: {normalized_diff:.2e}")
        if normalized_diff < 1e-10:
            print("[OK] 3 量子比特电路: 相差全局相位，矩阵匹配!")
        else:
            print("[FAIL] 3 量子比特电路: 矩阵不匹配")
    else:
        print("[FAIL] 3 量子比特电路: 矩阵不匹配")

print("\n" + "=" * 70)
print("测试完成")
print("=" * 70)
