"""简化的量子算法性能测试.

这个脚本创建一个稳定、可靠的测试，验证Sim-Fusion优化器的性能。
"""

import sys
import time
import numpy as np
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

# 导入依赖
try:
    from qibo import Circuit as QiboCircuit, gates
    QIBO_AVAILABLE = True
    print("Qibo 可用")
except ImportError:
    QIBO_AVAILABLE = False
    print("Qibo 不可用")

try:
    from sim_fusion import sim_fusion, sim_fusion_with_stats
    SIM_FUSION_AVAILABLE = True
    print("Sim-Fusion 可用")
except ImportError:
    SIM_FUSION_AVAILABLE = False
    print("Sim-Fusion 不可用")


class SimpleQuantumTest:
    """简化的量子测试类."""

    def __init__(self):
        """初始化测试."""
        self.results = {}

    def run_all_tests(self):
        """运行所有测试."""
        print("=" * 50)
        print("简化量子算法性能测试")
        print("=" * 50)

        if not QIBO_AVAILABLE or not SIM_FUSION_AVAILABLE:
            print("ERROR: 必需的依赖不可用")
            print(f"Qibo: {QIBO_AVAILABLE}")
            print(f"Sim-Fusion: {SIM_FUSION_AVAILABLE}")
            return

        # 测试算法列表
        algorithms = [
            ("Bell State", self.test_bell_state),
            ("GHZ State", self.test_ghz_state),
            ("Simple Circuit", self.test_simple_circuit),
            ("Multi-layer Circuit", self.test_multi_layer_circuit),
            ("Controlled Circuit", self.test_controlled_circuit),
        ]

        for alg_name, test_func in algorithms:
            print(f"\n测试 {alg_name}")
            print("-" * 30)
            try:
                test_func()
            except Exception as e:
                print(f"ERROR: {alg_name} 测试失败: {e}")

        self.print_summary()

    def test_bell_state(self):
        """测试Bell态电路."""
        circuit = QiboCircuit(2)
        circuit.add(gates.H(0))
        circuit.add(gates.CNOT(0, 1))
        self._test_optimization("Bell State", circuit)

    def test_ghz_state(self):
        """测试GHZ态电路."""
        circuit = QiboCircuit(3)
        circuit.add(gates.H(0))
        circuit.add(gates.CNOT(0, 1))
        circuit.add(gates.CNOT(0, 2))
        self._test_optimization("GHZ State", circuit)

    def test_simple_circuit(self):
        """测试简单电路."""
        circuit = QiboCircuit(3)
        for i in range(3):
            circuit.add(gates.H(i))
        circuit.add(gates.CNOT(0, 1))
        circuit.add(gates.CNOT(1, 2))
        self._test_optimization("Simple Circuit", circuit)

    def test_multi_layer_circuit(self):
        """测试多层电路."""
        circuit = QiboCircuit(4)

        # 第一层：Hadamard
        for i in range(4):
            circuit.add(gates.H(i))

        # 第二层：旋转
        for i in range(4):
            circuit.add(gates.RZ(np.pi/4 * (i+1), i))

        # 第三层：CNOT链
        for i in range(3):
            circuit.add(gates.CNOT(i, i+1))

        # 第四层：更多旋转
        for i in range(4):
            circuit.add(gates.RY(np.pi/8 * (i+1), i))

        self._test_optimization("Multi-layer Circuit", circuit)

    def test_controlled_circuit(self):
        """测试受控门电路."""
        circuit = QiboCircuit(3)

        # 初始叠加态
        circuit.add(gates.H(0))
        circuit.add(gates.H(1))

        # 受控操作
        circuit.add(gates.CNOT(0, 2))
        circuit.add(gates.CZ(1, 2))
        circuit.add(gates.CNOT(1, 0))

        # 最后一些单量子比特门
        circuit.add(gates.X(0))
        circuit.add(gates.Y(1))
        circuit.add(gates.Z(2))

        self._test_optimization("Controlled Circuit", circuit)

    def _test_optimization(self, name, circuit):
        """测试电路优化."""
        try:
            original_gates = circuit.ngates
            original_depth = circuit.depth
            print(f"  原始电路: {original_gates} 门, 深度 {original_depth}")

            # 测试基础Sim-Fusion
            start_time = time.time()
            optimized = sim_fusion(circuit, verbose=False)
            total_time = time.time() - start_time

            optimized_gates = optimized.ngates
            optimized_depth = optimized.depth
            gate_reduction = original_gates - optimized_gates
            depth_reduction = original_depth - optimized_depth

            gate_reduction_percent = (gate_reduction / original_gates) * 100 if original_gates > 0 else 0
            depth_reduction_percent = (depth_reduction / original_depth) * 100 if original_depth > 0 else 0

            print(f"  优化后: {optimized_gates} 门, 深度 {optimized_depth}")
            print(f"  门减少: {gate_reduction} ({gate_reduction_percent:.1f}%)")
            print(f"  深度减少: {depth_reduction} ({depth_reduction_percent:.1f}%)")
            print(f"  优化时间: {total_time:.4f}s")

            # 存储结果
            self.results[name] = {
                'original_gates': original_gates,
                'optimized_gates': optimized_gates,
                'gate_reduction': gate_reduction,
                'gate_reduction_percent': gate_reduction_percent,
                'original_depth': original_depth,
                'optimized_depth': optimized_depth,
                'depth_reduction': depth_reduction,
                'depth_reduction_percent': depth_reduction_percent,
                'optimization_time': total_time
            }

            # 尝试高级Sim-Fusion（如果可用）
            try:
                start_time = time.time()
                optimized_adv, stats = sim_fusion_with_stats(circuit, verbose=False)
                adv_time = time.time() - start_time

                print(f"  高级优化: {optimized_adv.ngates} 门, 效率: {stats.efficiency_score:.1f}%/s")

                self.results[name]['advanced_gates'] = optimized_adv.ngates
                self.results[name]['advanced_stats'] = stats

            except Exception as e:
                print(f"  高级优化不可用: {str(e)[:30]}")

        except Exception as e:
            print(f"  ERROR: 优化失败: {e}")

    def print_summary(self):
        """打印总结报告."""
        print("\n" + "=" * 60)
        print("性能测试总结报告")
        print("=" * 60)

        if not self.results:
            print("没有测试结果")
            return

        # 总体统计
        total_original = sum(r['original_gates'] for r in self.results.values())
        total_optimized = sum(r['optimized_gates'] for r in self.results.values())
        total_reduction = total_original - total_optimized
        avg_reduction = (total_reduction / total_original) * 100 if total_original > 0 else 0

        print(f"\n总体统计:")
        print(f"  测试算法数: {len(self.results)}")
        print(f"  总原始门数: {total_original}")
        print(f"  总优化门数: {total_optimized}")
        print(f"  总门减少: {total_reduction} ({avg_reduction:.1f}%)")

        # 详细结果
        print(f"\n详细结果:")
        print("-" * 50)
        print(f"{'算法':<20} {'原始':<6} {'优化':<6} {'减少率':<8} {'时间(s)':<8}")
        print("-" * 50)

        for name, result in self.results.items():
            reduction_pct = result.get('gate_reduction_percent', 0)
            time_taken = result.get('optimization_time', 0)
            print(f"{name:<20} {result['original_gates']:<6} {result['optimized_gates']:<6} "
                  f"{reduction_pct:<8.1f} {time_taken:<8.3f}")

        # 最佳性能
        best_reduction = max(r.get('gate_reduction_percent', 0) for r in self.results.values())
        best_algorithm = max(self.results.keys(),
                           key=lambda k: self.results[k].get('gate_reduction_percent', 0))

        print(f"\n最佳优化算法:")
        print(f"  算法: {best_algorithm}")
        print(f"  门减少率: {best_reduction:.1f}%")

        # 性能分析
        print(f"\n性能分析:")
        if avg_reduction > 20:
            print("  优秀: Sim-Fusion表现出色")
        elif avg_reduction > 10:
            print("  良好: Sim-Fusion提供了有效的优化")
        elif avg_reduction > 0:
            print("  一般: Sim-Fusion提供了轻微优化")
        else:
            print("  无优化: 电路已经是最优或不适合当前优化策略")

        print(f"\n建议:")
        print("  - 对于简单电路，优化空间有限")
        print("  - 对于复杂电路，Sim-Fusion能提供更好的优化")
        print("  - 考虑使用更复杂的电路来测试完整性能")


def main():
    """主函数."""
    test_suite = SimpleQuantumTest()
    test_suite.run_all_tests()

    print(f"\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()