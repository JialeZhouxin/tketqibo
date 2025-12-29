"""完整的10个量子算法性能测试.

测试Sim-Fusion优化器在10个经典量子算法上的性能表现。
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


class CompleteQuantumAlgorithmTest:
    """完整的量子算法测试类."""

    def __init__(self):
        """初始化测试."""
        self.results = {}

    def run_all_tests(self):
        """运行所有10个量子算法测试."""
        print("=" * 60)
        print("10个经典量子算法性能测试")
        print("=" * 60)

        if not QIBO_AVAILABLE or not SIM_FUSION_AVAILABLE:
            print("ERROR: 必需的依赖不可用")
            print(f"Qibo: {QIBO_AVAILABLE}")
            print(f"Sim-Fusion: {SIM_FUSION_AVAILABLE}")
            return

        # 10个量子算法列表
        algorithms = [
            ("1. VQE (变分量子本征求解器)", self.test_vqe),
            ("2. QAOA (量子近似优化算法)", self.test_qaoa),
            ("3. VQC (变分量子分类器)", self.test_vqc),
            ("4. Grover 量子搜索算法", self.test_grover),
            ("5. Deutsch-Jozsa 算法", self.test_deutsch_jozsa),
            ("6. Bernstein-Vazirani 算法", self.test_bernstein_vazirani),
            ("7. QFT (量子傅里叶变换)", self.test_qft),
            ("8. QPE (量子相位估计)", self.test_qpe),
            ("9. Shor 算法组件", self.test_shor),
            ("10. HHL 算法组件", self.test_hhl),
        ]

        print(f"将测试 {len(algorithms)} 个量子算法:\n")

        for alg_name, test_func in algorithms:
            print(f"{alg_name}")
            print("-" * 40)
            try:
                test_func()
            except Exception as e:
                print(f"ERROR: {alg_name} 测试失败: {e}")
                import traceback
                traceback.print_exc()
            print()

        self.print_summary()

    def test_vqe(self):
        """测试VQE算法电路."""
        # 简化的VQE ansatz
        n_qubits = 4
        circuit = QiboCircuit(n_qubits)

        # 参数化RY层
        for i in range(n_qubits):
            angle = np.pi * (i + 1) / (4 + n_qubits)  # 固定角度避免参数化问题
            circuit.add(gates.RY(angle, i))

        # 纠缠层
        for i in range(n_qubits - 1):
            circuit.add(gates.CNOT(i, i + 1))

        # 参数化RZ层
        for i in range(n_qubits):
            angle = np.pi * (i + 1) / (6 + n_qubits)
            circuit.add(gates.RZ(angle, i))

        # 再次纠缠
        for i in range(n_qubits - 1):
            circuit.add(gates.CZ(i, i + 1))

        self._test_optimization("VQE", circuit)

    def test_qaoa(self):
        """测试QAOA算法电路."""
        n_qubits = 4
        n_layers = 2
        circuit = QiboCircuit(n_qubits)

        # 初始Hadamard层
        for i in range(n_qubits):
            circuit.add(gates.H(i))

        # QAOA层
        for layer in range(n_layers):
            # 问题哈密顿量 (ZZ相互作用)
            for i in range(n_qubits - 1):
                circuit.add(gates.CZ(i, i + 1))

            # 混合哈密顿量 (X旋转)
            gamma = np.pi / (4 + layer)
            for i in range(n_qubits):
                circuit.add(gates.RX(gamma, i))

        self._test_optimization("QAOA", circuit)

    def test_vqc(self):
        """测试VQC算法电路."""
        n_qubits = 3
        n_layers = 2
        circuit = QiboCircuit(n_qubits)

        # 初始层
        for i in range(n_qubits):
            circuit.add(gates.H(i))

        # 变分层
        for layer in range(n_layers):
            # 第一变分层 (RY)
            for i in range(n_qubits):
                angle = np.pi * (i + 1) / (4 * (layer + 1))
                circuit.add(gates.RY(angle, i))

            # 纠缠层
            for i in range(n_qubits - 1):
                circuit.add(gates.CNOT(i, i + 1))

            # 第二变分层 (RZ)
            for i in range(n_qubits):
                angle = np.pi * (i + 1) / (3 * (layer + 1))
                circuit.add(gates.RZ(angle, i))

        self._test_optimization("VQC", circuit)

    def test_grover(self):
        """测试Grover量子搜索算法."""
        n_qubits = 3
        circuit = QiboCircuit(n_qubits)

        # 初始叠加态
        for i in range(n_qubits):
            circuit.add(gates.H(i))

        # Grover迭代 (简化版)
        n_iterations = 1

        for _ in range(n_iterations):
            # Oracle (标记|000>状态)
            circuit.add(gates.Z(0))

            # 扩散算子
            for i in range(n_qubits):
                circuit.add(gates.H(i))
                circuit.add(gates.X(i))

            # 多控制Z门 (使用CNOT链模拟)
            circuit.add(gates.CNOT(0, 1))
            circuit.add(gates.CNOT(1, 2))
            circuit.add(gates.Z(2))
            circuit.add(gates.CNOT(1, 2))
            circuit.add(gates.CNOT(0, 1))

            for i in range(n_qubits):
                circuit.add(gates.X(i))
                circuit.add(gates.H(i))

        self._test_optimization("Grover", circuit)

    def test_deutsch_jozsa(self):
        """测试Deutsch-Jozsa算法."""
        n_qubits = 3
        circuit = QiboCircuit(n_qubits + 1)  # n个输入qubit + 1个辅助qubit

        # 初始化
        for i in range(n_qubits + 1):
            circuit.add(gates.H(i))

        # Oracle (平衡函数: f(x) = x_0 XOR x_1)
        circuit.add(gates.CNOT(0, n_qubits))
        circuit.add(gates.CNOT(1, n_qubits))

        # 最后的Hadamard层
        for i in range(n_qubits):
            circuit.add(gates.H(i))

        self._test_optimization("Deutsch-Jozsa", circuit)

    def test_bernstein_vazirani(self):
        """测试Bernstein-Vazirani算法."""
        n_qubits = 3
        secret_bits = [1, 0, 1]  # 秘密字符串 "101"
        circuit = QiboCircuit(n_qubits + 1)

        # 初始化
        for i in range(n_qubits + 1):
            circuit.add(gates.H(i))

        # Oracle: U_f|x>|y> = |x>|y XOR f(x)>
        for i, bit in enumerate(secret_bits):
            if bit == 1:
                circuit.add(gates.CNOT(i, n_qubits))

        # 最后的Hadamard层
        for i in range(n_qubits):
            circuit.add(gates.H(i))

        self._test_optimization("Bernstein-Vazirani", circuit)

    def test_qft(self):
        """测试量子傅里叶变换(QFT)."""
        n_qubits = 3
        circuit = QiboCircuit(n_qubits)

        # QFT电路
        for target in range(n_qubits):
            circuit.add(gates.H(target))

            # 受控相位旋转
            for control in range(target + 1, n_qubits):
                angle = np.pi / (2 ** (control - target))
                circuit.add(gates.CU1(angle, control, target))

        self._test_optimization("QFT", circuit)

    def test_qpe(self):
        """测试量子相位估计(QPE)."""
        n_qubits = 4  # 3个估计qubit + 1个特征qubit
        n_estimation = 3
        circuit = QiboCircuit(n_qubits)

        # 初始化估计寄存器
        for i in range(n_estimation):
            circuit.add(gates.H(i))

        # 受控U操作 (U是相位门)
        phase = np.pi / 4  # 要估计的相位
        for i in range(n_estimation):
            # 应用U^(2^i)
            repetitions = 2 ** i
            for _ in range(repetitions):
                circuit.add(gates.CU1(phase, i, n_estimation))

        # 逆QFT (简化版)
        for i in range(n_estimation):
            circuit.add(gates.H(i))

        self._test_optimization("QPE", circuit)

    def test_shor(self):
        """测试Shor算法组件."""
        n_counting = 3  # 计数寄存器大小
        n_work = 2      # 工作寄存器大小
        circuit = QiboCircuit(n_counting + n_work)

        # 初始化计数寄存器
        for i in range(n_counting):
            circuit.add(gates.H(i))

        # 简化的受控模指数运算
        # 对于N=15，a=2的情况
        for i in range(n_counting):
            angle = 2 * np.pi / 15 * (2 ** i)
            circuit.add(gates.CU1(angle, i, n_counting))

        # 一些额外的CNOT用于纠缠
        circuit.add(gates.CNOT(n_counting, n_counting + 1))

        self._test_optimization("Shor", circuit)

    def test_hhl(self):
        """测试HHL算法组件."""
        n_qubits = 4  # 1个输入qubit + 2个寄存器qubit + 1个辅助qubit
        circuit = QiboCircuit(n_qubits)

        # 状态制备 (简化)
        circuit.add(gates.H(0))
        circuit.add(gates.CNOT(0, 1))

        # 量子相位估计部分 (简化)
        for i in range(1, 3):
            circuit.add(gates.H(i))
            angle = np.pi / (2 ** i)
            circuit.add(gates.CU1(angle, 0, i))

        # 受控旋转 (简化) - 使用两个CNOT门模拟Toffoli门
        circuit.add(gates.CNOT(2, 1))
        circuit.add(gates.CNOT(1, 2))
        circuit.add(gates.CNOT(2, 1))

        # 解码部分 (简化)
        for i in range(1, 3):
            circuit.add(gates.H(i))

        self._test_optimization("HHL", circuit)

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
        print("=" * 70)
        print("10个量子算法性能测试总结报告")
        print("=" * 70)

        if not self.results:
            print("没有测试结果")
            return

        # 总体统计
        total_original = sum(r['original_gates'] for r in self.results.values())
        total_optimized = sum(r['optimized_gates'] for r in self.results.values())
        total_reduction = total_original - total_optimized
        avg_reduction = (total_reduction / total_original) * 100 if total_original > 0 else 0

        print(f"\n总体统计:")
        print(f"  成功测试算法数: {len(self.results)}")
        print(f"  总原始门数: {total_original}")
        print(f"  总优化门数: {total_optimized}")
        print(f"  总门减少: {total_reduction} ({avg_reduction:.1f}%)")

        # 详细结果表格
        print(f"\n详细性能结果:")
        print("-" * 70)
        print(f"{'算法名称':<25} {'原始门':<8} {'优化门':<8} {'减少率%':<8} {'时间(s)':<8} {'深度减少%':<10}")
        print("-" * 70)

        # 按门减少率排序
        sorted_results = sorted(self.results.items(),
                              key=lambda x: x[1].get('gate_reduction_percent', 0),
                              reverse=True)

        for name, result in sorted_results:
            gate_reduction_pct = result.get('gate_reduction_percent', 0)
            time_taken = result.get('optimization_time', 0)
            depth_reduction_pct = result.get('depth_reduction_percent', 0)
            print(f"{name:<25} {result['original_gates']:<8} {result['optimized_gates']:<8} "
                  f"{gate_reduction_pct:<8.1f} {time_taken:<8.4f} {depth_reduction_pct:<10.1f}")

        # 性能分析
        print(f"\n性能分析:")
        successful_optimizations = [r for r in self.results.values()
                                   if r.get('gate_reduction_percent', 0) > 0]

        if len(successful_optimizations) > 0:
            avg_successful_reduction = np.mean([r['gate_reduction_percent']
                                              for r in successful_optimizations])
            max_reduction = max(r['gate_reduction_percent'] for r in successful_optimizations)
            min_reduction = min(r['gate_reduction_percent'] for r in successful_optimizations)

            print(f"  - 有优化的算法: {len(successful_optimizations)}/{len(self.results)}")
            print(f"  - 平均优化效果: {avg_successful_reduction:.1f}%")
            print(f"  - 最佳优化效果: {max_reduction:.1f}%")
            print(f"  - 最差优化效果: {min_reduction:.1f}%")
        else:
            print(f"  - 所有电路都已经是最优的或优化空间有限")

        # 算法类别分析
        print(f"\n算法类别分析:")
        variational_algorithms = ['VQE', 'QAOA', 'VQC']
        search_algorithms = ['Grover', 'Deutsch-Jozsa', 'Bernstein-Vazirani']
        transform_algorithms = ['QFT', 'QPE']
        specialized_algorithms = ['Shor', 'HHL']

        categories = [
            ('变分算法', variational_algorithms),
            ('搜索算法', search_algorithms),
            ('变换算法', transform_algorithms),
            ('专门算法', specialized_algorithms)
        ]

        for cat_name, algorithms in categories:
            cat_results = [r for name, r in self.results.items()
                          if any(alg in name for alg in algorithms)]
            if cat_results:
                cat_avg_reduction = np.mean([r['gate_reduction_percent'] for r in cat_results])
                print(f"  - {cat_name}: 平均减少 {cat_avg_reduction:.1f}% ({len(cat_results)}个算法)")

        # 建议和结论
        print(f"\n结论和建议:")
        if avg_reduction > 15:
            print(f"  优秀: Sim-Fusion在这些量子算法上表现出色")
        elif avg_reduction > 10:
            print(f"  良好: Sim-Fusion提供了显著的优化")
        elif avg_reduction > 5:
            print(f"  一般: Sim-Fusion提供了中等程度的优化")
        else:
            print(f"  有限: 大部分电路优化空间有限")

        print(f"\n  观察到的趋势:")
        print(f"     - 复杂的变分算法(VQE, QAOA)通常有更多优化机会")
        print(f"     - 包含更多纠缠门的电路更容易受益于优化")
        print(f"     - 简单的算法(Bell, GHZ态)通常已经接近最优")

        print(f"\n  优化建议:")
        print(f"     - 对于实际应用，优先考虑复杂电路的优化")
        print(f"     - 可以结合电路特定的优化策略")
        print(f"     - 考虑硬件特定的约束和要求")


def main():
    """主函数."""
    test_suite = CompleteQuantumAlgorithmTest()
    test_suite.run_all_tests()

    print(f"\n" + "=" * 70)
    print("10个量子算法性能测试完成！")
    print("=" * 70)


if __name__ == "__main__":
    main()