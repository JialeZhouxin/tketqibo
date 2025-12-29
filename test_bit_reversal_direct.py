#!/usr/bin/env python3
"""
直接测试位逆序排列，绕过优化器
"""

import sys
sys.path.insert(0, '.')

from qiskit import QuantumCircuit
from qiskit.quantum_info import Operator
from qibo import Circuit, gates
import numpy as np

def bit_reversal_permutation(matrix, n_qubits):
    """应用位逆序排列到酉矩阵."""
    dim = 2 ** n_qubits
    bit_reversal = []
    for i in range(dim):
        reversed_bits = format(i, f'0{n_qubits}b')[::-1]
        reversed_idx = int(reversed_bits, 2)
        bit_reversal.append(reversed_idx)
    return matrix[np.ix_(bit_reversal, bit_reversal)]

print("=" * 70)
print("直接测试位逆序排列")
print("=" * 70)

# 测试 1: Bell 电路
print("\n[测试 1] Bell 电路")
qc_qiskit = QuantumCircuit(2)
qc_qiskit.h(0)
qc_qiskit.cx(0, 1)

u_qiskit = Operator(qc_qiskit).data
print(f"Qiskit Bell 酉矩阵:\n{u_qiskit}")

qc_qibo = Circuit(2)
qc_qibo.add(gates.H(0))
qc_qibo.add(gates.CNOT(0, 1))
u_qibo = qc_qibo.unitary()
print(f"\nQibo Bell 酉矩阵（原始）:\n{u_qibo}")

# 应用位逆序排列
u_qibo_adjusted = bit_reversal_permutation(u_qibo, 2)
print(f"\nQibo Bell 酉矩阵（调整后）:\n{u_qibo_adjusted}")

# 检查差异
diff = np.linalg.norm(u_qiskit - u_qibo_adjusted, 'fro')
print(f"\nFrobenius 范数差异: {diff:.2e}")

if diff < 1e-10:
    print("[OK] 矩阵完全匹配!")
else:
    # 检查全局相位
    product = np.dot(u_qiskit.conj().T, u_qibo_adjusted)
    first_element = product[0, 0]
    print(f"U†V 的第一个元素: {first_element}")
    if np.abs(first_element) > 1e-15:
        phase = first_element / np.abs(first_element)
        normalized_diff = np.linalg.norm(u_qiskit - phase * u_qibo_adjusted, 'fro')
        print(f"全局相位: {phase}")
        print(f"消除全局相位后的差异: {normalized_diff:.2e}")
        if normalized_diff < 1e-10:
            print("[OK] 相差全局相位，矩阵匹配!")
        else:
            print("[FAIL] 矩阵不匹配")
    else:
        print("[FAIL] 矩阵不匹配")

# 测试 2: H + H (应该等于单位矩阵)
print("\n" + "=" * 70)
print("\n[测试 2] H + H (应该等于单位矩阵)")

qc_qiskit2 = QuantumCircuit(1)
qc_qiskit2.h(0)
qc_qiskit2.h(0)
u_qiskit2 = Operator(qc_qiskit2).data
print(f"Qiskit H+H 酉矩阵:\n{u_qiskit2}")

qc_qibo2 = Circuit(1)
qc_qibo2.add(gates.H(0))
qc_qibo2.add(gates.H(0))
u_qibo2 = qc_qibo2.unitary()
print(f"\nQibo H+H 酉矩阵:\n{u_qibo2}")

diff2 = np.linalg.norm(u_qiskit2 - u_qibo2, 'fro')
print(f"\nFrobenius 范数差异: {diff2:.2e}")

if diff2 < 1e-10:
    print("[OK] 矩阵完全匹配!")
else:
    print("[FAIL] 矩阵不匹配")

# 测试 3: 单个 X 门
print("\n" + "=" * 70)
print("\n[测试 3] 单个 X 门")

qc_qiskit3 = QuantumCircuit(1)
qc_qiskit3.x(0)
u_qiskit3 = Operator(qc_qiskit3).data
print(f"Qiskit X 酉矩阵:\n{u_qiskit3}")

qc_qibo3 = Circuit(1)
qc_qibo3.add(gates.X(0))
u_qibo3 = qc_qibo3.unitary()
print(f"\nQibo X 酉矩阵:\n{u_qibo3}")

diff3 = np.linalg.norm(u_qiskit3 - u_qibo3, 'fro')
print(f"\nFrobenius 范数差异: {diff3:.2e}")

if diff3 < 1e-10:
    print("[OK] 矩阵完全匹配!")
else:
    print("[FAIL] 矩阵不匹配")

print("\n" + "=" * 70)
