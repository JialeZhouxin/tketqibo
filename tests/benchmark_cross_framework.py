"""跨框架量子电路优化器性能基准测试.

这个模块提供了全面的性能基准测试，用于评估跨框架优化器的性能表现。
"""

import time
import sys
import os
import statistics
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
import matplotlib.pyplot as plt
import numpy as np

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

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
    from qiskit import transpile
    QISKIT_AVAILABLE = True
except ImportError:
    QISKIT_AVAILABLE = False
    QiskitCircuit = None
    transpile = None

try:
    from src.cross_framework_interface import (
        optimize_circuit,
        optimize_qasm,
        optimize_qiskit,
        optimize_qibo,
        batch_optimize,
        compare_strategies
    )
    INTERFACE_AVAILABLE = True
except ImportError:
    INTERFACE_AVAILABLE = False


class BenchmarkResult:
    """基准测试结果类."""

    def __init__(self, name: str):
        """初始化基准结果.

        Args:
            name: 测试名称
        """
        self.name = name
        self.conversion_times: List[float] = []
        self.optimization_times: List[float] = []
        self.total_times: List[float] = []
        self.original_gate_counts: List[int] = []
        self.optimized_gate_counts: List[int] = []
        self.original_depths: List[int] = []
        self.optimized_depths: List[int] = []
        self.error_count: int = 0

    def add_measurement(self, conversion_time: float, optimization_time: float,
                       total_time: float, original_gates: int, optimized_gates: int,
                       original_depth: int, optimized_depth: int):
        """添加一次测量结果."""
        self.conversion_times.append(conversion_time)
        self.optimization_times.append(optimization_time)
        self.total_times.append(total_time)
        self.original_gate_counts.append(original_gates)
        self.optimized_gate_counts.append(optimized_gates)
        self.original_depths.append(original_depth)
        self.optimized_depths.append(optimized_depth)

    def add_error(self):
        """记录一次错误."""
        self.error_count += 1

    @property
    def success_rate(self) -> float:
        """成功率."""
        total_runs = len(self.conversion_times) + self.error_count
        if total_runs == 0:
            return 0.0
        return len(self.conversion_times) / total_runs

    @property
    def avg_conversion_time(self) -> float:
        """平均转换时间."""
        return statistics.mean(self.conversion_times) if self.conversion_times else 0.0

    @property
    def avg_optimization_time(self) -> float:
        """平均优化时间."""
        return statistics.mean(self.optimization_times) if self.optimization_times else 0.0

    @property
    def avg_total_time(self) -> float:
        """平均总时间."""
        return statistics.mean(self.total_times) if self.total_times else 0.0

    @property
    def avg_gate_reduction(self) -> float:
        """平均门减少数量."""
        if not self.original_gate_counts or not self.optimized_gate_counts:
            return 0.0
        return statistics.mean([orig - opt for orig, opt in
                             zip(self.original_gate_counts, self.optimized_gate_counts)])

    @property
    def avg_gate_reduction_percent(self) -> float:
        """平均门减少百分比."""
        if not self.original_gate_counts or not self.optimized_gate_counts:
            return 0.0
        reductions = []
        for orig, opt in zip(self.original_gate_counts, self.optimized_gate_counts):
            if orig > 0:
                reductions.append(((orig - opt) / orig) * 100)
        return statistics.mean(reductions) if reductions else 0.0

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典."""
        return {
            'name': self.name,
            'success_rate': self.success_rate,
            'avg_conversion_time': self.avg_conversion_time,
            'avg_optimization_time': self.avg_optimization_time,
            'avg_total_time': self.avg_total_time,
            'avg_gate_reduction': self.avg_gate_reduction,
            'avg_gate_reduction_percent': self.avg_gate_reduction_percent,
            'error_count': self.error_count,
            'total_runs': len(self.conversion_times) + self.error_count
        }

    def __str__(self) -> str:
        """字符串表示."""
        return (f"{self.name}:\n"
                f"  成功率: {self.success_rate:.1%}\n"
                f"  平均总时间: {self.avg_total_time:.4f}s\n"
                f"  平均门减少: {self.avg_gate_reduction:.1f} ({self.avg_gate_reduction_percent:.1f}%)\n"
                f"  错误次数: {self.error_count}")


class CrossFrameworkBenchmark:
    """跨框架优化器基准测试类."""

    def __init__(self):
        """初始化基准测试."""
        self.results: Dict[str, BenchmarkResult] = {}
        self._test_circuits = {}

    def create_test_circuits(self) -> Dict[str, List[Any]]:
        """创建测试电路."""
        circuits = {}

        if QIBO_AVAILABLE:
            # Qibo测试电路
            circuits['qibo_simple'] = self._create_qibo_simple_circuits()
            circuits['qibo_medium'] = self._create_qibo_medium_circuits()
            circuits['qibo_complex'] = self._create_qibo_complex_circuits()

        if QISKIT_AVAILABLE:
            # Qiskit测试电路
            circuits['qiskit_simple'] = self._create_qiskit_simple_circuits()
            circuits['qiskit_medium'] = self._create_qiskit_medium_circuits()
            circuits['qiskit_complex'] = self._create_qiskit_complex_circuits()

        # QASM测试电路
        circuits['qasm_simple'] = self._create_qasm_simple_circuits()
        circuits['qasm_medium'] = self._create_qasm_medium_circuits()
        circuits['qasm_complex'] = self._create_qasm_complex_circuits()

        return circuits

    def _create_qibo_simple_circuits(self) -> List[QiboCircuit]:
        """创建简单Qibo电路."""
        circuits = []

        # Bell态电路
        bell = QiboCircuit(2)
        bell.add(gates.H(0))
        bell.add(gates.CNOT(0, 1))
        circuits.append(bell)

        # 单量子比特门电路
        single = QiboCircuit(1)
        single.add(gates.H(0))
        single.add(gates.X(0))
        single.add(gates.Y(0))
        circuits.append(single)

        return circuits

    def _create_qibo_medium_circuits(self) -> List[QiboCircuit]:
        """创建中等复杂度Qibo电路."""
        circuits = []

        # GHZ态电路
        ghz = QiboCircuit(3)
        ghz.add(gates.H(0))
        ghz.add(gates.CNOT(0, 1))
        ghz.add(gates.CNOT(0, 2))
        circuits.append(ghz)

        # 参数化电路
        param_circuit = QiboCircuit(2)
        param_circuit.add(gates.H(0))
        param_circuit.add(gates.RX(np.pi/4, 1))
        param_circuit.add(gates.CNOT(0, 1))
        param_circuit.add(gates.RY(np.pi/3, 1))
        circuits.append(param_circuit)

        return circuits

    def _create_qibo_complex_circuits(self) -> List[QiboCircuit]:
        """创建复杂Qibo电路."""
        circuits = []

        # 随机电路
        import random
        random.seed(42)

        for _ in range(3):
            n_qubits = random.randint(3, 5)
            n_gates = random.randint(15, 25)
            circuit = QiboCircuit(n_qubits)

            for _ in range(n_gates):
                gate_type = random.choice(['H', 'X', 'Y', 'Z', 'RX', 'RY', 'RZ', 'CNOT'])
                if gate_type == 'H':
                    circuit.add(gates.H(random.randint(0, n_qubits - 1)))
                elif gate_type == 'X':
                    circuit.add(gates.X(random.randint(0, n_qubits - 1)))
                elif gate_type == 'Y':
                    circuit.add(gates.Y(random.randint(0, n_qubits - 1)))
                elif gate_type == 'Z':
                    circuit.add(gates.Z(random.randint(0, n_qubits - 1)))
                elif gate_type in ['RX', 'RY', 'RZ']:
                    angle = random.uniform(0, 2 * np.pi)
                    qubit = random.randint(0, n_qubits - 1)
                    if gate_type == 'RX':
                        circuit.add(gates.RX(angle, qubit))
                    elif gate_type == 'RY':
                        circuit.add(gates.RY(angle, qubit))
                    else:
                        circuit.add(gates.RZ(angle, qubit))
                elif gate_type == 'CNOT' and n_qubits >= 2:
                    control = random.randint(0, n_qubits - 2)
                    target = random.randint(control + 1, n_qubits - 1)
                    circuit.add(gates.CNOT(control, target))

            circuits.append(circuit)

        return circuits

    def _create_qiskit_simple_circuits(self) -> List[QiskitCircuit]:
        """创建简单Qiskit电路."""
        circuits = []

        # Bell态电路
        bell = QiskitCircuit(2)
        bell.h(0)
        bell.cx(0, 1)
        circuits.append(bell)

        return circuits

    def _create_qiskit_medium_circuits(self) -> List[QiskitCircuit]:
        """创建中等复杂度Qiskit电路."""
        circuits = []

        # GHZ态电路
        ghz = QiskitCircuit(3)
        ghz.h(0)
        ghz.cx(0, 1)
        ghz.cx(0, 2)
        circuits.append(ghz)

        return circuits

    def _create_qiskit_complex_circuits(self) -> List[QiskitCircuit]:
        """创建复杂Qiskit电路."""
        circuits = []

        # 多层电路
        complex_circuit = QiskitCircuit(4)
        for layer in range(3):
            complex_circuit.h(range(4))
            complex_circuit.cx(0, 1)
            complex_circuit.cx(1, 2)
            complex_circuit.cx(2, 3)
            complex_circuit.rz(np.pi/4, range(4))

        circuits.append(complex_circuit)

        return circuits

    def _create_qasm_simple_circuits(self) -> List[str]:
        """创建简单QASM电路."""
        circuits = []

        # Bell态
        bell_qasm = """OPENQASM 2.0;
