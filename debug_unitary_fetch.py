#!/usr/bin/env python3
"""
调试酉矩阵获取
"""

import sys
sys.path.insert(0, '.')

from qiskit import QuantumCircuit
from qiskit.quantum_info import Operator
from qibo import Circuit, gates
from cross_framework_optimizer import CrossFrameworkOptimizer
import numpy as np

print("=" * 70)
print("调试酉矩阵获取")
print("=" * 70)

# 创建优化器
optimizer = CrossFrameworkOptimizer()

# 测试 1: H 门
print("\n[测试 1] H 门")
qc_h = QuantumCircuit(1)
qc_h.h(0)

u_h_qiskit = optimizer._get_unitary(qc_h)
print(f"Qiskit H 酉矩阵:\n{u_h_qiskit}")
print(f"形状: {u_h_qiskit.shape}")

qc_h_qibo = Circuit(1)
qc_h_qibo.add(gates.H(0))
u_h_qibo = optimizer._get_unitary(qc_h_qibo)
print(f"\nQibo H 酉矩阵:\n{u_h_qibo}")
print(f"形状: {u_h_qibo.shape}")

# 测试 2: X 门
print("\n[测试 2] X 门")
qc_x = QuantumCircuit(1)
qc_x.x(0)

u_x_qiskit = optimizer._get_unitary(qc_x)
print(f"Qiskit X 酉矩阵:\n{u_x_qiskit}")
print(f"形状: {u_x_qiskit.shape}")

qc_x_qibo = Circuit(1)
qc_x_qibo.add(gates.X(0))
u_x_qibo = optimizer._get_unitary(qc_x_qibo)
print(f"\nQibo X 酉矩阵:\n{u_x_qibo}")
print(f"形状: {u_x_qibo.shape}")

# 测试 3: RX 门
print("\n[测试 3] RX(0.5) 门")
qc_rx = QuantumCircuit(1)
qc_rx.rx(0.5, 0)

u_rx_qiskit = optimizer._get_unitary(qc_rx)
print(f"Qiskit RX 酉矩阵:\n{u_rx_qiskit}")
print(f"形状: {u_rx_qiskit.shape}")

qc_rx_qibo = Circuit(1)
qc_rx_qibo.add(gates.RX(0.5, 0))
u_rx_qibo = optimizer._get_unitary(qc_rx_qibo)
print(f"\nQibo RX 酉矩阵:\n{u_rx_qibo}")
print(f"形状: {u_rx_qibo.shape}")

# 测试 4: CX 门
print("\n[测试 4] CX 门")
qc_cx = QuantumCircuit(2)
qc_cx.cx(0, 1)

u_cx_qiskit = optimizer._get_unitary(qc_cx)
print(f"Qiskit CX 酉矩阵:\n{u_cx_qiskit}")
print(f"形状: {u_cx_qiskit.shape}")

qc_cx_qibo = Circuit(2)
qc_cx_qibo.add(gates.CNOT(0, 1))
u_cx_qibo = optimizer._get_unitary(qc_cx_qibo)
print(f"\nQibo CX 酉矩阵:\n{u_cx_qibo}")
print(f"形状: {u_cx_qibo.shape}")

# 测试 5: Bell 电路
print("\n[测试 5] Bell 电路 (H + CX)")
qc_bell = QuantumCircuit(2)
qc_bell.h(0)
qc_bell.cx(0, 1)

u_bell_qiskit = optimizer._get_unitary(qc_bell)
print(f"Qiskit Bell 酉矩阵:\n{u_bell_qiskit}")
print(f"形状: {u_bell_qiskit.shape}")

qc_bell_qibo = Circuit(2)
qc_bell_qibo.add(gates.H(0))
qc_bell_qibo.add(gates.CNOT(0, 1))
u_bell_qibo = optimizer._get_unitary(qc_bell_qibo)
print(f"\nQibo Bell 酉矩阵:\n{u_bell_qibo}")
print(f"形状: {u_bell_qibo.shape}")

print("\n" + "=" * 70)
