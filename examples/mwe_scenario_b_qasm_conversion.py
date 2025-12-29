#!/usr/bin/env python3
"""
场景 B: QASM → Qibo 转换（无优化）

需求: 仅转换格式，不进行优化

使用方法:
    python mwe_scenario_b_qasm_conversion.py
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.cross_framework_interface import optimize_qasm

def main():
    print("=" * 70)
    print("场景 B: QASM → Qibo 转换（无优化）")
    print("=" * 70)

    # ============================================
    # 步骤 1: 准备 QASM 字符串
    # ============================================
    print("\n[步骤 1] 准备 QASM 字符串")

    qasm_str = """
OPENQASM 2.0;
include "qelib1.inc";
qreg q[2];
h q[0];
cx q[0],q[1];
"""

    print("  QASM 字符串:")
    print("  " + qasm_str.strip().replace("\n", "\n  "))

    # ============================================
    # 步骤 2: 使用 strategy='none' 仅转换
    # ============================================
    print("\n[步骤 2] 执行转换（不优化）")
    print("  使用函数: optimize_qasm()")
    print("  参数: strategy='none'")

    converted_qibo = optimize_qasm(qasm_str, strategy="none")

    # ============================================
    # 步骤 3: 验证转换结果
    # ============================================
    print("\n[步骤 3] 验证转换结果")
    print(f"  转换后门数: {converted_qibo.ngates}")
    print(f"  深度: {converted_qibo.depth}")

    # 显示门序列
    print("\n  门序列:")
    for i, gate in enumerate(converted_qibo.queue):
        gate_name = gate.__class__.__name__
        print(f"    [{i}] {gate_name}")

    # ============================================
    # 步骤 4: 验证等价性
    # ============================================
    print("\n[步骤 4] 验证电路等价性")

    # 原始QASM应该有2个门（H和CX）
    original_gates = 2  # H q[0]; cx q[0],q[1];

    if converted_qibo.ngates == original_gates:
        print(f"  ✅ 转换正确: 保持 {original_gates} 个门（未优化）")
    else:
        print(f"  ⚠️  警告: 预期 {original_gates} 个门，实际 {converted_qibo.ngates} 个")

    # ============================================
    # 总结
    # ============================================
    print("\n" + "=" * 70)
    print("转换完成!")
    print("  说明: strategy='none' 仅执行格式转换，不进行优化")
    print("  用途: 适用于需要保留原始电路结构的场景")
    print("=" * 70)

if __name__ == "__main__":
    main()
