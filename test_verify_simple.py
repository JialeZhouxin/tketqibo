#!/usr/bin/env python3
"""
简化的验证测试
"""

import sys
sys.path.insert(0, '.')

from qiskit import QuantumCircuit
from src.cross_framework_interface import optimize_circuit

print("=" * 70)
print("简化的验证测试")
print("=" * 70)

# 测试 1: Bell 电路（无 Transpiler）
print("\n[测试 1] Bell 电路 - 不使用 Transpiler")
qc1 = QuantumCircuit(2)
qc1.h(0)
qc1.cx(0, 1)

try:
    optimized = optimize_circuit(
        qc1,
        strategy="qiskit_only",
        optimization_level=0,  # 不使用 Transpiler
        verify=True
    )
    print(f"[OK] 成功: {len(qc1)} -> {optimized.ngates} 个门")
except Exception as e:
    print(f"[FAIL] 失败: {e}")

# 测试 2: 单个 H 门
print("\n[测试 2] 单个 H 门")
qc2 = QuantumCircuit(1)
qc2.h(0)

try:
    optimized = optimize_circuit(
        qc2,
        strategy="qiskit_only",
        optimization_level=0,
        verify=True
    )
    print(f"[OK] 成功: {len(qc2)} -> {optimized.ngates} 个门")
except Exception as e:
    print(f"[FAIL] 失败: {e}")

# 测试 3: 单个 X 门
print("\n[测试 3] 单个 X 门")
qc3 = QuantumCircuit(1)
qc3.x(0)

try:
    optimized = optimize_circuit(
        qc3,
        strategy="qiskit_only",
        optimization_level=0,
        verify=True
    )
    print(f"[OK] 成功: {len(qc3)} -> {optimized.ngates} 个门")
except Exception as e:
    print(f"[FAIL] 失败: {e}")

# 测试 4: RX 门（参数化门）
print("\n[测试 4] RX 门")
qc4 = QuantumCircuit(1)
qc4.rx(0.5, 0)

try:
    optimized = optimize_circuit(
        qc4,
        strategy="qiskit_only",
        optimization_level=0,
        verify=True
    )
    print(f"[OK] 成功: {len(qc4)} -> {optimized.ngates} 个门")
except Exception as e:
    print(f"[FAIL] 失败: {e}")

print("\n" + "=" * 70)
print("测试完成")
print("=" * 70)
