#!/usr/bin/env python3
"""
门集支持矩阵与验证功能演示

演示内容：
1. 完全支持的门（直接映射）
2. 不支持的门的错误处理
3. 酉矩阵等价性验证

使用方法:
    python gate_support_demo.py
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qiskit import QuantumCircuit
from src.cross_framework_interface import optimize_circuit
from cross_framework_optimizer import (
    GateConversionError,
    VerificationError
)

def separator():
    print("=" * 70)

def demo_supported_gates():
    """演示 1: 完全支持的门"""
    print("\n[演示 1] 完全支持的门（直接映射）")
    print("-" * 70)

    # 创建包含完全支持的门的电路
    qc = QuantumCircuit(2)
    qc.h(0)          # H 门
    qc.cx(0, 1)      # CX 门
    qc.rx(0.5, 1)    # RX 门（参数化）

    print(f"原始 Qiskit 电路: {len(qc)} 个门")
    print("  门序列: H(0), CX(0,1), RX(0.5, 1)")

    try:
        # 优化（不验证）
        optimized = optimize_circuit(
            qc,
            strategy="qiskit_only",
            optimization_level=2,
            verify=False
        )

        print(f"\n✅ 优化成功!")
        print(f"  优化后: {optimized.ngates} 个门")

    except Exception as e:
        print(f"\n❌ 错误: {e}")


def demo_unsupported_gates():
    """演示 2: 不支持的门会抛出异常"""
    print("\n[演示 2] 不支持的门的错误处理")
    print("-" * 70)

    # 创建包含不支持门的电路
    qc = QuantumCircuit(2)
    qc.h(0)
    qc.crx(0.5, 0, 1)  # CRX 门（当前不支持）
    qc.h(1)

    print(f"原始 Qiskit 电路: {len(qc)} 个门")
    print("  门序列: H(0), CRX(0.5, 0,1) [不支持], H(1)")

    try:
        # 尝试优化（会抛出异常）
        optimized = optimize_circuit(
            qc,
            strategy="qiskit_only",
            optimization_level=2
        )

        print(f"\n✅ 优化成功（不应该到这里）")

    except GateConversionError as e:
        print(f"\n🔴 捕获到 GateConversionError（预期行为）:")
        print(f"  消息: {e.args[0]}")
        if hasattr(e, 'suggestion') and e.suggestion:
            print(f"  建议: {e.suggestion}")

    except Exception as e:
        print(f"\n❌ 未预期的错误: {type(e).__name__}: {e}")


def demo_transpiler_fallback():
    """演示 3: 使用 Transpiler 分解不支持的门"""
    print("\n[演示 3] 使用 Transpiler 分解不支持的门")
    print("-" * 70)

    # 创建包含 CCX（Toffoli）门的电路
    qc = QuantumCircuit(3)
    qc.h(0)
    qc.ccx(0, 1, 2)  # Toffoli 门（需要分解）
    qc.h(2)

    print(f"原始 Qiskit 电路: {len(qc)} 个门")
    print("  门序列: H(0), CCX(0,1,2) [需要分解], H(2)")

    try:
        # 使用 Level 2 优化（Transpiler 会自动分解 CCX）
        optimized = optimize_circuit(
            qc,
            strategy="qiskit_only",
            optimization_level=2  # ← 启用 Transpiler 分解
        )

        print(f"\n✅ 优化成功!")
        print(f"  原始: 3 个门")
        print(f"  优化后: {optimized.ngates} 个门")
        print(f"  说明: CCX 被分解为多个 CX 和 U3 门")

    except Exception as e:
        print(f"\n❌ 错误: {type(e).__name__}: {e}")


def demo_verification():
    """演示 4: 酉矩阵等价性验证"""
    print("\n[演示 4] 酉矩阵等价性验证")
    print("-" * 70)

    # 创建简单电路
    qc = QuantumCircuit(2)
    qc.h(0)
    qc.cx(0, 1)

    print(f"原始 Qiskit 电路: Bell 电路")
    print("  门序列: H(0), CX(0,1)")

    try:
        # 优化并启用验证
        optimized = optimize_circuit(
            qc,
            strategy="qiskit_only",
            optimization_level=2,
            verify=True,              # ← 启用等价性验证
            verify_tolerance=1e-8     # ← 设置容差
        )

        print(f"\n✅ 优化并验证成功!")
        print(f"  原始: 2 个门")
        print(f"  优化后: {optimized.ngates} 个门")
        print(f"  等价性验证: ✓ 通过")

    except VerificationError as e:
        print(f"\n🔴 等价性验证失败:")
        print(f"  {e}")
        if hasattr(e, 'suggestion') and e.suggestion:
            print(f"  建议: {e.suggestion}")

    except Exception as e:
        print(f"\n❌ 错误: {type(e).__name__}: {e}")


def demo_verification_failure():
    """演示 5: 模拟验证失败的情况"""
    print("\n[演示 5] 模拟验证失败（手动修改电路）")
    print("-" * 70)

    print("注意: 此演示需要手动修改代码来触发验证失败")
    print("正常情况下，优化器应该保持等价性")

    qc = QuantumCircuit(2)
    qc.h(0)
    qc.cx(0, 1)

    try:
        optimized = optimize_circuit(
            qc,
            strategy="qiskit_only",
            optimization_level=2,
            verify=True
        )

        print(f"✅ 验证通过（正常情况）")
        print(f"  如果要模拟失败，可以在 _convert_gate_to_qibo 中")
        print(f"  故意跳过某个门来触发 VerificationError")

    except VerificationError as e:
        print(f"🔴 验证失败（不应该发生）:")
        print(f"  {e}")


def main():
    """主函数"""
    separator()
    print("门集支持矩阵与验证功能演示")
    separator()

    # 演示 1: 完全支持的门
    demo_supported_gates()

    # 演示 2: 不支持的门
    demo_unsupported_gates()

    # 演示 3: Transpiler 分解
    demo_transpiler_fallback()

    # 演示 4: 等价性验证
    demo_verification()

    # 演示 5: 验证失败
    demo_verification_failure()

    # 总结
    print("\n" + "=" * 70)
    print("演示完成!")
    print("\n关键要点:")
    print("  1. 完全支持的门（18 种）可以直接映射")
    print("  2. 不支持的门会抛出 GateConversionError（而非静默跳过）")
    print("  3. 使用 optimization_level >= 1 可启用 Transpiler 分解")
    print("  4. verify=True 可进行酉矩阵等价性验证")
    print("=" * 70)


if __name__ == "__main__":
    main()
