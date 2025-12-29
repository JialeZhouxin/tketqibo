#!/usr/bin/env python3
"""
测试 Qiskit 和 Qibo 的 U3 门定义
"""

import sys
sys.path.insert(0, '.')

from qiskit import QuantumCircuit
from qiskit.quantum_info import Operator
from qibo import Circuit, gates
import numpy as np

print("=" * 70)
print("U3 门定义测试")
print("=" * 70)

# Qiskit H 门的酉矩阵
qc_h = QuantumCircuit(1)
qc_h.h(0)
u_h_qiskit = Operator(qc_h).data
print(f"\n[1] Qiskit H 门酉矩阵:\n{u_h_qiskit}")

# Qiskit U3(pi/2, 0, pi) 的酉矩阵（Qiskit 将 H 分解为此）
from qiskit.circuit.library import U3Gate
qc_u3_qiskit = QuantumCircuit(1)
qc_u3_qiskit.append(U3Gate(np.pi/2, 0, np.pi), [0])
u_u3_qiskit = Operator(qc_u3_qiskit).data
print(f"\n[2] Qiskit U3(pi/2, 0, pi) 酉矩阵:\n{u_u3_qiskit}")

# 检查是否相等
diff = np.linalg.norm(u_h_qiskit - u_u3_qiskit, 'fro')
print(f"\n[3] H 门与 U3(pi/2, 0, pi) 的 Frobenius 范数差异: {diff:.2e}")

# Qibo H 门
qc_h_qibo = Circuit(1)
qc_h_qibo.add(gates.H(0))
u_h_qibo = qc_h_qibo.unitary()
print(f"\n[4] Qibo H 门酉矩阵:\n{u_h_qibo}")

# Qibo U3(pi/2, 0, pi)
qc_u3_qibo = Circuit(1)
qc_u3_qibo.add(gates.U3(np.pi/2, 0, np.pi, 0))
u_u3_qibo = qc_u3_qibo.unitary()
print(f"\n[5] Qibo U3(pi/2, 0, pi) 酉矩阵:\n{u_u3_qibo}")

# 检查 Qibo U3 是否等于 Qiskit H
diff_qibo = np.linalg.norm(u_h_qiskit - u_u3_qibo, 'fro')
print(f"\n[6] Qiskit H 门与 Qibo U3(pi/2, 0, pi) 的 Frobenius 范数差异: {diff_qibo:.2e}")

# 测试 Qiskit 和 Qibo 的 U3 参数顺序
print(f"\n[7] 测试不同的 U3 参数组合:")
test_params = [
    (np.pi/2, 0, np.pi),      # Qiskit 默认
    (np.pi/2, np.pi, 0),      # 交换后两个参数
    (0, np.pi/2, np.pi),      # 交换第一个和第二个
    (np.pi, 0, np.pi/2),      # 交换第一个和第三个
]

for i, (a, b, c) in enumerate(test_params):
    qc = QuantumCircuit(1)
    qc.append(U3Gate(a, b, c), [0])
    u = Operator(qc).data
    diff = np.linalg.norm(u_h_qiskit - u, 'fro')
    print(f"  [{i}] U3({a:.4f}, {b:.4f}, {c:.4f}): diff = {diff:.2e}")

    # 在 Qibo 中测试
    qc_q = Circuit(1)
    qc_q.add(gates.U3(a, b, c, 0))
    u_q = qc_q.unitary()
    diff_q = np.linalg.norm(u_h_qiskit - u_q, 'fro')
    print(f"       Qibo U3({a:.4f}, {b:.4f}, {c:.4f}): diff = {diff_q:.2e}")

print("\n" + "=" * 70)
