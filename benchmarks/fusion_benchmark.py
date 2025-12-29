#!/usr/bin/env python3
"""
Qibo Fusion 性能基准测试

对比修复前后 sim_fusion 策略的仿真执行时间。
验证矩阵融合对状态向量模拟的加速效果。
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
import numpy as np
from qibo import Circuit, gates
from sim_fusion import sim_fusion

print("=" * 80)
print("Qibo Fusion 性能基准测试")
print("=" * 80)

def create_random_circuit(n_qubits, depth):
    """创建随机量子电路.

    Args:
        n_qubits: 量子比特数
        depth: 电路深度（层数）

    Returns:
        随机量子电路
    """
    circuit = Circuit(n_qubits)

    single_qubit_gates = [gates.H, gates.X, gates.Y, gates.Z, gates.RX, gates.RY, gates.RZ]
    two_qubit_gates = [gates.CNOT, gates.CZ]

    for layer in range(depth):
        # 单量子比特门层
        for q in range(n_qubits):
            gate_class = np.random.choice(single_qubit_gates)
            if gate_class in [gates.RX, gates.RY, gates.RZ]:
                angle = np.random.uniform(0, 2 * np.pi)
                circuit.add(gate_class(q, angle))
            else:
                circuit.add(gate_class(q))

        # 两量子比特门层（仅偶数连接）
        for q in range(0, n_qubits - 1, 2):
            gate_class = np.random.choice(two_qubit_gates)
            circuit.add(gate_class(q, q + 1))

    return circuit


def benchmark_execution(circuit, nshots=10):
    """测试电路执行时间.

    Args:
        circuit: Qibo 电路
        nshots: 重复执行次数

    Returns:
        平均执行时间（秒）
    """
    times = []

    for _ in range(nshots):
        start = time.perf_counter()
        result = circuit()
        elapsed = time.perf_counter() - start
        times.append(elapsed)

    return np.mean(times), np.std(times)


def run_benchmark(n_qubits_list, depth, nshots=10):
    """运行基准测试.

    Args:
        n_qubits_list: 测试的量子比特数列表
        depth: 电路深度
        nshots: 重复执行次数
    """
    print(f"\n测试配置: depth={depth}, nshots={nshots}")
    print("-" * 80)

    results = []

    for n_qubits in n_qubits_list:
        print(f"\n[测试] {n_qubits} 量子比特电路")

        # 创建随机电路
        circuit = create_random_circuit(n_qubits, depth)

        # 获取电路深度（Qibo 中 depth 是属性，不是方法）
        try:
            circuit_depth = circuit.depth
        except AttributeError:
            circuit_depth = len(circuit.queue)

        # 测试未融合电路
        print(f"  原始电路: {circuit.ngates} 个门, 深度 {circuit_depth}")
        time_mean, time_std = benchmark_execution(circuit, nshots)
        print(f"  未融合执行时间: {time_mean*1000:.2f} ± {time_std*1000:.2f} ms")

        # 测试融合电路
        fused_circuit = circuit.fuse()
        print(f"  融合电路: {fused_circuit.ngates} 个门")
        time_mean_fused, time_std_fused = benchmark_execution(fused_circuit, nshots)
        print(f"  融合执行时间: {time_mean_fused*1000:.2f} ± {time_std_fused*1000:.2f} ms")

        # 计算加速比
        speedup = time_mean / time_mean_fused
        reduction = circuit.ngates - fused_circuit.ngates
        reduction_pct = (reduction / circuit.ngates * 100) if circuit.ngates > 0 else 0

        print(f"  门减少: {reduction} 门 ({reduction_pct:.1f}%)")
        print(f"  加速比: {speedup:.2f}x")

        results.append({
            'n_qubits': n_qubits,
            'original_gates': circuit.ngates,
            'fused_gates': fused_circuit.ngates,
            'original_time_ms': time_mean * 1000,
            'fused_time_ms': time_mean_fused * 1000,
            'speedup': speedup,
            'gate_reduction_pct': reduction_pct
        })

    return results


def test_sim_fusion_integration():
    """测试 sim_fusion 整体功能（包含 TKET 预处理）。"""
    print("\n" + "=" * 80)
    print("Sim-Fusion 完整流程测试")
    print("=" * 80)

    # 测试中等规模电路
    n_qubits = 15
    depth = 5

    circuit = create_random_circuit(n_qubits, depth)

    # 获取电路深度
    try:
        circuit_depth = circuit.depth
    except AttributeError:
        circuit_depth = len(circuit.queue)

    print(f"\n测试电路: {n_qubits} 量子比特, {depth} 深度, {circuit.ngates} 个门")

    # 使用 sim_fusion 优化
    print("\n应用 sim_fusion 优化...")
    start_opt = time.time()
    optimized_circuit, stats = sim_fusion(circuit, return_stats=True, verbose=True)
    opt_time = time.time() - start_opt

    print(f"\n优化完成，耗时: {opt_time:.4f}s")
    print(f"  门减少: {stats.gate_reduction} ({stats.gate_reduction_percent:.1f}%)")

    # 对比执行时间
    print("\n执行时间对比...")
    time_orig, _ = benchmark_execution(circuit, nshots=5)
    time_opt, _ = benchmark_execution(optimized_circuit, nshots=5)

    print(f"  原始电路: {time_orig*1000:.2f} ms")
    print(f"  优化电路: {time_opt*1000:.2f} ms")
    print(f"  执行加速: {time_orig/time_opt:.2f}x")


def main():
    """主测试函数."""
    print("\n开始性能基准测试...\n")

    # 测试 1: 不同量子比特数的电路
    print("\n[测试 1] 不同量子比特数的电路 (depth=5)")
    results1 = run_benchmark(
        n_qubits_list=[10, 15, 20],
        depth=5,
        nshots=10
    )

    # 测试 2: 深层电路
    print("\n[测试 2] 深层电路 (n_qubits=15, depth=10)")
    results2 = run_benchmark(
        n_qubits_list=[15],
        depth=10,
        nshots=5
    )

    # 测试 3: Sim-Fusion 完整流程
    test_sim_fusion_integration()

    # 总结报告
    print("\n" + "=" * 80)
    print("性能总结报告")
    print("=" * 80)

    all_results = results1 + results2

    print("\n门融合效果:")
    avg_reduction = np.mean([r['gate_reduction_pct'] for r in all_results])
    print(f"  平均门减少率: {avg_reduction:.1f}%")

    print("\n执行时间加速:")
    avg_speedup = np.mean([r['speedup'] for r in all_results])
    print(f"  平均加速比: {avg_speedup:.2f}x")

    min_speedup = np.min([r['speedup'] for r in all_results])
    max_speedup = np.max([r['speedup'] for r in all_results])
    print(f"  加速比范围: {min_speedup:.2f}x - {max_speedup:.2f}x")

    # 预期结果检查
    print("\n预期结果验证:")
    if avg_speedup >= 1.5:
        print(f"  ✅ 平均加速比 {avg_speedup:.2f}x >= 1.5x (预期范围: 1.5-3x)")
    else:
        print(f"  ⚠️  平均加速比 {avg_speedup:.2f}x < 1.5x (低于预期)")

    if avg_reduction >= 10:
        print(f"  ✅ 平均门减少率 {avg_reduction:.1f}% >= 10% (预期范围: 10-30%)")
    else:
        print(f"  ⚠️  平均门减少率 {avg_reduction:.1f}% < 10% (低于预期)")

    print("\n" + "=" * 80)
    print("基准测试完成")
    print("=" * 80)


if __name__ == "__main__":
    main()
