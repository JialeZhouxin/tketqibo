#!/usr/bin/env python3
"""Sim-Fusion 快速入门测试脚本
运行此脚本来验证 Sim-Fusion 的基本功能
"""

from qibo import Circuit, gates
from sim_fusion import sim_fusion, quick_sim_fusion, sim_fusion_with_stats, analyze_optimization

def test_basic_usage():
    """测试基础使用"""
    print("=== 1. 基础使用测试 ===")

    circuit = Circuit(2)
    circuit.add(gates.H(0))
    circuit.add(gates.CNOT(0, 1))

    print(f"原始电路: {circuit.ngates} 个门")

    # 基本优化
    optimized = sim_fusion(circuit)
    print(f"优化后: {optimized.ngates} 个门")

    # 快速优化
    quick_opt = quick_sim_fusion(circuit)
    print(f"快速优化后: {quick_opt.ngates} 个门")

    return True

def test_statistics():
    """测试统计信息"""
    print("\n=== 2. 统计信息测试 ===")

    circuit = Circuit(2)
    circuit.add(gates.H(0))
    circuit.add(gates.CNOT(0, 1))

    optimized, stats = sim_fusion_with_stats(circuit, verbose=False)

    print(f"门减少: {stats.gate_reduction} ({stats.gate_reduction_percent:.1f}%)")
    print(f"优化时间: {stats.total_time:.6f}s")
    print(f"TKET时间: {stats.tket_time:.6f}s")
    print(f"效率分数: {stats.efficiency_score:.1f}%/s")

    return True

def test_redundancy_removal():
    """测试冗余消除"""
    print("\n=== 3. 冗余消除测试 ===")

    # 创建包含冗余操作的电路
    circuit = Circuit(2)
    circuit.add(gates.H(0))
    circuit.add(gates.H(0))      # H*H = I
    circuit.add(gates.X(1))
    circuit.add(gates.X(1))      # X*X = I
    circuit.add(gates.CNOT(0, 1))

    print(f"冗余电路原始: {circuit.ngates} 个门")

    optimized, stats = sim_fusion_with_stats(circuit, verbose=False)

    print(f"优化后: {optimized.ngates} 个门")
    print(f"减少: {stats.gate_reduction} 个门 ({stats.gate_reduction_percent:.1f}%)")

    return True

def test_circuit_analysis():
    """测试电路分析"""
    print("\n=== 4. 电路分析测试 ===")

    circuit = Circuit(2)
    circuit.add(gates.H(0))
    circuit.add(gates.CNOT(0, 1))

    analysis = analyze_optimization(circuit)

    print(f"电路统计: {analysis['basic_stats']}")
    print(f"门分布: {analysis['gate_distribution']}")
    print(f"优化潜力: {analysis['optimization_potential']}")
    print(f"TKET可用: {analysis['tket_available']}")

    return True

def test_error_handling():
    """测试错误处理"""
    print("\n=== 5. 错误处理测试 ===")

    try:
        from sim_fusion import SimFusionError

        # 测试无效输入
        sim_fusion("not_a_circuit")
        print("ERROR: 应该抛出错误")
        return False

    except SimFusionError as e:
        print(f"PASS: 正确捕获错误: {e}")
        return True
    except Exception as e:
        print(f"ERROR: 意外错误: {e}")
        return False

def test_environment():
    """测试环境配置"""
    print("\n=== 6. 环境检查 ===")

    import sim_fusion

    print(f"QIBO_AVAILABLE: {sim_fusion.QIBO_AVAILABLE}")
    print(f"TKET_AVAILABLE: {sim_fusion.TKET_AVAILABLE}")

    if sim_fusion.TKET_AVAILABLE:
        print("FULL: 完整功能可用 (TKET + Qibo)")
    else:
        print("LIMITED: 仅回退功能可用 (Qibo only)")

    return True

def run_all_tests():
    """运行所有测试"""
    print("Sim-Fusion 快速入门测试")
    print("=" * 40)

    tests = [
        ("基础使用", test_basic_usage),
        ("统计信息", test_statistics),
        ("冗余消除", test_redundancy_removal),
        ("电路分析", test_circuit_analysis),
        ("错误处理", test_error_handling),
        ("环境检查", test_environment),
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                print(f"FAIL: {test_name} 测试失败")
        except Exception as e:
            print(f"ERROR: {test_name} 测试出错: {e}")

    print(f"\n=== 测试结果 ===")
    print(f"通过: {passed}/{total}")
    print(f"成功率: {passed/total*100:.1f}%")

    if passed == total:
        print("SUCCESS: 所有测试通过！Sim-Fusion 准备就绪。")
    else:
        print("WARNING: 部分测试失败，请检查环境配置。")

    return passed == total

if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)