"""
自定义量子算法测试脚本

该脚本提供了灵活的测试配置选项，用户可以：
- 选择特定的算法进行测试
- 指定量子比特范围
- 选择优化策略
- 自定义测试参数

Author: Claude AI Assistant
Date: 2025-12-19
"""

import sys
import os
from pathlib import Path
import json
from datetime import datetime

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from simple_quantum_benchmark import SimpleQuantumBenchmark

def run_custom_test():
    """运行自定义测试"""
    print("=" * 60)
    print("量子算法优化基准测试 - 自定义测试模式")
    print("=" * 60)

    # 测试配置选项
    algorithms_available = ["Bell State", "VQE", "Grover", "QFT", "Deutsch-Jozsa"]
    strategies_available = ["none", "qiskit_only"]

    print("\n📋 可用选项:")
    print(f"算法: {', '.join(algorithms_available)}")
    print(f"策略: {', '.join(strategies_available)}")

    # 用户输入配置
    print("\n⚙️  测试配置:")

    # 选择算法
    try:
        user_input = input("请输入要测试的算法 (用逗号分隔，留空测试所有): ").strip()
        if user_input:
            selected_algorithms = [alg.strip() for alg in user_input.split(',')]
            # 验证算法名称
            for alg in selected_algorithms:
                if alg not in algorithms_available:
                    print(f"⚠️  警告: '{alg}' 不是可用算法，将被忽略")
            selected_algorithms = [alg for alg in selected_algorithms if alg in algorithms_available]
        else:
            selected_algorithms = algorithms_available

        print(f"✅ 选择的算法: {', '.join(selected_algorithms)}")
    except KeyboardInterrupt:
        print("\n👋 测试已取消")
        return
    except Exception as e:
        print(f"❌ 输入错误: {e}")
        selected_algorithms = algorithms_available
        print(f"✅ 使用默认算法: {', '.join(selected_algorithms)}")

    # 选择策略
    try:
        user_input = input("请输入优化策略 (用逗号分隔，留空测试所有): ").strip()
        if user_input:
            selected_strategies = [strategy.strip() for strategy in user_input.split(',')]
            # 验证策略名称
            for strategy in selected_strategies:
                if strategy not in strategies_available:
                    print(f"⚠️  警告: '{strategy}' 不是可用策略，将被忽略")
            selected_strategies = [strategy for strategy in selected_strategies if strategy in strategies_available]
        else:
            selected_strategies = strategies_available

        print(f"✅ 选择的策略: {', '.join(selected_strategies)}")
    except KeyboardInterrupt:
        print("\n👋 测试已取消")
        return
    except Exception as e:
        print(f"❌ 输入错误: {e}")
        selected_strategies = strategies_available
        print(f"✅ 使用默认策略: {', '.join(selected_strategies)}")

    # 量子比特数配置
    sizes_config = {
        "Bell State": [3, 5, 7],
        "VQE": [4, 6, 8],
        "Grover": [3, 5, 7],
        "QFT": [4, 6, 8],
        "Deutsch-Jozsa": [3, 5, 7]
    }

    print(f"\n🔢 量子比特配置:")
    for algorithm in selected_algorithms:
        sizes = sizes_config.get(algorithm, [4, 6])
        print(f"  {algorithm}: {sizes} 量子比特")

    # 确认测试
    try:
        confirm = input(f"\n🚀 准备开始测试 {len(selected_algorithms)} 种算法，{len(selected_strategies)} 种策略。继续吗？ (y/N): ").strip().lower()
        if confirm not in ['y', 'yes', '是']:
            print("👋 测试已取消")
            return
    except KeyboardInterrupt:
        print("\n👋 测试已取消")
        return

    # 运行基准测试
    print(f"\n🧪 开始运行基准测试...")
    print(f"📅 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 60)

    try:
        # 创建基准测试实例
        benchmark = SimpleQuantumBenchmark(verbose=True)

        # 运行自定义测试
        results = benchmark.run_simple_benchmark(
            algorithms=selected_algorithms,
            strategies=selected_strategies
        )

        # 显示测试摘要
        successful_tests = sum(1 for r in results if r.test_success)
        total_tests = len(results)

        print("-" * 60)
        print(f"📊 测试完成!")
        print(f"✅ 成功测试: {successful_tests}/{total_tests}")
        print(f"📈 成功率: {successful_tests/total_tests*100:.1f}%")

        # 保存自定义结果
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        custom_results_file = f"custom_benchmark_results_{timestamp}.json"
        benchmark.save_results(custom_results_file)

        # 生成自定义报告
        custom_report_file = f"custom_benchmark_report_{timestamp}.md"
        report = benchmark.generate_simple_report()
        with open(custom_report_file, 'w', encoding='utf-8') as f:
            f.write(report)

        print(f"\n📁 结果文件:")
        print(f"  - 测试数据: {custom_results_file}")
        print(f"  - 测试报告: {custom_report_file}")

        # 显示最佳结果
        successful_results = [r for r in results if r.test_success]
        if successful_results:
            print(f"\n🏆 最佳测试结果 (门减少率):")
            top_3 = sorted(successful_results, key=lambda x: x.gate_reduction_percent, reverse=True)[:3]

            for i, result in enumerate(top_3, 1):
                print(f"  {i}. {result.algorithm_name} ({result.optimization_strategy})")
                print(f"     量子比特: {result.n_qubits}, 门减少: {result.gate_reduction_percent:.1f}%, "
                      f"深度减少: {result.depth_reduction_percent:.1f}%")

    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

def run_quick_test():
    """运行快速测试 (预设参数)"""
    print("=" * 60)
    print("量子算法优化基准测试 - 快速测试模式")
    print("=" * 60)

    # 快速测试配置
    quick_algorithms = ["Bell State", "QFT"]
    quick_strategies = ["none", "qiskit_only"]

    print(f"🚀 快速测试配置:")
    print(f"算法: {', '.join(quick_algorithms)}")
    print(f"策略: {', '.join(quick_strategies)}")

    try:
        benchmark = SimpleQuantumBenchmark(verbose=True)

        print("\n🧪 开始快速基准测试...")
        results = benchmark.run_simple_benchmark(
            algorithms=quick_algorithms,
            strategies=quick_strategies
        )

        successful_tests = sum(1 for r in results if r.test_success)
        total_tests = len(results)

        print(f"\n📊 快速测试结果:")
        print(f"✅ 成功: {successful_tests}/{total_tests} ({successful_tests/total_tests*100:.1f}%)")

        if successful_tests > 0:
            successful_results = [r for r in results if r.test_success]
            avg_gate_reduction = sum(r.gate_reduction_percent for r in successful_results) / len(successful_results)
            avg_depth_reduction = sum(r.depth_reduction_percent for r in successful_results) / len(successful_results)

            print(f"📈 平均门减少: {avg_gate_reduction:.1f}%")
            print(f"📈 平均深度减少: {avg_depth_reduction:.1f}%")

    except Exception as e:
        print(f"❌ 快速测试失败: {e}")

def main():
    """主函数"""
    print("🔬 量子算法优化基准测试工具")
    print("选择测试模式:")
    print("1. 自定义测试 (选择算法和策略)")
    print("2. 快速测试 (预设参数)")
    print("3. 退出")

    try:
        choice = input("\n请选择 (1-3): ").strip()

        if choice == "1":
            run_custom_test()
        elif choice == "2":
            run_quick_test()
        elif choice == "3":
            print("👋 退出测试工具")
        else:
            print("❌ 无效选择，请重新运行程序")

    except KeyboardInterrupt:
        print("\n👋 测试已取消")
    except Exception as e:
        print(f"❌ 程序错误: {e}")

if __name__ == "__main__":
    main()