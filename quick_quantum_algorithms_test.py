"""快速量子算法性能测试.

这个脚本提供了10种经典量子算法的快速测试，展示跨框架优化器的性能。
"""

import sys
import time
import numpy as np
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / 'src'))

# 动态导入依赖
try:
    from qibo import Circuit as QiboCircuit, gates
    QIBO_AVAILABLE = True
except ImportError:
    QIBO_AVAILABLE = False
    QiboCircuit = None
    gates = None

try:
    from qiskit import QuantumCircuit as QiskitCircuit
    from qiskit.circuit.library import QFT, TwoLocal
    QISKIT_AVAILABLE = True
except ImportError:
    QISKIT_AVAILABLE = False
    QiskitCircuit = None

try:
    from src.cross_framework_interface import (
        optimize_circuit,
        optimize_circuit_with_stats,
        quick_optimize
    )
    INTERFACE_AVAILABLE = True
except ImportError:
    INTERFACE_AVAILABLE = False


class QuantumAlgorithmQuickTest:
    """快速量子算法测试类."""

    def __init__(self):
        """初始化测试."""
        self.results = {}

    def run_all_tests(self):
        """运行所有快速测试."""
        print("🚀 快速量子算法性能测试")
        print("=" * 50)

        if not INTERFACE_AVAILABLE:
            print("❌ 跨框架接口不可用")
            return

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
            try:
                print(f"\n🔍 {alg_name}")
                test_func()
            except Exception as e:
                print(f"❌ {alg_name} 测试失败: {e}")

        self.print_summary()

    def test_vqe(self):
        """测试VQE算法."""
        if not QIBO_AVAILABLE:
            print("  ⚠️ Qibo不可用，跳过")
            return

        # 简化的VQE电路
        circuit = QiboCircuit(4)
        # 参数化层
        for i in range(4):
            circuit.add(gates.RY(np.random.uniform(0, 2*np.pi), i))
        # 纠缠层
        for i in range(3):
            circuit.add(gates.CNOT(i, i+1))
        # 另一组参数化门
        for i in range(4):
            circuit.add(gates.RZ(np.random.uniform(0, 2*np.pi), i))

        self._test_optimization("VQE", circuit)

    def test_qaoa(self):
        """测试QAOA算法."""
        if not QIBO_AVAILABLE:
            print("  ⚠️ Qibo不可用，跳过")
            return

        n_qubits = 4
        n_layers = 2
        circuit = QiboCircuit(n_qubits)

        # 初始态
        for i in range(n_qubits):
            circuit.add(gates.H(i))

        # QAOA层
        for layer in range(n_layers):
            # 问题哈密顿量（简化版）
            for i in range(n_qubits-1):
                circuit.add(gates.CZ(i, i+1))
            # 混合哈密顿量
            for i in range(n_qubits):
                circuit.add(gates.RX(np.random.uniform(0, np.pi), i))

        self._test_optimization("QAOA", circuit)

    def test_vqc(self):
        """测试VQC算法."""
        if QISKIT_AVAILABLE:
            # 使用Qiskit的TwoLocal
            circuit = TwoLocal(3, ['ry', 'rz'], 'cx', reps=2)
            circuit = circuit.bind_parameters(np.random.uniform(-np.pi, np.pi, circuit.num_parameters))
            self._test_optimization("VQC", circuit)

        elif QIBO_AVAILABLE:
            # 手动创建VQC
            circuit = QiboCircuit(3)
            # 层1: RY + CX
            for i in range(3):
                circuit.add(gates.RY(np.random.uniform(-np.pi, np.pi), i))
            circuit.add(gates.CNOT(0, 1))
            circuit.add(gates.CNOT(1, 2))
            # 层2: RZ + CX
            for i in range(3):
                circuit.add(gates.RZ(np.random.uniform(-np.pi, np.pi), i))
            circuit.add(gates.CNOT(0, 1))
            circuit.add(gates.CNOT(1, 2))

            self._test_optimization("VQC", circuit)

        else:
            print("  ⚠️  Qiskit和Qibo都不可用，跳过")

    def test_grover(self):
        """测试Grover算法."""
        n_qubits = 3

        if QIBO_AVAILABLE:
            circuit = QiboCircuit(n_qubits)
            # 初始叠加态
            for i in range(n_qubits):
                circuit.add(gates.H(i))
            # Grover迭代（简化版）
            for i in range(n_qubits-1):
                circuit.add(gates.CNOT(i, i+1))
            # Oracle（简化）
            circuit.add(gates.Z(0))
            # 扩散算子（简化）
            for i in range(n_qubits):
                circuit.add(gates.H(i))
                circuit.add(gates.X(i))

            self._test_optimization("Grover", circuit)
        else:
            print("  ⚠️  Qibo不可用，跳过")

    def test_deutsch_jozsa(self):
        """测试Deutsch-Jozsa算法."""
        n_qubits = 3

        if QIBO_AVAILABLE:
            circuit = QiboCircuit(n_qubits + n_qubits)
            # 初始化
            for i in range(n_qubits):
                circuit.add(gates.H(i))
            # Oracle（平衡函数）
            circuit.add(gates.CNOT(0, 1))
            circuit.add(gates.CNOT(1, 2))
            # Hadamard
            for i in range(n_qubits):
                circuit.add(gates.H(i))

            self._test_optimization("Deutsch-Jozsa", circuit)
        else:
            print("  ⚠️  Qibo不可用，跳过")

    def test_bernstein_vazirani(self):
        """测试Bernstein-Vazirani算法."""
        n_qubits = 3
        secret_bits = [1, 0, 1]  # "101"

        if QIBO_AVAILABLE:
            circuit = QiboCircuit(n_qubits + n_qubits)
            # 初始化
            for i in range(n_qubits):
                circuit.add(gates.H(i))
            # Oracle
            for i, bit in enumerate(secret_bits):
                if bit == 1:
                    circuit.add(gates.CNOT(i, n_qubits-1))
            # Hadamard
            for i in range(n_qubits):
                circuit.add(gates.H(i))

            self._test_optimization("Bernstein-Vazirani", circuit)
        else:
            print("  ⚠️  Qibo不可用，跳过")

    def test_qft(self):
        """测试QFT算法."""
        if QISKIT_AVAILABLE:
            circuit = QFT(4, do_swaps=False)
            self._test_optimization("QFT", circuit)

        elif QIBO_AVAILABLE:
            # 手动创建QFT
            n_qubits = 3
            circuit = QiboCircuit(n_qubits)

            for target in range(n_qubits):
                circuit.add(gates.H(target))
                for control in range(target+1, n_qubits):
                    angle = np.pi / (2**(control-target))
                    circuit.add(gates.CU1(angle, control, target))

            self._test_optimization("QFT", circuit)
        else:
            print("  ⚠️  Qiskit和Qibo都不可用，跳过")

    def test_qpe(self):
        """测试QPE算法."""
        if QIBO_AVAILABLE:
            # 简化的QPE
            n_qubits = 4
            n_estimation = 3
            circuit = QiboCircuit(n_qubits)

            # 初始化估计寄存器
            for i in range(n_estimation):
                circuit.add(gates.H(i))

            # 受控U操作（简化）
            phase = np.pi/4
            for i in range(n_estimation):
                for _ in range(2**i):
                    circuit.add(gates.CU1(phase, i, n_estimation))

            self._test_optimization("QPE", circuit)
        else:
            print("  ⚠️  Qibo不可用，跳过")

    def test_shor(self):
        """测试Shor算法（简化版）。"""
        if QISKIT_AVAILABLE:
            # 简化的Shor算法组件
            circuit = QiskitCircuit(6)  # 4个计数比特 + 2个工作比特

            # 初始化计数寄存器
            for i in range(4):
                circuit.h(i)

            # 受控模指数运算（简化）
            for i in range(4):
                angle = 2*np.pi/15 * (2**i)  # 2^i mod 15
                circuit.cp(angle, i, 4)

            self._test_optimization("Shor", circuit)
        else:
            print("  ⚠️  Qiskit不可用，跳过")

    def test_hhl(self):
        """测试HHL算法（简化版）。"""
        if QISKIT_AVAILABLE:
            # 简化的HHL组件
            circuit = QiskitCircuit(4)

            # 状态制备（简化）
            circuit.h(0)
            circuit.cx(0, 1)

            # 量子相位估计部分（简化）
            for i in range(1, 3):
                circuit.h(i)
                circuit.cp(np.pi/(2**i), 0, i)

            # 受控旋转（简化）
            circuit.ccx(1, 2, 3)

            # 解码（简化）
            circuit.h(1)
            circuit.h(2)

            self._test_optimization("HHL", circuit)
        else:
            print("  ⚠️  Qiskit不可用，跳过")

    def _test_optimization(self, alg_name: str, circuit):
        """测试单个电路的优化."""
        try:
            # 转换为QASM（如果是Qibo电路）
            if QIBO_AVAILABLE and hasattr(circuit, 'ngates'):
                original_gates = circuit.ngates
                qasm_str = self._qibo_to_qasm(circuit)
            elif QISKIT_AVAILABLE and hasattr(circuit, 'num_qubits'):
                original_gates = len(circuit)
                qasm_str = circuit.qasm()
            else:
                original_gates = 0
                qasm_str = str(circuit)

            print(f"    原始电路: {original_gates} 个门")

            # 测试不同策略
            strategies = ["none", "qiskit_only"]
            results = {}

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
                        'optimized_gates': stats['optimized_gates'],
                        'reduction_percent': stats['gate_reduction_percent'],
                        'time': total_time
                    }

                    reduction = original_gates - stats['optimized_gates']
                    print(f"    {strategy:12}: {original_gates:3}→{stats['optimized_gates']:3} 门 "
                          f"({stats['gate_reduction_percent']:5.1f}%) "
                          f"时间 {total_time:.4f}s")

                except Exception as e:
                    results[strategy] = {
                        'success': False,
                        'error': str(e)
                    }
                    print(f"    {strategy:12}: ❌ {str(e)[:30]}")

            # 存储结果
            self.results[alg_name] = {
                'original_gates': original_gates,
                'results': results
            }

        except Exception as e:
            print(f"    ❌ 测试失败: {e}")

    def _qibo_to_qasm(self, circuit: QiboCircuit) -> str:
        """将Qibo电路转换为QASM字符串。"""
        n_qubits = circuit.nqubits
        qasm_lines = [
            f"OPENQASM 2.0;",
            f'include "qelib1.inc";',
            f"qreg q[{n_qubits}];"
        ]

        gate_map = {
            'H': 'h', 'X': 'x', 'Y': 'y', 'Z': 'z',
            'CNOT': 'cx', 'CZ': 'cz', 'SWAP': 'swap',
            'RX': 'rx', 'RY': 'ry', 'RZ': 'rz',
            'U1': 'u1', 'CU1': 'cu1'
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

    def print_summary(self):
        """打印总结报告。"""
        print("\n" + "=" * 60)
        print("📊 快速测试总结报告")
        print("=" * 60)

        if not self.results:
            print("没有测试结果")
            return

        # 统计各策略的优化效果
        strategies = ["none", "qiskit_only"]
        total_original_gates = sum(r['original_gates'] for r in self.results.values())

        print(f"\n📈 总体统计:")
        print(f"测试算法数: {len(self.results)}")
        print(f"总原始门数: {total_original_gates}")

        for strategy in strategies:
            success_count = 0
            total_optimized_gates = 0
            total_reduction_percent = 0

            for alg_name, result in self.results.items():
                if strategy in result['results'] and result['results'][strategy]['success']:
                    success_count += 1
                    total_optimized_gates += result['results'][strategy]['optimized_gates']
                    total_reduction_percent += result['results'][strategy]['reduction_percent']

            success_rate = success_count / len(self.results) * 100
            avg_reduction = total_reduction_percent / len(self.results) if self.results else 0

            print(f"\n{strategy:12}:")
            print(f"  成功率: {success_rate:.1f}% ({success_count}/{len(self.results)})")
            print(f"  平均门减少: {avg_reduction:.1f}%")
            if success_count > 0:
                print(f"  优化后总门数: {total_optimized_gates}")

        # 找出最佳优化效果
        best_reduction = 0
        best_algorithm = ""
        best_strategy = ""

        for alg_name, result in self.results.items():
            for strategy, stats in result['results'].items():
                if stats['success'] and stats['reduction_percent'] > best_reduction:
                    best_reduction = stats['reduction_percent']
                    best_algorithm = alg_name
                    best_strategy = strategy

        if best_algorithm:
            print(f"\n🏆 最佳优化效果:")
            print(f"  算法: {best_algorithm}")
            print(f"  策略: {best_strategy}")
            print(f"  门减少率: {best_reduction:.1f}%")

        print(f"\n💡 使用建议:")
        print(f"  - 对于大部分电路，使用 'qiskit_only' 策略获得良好效果")
        print(f"  - 'none' 策略仅用于格式转换验证")
        print(f"  - 大型电路可考虑更高级别的优化设置")


def main():
    """主函数。"""
    test_suite = QuantumAlgorithmQuickTest()
    test_suite.run_all_tests()


if __name__ == "__main__":
    main()