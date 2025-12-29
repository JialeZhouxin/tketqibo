#!/usr/bin/env python3
"""
快速验证 Qibo Fusion 修复效果
"""

import sys
sys.path.insert(0, '.')

from qibo import Circuit, gates
import time

print("=" * 70)
print("Qibo Fusion 快速验证测试")
print("=" * 70)

# 创建一个简单的测试电路
print("\n[测试 1] 简单电路 (10 量子比特)")
circuit1 = Circuit(10)

# 添加一些门
for q in range(10):
    circuit1.add(gates.H(q))
    circuit1.add(gates.RY(q, 0.5))

for q in range(0, 9, 2):
    circuit1.add(gates.CNOT(q, q + 1))

print(f"原始电路: {circuit1.ngates} 个门")

# 应用融合
fused1 = circuit1.fuse()
print(f"融合电路: {fused1.ngates} 个门")
print(f"门减少: {circuit1.ngates - fused1.ngates} ({(circuit1.ngates - fused1.ngates)/circuit1.ngates*100:.1f}%)")

# 测试执行时间
print("\n执行时间对比:")

# 原始电路
start = time.time()
for _ in range(5):
    result1 = circuit1()
time_original = time.time() - start

# 融合电路
start = time.time()
for _ in range(5):
    result2 = fused1()
time_fused = time.time() - start

print(f"  原始电路: {time_original*1000:.2f} ms")
print(f"  融合电路: {time_fused*1000:.2f} ms")
print(f"  加速比: {time_original/time_fused:.2f}x")

# 测试 2: 更深的电路
print("\n[测试 2] 深层电路 (15 量子比特)")
circuit2 = Circuit(15)

for layer in range(3):
    for q in range(15):
        circuit2.add(gates.RX(q, 0.3))
    for q in range(0, 14, 2):
        circuit2.add(gates.CNOT(q, q + 1))

print(f"原始电路: {circuit2.ngates} 个门")

fused2 = circuit2.fuse()
print(f"融合电路: {fused2.ngates} 个门")
print(f"门减少: {circuit2.ngates - fused2.ngates} ({(circuit2.ngates - fused2.ngates)/circuit2.ngates*100:.1f}%)")

# 执行时间（仅运行一次以节省时间）
print("\n执行时间对比 (单次运行):")

start = time.time()
result3 = circuit2()
time_original2 = time.time() - start

start = time.time()
result4 = fused2()
time_fused2 = time.time() - start

print(f"  原始电路: {time_original2*1000:.2f} ms")
print(f"  融合电路: {time_fused2*1000:.2f} ms")
print(f"  加速比: {time_original2/time_fused2:.2f}x")

# 测试 3: sim_fusion 完整流程
print("\n[测试 3] Sim-Fusion 完整流程")
from sim_fusion import sim_fusion

circuit3 = Circuit(12)
for q in range(12):
    circuit3.add(gates.H(q))
for q in range(0, 11, 2):
    circuit3.add(gates.CZ(q, q + 1))

print(f"原始电路: {circuit3.ngates} 个门")

start = time.time()
optimized, stats = sim_fusion(circuit3, return_stats=True, verbose=False)
opt_time = time.time() - start

print(f"优化后电路: {optimized.ngates} 个门")
print(f"优化时间: {opt_time*1000:.2f} ms")
print(f"门减少: {stats.gate_reduction} ({stats.gate_reduction_percent:.1f}%)")

print("\n" + "=" * 70)
print("✅ Fusion 修复验证完成")
print("=" * 70)