include "qelib1.inc";
qreg q[2];
h q[0];
cx q[0],q[1];
"""
        circuits.append(bell_qasm)

        return circuits

    def _create_qasm_medium_circuits(self) -> List[str]:
        """创建中等复杂度QASM电路."""
        circuits = []

        # GHZ态
        ghz_qasm = """OPENQASM 2.0;
include "qelib1.inc";
qreg q[3];
h q[0];
cx q[0],q[1];
cx q[0],q[2];
"""
        circuits.append(ghz_qasm)

        return circuits

    def _create_qasm_complex_circuits(self) -> List[str]:
        """创建复杂QASM电路."""
        circuits = []

        # 复杂电路
        complex_qasm = """OPENQASM 2.0;
include "qelib1.inc";
qreg q[4];
h q[0];
h q[1];
h q[2];
h q[3];
cx q[0],q[1];
cx q[1],q[2];
cx q[2],q[3];
rz(1.5708) q[0];
rz(1.5708) q[1];
rz(1.5708) q[2];
rz(1.5708) q[3];
"""
        circuits.append(complex_qasm)

        return circuits

    def run_benchmark(self, circuit_type: str, circuit_name: str,
                     strategy: str = "qiskit_only", num_runs: int = 5) -> BenchmarkResult:
        """运行单个基准测试.

        Args:
            circuit_type: 电路类型 ('qibo', 'qiskit', 'qasm')
            circuit_name: 电路名称 ('simple', 'medium', 'complex')
            strategy: 优化策略
            num_runs: 运行次数

        Returns:
            基准测试结果
        """
        if not INTERFACE_AVAILABLE:
            raise RuntimeError("Interface not available")

        test_key = f"{circuit_type}_{circuit_name}"
        if test_key not in self._test_circuits:
            self._test_circuits = self.create_test_circuits()

        circuits = self._test_circuits.get(test_key, [])
        if not circuits:
            raise ValueError(f"No test circuits found for {test_key}")

        result = BenchmarkResult(f"{circuit_type}_{circuit_name}_{strategy}")

        for circuit in circuits:
            for _ in range(num_runs):
                try:
                    start_time = time.time()

                    # 优化电路
                    optimized, stats = optimize_circuit_with_stats(
                        circuit,
                        strategy=strategy,
                        verbose=False
                    )

                    total_time = time.time() - start_time

                    # 获取原始电路信息
                    if circuit_type == 'qibo':
                        original_gates = circuit.ngates
                        original_depth = circuit.depth()
                    elif circuit_type == 'qiskit':
                        original_gates = len(circuit)
                        original_depth = circuit.depth()
                    else:  # QASM
                        # 粗略计算
                        lines = circuit.strip().split('\n')
                        gate_lines = [line for line in lines
                                   if any(gate in line for gate in ['h', 'x', 'y', 'z', 'cx', 'cz', 'rx', 'ry', 'rz'])
                                   and not line.strip().startswith(('qreg', 'creg', 'include', 'OPENQASM'))]
                        original_gates = len(gate_lines)
                        original_depth = original_gates // 2  # 粗略估计

                    optimized_gates = optimized.ngates
                    optimized_depth = optimized.depth()

                    conversion_time = stats.get('conversion_time', 0.0)
                    optimization_time = stats.get('optimization_time', 0.0)

                    result.add_measurement(
                        conversion_time, optimization_time, total_time,
                        original_gates, optimized_gates,
                        original_depth, optimized_depth
                    )

                except Exception as e:
                    print(f"Error in benchmark: {e}")
                    result.add_error()

        return result

    def run_comprehensive_benchmark(self) -> Dict[str, BenchmarkResult]:
        """运行全面的基准测试.

        Returns:
            所有基准测试结果
        """
        if not INTERFACE_AVAILABLE:
            raise RuntimeError("Interface not available")

        circuit_types = ['qibo', 'qiskit', 'qasm']
        circuit_complexities = ['simple', 'medium', 'complex']
        strategies = ['none', 'qiskit_only']

        all_results = {}

        for circuit_type in circuit_types:
            for complexity in circuit_complexities:
                test_key = f"{circuit_type}_{complexity}"

                # 检查是否有测试电路
                self._test_circuits = self.create_test_circuits()
                if test_key not in self._test_circuits or not self._test_circuits[test_key]:
                    print(f"Skipping {test_key} - no test circuits available")
                    continue

                for strategy in strategies:
                    benchmark_name = f"{test_key}_{strategy}"
                    print(f"Running benchmark: {benchmark_name}")

                    try:
                        result = self.run_benchmark(circuit_type, complexity, strategy, num_runs=3)
                        all_results[benchmark_name] = result
                        print(f"  ✅ {result}")
                    except Exception as e:
                        print(f"  ❌ Error: {e}")

        return all_results

    def compare_strategies_benchmark(self, circuit_type: str, circuit_name: str,
                                   strategies: Optional[List[str]] = None) -> Dict[str, BenchmarkResult]:
        """比较不同优化策略的性能.

        Args:
            circuit_type: 电路类型
            circuit_name: 电路名称
            strategies: 要比较的策略列表

        Returns:
            各策略的基准测试结果
        """
        if strategies is None:
            strategies = ['none', 'qiskit_only', 'sim_fusion', 'hybrid']

        results = {}
        for strategy in strategies:
            try:
                result = self.run_benchmark(circuit_type, circuit_name, strategy, num_runs=5)
                results[strategy] = result
            except Exception as e:
                print(f"Error running benchmark for strategy {strategy}: {e}")

        return results

    def generate_performance_report(self, results: Dict[str, BenchmarkResult]) -> str:
        """生成性能报告.

        Args:
            results: 基准测试结果

        Returns:
            性能报告字符串
        """
        report = []
        report.append("=" * 80)
        report.append("跨框架量子电路优化器性能报告")
        report.append("=" * 80)
        report.append(f"测试时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"总测试数: {len(results)}")
        report.append("")

        # 总体统计
        all_success_rates = [r.success_rate for r in results.values()]
        all_total_times = [r.avg_total_time for r in results.values()]
        all_gate_reductions = [r.avg_gate_reduction_percent for r in results.values()]

        if all_success_rates:
            report.append("📊 总体统计:")
            report.append(f"  平均成功率: {statistics.mean(all_success_rates):.1%}")
            report.append(f"  平均执行时间: {statistics.mean(all_total_times):.4f}s")
            report.append(f"  平均门减少率: {statistics.mean(all_gate_reductions):.1f}%")
            report.append("")

        # 按类别分组
        categories = {}
        for name, result in results.items():
            parts = name.split('_')
            if len(parts) >= 2:
                category = '_'.join(parts[:-1])
                if category not in categories:
                    categories[category] = []
                categories[category].append(result)

        # 按类别显示结果
        for category, cat_results in categories.items():
            report.append(f"🔍 {category.upper()}:")
            for result in cat_results:
                report.append(f"  {result.name.replace(category + '_', '')}:")
                report.append(f"    成功率: {result.success_rate:.1%}")
                report.append(f"    平均时间: {result.avg_total_time:.4f}s")
                report.append(f"    门减少: {result.avg_gate_reduction:.1f} ({result.avg_gate_reduction_percent:.1f}%)")
            report.append("")

        # 最佳性能
        if results:
            best_time = min(results.values(), key=lambda r: r.avg_total_time)
            best_reduction = max(results.values(), key=lambda r: r.avg_gate_reduction_percent)
            best_success = max(results.values(), key=lambda r: r.success_rate)

            report.append("🏆 最佳性能:")
            report.append(f"  最快执行: {best_time.name} ({best_time.avg_total_time:.4f}s)")
            report.append(f"  最大优化: {best_reduction.name} ({best_reduction.avg_gate_reduction_percent:.1f}%)")
            report.append(f"  最高成功率: {best_success.name} ({best_success.success_rate:.1%})")
            report.append("")

        # 建议
        report.append("💡 建议:")
        if all_success_rates and statistics.mean(all_success_rates) < 0.9:
            report.append("  - 某些测试的成功率较低，建议检查错误日志")
        if all_total_times and statistics.mean(all_total_times) > 1.0:
            report.append("  - 执行时间较长，考虑优化算法或使用更快的优化级别")
        if all_gate_reductions and statistics.mean(all_gate_reductions) < 5.0:
            report.append("  - 门减少率较低，可能需要更激进的优化策略")

        return "\n".join(report)

    def save_results_to_file(self, results: Dict[str, BenchmarkResult], filename: str):
        """保存结果到文件.

        Args:
            results: 基准测试结果
            filename: 输出文件名
        """
        # 生成JSON格式结果
        import json
        json_results = {name: result.to_dict() for name, result in results.items()}

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(json_results, f, indent=2, ensure_ascii=False)

    def plot_performance_comparison(self, results: Dict[str, BenchmarkResult],
                                  save_path: Optional[str] = None):
        """绘制性能比较图.

        Args:
            results: 基准测试结果
            save_path: 保存路径
        """
        if not results:
            print("No results to plot")
            return

        # 准备数据
        names = []
        times = []
        reductions = []
        success_rates = []

        for name, result in results.items():
            names.append(name.replace('_', ' ').title())
            times.append(result.avg_total_time)
            reductions.append(result.avg_gate_reduction_percent)
            success_rates.append(result.success_rate * 100)

        # 创建子图
        fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(15, 5))

        # 执行时间比较
        ax1.bar(names, times)
        ax1.set_title('平均执行时间')
        ax1.set_ylabel('时间 (秒)')
        ax1.tick_params(axis='x', rotation=45)

        # 优化效果比较
        ax2.bar(names, reductions, color='orange')
        ax2.set_title('平均门减少率')
        ax2.set_ylabel('减少率 (%)')
        ax2.tick_params(axis='x', rotation=45)

        # 成功率比较
        ax3.bar(names, success_rates, color='green')
        ax3.set_title('成功率')
        ax3.set_ylabel('成功率 (%)')
        ax3.tick_params(axis='x', rotation=45)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()


def main():
    """主函数 - 运行基准测试."""
    print("🚀 开始跨框架量子电路优化器基准测试")
    print("=" * 60)

    if not INTERFACE_AVAILABLE:
        print("❌ 接口模块不可用，请确保安装了所需依赖")
        return

    if not QIBO_AVAILABLE:
        print("⚠️  Qibo不可用，相关测试将被跳过")

    if not QISKIT_AVAILABLE:
        print("⚠️  Qiskit不可用，相关测试将被跳过")

    try:
        benchmark = CrossFrameworkBenchmark()

        print("📊 运行全面基准测试...")
        results = benchmark.run_comprehensive_benchmark()

        print("\n📝 生成性能报告...")
        report = benchmark.generate_performance_report(results)
        print(report)

        # 保存结果
        timestamp = time.strftime('%Y%m%d_%H%M%S')

        json_filename = f"benchmark_results_{timestamp}.json"
        benchmark.save_results_to_file(results, json_filename)
        print(f"\n💾 结果已保存到: {json_filename}")

        # 生成报告文件
        report_filename = f"benchmark_report_{timestamp}.txt"
        with open(report_filename, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"📄 报告已保存到: {report_filename}")

        # 绘制图表（如果matplotlib可用）
        try:
            plot_filename = f"benchmark_plot_{timestamp}.png"
            benchmark.plot_performance_comparison(results, save_path=plot_filename)
            print(f"📈 性能图表已保存到: {plot_filename}")
        except Exception as e:
            print(f"⚠️  无法生成图表: {e}")

    except Exception as e:
        print(f"❌ 基准测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()