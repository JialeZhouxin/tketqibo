#!/usr/bin/env python3
"""
场景 A: Qiskit电路优化（默认策略）

需求: 输入Qiskit电路 → 使用默认策略优化 → 导出Qibo对象

使用方法:
    python mwe_scenario_a_qiskit_to_qibo.py
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qiskit import QuantumCircuit
from src.cross_framework_interface import optimize_qiskit

def main():
    print("=" * 70)
    print("场景 A: Qiskit → Qibo 优化（使用默认策略）")
    print("=" * 70)

    # ============================================
    # 步骤 1: 创建 Qiskit 电路
    # ============================================
    print("\n[步骤 1] 创建 Qiskit 电路")
    qc_qiskit = QuantumCircuit(2)
    qc_qiskit.h(0)          # Hadamard 门
    qc_qiskit.cx(0, 1)      # CNOT 门
    qc_qiskit.h(0)          # 冗余的 H 门（将被优化）
    qc_qiskit.x(1)          # X 门
    qc_qiskit.x(1)          # 冗余的 X 门（将被抵消）

    print(f"  原始 Qiskit 电路: {len(qc_qiskit)} 个门")
    print(f"  深度: {qc_qiskit.depth()}")

    # ============================================
    # 步骤 2: 使用默认策略优化转换
    # ============================================
    print("\n[步骤 2] 执行优化转换")
    print("  使用函数: optimize_qiskit()")
    print("  默认参数: strategy='qiskit_only', level=2")

    optimized_qibo = optimize_qiskit(qc_qiskit)

    # ============================================
    # 步骤 3: 验证优化结果
    # ============================================
    print("\n[步骤 3] 验证优化结果")
    print(f"  优化后 Qibo 电路: {optimized_qibo.ngates} 个门")
    print(f"  深度: {optimized_qibo.depth}")

    # 显示门序列
    print("\n  门序列:")
    for i, gate in enumerate(optimized_qibo.queue):
        gate_name = gate.__class__.__name__
        print(f"    [{i}] {gate_name}")

    # ============================================
    # 步骤 4: 执行电路
    # ============================================
    print("\n[步骤 4] 执行 Qibo 电路")
    result = optimized_qibo()

    print(f"  测量结果: {result}")

    # ============================================
    # 总结
    # ============================================
    print("\n" + "=" * 70)
    print("优化完成!")
    print(f"  门数变化: {len(qc_qiskit)} → {optimized_qibo.ngates}")
    print(f"  减少: {len(qc_qiskit) - optimized_qibo.ngates} 个门")
    print("=" * 70)

if __name__ == "__main__":
    main()
