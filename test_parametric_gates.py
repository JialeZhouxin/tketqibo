#!/usr/bin/env python3
"""
测试参数化门（RX, RY, RZ）的验证
"""

import sys
sys.path.insert(0, '.')

from qiskit import QuantumCircuit
from src.cross_framework_interface import optimize_circuit

print("=" * 70)
print("参数化门验证测试")
print("=" * 70)

# 测试 1: RX 门
print("\n[测试 1] RX(0.5) 门")
qc1 = QuantumCircuit(1)
qc1.rx(0.5, 0)

try:
    optimized = optimize_circuit(qc1, optimization_level=0, verify=True)
    print(f"[OK] 成功: 1 -> {optimized.ngates} 个门 (验证通过)")
except Exception as e:
    print(f"[FAIL] 失败: {e}")

# 测试 2: RY 门
print("\n[测试 2] RY(1.2) 门")
qc2 = QuantumCircuit(1)
qc2.ry(1.2, 0)

try:
    optimized = optimize_circuit(qc2, optimization_level=0, verify=True)
    print(f"[OK] 成功: 1 -> {optimized.ngates} 个门 (验证通过)")
except Exception as e:
    print(f"[FAIL] 失败: {e}")

# 测试 3: RZ 门
print("\n[测试 3] RZ(0.8) 门")
qc3 = QuantumCircuit(1)
qc3.rz(0.8, 0)

try:
    optimized = optimize_circuit(qc3, optimization_level=0, verify=True)
    print(f"[OK] 成功: 1 -> {optimized.ngates} 个门 (验证通过)")
except Exception as e:
    print(f"[FAIL] 失败: {e}")

# 测试 4: 混合参数化门
print("\n[测试 4] RX + RY + RZ 组合")
qc4 = QuantumCircuit(1)
qc4.rx(0.3, 0)
qc4.ry(0.7, 0)
qc4.rz(1.1, 0)

try:
    optimized = optimize_circuit(qc4, optimization_level=0, verify=True)
    print(f"[OK] 成功: 3 -> {optimized.ngates} 个门 (验证通过)")
except Exception as e:
    print(f"[FAIL] 失败: {e}")

# 测试 5: 带参数化的多量子比特电路
print("\n[测试 5] RX(0) + CX + RY(1)")
qc5 = QuantumCircuit(2)
qc5.rx(0.5, 0)
qc5.cx(0, 1)
qc5.ry(0.8, 1)

try:
    optimized = optimize_circuit(qc5, optimization_level=0, verify=True)
    print(f"[OK] 成功: 3 -> {optimized.ngates} 个门 (验证通过)")
except Exception as e:
    print(f"[FAIL] 失败: {e}")

print("\n" + "=" * 70)
print("测试完成")
print("=" * 70)
