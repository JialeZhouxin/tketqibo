#!/usr/bin/env python3
"""
测试 Qibo 门对象的所有可用属性和方法
"""

import sys
sys.path.insert(0, '.')

from qibo import Circuit, gates
import numpy as np

print("=" * 70)
print("Qibo 门对象属性测试")
print("=" * 70)

# 测试 RX 门
print("\n[测试 1] RX 门对象属性")
rx_gate = gates.RX(0, 0.5)
print(f"RX 门类型: {type(rx_gate)}")
print(f"RX 门类名: {rx_gate.__class__.__name__}")
print(f"RX 门酉矩阵属性名: 'unitary'")
print(f"RX 门有 unitary 属性: {hasattr(rx_gate, 'unitary')}")

if hasattr(rx_gate, 'unitary'):
    print(f"RX.unitary 类型: {type(rx_gate.unitary)}")
    print(f"RX.unitary 值: {rx_gate.unitary}")
    print(f"说明: unitary 是 bool 属性，表示该门是否为酉门")

# 测试 H 门
print("\n[测试 2] H 门对象属性")
h_gate = gates.H(0)
print(f"H 门类型: {type(h_gate)}")
print(f"H 门类名: {h_gate.__class__.__name__}")
print(f"H 门有 unitary 属性: {hasattr(h_gate, 'unitary')}")

if hasattr(h_gate, 'unitary'):
    print(f"H.unitary 值: {h_gate.unitary}")

# 查找获取矩阵的方法
print(f"\n[H 门] 查找矩阵相关方法:")
all_attrs = dir(h_gate)
matrix_methods = [attr for attr in all_attrs if not attr.startswith('_') and callable(getattr(h_gate, attr, None))]
print(f"可调用方法（前10个）: {matrix_methods[:10]}")

# 测试 Circuit 的 unitary() 方法
print("\n[测试 3] Circuit.unitary() 方法")
qc = Circuit(1)
qc.add(gates.RX(0, 0.5))
print(f"Circuit 类型: {type(qc)}")
print(f"Circuit.nqubits: {qc.nqubits}")

# 调用 unitary() 方法
u_circuit = qc.unitary()
print(f"Circuit.unitary() 类型: {type(u_circuit)}")
print(f"Circuit.unitary() 形状: {u_circuit.shape}")
print(f"Circuit.unitary():\n{u_circuit}")

# 对比
print("\n[对比] RX 门 vs Circuit")
print(f"RX 门 unitary (bool): {rx_gate.unitary}")
print(f"Circuit.unitary() 类型: {type(u_circuit)}")
print(f"Circuit.unitary() 形状: {u_circuit.shape}")
print(f"Circuit.unitary():\n{u_circuit}")

# 测试多量子比特电路
print("\n[测试 4] 多量子比特 Circuit")
qc2 = Circuit(2)
qc2.add(gates.RX(0, 0.5))
qc2.add(gates.H(1))

u_circuit2 = qc2.unitary()
print(f"Circuit (2 qubits).unitary() 形状: {u_circuit2.shape}")
print(f"预期形状: (4, 4) = (2^2, 2^2)")

# 测试单量子比特电路
print("\n[测试 5] 单量子比特电路与门对比")
qc_single = Circuit(1)
qc_single.add(gates.RX(0, 0.5))

u_single_circuit = qc_single.unitary()
u_single_gate = gates.RX(0, 0.5).unitary

print(f"单量子比特 Circuit.unitary() 形状: {u_single_circuit.shape}")
print(f"单个 RX 门 unitary 形状: {u_single_gate.shape}")
print(f"是否相同: {np.allclose(u_single_circuit, u_single_gate)}")

# 检查所有可用属性
print("\n[测试 6] RX 门所有属性和方法")
rx = gates.RX(0, 0.5)
attrs = [attr for attr in dir(rx) if not attr.startswith('_')]
print(f"RX 门的公开属性/方法: {attrs[:20]}...")  # 只显示前20个

# 特别查找矩阵相关的方法
print("\n[测试 7] 查找矩阵相关属性")
matrix_attrs = [attr for attr in attrs if 'matrix' in attr.lower() or 'unitary' in attr.lower()]
print(f"矩阵相关属性: {matrix_attrs}")

print("\n" + "=" * 70)
