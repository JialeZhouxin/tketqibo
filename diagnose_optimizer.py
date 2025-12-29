#!/usr/bin/env python3
"""
诊断优化器转换问题
"""

import sys
sys.path.insert(0, '.')

from qiskit import QuantumCircuit, transpile
from qiskit.quantum_info import Operator
from qibo import Circuit, gates
import numpy as np

print("=" * 70)
print("优化器转换诊断")
print("=" * 70)

# 创建测试电路
qc = QuantumCircuit(2)
qc.h(0)
qc.cx(0, 1)

print("\n[1] 原始 Qiskit 电路")
print(f"  门数: {len(qc)}")
for i, instruction in enumerate(qc.data):
    gate = instruction.operation if hasattr(instruction, 'operation') else instruction[0]
    qubits = instruction.qubits if hasattr(instruction, 'qubits') else instruction[1]
    qubit_indices = [qc.qubits.index(q) for q in qubits]
    print(f"    [{i}] {gate.name} on qubits {qubit_indices}")

# 获取原始酉矩阵
u_original = Operator(qc).data
print(f"\n[2] 原始酉矩阵 (Qiskit):\n{u_original}")

# Transpile（模拟优化器的行为）
print("\n[3] Transpile 后的电路")
qc_transpiled = transpile(qc, optimization_level=2, basis_gates=['u3', 'cx'])
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

# 获取 transpile 后的酉矩阵
u_transpiled = Operator(qc_transpiled).data
print(f"\n[4] Transpile 后的酉矩阵 (Qiskit):\n{u_transpiled}")

# 检查差异
diff = np.linalg.norm(u_original - u_transpiled, 'fro')
print(f"\n[5] Transpile 前后 Frobenius 范数差异: {diff:.2e}")

# 手动转换到 Qibo（模拟 _convert_to_qibo）
print("\n[6] 手动转换到 Qibo")
qc_qibo = Circuit(2)

# 门映射（来自 cross_framework_optimizer.py）
gate_mapping = {
    'h': gates.H,
    'x': gates.X,
    'y': gates.Y,
    'z': gates.Z,
    'cx': gates.CNOT,
    'cz': gates.CZ,
    'swap': gates.SWAP,
    'rx': gates.RX,
    'ry': gates.RY,
    'rz': gates.RZ,
    'u1': gates.U1,
    'u2': gates.U2,
    'u3': gates.U3,
    's': gates.S,
    'sdg': lambda q: gates.S(q, trainable=False).dagger(),
    't': gates.T,
    'tdg': lambda q: gates.T(q, trainable=False).dagger(),
    'sx': gates.SX,
}

for instruction in qc_transpiled.data:
    if hasattr(instruction, 'operation'):
        gate = instruction.operation
        qubits_list = instruction.qubits
    else:
        gate = instruction[0]
        qubits_list = instruction[1]

    try:
        qubits = [q._index for q in qubits_list]
    except AttributeError:
        qubits = [qc_transpiled.qubits.index(q) for q in qubits_list]

    params = gate.params if hasattr(gate, 'params') else []
    gate_name = gate.name.lower()

    print(f"  转换: {gate_name} on {qubits}, params={params}")

    if gate_name in gate_mapping:
        gate_class = gate_mapping[gate_name]
        if params:
            qc_qibo.add(gate_class(*params, *qubits))
        else:
            qc_qibo.add(gate_class(*qubits))
    else:
        print(f"    [ERROR] 不支持的门: {gate_name}")

u_qibo = qc_qibo.unitary()
print(f"\n[7] Qibo 酉矩阵（原始）:\n{u_qibo}")

# 应用位逆序排列
n_qubits = 2
dim = 2 ** n_qubits
bit_reversal = []
for i in range(dim):
    reversed_bits = format(i, f'0{n_qubits}b')[::-1]
    reversed_idx = int(reversed_bits, 2)
    bit_reversal.append(reversed_idx)

print(f"\n[8] 位逆序排列: {bit_reversal}")
u_qibo_adjusted = u_qibo[np.ix_(bit_reversal, bit_reversal)]
print(f"Qibo 酉矩阵（调整后）:\n{u_qibo_adjusted}")

# 检查与原始电路的差异
diff_with_original = np.linalg.norm(u_original - u_qibo_adjusted, 'fro')
print(f"\n[9] 与原始电路的 Frobenius 范数差异: {diff_with_original:.2e}")

# 检查与 transpile 后电路的差异
diff_with_transpiled = np.linalg.norm(u_transpiled - u_qibo_adjusted, 'fro')
print(f"[10] 与 transpile 后电路的 Frobenius 范数差异: {diff_with_transpiled:.2e}")

# 检查全局相位
product = np.dot(u_original.conj().T, u_qibo_adjusted)
first_element = product[0, 0]
print(f"\n[11] 全局相位检查")
print(f"  U†V 的第一个元素: {first_element}")
print(f"  幅度: {np.abs(first_element)}")
print(f"  相位: {np.angle(first_element)}")

if np.abs(first_element) > 1e-15:
    phase = first_element / np.abs(first_element)
    print(f"  归一化相位: {phase}")
    normalized_diff = np.linalg.norm(u_original - phase * u_qibo_adjusted, 'fro')
    print(f"  消除全局相位后的差异: {normalized_diff:.2e}")

print("\n" + "=" * 70)
