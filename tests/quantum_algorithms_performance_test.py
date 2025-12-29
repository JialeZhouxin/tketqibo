"""经典量子算法性能测试.

这个脚本测试跨框架量子电路优化器在多种经典量子算法上的性能表现。
包括VQE、QAOA、VQC、Grover、Deutsch-Jozsa、Bernstein-Vazirani、QFT、QPE、Shor和HHL算法。
"""

import sys
import time
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
import matplotlib.pyplot as plt
import seaborn as sns

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

# 动态导入依赖
try:
    from qibo import Circuit as QiboCircuit, gates
    from qibo.models import VQE, QAOA
    from qibo.hamiltonians import XXZ, MaxCut
    QIBO_AVAILABLE = True
except ImportError:
    QIBO_AVAILABLE = False
    QiboCircuit = None
    gates = None
    VQE = None
    QAOA = None

try:
    from qiskit import QuantumCircuit as QiskitCircuit
    from qiskit.circuit.library import (TwoLocal, RealAmplitudes, QFT, PhaseEstimation,
                                       GroverOperator, DeutschJozsa, BernsteinVazirani)
    from qiskit.algorithms import Grover, AmplificationProblem
    from qiskit.primitives import Sampler
    QISKIT_AVAILABLE = True
except ImportError:
    QISKIT_AVAILABLE = False
    QiskitCircuit = None
    Sampler = None

try:
    from src.cross_framework_interface import (
        optimize_circuit,
        optimize_circuit_with_stats,
        compare_strategies,
        analyze_circuit
    )
    INTERFACE_AVAILABLE = True
except ImportError:
    INTERFACE_AVAILABLE = False


