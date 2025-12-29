#!/usr/bin/env python3
"""
测试 Qiskit 和 Qibo 的量子比特排序约定
"""

import sys
sys.path.insert(0, '.')

from qiskit import QuantumCircuit
from qiskit.quantum_info import Operator
from qibo import Circuit, gates
import numpy as np

print("=" * 70)
print("Qiskit vs Qibo 量子比特排序约定测试")
print("=" * 70)

# 创建简单的电路来测试约定
qc = QuantumCircuit(2)
qc.x(1)  # 只作用在第 1 个量子比特上

print("\n[1] 测试电路: X(1)")
print("  预期: |01> -> |11>")

# Qiskit 酉矩阵
op_qiskit = Operator(qc)
u_qiskit = op_qiskit.data
print(f"\n[2] Qiskit 酉矩阵:\n{u_qiskit}")

# Qibo 酉矩阵
qc_qibo = Circuit(2)
qc_qibo.add(gates.X(1))
u_qibo = qc_qibo.unitary()
print(f"\n[3] Qibo 酉矩阵:\n{u_qibo}")

# 查看非零元素
print(f"\n[4] Qiskit 非零元素位置 (行, 列):")
qiskit_nonzero = np.argwhere(np.abs(u_qiskit) > 0.1)
for row, col in qiskit_nonzero:
    val = u_qiskit[row, col]
    print(f"  [{row}, {col}] = {val}")

print(f"\n[5] Qibo 非零元素位置 (行, 列):")
qibo_nonzero = np.argwhere(np.abs(u_qibo) > 0.1)
for row, col in qibo_nonzero:
    val = u_qibo[row, col]
    print(f"  [{row}, {col}] = {val}")

# 推断约定
print(f"\n[6] 推断约定:")
print(f"  Qiskit 非零位置: {qiskit_nonzero.tolist()}")
print(f"  Qibo 非零位置: {qibo_nonzero.tolist()}")

if np.array_equal(qiskit_nonzero, qibo_nonzero):
    print(f"  结论: Qiskit 和 Qibo 使用相同的约定!")
else:
    print(f"  结论: Qiskit 和 Qibo 使用不同的约定!")

    # 尝试找到映射关系
    print(f"\n[7] 尝试找到映射关系...")

    # 对于 2 量子比特，有 4 种可能的映射
    mappings = [
        ((0,1), (0,1)),  # 直接映射
        ((0,1), (1,0)),  # 翻转
        ((1,0), (0,1)),
        ((1,0), (1,0)),
    ]

    for i, (qiskit_idx, qibo_idx) in enumerate(qiskit_nonzero):
        # qiskit_idx 对应 |q1 q0⟩
        # qibo_idx 对应 |q0 q1⟩
        # 转换关系
        print(f"  Qiskit [{qiskit_idx[0]},{qiskit_idx[1]}] -> Qibo [{qibo_idx[0]},{qibo_idx[1]}]")
        # 这意味着 |q1=0, q0=1⟩_Qiskit = |q0=0, q1=1⟩_Qibo
        # 即 |01⟩_Qiskit = |01⟩_Qibo

print("\n" + "=" * 70)
