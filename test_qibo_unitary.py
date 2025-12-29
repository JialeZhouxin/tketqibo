#!/usr/bin/env python3
"""
直接测试 Qibo 的 unitary() 方法
"""

import sys
sys.path.insert(0, '.')

from qibo import Circuit, gates
import numpy as np

print("=" * 70)
print("Qibo unitary() 方法测试")
print("=" * 70)

# 测试 1: 单量子比特电路
print("\n[测试 1] 单量子比特 H 门")
qc1 = Circuit(1)
qc1.add(gates.H(0))
print(f"电路量子比特数: {qc1.nqubits}")
print(f"电路门数: {qc1.ngates}")
u1 = qc1.unitary()
print(f"酉矩阵形状: {u1.shape}")
print(f"酉矩阵:\n{u1}")

# 测试 2: 单量子比特 RX 门
print("\n[测试 2] 单量子比特 RX 门")
qc2 = Circuit(1)
qc2.add(gates.RX(0.5, 0))
print(f"电路量子比特数: {qc2.nqubits}")
print(f"电路门数: {qc2.ngates}")
u2 = qc2.unitary()
print(f"酉矩阵形状: {u2.shape}")
print(f"酉矩阵:\n{u2}")

# 测试 3: 使用 execute() 获取酉矩阵
print("\n[测试 3] 使用 execute() 获取 RX 门的酉矩阵")
from qibo import set_backend
set_backend("numpy")

qc3 = Circuit(1)
qc3.add(gates.RX(0.5, 0))
result = qc3.execute()
state_vector = result.state()
print(f"状态向量形状: {state_vector.shape}")
print(f"状态向量:\n{state_vector}")

# 测试 4: 直接从门获取酉矩阵
print("\n[测试 4] 直接从 RX 门获取酉矩阵")
rx_gate = gates.RX(0.5)
u_rx = rx_gate.unitary
print(f"RX 门酉矩阵形状: {u_rx.shape}")
print(f"RX 门酉矩阵:\n{u_rx}")

# 测试 5: H 门酉矩阵
print("\n[测试 5] 直接从 H 门获取酉矩阵")
h_gate = gates.H()
u_h = h_gate.unitary
print(f"H 门酉矩阵形状: {u_h.shape}")
print(f"H 门酉矩阵:\n{u_h}")

print("\n" + "=" * 70)
