#!/usr/bin/env python3
"""
诊断等价性验证问题
"""

import sys
sys.path.insert(0, '.')

from qiskit import QuantumCircuit
from qiskit.quantum_info import Operator
from qibo import Circuit, gates

# 创建 Bell 电路
qc_qiskit = QuantumCircuit(2)
qc_qiskit.h(0)
qc_qiskit.cx(0, 1)

print("=" * 70)
print("等价性验证诊断")
print("=" * 70)

# 获取 Qiskit 酉矩阵
print("\n[1] Qiskit 酉矩阵（使用 Operator）")
operator = Operator(qc_qiskit)
unitary_qiskit = operator.data
print(f"  形状: {unitary_qiskit.shape}")
print(f"  数据类型: {unitary_qiskit.dtype}")
print(f"  矩阵:\n{unitary_qiskit}")

# 获取 Qibo 酉矩阵
print("\n[2] Qibo 酉矩阵")
qc_qibo = Circuit(2)
qc_qibo.add(gates.H(0))
qc_qibo.add(gates.CNOT(0, 1))
unitary_qibo = qc_qibo.unitary()
print(f"  形状: {unitary_qibo.shape}")
print(f"  数据类型: {unitary_qibo.dtype}")
print(f"  矩阵:\n{unitary_qibo}")

# 对比
print("\n[3] 对比分析")
import numpy as np
diff = unitary_qiskit - unitary_qibo
frobenius_diff = np.linalg.norm(diff, 'fro')
print(f"  Frobenius 范数差异: {frobenius_diff:.6e}")

# 检查全局相位
print("\n[4] 全局相位检查")
product = np.dot(unitary_qiskit.conj().T, unitary_qibo)
first_element = product[0, 0]
print(f"  U†V 的第一个元素: {first_element}")
print(f"  幅度: {np.abs(first_element)}")
print(f"  相位: {np.angle(first_element)}")

if np.abs(first_element) > 1e-15:
    phase = first_element / np.abs(first_element)
    print(f"  归一化相位: {phase}")

    normalized_diff = np.linalg.norm(unitary_qiskit - phase * unitary_qibo, 'fro')
    print(f"  消除全局相位后的 Frobenius 范数差异: {normalized_diff:.6e}")

    if normalized_diff < 1e-8:
        print(f"  ✅ 电路是等价的（相差全局相位 {phase}）")
    else:
        print(f"  ❌ 电路不等价")
else:
    print(f"  ❌ 无法消除全局相位")

# 测试 transpile 后的电路
print("\n[5] transpile 后的电路")
from qiskit import transpile
qc_transpiled = transpile(qc_qiskit, optimization_level=2, basis_gates=['u3', 'cx'])
print(f"  transpile 后门数: {len(qc_transpiled)}")
print(f"  门序列:")
for i, instruction in enumerate(qc_transpiled.data):
    gate = instruction.operation if hasattr(instruction, 'operation') else instruction[0]
    qubits = [q.qubit for q in instruction.qubits]
    print(f"    [{i}] {gate.name} on qubits {[q.index for q in qubits]}")

operator_transpiled = Operator(qc_transpiled)
unitary_transpiled = operator_transpiled.data
print(f"\n  transpile 后的酉矩阵:\n{unitary_transpiled}")

diff_transpiled = unitary_qiskit - unitary_transpiled
frobenius_diff_transpiled = np.linalg.norm(diff_transpiled, 'fro')
print(f"\n  transpile 前后 Frobenius 范数差异: {frobenius_diff_transpiled:.6e}")

# 检查 transpile 后的全局相位
product_transpiled = np.dot(unitary_qiskit.conj().T, unitary_transpiled)
first_element_transpiled = product_transpiled[0, 0]
print(f"\n  transpile 后 U†V 的第一个元素: {first_element_transpiled}")

if np.abs(first_element_transpiled) > 1e-15:
    phase_transpiled = first_element_transpiled / np.abs(first_element_transpiled)
    normalized_diff_transpiled = np.linalg.norm(unitary_qiskit - phase_transpiled * unitary_transpiled, 'fro')
    print(f"  消除全局相位后的 Frobenius 范数差异: {normalized_diff_transpiled:.6e}")

    if normalized_diff_transpiled < 1e-8:
        print(f"  ✅ transpile 保持了等价性（相差全局相位 {phase_transpiled}）")
    else:
        print(f"  ❌ transpile 破坏了等价性")

print("\n" + "=" * 70)
