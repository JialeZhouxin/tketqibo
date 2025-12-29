#!/usr/bin/env python3
"""
场景 C: 手动指定优化等级 + 统计对比

需求: 指定optimization_level并获取详细统计数据对比

使用方法:
    python mwe_scenario_c_optimization_levels.py
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qiskit import QuantumCircuit
from src.cross_framework_interface import optimize_circuit_with_stats

def print_separator():
    print("-" * 70)

def main():
    print("=" * 70)
    print("场景 C: 优化等级对比 + 统计分析")
    print("=" * 70)

    # ============================================
    # 步骤 1: 创建测试电路（包含冗余门）
    # ============================================
    print("\n[步骤 1] 创建测试电路")

    qc = QuantumCircuit(3)
    qc.h(0)
    qc.cx(0, 1)
    qc.h(0)          # 冗余H（会被优化掉）
    qc.x(2)
    qc.x(2)          # 冗余X（会被抵消）

    print(f"  原始电路: {len(qc)} 个门")
    print("  门序列: H(0), CX(0,1), H(0), X(2), X(2)")

    # ============================================
    # 步骤 2: 测试不同优化等级
    # ============================================
    print("\n[步骤 2] 测试不同优化等级 (0-3)")
    print("  使用函数: optimize_circuit_with_stats()")

    results = []

    for level in [0, 1, 2, 3]:
        print(f"\n  优化等级 {level}:")

        try:
            # 调用优化函数
            optimized, stats = optimize_circuit_with_stats(
                qc,
                strategy="qiskit_only",
                optimization_level=level,
                verbose=False
            )

            # 提取关键统计
            original = stats['original_gates']
            opt_gates = stats['optimized_gates']
            reduction = stats['gate_reduction']
            reduction_pct = stats['gate_reduction_percent']
            opt_time = stats['optimization_time']
            conv_time = stats['conversion_time']
            total_time = stats['total_time']

            # 输出统计
            print(f"    优化后: {opt_gates} 个门")
            print(f"    门减少: {reduction} ({reduction_pct:.1f}%)")
            print(f"    优化时间: {opt_time:.4f}s")
            print(f"    转换时间: {conv_time:.4f}s")
            print(f"    总时间: {total_time:.4f}s")

            # 保存结果
            results.append({
                'level': level,
                'original': original,
                'optimized': opt_gates,
                'reduction_pct': reduction_pct,
                'opt_time': opt_time
            })

        except Exception as e:
            print(f"    ❌ 错误: {e}")

    # ============================================
    # 步骤 3: 生成对比表格
    # ============================================
    print("\n[步骤 3] 优化等级对比表")
    print_separator()

    print(f"{'等级':^6} {'原始门':^8} {'优化后':^8} {'减少率':^10} {'优化时间':^12}")
    print_separator()

    for r in results:
        print(f"{r['level']:^6} {r['original']:^8} {r['optimized']:^8} "
              f"{r['reduction_pct']:^9.1f}% {r['opt_time']:^12.4f}")

    # ============================================
    # 步骤 4: 推荐最佳等级
    # ============================================
    print("\n[步骤 4] 优化建议")

    # 找到门减少最多的等级
    best = max(results, key=lambda x: x['reduction_pct'])

    print(f"  推荐等级: {best['level']}")
    print(f"  门减少率: {best['reduction_pct']:.1f}%")
    print(f"  适用场景: 需要最大优化效果")

    if best['level'] == 3:
        print(f"  注意: 等级3耗时较长，适合最终部署")

    # ============================================
    # 总结
    # ============================================
    print("\n" + "=" * 70)
    print("统计对比完成!")
    print("\n关键发现:")
    print(f"  • 等级0: 不进行优化（快速）")
    print(f"  • 等级1-2: 轻度到中度优化（推荐日常使用）")
    print(f"  • 等级3: 激进优化（耗时较长，适合生产部署）")
    print("=" * 70)

if __name__ == "__main__":
    main()