class QuantumAlgorithmTestSuite:
    """量子算法测试套件."""

    def __init__(self):
        """初始化测试套件."""
        self.results: Dict[str, Dict[str, Any]] = {}
        self.test_algorithms = []

    def run_all_tests(self):
        """运行所有算法测试."""
        print("🚀 开始经典量子算法性能测试")
        print("=" * 60)

        if not INTERFACE_AVAILABLE:
            print("❌ 跨框架接口不可用")
            return

        if not QIBO_AVAILABLE:
            print("⚠️  Qibo不可用，相关算法测试将被跳过")

        if not QISKIT_AVAILABLE:
            print("⚠️  Qiskit不可用，相关算法测试将被跳过")

        algorithms = [
            ("VQE", self.test_vqe),
            ("QAOA", self.test_qaoa),
            ("VQC", self.test_vqc),
            ("Grover", self.test_grover),
            ("Deutsch-Jozsa", self.test_deutsch_jozsa),
            ("Bernstein-Vazirani", self.test_bernstein_vazirani),
            ("QFT", self.test_qft),
            ("QPE", self.test_qpe),
            ("Shor", self.test_shor),
            ("HHL", self.test_hhl),
        ]

        for alg_name, test_func in algorithms:
            print(f"\n🔍 测试算法: {alg_name}")
            print("-" * 40)
            try:
                start_time = time.time()
                test_func()
                total_time = time.time() - start_time
                print(f"✅ {alg_name} 测试完成 (耗时: {total_time:.2f}s)")
            except Exception as e:
                print(f"❌ {alg_name} 测试失败: {e}")
                import traceback
                traceback.print_exc()

        self.generate_summary_report()

    def test_vqe(self):
        """测试变分量子本征求解器 (VQE)."""
        if not QIBO_AVAILABLE:
            print("⚠️  Qibo不可用，跳过VQE测试")
            return

        # 创建XXZ哈密顿量
        n_qubits = 4
        hamiltonian = XXZ(n_qubits=n_qubits, hz=0.5)

        # 创建VQE ansatz电路
        def create_vqe_circuit(params):
            circuit = QiboCircuit(n_qubits)
            for i in range(n_qubits):
                circuit.add(gates.RY(params[i], i))
            for i in range(n_qubits - 1):
                circuit.add(gates.CNOT(i, i + 1))
            for i in range(n_qubits):
                circuit.add(gates.RZ(params[i + n_qubits], i))
            return circuit

        # 创建测试参数
        test_params = np.random.uniform(0, 2 * np.pi, 2 * n_qubits)
        vqe_circuit = create_vqe_circuit(test_params)

        # 转换为QASM
        qasm_str = self._qibo_to_qasm(vqe_circuit, "VQE Circuit")

        # 测试优化
        self._test_circuit_optimization("VQE", qasm_str, circuit=vqe_circuit)

    def test_qaoa(self):
        """测试量子近似优化算法 (QAOA)."""
        if not QIBO_AVAILABLE:
            print("⚠️  Qibo不可用，跳过QAOA测试")
            return

        n_qubits = 4
        n_layers = 2

        # 创建QAOA电路
        def create_qaoa_circuit(params):
            circuit = QiboCircuit(n_qubits)

            # 初始态
            for i in range(n_qubits):
                circuit.add(gates.H(i))

            # QAOA层
            params_per_layer = 2 * n_qubits
            for layer in range(n_layers):
                layer_params = params[layer * params_per_layer:(layer + 1) * params_per_layer]

                # 问题哈密顿量 (MaxCut的简化版本)
                for i in range(n_qubits - 1):
                    circuit.add(gates.CZ(i, i + 1))

                # 混合哈密顿量
                for i in range(n_qubits):
                    circuit.add(gates.RX(layer_params[i], i))
                    circuit.add(gates.RX(layer_params[i + n_qubits], i))

            return circuit

        test_params = np.random.uniform(0, np.pi, n_layers * 2 * n_qubits)
        qaoa_circuit = create_qaoa_circuit(test_params)

        # 转换为QASM
        qasm_str = self._qibo_to_qasm(qaoa_circuit, "QAOA Circuit")

        # 测试优化
        self._test_circuit_optimization("QAOA", qasm_str, circuit=qaoa_circuit)

    def test_vqc(self):
        """测试变分量子分类器 (VQC)."""
        if not QISKIT_AVAILABLE:
            print("⚠️  Qiskit不可用，跳过VQC测试")
            return

        # 使用Qiskit的TwoLocal创建VQC电路
        n_qubits = 3
        vqc_circuit = TwoLocal(n_qubits, ['ry', 'rz'], 'cx', reps=2, entanglement='linear')

        # 绑定参数（随机值）
        vqc_circuit = vqc_circuit.bind_parameters(np.random.uniform(-np.pi, np.pi, vqc_circuit.num_parameters))

        # 转换为QASM
        qasm_str = vqc_circuit.qasm()

        # 测试优化
        self._test_circuit_optimization("VQC", qasm_str, circuit=vqc_circuit)

    def test_grover(self):
        """测试格罗弗搜索算法."""
        if QISKIT_AVAILABLE:
            # 使用Qiskit创建Grover电路
            n_qubits = 3
            # 创建oracle (|000⟩ 状态)
            oracle = QuantumCircuit(n_qubits)
            oracle.z(0)  # 简单oracle

            # 创建Grover算子
            grover_operator = GroverOperator(oracle)

            # 创建Grover电路
            grover_circuit = QuantumCircuit(n_qubits)
            # 初始状态
            for i in range(n_qubits):
                grover_circuit.h(i)
            # 应用Grover算子
            grover_circuit.compose(grover_operator, inplace=True)

            qasm_str = grover_circuit.qasm()
            self._test_circuit_optimization("Grover", qasm_str, circuit=grover_circuit)

        elif QIBO_AVAILABLE:
            # 使用Qibo创建简化的Grover电路
            n_qubits = 3
            grover_circuit = QiboCircuit(n_qubits)

            # 初始叠加态
            for i in range(n_qubits):
                grover_circuit.add(gates.H(i))

            # 简化的Grover迭代
            for i in range(n_qubits - 1):
                grover_circuit.add(gates.CNOT(i, i + 1))

            # Oracle标记 (简化的相位标记)
            grover_circuit.add(gates.Z(0))

            # 扩散算子 (简化版本)
            for i in range(n_qubits):
                grover_circuit.add(gates.H(i))
                grover_circuit.add(gates.X(i))

            if n_qubits > 1:
                grover_circuit.add(gates.CNOT(0, n_qubits - 1))

            for i in range(n_qubits):
                grover_circuit.add(gates.X(i))
                grover_circuit.add(gates.H(i))

            qasm_str = self._qibo_to_qasm(grover_circuit, "Grover Circuit")
            self._test_circuit_optimization("Grover", qasm_str, circuit=grover_circuit)

        else:
            print("⚠️  Qiskit和Qibo都不可用，跳过Grover测试")

    def test_deutsch_jozsa(self):
        """测试德意志-乔萨算法."""
        if QISKIT_AVAILABLE:
            # 使用Qiskit的Deutsch-Jozsa电路
            n_qubits = 3
            dj_circuit = DeutschJozsa(n_qubits, oracle_type='balanced')
            dj_circuit.measure_all()  # 添加测量

            qasm_str = dj_circuit.qasm()
            self._test_circuit_optimization("Deutsch-Jozsa", qasm_str, circuit=dj_circuit)

        elif QIBO_AVAILABLE:
            # 手动创建Deutsch-Jozsa电路
            n_qubits = 2
            dj_circuit = QiboCircuit(n_qubits + n_qubits)  # n个量子比特 + n个经典比特

            # 初始化
            for i in range(n_qubits):
                dj_circuit.add(gates.H(i))

            # Oracle (平衡函数的简化版本)
            dj_circuit.add(gates.CNOT(0, 1))

            # 应用Hadamard门
            for i in range(n_qubits):
                dj_circuit.add(gates.H(i))

            qasm_str = self._qibo_to_qasm(dj_circuit, "Deutsch-Jozsa Circuit")
            self._test_circuit_optimization("Deutsch-Jozsa", qasm_str, circuit=dj_circuit)

        else:
            print("⚠️  Qiskit和Qibo都不可用，跳过Deutsch-Jozsa测试")

    def test_bernstein_vazirani(self):
        """测试伯恩斯坦-瓦兹拉尼算法."""
        if QISKIT_AVAILABLE:
            # 使用Qiskit的Bernstein-Vazirani电路
            n_qubits = 3
            secret_string = "101"
            bv_circuit = BernsteinVazirani(n_qubits, oracle_type='bitstring', secret_string=secret_string)
            bv_circuit.measure_all()

            qasm_str = bv_circuit.qasm()
            self._test_circuit_optimization("Bernstein-Vazirani", qasm_str, circuit=bv_circuit)

        elif QIBO_AVAILABLE:
            # 手动创建Bernstein-Vazirani电路
            n_qubits = 3
            secret_bits = [1, 0, 1]  # "101"

            bv_circuit = QiboCircuit(n_qubits + n_qubits)

            # 初始化
            for i in range(n_qubits):
                bv_circuit.add(gates.H(i))

            # Oracle
            for i, bit in enumerate(secret_bits):
                if bit == 1:
                    bv_circuit.add(gates.CNOT(i, n_qubits - 1))

            # 应用Hadamard门
            for i in range(n_qubits):
                bv_circuit.add(gates.H(i))

            qasm_str = self._qibo_to_qasm(bv_circuit, "Bernstein-Vazirani Circuit")
            self._test_circuit_optimization("Bernstein-Vazirani", qasm_str, circuit=bv_circuit)

        else:
            print("⚠️  Qiskit和Qibo都不可用，跳过Bernstein-Vazirani测试")

    def test_qft(self):
        """测试量子傅里叶变换."""
        if QISKIT_AVAILABLE:
            # 使用Qiskit的QFT电路
            n_qubits = 4
            qft_circuit = QFT(n_qubits, do_swaps=False)

            # 添加一些预处理门使其更复杂
            for i in range(n_qubits):
                qft_circuit.h(i)

            qft_circuit.measure_all()
            qasm_str = qft_circuit.qasm()

            self._test_circuit_optimization("QFT", qasm_str, circuit=qft_circuit)

        elif QIBO_AVAILABLE:
            # 手动创建QFT电路
            n_qubits = 3
            qft_circuit = QiboCircuit(n_qubits + n_qubits)

            # QFT算法
            for target in range(n_qubits):
                qft_circuit.add(gates.H(target))

                for control in range(target + 1, n_qubits):
                    angle = np.pi / (2 ** (control - target))
                    qft_circuit.add(gates.CU1(angle, control, target))

            # 交换量子比特
            for i in range(n_qubits // 2):
                qft_circuit.add(gates.SWAP(i, n_qubits - i - 1))

            qasm_str = self._qibo_to_qasm(qft_circuit, "QFT Circuit")
            self._test_circuit_optimization("QFT", qasm_str, circuit=qft_circuit)

        else:
            print("⚠️  Qiskit和Qibo都不可用，跳过QFT测试")

    def test_qpe(self):
        """测试量子相位估计."""
        if QISKIT_AVAILABLE:
            # 简化的QPE电路
            n_estimation_qubits = 3
            n_target_qubits = 1

            # 创建目标相位的控制门
            from qiskit.circuit.library import U1Gate
            phase = np.pi / 4  # 待估计的相位
            unitary = U1Gate(phase)

            qpe_circuit = PhaseEstimation(n_estimation_qubits, unitary)
            qpe_circuit.measure_all()

            qasm_str = qpe_circuit.qasm()
            self._test_circuit_optimization("QPE", qasm_str, circuit=qpe_circuit)

        else:
            # 手动创建简化的QPE电路
            n_qubits = 3
            qpe_circuit = self._create_manual_qpe(n_qubits)
            qasm_str = self._qibo_to_qasm(qpe_circuit, "QPE Circuit")
            self._test_circuit_optimization("QPE", qasm_str, circuit=qpe_circuit)

    def test_shor(self):
        """测试小规模Shor算法."""
        if QISKIT_AVAILABLE:
            # 创建小规模的Shor算法电路 (N=15)
            n_counting_qubits = 4
            from qiskit.circuit.library import ModularExpNode

            # 简化的Shor算法 - 只包含模指数部分
            shor_circuit = QuantumCircuit(n_counting_qubits + 2)

            # 初始化计数寄存器
            for i in range(n_counting_qubits):
                shor_circuit.h(i)

            # 添加一些受控U门
            for i in range(n_counting_qubits):
                angle = 2 * np.pi / 15 * (2 ** i)  # 2^i mod 15
                shor_circuit.cp(angle, i, n_counting_qubits)

            shor_circuit.measure_all()
            qasm_str = shor_circuit.qasm()

            self._test_circuit_optimization("Shor", qasm_str, circuit=shor_circuit)

        else:
            print("⚠️  Qiskit不可用，跳过Shor测试")

    def test_hhl(self):
        """测试HHL算法."""
        # HHL算法非常复杂，我们创建一个简化版本
        if QISKIT_AVAILABLE:
            # 创建简化的HHL电路组件
            n_qubits = 4  # 简化版本

            hhl_circuit = QuantumCircuit(n_qubits)

            # 状态制备 (简化)
            hhl_circuit.h(0)
            hhl_circuit.cx(0, 1)

            # 量子相位估计部分 (简化)
            for i in range(1, 3):
                hhl_circuit.h(i)
                hhl_circuit.cp(np.pi / (2 ** i), 0, i)

            # 受控旋转 (简化)
            hhl_circuit.ccx(1, 2, 3)

            # 解码部分 (简化)
            hhl_circuit.h(1)
            hhl_circuit.h(2)

            hhl_circuit.measure_all()
            qasm_str = hhl_circuit.qasm()

            self._test_circuit_optimization("HHL", qasm_str, circuit=hhl_circuit)

        else:
            print("⚠️  Qiskit不可用，跳过HHL测试")

    def _create_manual_qpe(self, n_qubits: int) -> QiboCircuit:
        """创建手动QPE电路."""
        if not QIBO_AVAILABLE:
            raise RuntimeError("Qibo不可用")

        n_estimation = n_qubits - 1
        qpe_circuit = QiboCircuit(n_qubits + n_estimation)

        # 初始化估计寄存器
        for i in range(n_estimation):
            qpe_circuit.add(gates.H(i))

        # 应用受控U操作
        phase = np.pi / 4
        for i in range(n_estimation):
            power = 2 ** i
            for _ in range(power):
                qpe_circuit.add(gates.CU1(phase, i, n_qubits - 1))

        # 应用逆QFT
        for target in range(n_estimation):
            qpe_circuit.add(gates.H(target))

            for control in range(target + 1, n_estimation):
                angle = -np.pi / (2 ** (control - target))
                qpe_circuit.add(gates.CU1(angle, control, target))

        return qpe_circuit

    def _test_circuit_optimization(self, algorithm_name: str, qasm_str: str, circuit: Any = None):
        """测试电路优化."""
        strategies = ["none", "qiskit_only", "sim_fusion", "hybrid"]
        results = {}

        print(f"  测试策略: {strategies}")

        for strategy in strategies:
            try:
                start_time = time.time()
                optimized, stats = optimize_circuit_with_stats(
                    qasm_str,
                    strategy=strategy,
                    verbose=False
                )
                total_time = time.time() - start_time

                results[strategy] = {
                    'success': True,
                    'stats': stats,
                    'optimized_circuit': optimized,
                    'total_time': total_time
                }

                print(f"    {strategy:15}: 门减少 {stats['gate_reduction_percent']:5.1f}% "
                      f"时间 {total_time:.4f}s "
                      f"原始{stats['original_gates']:3}→优化{stats['optimized_gates']:3}")

            except Exception as e:
                results[strategy] = {
                    'success': False,
                    'error': str(e),
                    'total_time': time.time() - start_time
                }
                print(f"    {strategy:15}: ❌ 错误 - {str(e)[:50]}")

        # 存储结果
        self.results[algorithm_name] = results

    def _qibo_to_qasm(self, circuit: QiboCircuit, name: str) -> str:
        """将Qibo电路转换为QASM字符串."""
        if not QIBO_AVAILABLE:
            return ""

        n_qubits = circuit.nqubits
        qasm_lines = [
            f"OPENQASM 2.0;",
            f'include "qelib1.inc";',
            f"qreg q[{n_qubits}];"
        ]

        gate_map = {
            'H': 'h',
            'X': 'x',
            'Y': 'y',
            'Z': 'z',
            'CNOT': 'cx',
            'CZ': 'cz',
            'SWAP': 'swap',
            'RX': 'rx',
            'RY': 'ry',
            'RZ': 'rz',
            'U1': 'u1',
            'U2': 'u2',
            'U3': 'u3',
            'CU1': 'cu1'
        }

        for gate in circuit.queue:
            gate_name = gate.__class__.__name__
            qubits = gate.qubits

            if gate_name in gate_map:
                qasm_gate = gate_map[gate_name]

                if gate_name in ['H', 'X', 'Y', 'Z', 'S', 'T']:
                    qasm_lines.append(f"{qasm_gate} q[{qubits[0]}];")
                elif gate_name in ['CNOT', 'CZ', 'SWAP']:
                    qasm_lines.append(f"{qasm_gate} q[{qubits[0]}], q[{qubits[1]}];")
                elif gate_name in ['RX', 'RY', 'RZ']:
                    if hasattr(gate, 'theta'):
                        qasm_lines.append(f"{qasm_gate}({gate.theta:.6f}) q[{qubits[0]}];")
                elif gate_name == 'U1':
                    if hasattr(gate, 'phi'):
                        qasm_lines.append(f"u1({gate.phi:.6f}) q[{qubits[0]}];")
                elif gate_name == 'CU1':
                    if hasattr(gate, 'phi'):
                        qasm_lines.append(f"cu1({gate.phi:.6f}) q[{qubits[0]}], q[{qubits[1]}];")

        return "\n".join(qasm_lines)

    def generate_summary_report(self):
        """生成总结报告."""
        print("\n" + "=" * 80)
        print("📊 量子算法性能测试总结报告")
        print("=" * 80)

        if not self.results:
            print("没有测试结果")
            return

        # 统计各算法的成功率
        strategies = ["none", "qiskit_only", "sim_fusion", "hybrid"]
        success_rates = {strategy: [] for strategy in strategies}
        gate_reductions = {strategy: [] for strategy in strategies}

        for alg_name, results in self.results.items():
            print(f"\n🔍 {alg_name} 算法结果:")
            print("-" * 50)

            for strategy in strategies:
                if strategy in results and results[strategy]['success']:
                    stats = results[strategy]['stats']
                    success_rates[strategy].append(True)
                    gate_reductions[strategy].append(stats['gate_reduction_percent'])
                    print(f"  {strategy:15}: ✅ 门减少 {stats['gate_reduction_percent']:5.1f}% "
                          f"时间 {results[strategy]['total_time']:.4f}s")
                else:
                    success_rates[strategy].append(False)
                    print(f"  {strategy:15}: ❌ 失败")

        # 计算总体统计
        print(f"\n📈 总体统计:")
        print("-" * 50)

        total_algorithms = len(self.results)
        for strategy in strategies:
            success_count = sum(success_rates[strategy])
            success_rate = success_count / total_algorithms * 100

            if gate_reductions[strategy]:
                avg_reduction = np.mean(gate_reductions[strategy])
                max_reduction = np.max(gate_reductions[strategy])
                min_reduction = np.min(gate_reductions[strategy])
            else:
                avg_reduction = max_reduction = min_reduction = 0

            print(f"{strategy:15}: 成功率 {success_rate:.1f}% "
                  f"| 平均门减少 {avg_reduction:.1f}% "
                  f"(最大 {max_reduction:.1f}%, 最小 {min_reduction:.1f}%)")

        # 找出最佳性能
        if gate_reductions["qiskit_only"]:
            best_alg = max(self.results.keys(),
                         key=lambda k: self.results[k].get("qiskit_only", {}).get("stats", {}).get("gate_reduction_percent", 0))
            best_reduction = self.results[best_alg]["qiskit_only"]["stats"]["gate_reduction_percent"]
            print(f"\n🏆 最佳优化效果: {best_alg} 算法，门减少 {best_reduction:.1f}%")

        # 绘制性能比较图
        self._plot_performance_comparison()

    def _plot_performance_comparison(self):
        """绘制性能比较图."""
        try:
            strategies = ["none", "qiskit_only", "sim_fusion", "hybrid"]
            alg_names = list(self.results.keys())

            if not alg_names:
                return

            # 准备数据
            reduction_data = []
            success_data = []

            for alg_name in alg_names:
                alg_reductions = []
                alg_successes = []

                for strategy in strategies:
                    if strategy in self.results[alg_name] and self.results[alg_name][strategy]['success']:
                        alg_reductions.append(self.results[alg_name][strategy]['stats']['gate_reduction_percent'])
                        alg_successes.append(True)
                    else:
                        alg_reductions.append(0)
                        alg_successes.append(False)

                reduction_data.append(alg_reductions)
                success_data.append(alg_successes)

            # 创建图表
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

            # 门减少比较图
            reduction_array = np.array(reduction_data)
            im1 = ax1.imshow(reduction_array, cmap='RdYlGn', aspect='auto')
            ax1.set_xticks(range(len(strategies)))
            ax1.set_xticklabels(strategies, rotation=45)
            ax1.set_yticks(range(len(alg_names)))
            ax1.set_yticklabels(alg_names)
            ax1.set_title('门减少百分比 (%)')
            plt.colorbar(im1, ax=ax1, label='Reduction %')

            # 添加数值标签
            for i in range(len(alg_names)):
                for j in range(len(strategies)):
                    text = ax1.text(j, i, f'{reduction_array[i, j]:.1f}',
                                   ha="center", va="center", color="black")

            # 成功率热图
            success_array = np.array(success_data, dtype=int)
            im2 = ax2.imshow(success_array, cmap='RdYlGn', aspect='auto')
            ax2.set_xticks(range(len(strategies)))
            ax2.set_xticklabels(strategies, rotation=45)
            ax2.set_yticks(range(len(alg_names)))
            ax2.set_yticklabels(alg_names)
            ax2.set_title('优化成功率')
            plt.colorbar(im2, ax=ax2, label='Success (1=Yes, 0=No)')

            plt.tight_layout()

            # 保存图表
            timestamp = time.strftime('%Y%m%d_%H%M%S')
            plot_filename = f"quantum_algorithms_performance_{timestamp}.png"
            plt.savefig(plot_filename, dpi=300, bbox_inches='tight')
            print(f"\n📈 性能对比图已保存到: {plot_filename}")

            plt.show()

        except Exception as e:
            print(f"⚠️  无法绘制图表: {e}")


def main():
    """主函数."""
    print("🚀 经典量子算法性能测试开始")
    print("=" * 60)

    test_suite = QuantumAlgorithmTestSuite()
    test_suite.run_all_tests()


if __name__ == "__main__":
    main()