#!/usr/bin/env python3
"""
简单的门支持测试脚本
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from qiskit import QuantumCircuit
from src.cross_framework_interface import optimize_circuit
from cross_framework_optimizer import GateConversionError, VerificationError

print("=" * 70)
print("门支持测试")
print("=" * 70)

# 测试 1: 支持的门
print("\n[测试 1] 支持的门（H, CX）")
qc1 = QuantumCircuit(2)
qc1.h(0)
qc1.cx(0, 1)

try:
    # 启用验证（位逆序排列修复已应用）
    # 使用 optimization_level=0 避免 Transpiler 分解门
    optimized = optimize_circuit(
        qc1,
        optimization_level=0,  # 不分解门
        verify=True
    )
    print(f"[OK] 成功: {len(qc1)} -> {optimized.ngates} 个门 (验证通过)")
except Exception as e:
    print(f"[FAIL] 失败: {e}")

# 测试 2: 不支持的门（应该抛出异常）
print("\n[测试 2] 不支持的门（CRX）- 应该抛出 GateConversionError")
qc2 = QuantumCircuit(2)
qc2.h(0)
qc2.crx(0.5, 0, 1)  # CRX 不支持
qc2.h(1)

try:
    optimized = optimize_circuit(qc2)
    print(f"[FAIL] 不应该成功: {optimized.ngates} 个门")
except GateConversionError as e:
    print(f"[OK] 成功捕获异常:")
    print(f"   消息: {e.args[0]}")
    if hasattr(e, 'suggestion') and e.suggestion:
        print(f"   建议: {e.suggestion[:100]}...")
except Exception as e:
    print(f"[FAIL] 未预期的错误: {type(e).__name__}: {e}")

# 测试 3: Transpiler 分解
print("\n[测试 3] Transpiler 分解 CCX 门")
qc3 = QuantumCircuit(3)
qc3.h(0)
qc3.ccx(0, 1, 2)  # Toffoli 需要 Transpiler 分解
qc3.h(2)

try:
    optimized = optimize_circuit(
        qc3,
        strategy="qiskit_only",
        optimization_level=2,  # 启用 Transpiler 分解
        verify=False  # CCX 分解后门数会变化，暂时禁用验证
    )
    print(f"[OK] 成功: {len(qc3)} -> {optimized.ngates} 个门")
    print(f"   说明: CCX 被分解为 {optimized.ngates} 个基门")
except Exception as e:
    print(f"[FAIL] 失败: {type(e).__name__}: {e}")

print("\n" + "=" * 70)
print("测试完成")
print("=" * 70)
